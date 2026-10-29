"""Real adapters with synthetic HTTP transport; no provider credentials needed."""

import asyncio
import os
import sys
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch
import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "kova-ai"))
from app.integrations.google_calendar import day_window, normalize_events, read_calendar
from app.services.mcp_workspace import WorkspaceService, render_dashboard

CALENDAR_ENV = {
    "KOVA_GOOGLE_CLIENT_ID": "test-client",
    "KOVA_GOOGLE_CLIENT_SECRET": "synthetic-secret",
    "KOVA_GOOGLE_CALENDAR_REFRESH_TOKEN": "synthetic-refresh",
    "KOVA_GOOGLE_CALENDAR_ID": "approved@example.invalid",
    "KOVA_TIMEZONE": "America/New_York",
}
SCOPE = "https://www.googleapis.com/auth/calendar.events.readonly"


def event(event_id="one", uid="uid-one", start="2026-10-29T09:00:00-04:00"):
    return {
        "id": event_id,
        "iCalUID": uid,
        "summary": "Owner event",
        "status": "confirmed",
        "start": {"dateTime": start},
        "end": {"dateTime": "2026-10-29T10:00:00-04:00"},
        "htmlLink": "https://calendar.google.com/calendar/event?eid=synthetic",
    }


class CalendarTests(unittest.IsolatedAsyncioTestCase):
    async def test_read_only_scope_and_paginated_deduplication(self):
        calls = []

        def handler(request):
            calls.append(request)
            if request.url.host == "oauth2.googleapis.com":
                self.assertEqual(request.method, "POST")
                return httpx.Response(
                    200, json={"access_token": "synthetic-access", "scope": SCOPE}
                )
            self.assertEqual(request.method, "GET")
            self.assertIn("approved%40example.invalid", str(request.url))
            self.assertEqual(
                request.headers["Authorization"], "Bearer synthetic-access"
            )
            self.assertEqual(request.url.params["singleEvents"], "true")
            self.assertNotIn("attendees", request.url.params["fields"])
            if request.url.params.get("pageToken"):
                return httpx.Response(
                    200,
                    json={
                        "kind": "calendar#events",
                        "items": [
                            event("copy"),
                            event("next", "uid-one", "2026-10-29T14:00:00-04:00"),
                        ],
                    },
                )
            return httpx.Response(
                200,
                json={
                    "kind": "calendar#events",
                    "items": [event()],
                    "nextPageToken": "next",
                },
            )

        with patch.dict(os.environ, CALENDAR_ENV, clear=True):
            result = await read_calendar("2026-10-29", httpx.MockTransport(handler))
        self.assertEqual(result["status"], "connected")
        self.assertTrue(result["complete"])
        self.assertEqual(len(result["events"]), 2)
        self.assertEqual(len(calls), 3)

    async def test_missing_connection_does_not_touch_network(self):
        def fail(request):
            self.fail("Unconfigured adapter made a network request")

        with patch.dict(os.environ, {}, clear=True):
            result = await read_calendar("2026-10-29", httpx.MockTransport(fail))
        self.assertEqual(result["status"], "needs_connection")

    async def test_broad_or_unproven_scope_never_reads_calendar(self):
        for scope in (
            "",
            "https://www.googleapis.com/auth/calendar",
            SCOPE + " https://www.googleapis.com/auth/drive",
        ):
            calls = []

            def handler(request):
                calls.append(request)
                return httpx.Response(
                    200, json={"access_token": "synthetic-access", "scope": scope}
                )

            with patch.dict(os.environ, CALENDAR_ENV, clear=True):
                result = await read_calendar("2026-10-29", httpx.MockTransport(handler))
            self.assertEqual(result["status"], "broken")
            self.assertEqual(len(calls), 1)

    async def test_provider_errors_are_sanitized(self):
        for status in (401, 403, 429, 500):
            with patch.dict(os.environ, CALENDAR_ENV, clear=True):
                result = await read_calendar(
                    "2026-10-29",
                    httpx.MockTransport(
                        lambda request: httpx.Response(
                            status, text="synthetic-secret-provider-body"
                        )
                    ),
                )
            self.assertNotIn("synthetic-secret", str(result))
            self.assertEqual(result["http_status"], status)
            self.assertNotEqual(result["status"], "connected")

    async def test_pagination_limit_reports_partial_and_repeated_token_is_broken(self):
        count = 0

        def handler(request):
            nonlocal count
            if request.url.host == "oauth2.googleapis.com":
                return httpx.Response(
                    200, json={"access_token": "synthetic", "scope": SCOPE}
                )
            count += 1
            return httpx.Response(
                200,
                json={
                    "kind": "calendar#events",
                    "items": [event(str(count), str(count))],
                    "nextPageToken": str(count),
                },
            )

        with patch.dict(os.environ, CALENDAR_ENV, clear=True):
            result = await read_calendar("2026-10-29", httpx.MockTransport(handler))
        self.assertEqual(count, 10)
        self.assertEqual(result["status"], "partial")
        self.assertFalse(result["complete"])

        def repeated(request):
            if request.url.host == "oauth2.googleapis.com":
                return httpx.Response(
                    200, json={"access_token": "synthetic", "scope": SCOPE}
                )
            return httpx.Response(
                200,
                json={"kind": "calendar#events", "items": [], "nextPageToken": "same"},
            )

        with patch.dict(os.environ, CALENDAR_ENV, clear=True):
            result = await read_calendar("2026-10-29", httpx.MockTransport(repeated))
        self.assertEqual(result["status"], "broken")

    def test_dst_windows_and_strict_date(self):
        with patch.dict(os.environ, {"KOVA_TIMEZONE": "America/New_York"}):
            for day, hours in [("2026-03-08", 23), ("2026-11-01", 25)]:
                start, end = day_window(day)
                self.assertEqual(
                    (
                        datetime.fromisoformat(end) - datetime.fromisoformat(start)
                    ).total_seconds()
                    / 3600,
                    hours,
                )
            with self.assertRaises(ValueError):
                day_window("20261029")

    def test_equal_titles_do_not_merge_distinct_events(self):
        self.assertEqual(len(normalize_events([event("a", "a"), event("b", "b")])), 2)
        self.assertEqual(len(normalize_events([event("a"), event("b")])), 1)
        self.assertEqual(normalize_events([{**event(), "status": "cancelled"}]), [])

    def test_all_day_events_and_moved_recurring_occurrences(self):
        all_day = {
            **event("all-day", "all-day"),
            "start": {"date": "2026-10-29"},
            "end": {"date": "2026-10-30"},
        }
        self.assertEqual(normalize_events([all_day])[0]["start"], {"date": "2026-10-29"})

        moved = event("moved", "series", "2026-10-29T11:00:00-04:00")
        moved["originalStartTime"] = {"dateTime": "2026-10-29T09:00:00-04:00"}
        second = {
            **moved,
            "id": "second-occurrence",
            "originalStartTime": {"dateTime": "2026-10-29T10:00:00-04:00"},
        }
        duplicate = {**moved, "id": "duplicate"}
        self.assertEqual(len(normalize_events([moved, second])), 2)
        self.assertEqual(len(normalize_events([moved, duplicate])), 1)


