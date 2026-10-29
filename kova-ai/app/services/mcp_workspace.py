"""Private read-only KOVA command center, reusing the canonical registry."""

import asyncio
import copy
import hashlib
import html
import os
import time
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo
import httpx
from app.integrations.google_calendar import CONFIG_NAMES, day_window, read_calendar
from app.services.multi_repo_sync_service import MultiRepoSyncService

VIEW_URI = "ui://kova/dashboard.html"
VIEW_MIME = "text/html;profile=mcp-app"
DATE_SCHEMA = {
    "type": "string",
    "format": "date",
    "description": "YYYY-MM-DD in the server-configured timezone.",
}
DEFINITIONS = {
    "open_kova_dashboard": (
        "Open the private KOVA today view with source evidence and setup blockers.",
        {},
    ),
    "get_kova_status": (
        "Read Core availability and integration evidence; not a deployment certification.",
        {},
    ),
    "get_daily_digest": (
        "Read calendar and enabled GitHub repository metadata for a day. Does not infer priorities or completed work.",
        {"date": DATE_SCHEMA},
    ),
    "get_calendar_events": (
        "Read the approved owner calendar for one day; never accepts a different calendar.",
        {"date": DATE_SCHEMA},
    ),
    "get_integration_status": (
        "Probe GitHub and Google Calendar; show unsupported providers as not implemented.",
        {},
    ),
    "refresh_integration": (
        "Repeat a read-only GitHub or Calendar health probe, bypassing the short cache.",
        {"integration": {"type": "string", "enum": ["github", "google_calendar"]}},
    ),
    "list_kova_projects": (
        "List enabled project repository references from the canonical registry; not proof of deployment.",
        {},
    ),
    "get_project_status": (
        "Read GitHub metadata for one enabled project repository.",
        {"project_id": {"type": "string"}},
    ),
}
TOOLS = []
for name, (description, properties) in DEFINITIONS.items():
    schema = {"type": "object", "properties": properties, "additionalProperties": False}
    if name == "refresh_integration":
        schema["required"] = ["integration"]
    if name == "get_project_status":
        schema["required"] = ["project_id"]
    tool = {
        "name": name,
        "description": description,
        "inputSchema": schema,
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    }
    if name == "open_kova_dashboard":
        tool["_meta"] = {"ui": {"resourceUri": VIEW_URI}}
    TOOLS.append(tool)


