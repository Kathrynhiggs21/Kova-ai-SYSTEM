"""Server-only CORE 0.7.20 synthetic pilot; not registered as an API route.

KOVA supplies authoritative authorization and a durable ledger sink. This module
accepts no arbitrary memory text, task instructions, URLs, or browser credentials.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable, Protocol
from urllib.parse import urlsplit
from uuid import UUID, uuid4

import httpx

CORE_VERSION = "0.7.20"
MEMORY_TEXT = "Synthetic KOVA test: the imaginary blue cube is on shelf seven."
TASK_TITLE = "Synthetic KOVA connectivity fixture"


class CoreUnavailable(RuntimeError):
    pass


class CoreDenied(PermissionError):
    pass


@dataclass(frozen=True)
class CoreConfig:
    origin: str
    token: str = field(repr=False)
    workspace_id: str = field(repr=False)
    enabled: bool = False
    task_writes_enabled: bool = False

    def __post_init__(self):
        url = urlsplit(self.origin)
        if (
            url.scheme != "https"
            or not url.hostname
            or url.username
            or url.password
            or url.path not in ("", "/")
            or url.query
            or url.fragment
        ):
            raise ValueError("CORE requires an explicit HTTPS origin")
        if not self.token.strip() or not self.workspace_id.strip():
            raise ValueError("CORE server credentials and workspace are required")


@dataclass(frozen=True)
class CoreContext:
    # Construct only after server-side KOVA authentication, never from JSON body.
    principal_id: str
    data_scope: str = "synthetic"


class MemoryPort(Protocol):
    def create_memory(self, context: CoreContext) -> dict: ...
    def read_memory(self, context: CoreContext, session_id: str) -> dict: ...


class TaskPort(Protocol):
    def create_task(self, context: CoreContext) -> dict: ...
    def read_task(self, context: CoreContext, task_id: str) -> dict: ...


class ToolPort(Protocol):
    def execute_tool(self, context: CoreContext) -> dict: ...


class HealthPort(Protocol):
    def health(self, context: CoreContext) -> dict: ...


class KovaCoreAdapter:
    """Narrow pilot with fail-closed gates; all reads are resource-authorized.

    authorize(principal, action, resource) must consult KOVA's server-owned policy.
    approve_task(principal) must atomically consume an owner approval for this
    fixed synthetic task, including CORE's automatic recurrence/model side effect.
    record(event) must durably persist schema-compatible ledger events or raise.
    No default grant, approval store, ledger store, scheduler, or public route.
    """

    def __init__(
        self,
        config: CoreConfig,
        authorize: Callable[[str, str, str], bool],
        record: Callable[[dict], None],
        approve_task: Callable[[str], bool] = lambda _: False,
        *,
        transport: httpx.BaseTransport | None = None,
    ):
        self._config = config
        self._authorize = authorize
        self._record = record
        self._approve_task = approve_task
        self._client = httpx.Client(
            base_url=config.origin.rstrip("/"),
            headers={"Authorization": f"Bearer {config.token}"},
            timeout=15,
            follow_redirects=False,
            trust_env=False,
            transport=transport,
        )

    def close(self):
        self._client.close()

    def _request(self, method, path, body=None):
        # Never expose raw provider bodies/errors (e.g. /me has collabToken).
        try:
            response = self._client.request(method, path, json=body)
            if response.status_code not in (200, 201, 202):
                raise CoreUnavailable("CORE request failed; no automatic retry")
            return response.json()
        except (httpx.HTTPError, ValueError):
            raise CoreUnavailable("CORE request failed; no automatic retry") from None

    def _run(self, context, action, resource, operation):
        event = {
            "task_id": str(uuid4()),
            "agent_provider": "redplanethq-core",
            "model_or_version": CORE_VERSION,
            "module": "connectors",
            "actions": [action],
            "status": "running",
            "approval_state": "not_required",
            "validation_state": "not_run",
            "started_at": datetime.now(timezone.utc).isoformat(),
        }
        # A failed intent write prevents external activity.
        self._record(dict(event))
        try:
            if (
                not self._config.enabled
                or not context.principal_id
                or context.data_scope != "synthetic"
                or not self._authorize(context.principal_id, action, resource)
            ):
                raise CoreDenied("KOVA authorization or synthetic pilot gate denied")
            if action == "tool.execute":
                event["approval_state"] = "pending"
                raise CoreDenied("Tool execution is disabled in this pilot")
            if action == "task.create":
                event["approval_state"] = "pending"
                if not self._config.task_writes_enabled:
                    raise CoreDenied("CORE task writes require recurrence isolation")
                if not self._approve_task(context.principal_id):
                    raise CoreDenied("Owner approval required for synthetic task")
                event["approval_state"] = "approved"
            identity = self._request("GET", "/api/v1/me")
            if (
                not isinstance(identity, dict)
                or identity.get("workspaceId") != self._config.workspace_id
            ):
                raise CoreDenied("CORE workspace binding failed")
            result = operation()
            event["status"] = "completed"
            # Endpoint acceptance is not proof of ingestion or execution.
            event["output_summary"] = (
                "Synthetic adapter request accepted; processing not certified"
            )
            return result
        except Exception:
            event["status"] = "failed"
            event["output_summary"] = (
                "Adapter request denied or failed; reconcile before retry"
            )
            raise
        finally:
            event["completed_at"] = datetime.now(timezone.utc).isoformat()
            self._record(dict(event))

    def health(self, context):
        return self._run(
            context,
            "health.read",
            "self",
            lambda: {
                "status": "authenticated",
                "expected_version": CORE_VERSION,
                "version_verified": False,
                "memory_verified": False,
                "task_execution_verified": False,
            },
        )

    def create_memory(self, context):
        session_id = "kova-synthetic-" + str(uuid4())

        def create():
            result = self._request(
                "POST",
                "/api/v1/add",
                {
                    "episodeBody": MEMORY_TEXT,
                    "referenceTime": "2026-01-01T00:00:00Z",
                    "source": "kova-synthetic-pilot",
                    "sessionId": session_id,
                    "metadata": {"synthetic": True, "needs_review": True},
                },
            )
            if (
                not isinstance(result, dict)
                or result.get("success") is not True
                or not isinstance(result.get("id"), str)
            ):
                raise CoreUnavailable("CORE ingestion response invalid")
            # Provider acceptance returns a queue ID, not a memory fact ID.
            return {"session_id": session_id, "status": "queued"}

        return self._run(context, "memory.create", session_id, create)

    def read_memory(self, context, session_id):
        if not session_id.startswith("kova-synthetic-"):
            raise CoreDenied("Only synthetic sessions are supported")
        try:
            UUID(session_id.removeprefix("kova-synthetic-"))
        except ValueError:
            raise CoreDenied("Invalid synthetic session") from None

        def read():
            result = self._request("GET", f"/api/v1/episodes/session/{session_id}")
            if not isinstance(result, dict) or not isinstance(
                result.get("episodes"), list
            ):
                raise CoreUnavailable("CORE session response invalid")
            episodes = result["episodes"]
            # Return no arbitrary provider content to a future browser caller.
            matches = [
                e
                for e in episodes
                if isinstance(e, dict) and e.get("content") == MEMORY_TEXT
            ]
            return {
                "fixture_found": bool(matches),
                "ingestion_completed": any(
                    e.get("status") == "COMPLETED" for e in matches
                ),
            }

        return self._run(context, "memory.read", session_id, read)

    def create_task(self, context):
        def create():
            result = self._request(
                "POST",
                "/api/v1/tasks",
                {
                    "title": TASK_TITLE,
                    "source": "kova-synthetic-pilot",
                    "status": "Done",
                },
            )
            if not isinstance(result, dict) or not isinstance(result.get("id"), str):
                raise CoreUnavailable("CORE task response invalid")
            task_id = result["id"]
            if not task_id.isalnum() or len(task_id) > 128:
                raise CoreUnavailable("CORE task identifier invalid")
            return {
                "task_id": task_id,
                "status": "created",
                "execution_verified": False,
            }

        return self._run(context, "task.create", "synthetic-fixture", create)

    def read_task(self, context, task_id):
        if not task_id.isalnum() or len(task_id) > 128:
            raise CoreDenied("Invalid task identifier")

        def read():
            result = self._request("GET", f"/api/v1/tasks/{task_id}")
            if not isinstance(result, dict) or result.get("title") != TASK_TITLE:
                raise CoreDenied("Not a synthetic fixture")
            return {"fixture_found": True, "execution_verified": False}

        return self._run(context, "task.read", task_id, read)

    def execute_tool(self, context):
        return self._run(context, "tool.execute", "synthetic-fixture", lambda: {})