class GithubAndCacheTests(unittest.IsolatedAsyncioTestCase):
    async def test_github_registry_scope_cache_and_refresh(self):
        requests = []

        def handler(request):
            requests.append(request)
            self.assertEqual(request.url.host, "api.github.com")
            coordinate = request.url.path.removeprefix("/repos/")
            self.assertIn(
                coordinate,
                {"Kathrynhiggs21/Kova-ai-SYSTEM", "Kathrynhiggs21/kovaos-site"},
            )
            return httpx.Response(
                200,
                json={
                    "full_name": coordinate,
                    "default_branch": "main",
                    "open_issues_count": 2,
                    "updated_at": "2026-10-29T00:00:00Z",
                },
            )

        with patch.dict(os.environ, {"GITHUB_TOKEN": "synthetic-token"}, clear=True):
            service = WorkspaceService(httpx.MockTransport(handler))
            first = await service.cached("github")
            second = await service.cached("github")
            self.assertEqual(first["status"], "connected")
            self.assertTrue(second["cached"])
            self.assertEqual(first["last_checked"], second["last_checked"])
            self.assertEqual(len(requests), 2)
            await service.call("refresh_integration", {"integration": "github"})
            self.assertEqual(len(requests), 4)
            os.environ["GITHUB_TOKEN"] = "different-synthetic-owner"
            await service.cached("github")
            self.assertEqual(len(requests), 6)

    async def test_github_failures_do_not_leak_responses(self):
        with patch.dict(os.environ, {"GITHUB_TOKEN": "synthetic-token"}, clear=True):
            service = WorkspaceService(
                httpx.MockTransport(
                    lambda req: httpx.Response(
                        403, json={"message": "private-provider-body"}
                    )
                )
            )
            result = await service.github()
        self.assertEqual(result["status"], "broken")
        self.assertNotIn("private-provider-body", str(result))
        self.assertTrue(all(item["http_status"] == 403 for item in result["projects"]))

    async def test_failed_reads_never_leave_successful_cached_results(self):
        connected = True

        def handler(request):
            if not connected:
                return httpx.Response(401)
            return httpx.Response(
                200,
                json={
                    "full_name": request.url.path.removeprefix("/repos/"),
                    "default_branch": "main",
                },
            )

        with patch.dict(os.environ, {"GITHUB_TOKEN": "synthetic-token"}, clear=True):
            service = WorkspaceService(httpx.MockTransport(handler))
            self.assertEqual((await service.cached("github"))["status"], "connected")
            connected = False
            self.assertEqual(
                (await service.cached("github", refresh=True))["status"], "broken"
            )
            self.assertNotEqual((await service.cached("github"))["status"], "connected")

    async def test_read_started_before_refresh_cannot_overwrite_refresh_result(self):
        started = asyncio.Event()
        release = asyncio.Event()
        calls = 0

        async def github():
            nonlocal calls
            calls += 1
            if calls == 1:
                started.set()
                await release.wait()
                return {"status": "connected", "projects": [], "last_checked": "old"}
            return {"status": "broken", "projects": [], "last_checked": "new"}

        service = WorkspaceService()
        service.github = github
        older_read = asyncio.create_task(service.cached("github"))
        await started.wait()
        refreshed = await service.cached("github", refresh=True)
        self.assertEqual(refreshed["status"], "broken")
        release.set()
        await older_read
        cached = await service.cached("github")
        self.assertEqual(cached["status"], "broken")
        self.assertEqual(cached["last_checked"], "new")
        self.assertTrue(cached["cached"])

    async def test_concurrent_ordinary_reads_keep_newest_evidence(self):
        for expired in (False, True):
            with self.subTest(expired=expired):
                service = WorkspaceService()
                if expired:
                    key = (service.fingerprint(), "github", None)
                    service.cache[key] = (0, {"status": "connected"})
                started = asyncio.Event()
                release = asyncio.Event()
                calls = 0

                async def github():
                    nonlocal calls
                    calls += 1
                    if calls == 1:
                        started.set()
                        await release.wait()
                        return {"status": "connected", "last_checked": "old"}
                    return {"status": "broken", "last_checked": "new"}

                service.github = github
                older = asyncio.create_task(service.cached("github"))
                await started.wait()
                newer = await service.cached("github")
                self.assertEqual(newer["status"], "broken")
                release.set()
                await older
                cached = await service.cached("github")
                self.assertEqual(cached["status"], "broken")
                self.assertEqual(cached["last_checked"], "new")
                self.assertTrue(cached["cached"])

    async def test_cancelled_read_cleans_tracking_and_does_not_cache(self):
        service = WorkspaceService()
        started = asyncio.Event()

        async def github():
            started.set()
            await asyncio.Event().wait()

        service.github = github
        read = asyncio.create_task(service.cached("github"))
        await started.wait()
        read.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await read
        self.assertEqual(service.cache_reads, {})
        self.assertEqual(service.cache, {})

    async def test_project_status_uses_cached_github_snapshot(self):
        requests = []

        def handler(request):
            requests.append(request)
            coordinate = request.url.path.removeprefix("/repos/")
            return httpx.Response(
                200,
                json={
                    "full_name": coordinate,
                    "default_branch": "main",
                    "open_issues_count": 0,
                },
            )

        with patch.dict(os.environ, {"GITHUB_TOKEN": "synthetic-token"}, clear=True):
            service = WorkspaceService(httpx.MockTransport(handler))
            await service.cached("github")
            request_count = len(requests)
            result = await service.call(
                "get_project_status", {"project_id": "Kathrynhiggs21/Kova-ai-SYSTEM"}
            )
        self.assertEqual(len(requests), request_count)
        self.assertTrue(result["cached"])
        self.assertEqual(
            [project["id"] for project in result["projects"]],
            ["Kathrynhiggs21/Kova-ai-SYSTEM"],
        )

    async def test_view_escapes_provider_text(self):
        with patch.dict(os.environ, {}, clear=True):
            data = await WorkspaceService().dashboard()
        data["calendar"]["events"] = [
            {
                "title": "<script>alert(1)</script>",
                "start": {"dateTime": "2026-10-29T09:00:00-04:00"},
                "end": {"dateTime": "2026-10-29T10:00:00-04:00"},
            },
            {
                "title": "All day",
                "start": {"date": "2026-10-29"},
                "end": {"date": "2026-10-30"},
            },
        ]
        view = render_dashboard(data)
        self.assertNotIn("<script>", view)
        self.assertIn("&lt;script&gt;", view)
        self.assertIn("9:00 AM–10:00 AM", view)
        self.assertIn("All day", view)
        self.assertIn("default-src 'none'", view)