class WorkspaceService:
    def __init__(self, transport=None):
        self.transport = transport
        self.cache = {}
        self.cache_generation = {}

    def projects(self):
        return [
            {
                "id": name,
                "title": name.split("/")[-1],
                "source": "github",
                "url": "https://github.com/" + name,
                "status": "configured",
            }
            for name in MultiRepoSyncService().get_enabled_repos()
        ]

    def today(self):
        try:
            return (
                datetime.now(ZoneInfo(os.getenv("KOVA_TIMEZONE", "America/New_York")))
                .date()
                .isoformat()
            )
        except (KeyError, ValueError) as error:
            raise RuntimeError("Server timezone needs configuration") from error

    def checked(self):
        return datetime.now(timezone.utc).isoformat()

    def fingerprint(self):
        names = (
            *CONFIG_NAMES,
            "GITHUB_TOKEN",
            "KOVA_TIMEZONE",
            "KOVA_REPOS_CONFIG",
            "KOVA_OWNER_API_KEY",
        )
        # Hash configuration; never expose credential values or reuse cache across identities.
        raw = repr([(name, os.getenv(name, "")) for name in names]) + repr(
            self.projects()
        )
        return hashlib.sha256(raw.encode()).hexdigest()

    async def cached(self, provider, day=None, refresh=False):
        key = (self.fingerprint(), provider, day)
        if refresh:
            self.cache_generation[provider] = self.cache_generation.get(provider, 0) + 1
            self.cache = {
                cache_key: value
                for cache_key, value in self.cache.items()
                if cache_key[1] != provider
            }
        generation = self.cache_generation.get(provider, 0)
        entry = self.cache.get(key)
        if entry and not refresh and time.monotonic() - entry[0] < 60:
            return {**copy.deepcopy(entry[1]), "cached": True}
        result = await (
            self.github()
            if provider == "github"
            else read_calendar(day or self.today(), self.transport)
        )
        if generation == self.cache_generation.get(provider, 0):
            if len(self.cache) >= 32:
                self.cache.clear()
            self.cache[key] = (time.monotonic(), copy.deepcopy(result))
        return {**result, "cached": False}

    async def github(self, project_id=None):
        base = {"source": "github", "last_checked": self.checked(), "projects": []}
        token = os.getenv("GITHUB_TOKEN", "").strip()
        if not token:
            return {
                **base,
                "status": "needs_connection",
                "reason": "Approved GitHub credentials are not configured.",
            }
        projects = self.projects()
        if project_id:
            projects = [project for project in projects if project["id"] == project_id]
        if not projects:
            return {
                **base,
                "status": "unknown",
                "reason": "No enabled projects are configured.",
            }
        results = []
        async with httpx.AsyncClient(
            timeout=10.0, follow_redirects=False, transport=self.transport
        ) as client:
            for project in projects:
                try:
                    response = await client.get(
                        "https://api.github.com/repos/" + project["id"],
                        headers={
                            "Authorization": "Bearer " + token,
                            "Accept": "application/vnd.github+json",
                        },
                    )
                    response.raise_for_status()
                    data = response.json()
                    if (
                        not isinstance(data, dict)
                        or data.get("full_name", "").casefold()
                        != project["id"].casefold()
                        or not isinstance(data.get("default_branch"), str)
                    ):
                        raise ValueError("Unverified repository response")
                    results.append(
                        {
                            **project,
                            "status": "connected",
                            "default_branch": data["default_branch"],
                            "updated_at": data.get("updated_at"),
                            "open_issues": data.get("open_issues_count"),
                        }
                    )
                except httpx.HTTPStatusError as error:
                    results.append(
                        {
                            **project,
                            "status": (
                                "needs_connection"
                                if error.response.status_code == 401
                                else "broken"
                            ),
                            "http_status": error.response.status_code,
                            "reason": "GitHub access could not be verified.",
                        }
                    )
                except (httpx.HTTPError, ValueError, TypeError, AttributeError):
                    results.append(
                        {
                            **project,
                            "status": "broken",
                            "reason": "GitHub read could not be verified.",
                        }
                    )
        return {
            **base,
            "projects": results,
            "status": (
                "connected"
                if all(item["status"] == "connected" for item in results)
                else "broken"
            ),
        }

    async def integrations(self):
        github, calendar = await asyncio.gather(
            self.cached("github"), self.cached("google_calendar", self.today())
        )
        return {
            "github": github,
            "google_calendar": calendar,
            **{
                name: {
                    "status": "not_implemented",
                    "reason": "No runtime adapter in MCP v0.1.",
                }
                for name in ("google_contacts", "manus", "dropbox", "notion", "openai")
            },
        }

    async def dashboard(self, day=None):
        day = day or self.today()
        github, calendar = await asyncio.gather(
            self.cached("github"), self.cached("google_calendar", day)
        )
        blockers = [
            value.get("reason", name + " read needs attention.")
            for name, value in [("GitHub", github), ("Calendar", calendar)]
            if value["status"] != "connected"
        ]
        return {
            "date": day,
            "timezone": os.getenv("KOVA_TIMEZONE", "America/New_York"),
            "calendar": calendar,
            "projects": github["projects"] or self.projects(),
            "integrations": {"github": github, "google_calendar": calendar},
            "blockers": blockers,
            "next_actions": (
                ["Complete the approved provider connection and repeat its read probe."]
                if blockers
                else ["Review today’s events and project metadata."]
            ),
            "generated_at": self.checked(),
            "note": "A source-backed snapshot, not an inferred task list or deployment certification.",
        }

    async def call(self, name, arguments):
        allowed = DEFINITIONS[name][1]
        if set(arguments) - set(allowed):
            raise ValueError("Unsupported arguments")
        if "date" in arguments:
            value = arguments["date"]
            if not isinstance(value, str):
                raise ValueError("Invalid date")
            day_window(value)
        if name in {"open_kova_dashboard", "get_daily_digest"}:
            return await self.dashboard(arguments.get("date"))
        if name == "get_calendar_events":
            return await self.cached(
                "google_calendar", arguments.get("date") or self.today()
            )
        if name == "get_integration_status":
            return {"integrations": await self.integrations()}
        if name == "get_kova_status":
            return {
                "core": "responding",
                "checked_at": self.checked(),
                "integrations": await self.integrations(),
                "deployment": "unverified",
                "version": "0.1.0",
            }
        if name == "list_kova_projects":
            return {
                "projects": self.projects(),
                "evidence": "configured registry; no provider probe",
            }
        if name == "get_project_status":
            project_id = arguments.get("project_id")
            if project_id not in [item["id"] for item in self.projects()]:
                raise ValueError("Project is not enabled")
            snapshot = await self.cached("github")
            projects = [
                project
                for project in snapshot.get("projects", [])
                if project["id"] == project_id
            ]
            return {
                **snapshot,
                "projects": projects,
                "status": projects[0]["status"] if projects else snapshot["status"],
            }
        if name == "refresh_integration":
            provider = arguments.get("integration")
            if not isinstance(provider, str) or provider not in {
                "github",
                "google_calendar",
            }:
                raise ValueError("Unsupported integration")
            return await self.cached(
                provider,
                self.today() if provider == "google_calendar" else None,
                refresh=True,
            )
        raise KeyError(name)


