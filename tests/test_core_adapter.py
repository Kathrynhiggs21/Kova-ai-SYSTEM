import json
import unittest
from dataclasses import replace

import httpx

from app.integrations.core_adapter import (
    CoreConfig,
    CoreContext,
    CoreDenied,
    CoreUnavailable,
    KovaCoreAdapter,
    MEMORY_TEXT,
    TASK_TITLE,
)


class CoreAdapterTests(unittest.TestCase):
    def setUp(self):
        self.events = []
        self.requests = []
        self.memory = {}
        self.tasks = {}
        self.config = CoreConfig(
            "https://core.example.test",
            "secret-fixture",
            "synthetic-workspace",
            enabled=True,
        )
        self.context = CoreContext("synthetic-owner")

    def handler(self, request):
        self.requests.append(request)
        self.assertEqual(request.headers["Authorization"], "Bearer secret-fixture")
        path = request.url.path
        if path == "/api/v1/me":
            return httpx.Response(
                200,
                json={
                    "workspaceId": "synthetic-workspace",
                    "collabToken": "never-return-this",
                    "email": "private",
                },
            )
        if path == "/api/v1/add":
            body = json.loads(request.content)
            self.memory[body["sessionId"]] = body
            return httpx.Response(200, json={"success": True, "id": "queue123"})
        if path.startswith("/api/v1/episodes/session/"):
            body = self.memory[path.split("/")[-1]]
            return httpx.Response(
                200,
                json={
                    "episodes": [
                        {"content": body["episodeBody"], "status": "COMPLETED"}
                    ]
                },
            )
        if path == "/api/v1/tasks":
            self.tasks["task123"] = json.loads(request.content)
            return httpx.Response(200, json={"id": "task123"})
        if path == "/api/v1/tasks/task123":
            return httpx.Response(200, json=self.tasks["task123"])
        return httpx.Response(404)

    def adapter(self, **kwargs):
        adapter = KovaCoreAdapter(
            kwargs.pop("config", self.config),
            kwargs.pop(
                "authorize",
                lambda principal, action, resource: principal == "synthetic-owner",
            ),
            kwargs.pop("record", self.events.append),
            transport=httpx.MockTransport(kwargs.pop("handler", self.handler)),
            **kwargs,
        )
        self.addCleanup(adapter.close)
        return adapter

    def test_memory_roundtrip_is_fixture_only_and_queued_not_ingested(self):
        adapter = self.adapter()
        receipt = adapter.create_memory(self.context)
        self.assertEqual(receipt["status"], "queued")
        self.assertEqual(
            adapter.read_memory(self.context, receipt["session_id"]),
            {"fixture_found": True, "ingestion_completed": True},
        )
        self.assertEqual(next(iter(self.memory.values()))["episodeBody"], MEMORY_TEXT)
        self.assertNotIn("secret-fixture", json.dumps(self.events))
        self.assertNotIn(MEMORY_TEXT, json.dumps(self.events))

    def test_health_does_not_return_provider_tokens_or_claim_full_health(self):
        result = self.adapter().health(self.context)
        self.assertEqual(result["status"], "authenticated")
        self.assertFalse(result["version_verified"])
        self.assertFalse(result["memory_verified"])
        self.assertNotIn("never-return-this", json.dumps(result))
        self.assertNotIn("secret-fixture", repr(self.config))

    def test_disabled_and_foreign_principal_and_real_scopes_block_before_network(self):
        for config, context in [
            (replace(self.config, enabled=False), self.context),
            (self.config, CoreContext("intruder")),
            (self.config, CoreContext("")),
            (self.config, CoreContext("synthetic-owner", "family")),
        ]:
            with self.subTest(context=context), self.assertRaises(CoreDenied):
                self.adapter(config=config).create_memory(context)
        self.assertEqual(self.requests, [])

    def test_wrong_workspace_prevents_write(self):
        with self.assertRaises(CoreDenied):
            self.adapter(
                config=replace(self.config, workspace_id="other")
            ).create_memory(self.context)
        self.assertEqual(len(self.requests), 1)
        self.assertEqual(self.memory, {})

    def test_task_create_has_two_independent_gates(self):
        for config, approved in [
            (self.config, True),
            (replace(self.config, task_writes_enabled=True), False),
        ]:
            with self.subTest(config=config), self.assertRaises(CoreDenied):
                self.adapter(
                    config=config, approve_task=lambda _: approved
                ).create_task(self.context)
        self.assertEqual(self.requests, [])
        self.assertEqual(self.events[-1]["approval_state"], "pending")

    def test_approved_task_roundtrip_is_only_mock_execution(self):
        approvals = [True]
        adapter = self.adapter(
            config=replace(self.config, task_writes_enabled=True),
            approve_task=lambda _: approvals.pop() if approvals else False,
        )
        result = adapter.create_task(self.context)
        self.assertEqual(
            adapter.read_task(self.context, result["task_id"]),
            {"fixture_found": True, "execution_verified": False},
        )
        self.assertEqual(
            self.tasks["task123"],
            {"title": TASK_TITLE, "source": "kova-synthetic-pilot", "status": "Done"},
        )
        with self.assertRaises(CoreDenied):
            adapter.create_task(self.context)

    def test_high_impact_tool_stays_disabled(self):
        with self.assertRaises(CoreDenied):
            self.adapter(approve_task=lambda _: True).execute_tool(self.context)
        self.assertEqual(self.requests, [])

    def test_resource_authorization_is_required_for_reads(self):
        with self.assertRaises(CoreDenied):
            self.adapter(authorize=lambda p, a, r: r == "allowed").read_task(
                self.context, "task123"
            )
        self.assertEqual(self.requests, [])

    def test_invalid_ids_cannot_change_request_path(self):
        adapter = self.adapter()
        for value in ["../../me", "a?token=secret", "", "a" * 129]:
            with self.subTest(value=value), self.assertRaises(CoreDenied):
                adapter.read_task(self.context, value)
        with self.assertRaises(CoreDenied):
            adapter.read_memory(self.context, "kova-synthetic-../../me")
        self.assertEqual(self.requests, [])

    def test_redirects_and_errors_never_expose_provider_body_or_retry(self):
        for status in [302, 401, 403, 429, 500]:
            calls = []

            def respond(request):
                calls.append(request)
                return httpx.Response(
                    status,
                    headers={"location": "https://evil.example"},
                    text="secret-fixture",
                )

            with self.subTest(status=status), self.assertRaises(
                CoreUnavailable
            ) as error:
                self.adapter(handler=respond).health(self.context)
            self.assertNotIn("secret-fixture", str(error.exception))
            self.assertEqual(len(calls), 1)

    def test_ledger_failure_prevents_outbound_request(self):
        def failed_record(event):
            raise OSError("ledger unavailable")

        with self.assertRaises(OSError):
            self.adapter(record=failed_record).create_memory(self.context)
        self.assertEqual(self.requests, [])

    def test_origin_rejects_credentials_plaintext_and_paths(self):
        for origin in [
            "http://core.example",
            "https://user:pass@core.example",
            "https://core.example/api",
            "https://core.example?x=y",
        ]:
            with self.subTest(origin=origin), self.assertRaises(ValueError):
                replace(self.config, origin=origin)


if __name__ == "__main__":
    unittest.main()