def render_dashboard(data):
    def escape(value):
        return html.escape(str(value), quote=True)

    def event_time(value):
        if isinstance(value.get("date"), str):
            return "All day"
        stamp = datetime.fromisoformat(value["dateTime"].replace("Z", "+00:00"))
        local = stamp.astimezone(ZoneInfo(data["timezone"]))
        return local.strftime("%I:%M %p").lstrip("0")

    integrations = "".join(
        "<li>"
        + escape(name.replace("_", " "))
        + ": "
        + escape(item["status"].replace("_", " "))
        + "</li>"
        for name, item in data["integrations"].items()
    )
    events = "".join(
        "<li>"
        + escape(item["title"])
        + " — "
        + escape(
            "All day"
            if isinstance(item["start"].get("date"), str)
            else event_time(item["start"]) + "–" + event_time(item["end"])
        )
        + "</li>"
        for item in data["calendar"]["events"]
    )
    if not events:
        events = (
            "<li>"
            + (
                "No events found."
                if data["calendar"]["status"] == "connected"
                else "Calendar read not verified."
            )
            + "</li>"
        )
    projects = "".join(
        "<li>"
        + escape(item["title"])
        + " — "
        + escape(item["status"].replace("_", " "))
        + "</li>"
        for item in data["projects"]
    )
    blockers = (
        "".join("<li>" + escape(item) + "</li>" for item in data["blockers"])
        or "<li>No read blockers reported.</li>"
    )
    actions = "".join("<li>" + escape(item) + "</li>" for item in data["next_actions"])
    return (
        """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'"><title>KOVA Today</title><style>body{font:18px/1.65 system-ui,sans-serif;margin:0;padding:24px;color:#192431;background:#f4f7fa}main{max-width:48rem;margin:auto}section{padding:16px;margin:16px 0;background:white;border-radius:16px;overflow-wrap:anywhere}h1,h2{line-height:1.3}h2{font-size:1.2rem}a{color:#184e94}a:focus-visible{outline:3px solid #184e94;outline-offset:4px}ul{padding-left:24px}</style></head><body><main><h1>KOVA Today</h1><p>"""
        + escape(data["date"])
        + " · "
        + escape(data["timezone"])
        + "</p><section><h2>Calendar</h2><ul>"
        + events
        + "</ul></section><section><h2>Projects</h2><ul>"
        + projects
        + "</ul></section><section><h2>Integrations</h2><ul>"
        + integrations
        + "</ul></section><section><h2>Blockers</h2><ul>"
        + blockers
        + "</ul></section><section><h2>Next actions</h2><ul>"
        + actions
        + "</ul></section><p>Snapshot: "
        + escape(data["generated_at"])
        + "</p><p>Ask KOVA to refresh this view for new evidence.</p></main></body></html>"
    )


workspace = WorkspaceService()
