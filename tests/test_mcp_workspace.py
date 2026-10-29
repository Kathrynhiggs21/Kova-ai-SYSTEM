"""Owner-only MCP v0.1 acceptance tests; provider responses are synthetic."""

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "kova-ai"))
from app.main import app


class WorkspaceTests(unittest.IsolatedAsyncioTestCase):
    async def message(self, method, params=None, key="synthetic-owner"):
        headers = {"X-Kova-API-Key": key} if key else {}
        with patch.dict(os.environ, {"KOVA_OWNER_API_KEY": "synthetic-owner"}):
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://test"
            ) as client:
                return await client.post(
                    "/mcp",
                    headers=headers,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": method,
                        "params": params or {},
                    },
                )

    async def tool(self, name, arguments=None):
        response = await self.message(
            "tools/call", {"name": name, "arguments": arguments or {}}
        )
        self.assertEqual(response.status_code, 200)
        return response.json()

    async def test_discovery_includes_v01_tools(self):
        response = await self.message("tools/list")
        names = {item["name"] for item in response.json()["result"]["tools"]}
        self.assertTrue(
            {
                "open_kova_dashboard",
                "get_kova_status",
                "get_daily_digest",
                "get_calendar_events",
                "get_integration_status",
                "refresh_integration",
                "list_kova_projects",
                "get_project_status",
            }
            <= names
        )
        self.assertIn("kova_health", names)

    async def test_every_new_tool_rejects_anonymous_and_wrong_owner_before_execution(
        self,
    ):
        for key in (None, "different-owner"):
            for name in (
                "open_kova_dashboard",
                "get_kova_status",
                "get_daily_digest",
                "get_calendar_events",
                "get_integration_status",
                "refresh_integration",
                "list_kova_projects",
                "get_project_status",
            ):
                response = await self.message("tools/call", {"name": name}, key=key)
                self.assertEqual(response.status_code, 401)

    async def test_missing_provider_credentials_are_not_reported_as_connected(self):
        with patch.dict(os.environ, {}, clear=True):
            result = await self.tool("get_integration_status")
        integrations = result["result"]["structuredContent"]["integrations"]
        self.assertEqual(integrations["github"]["status"], "needs_connection")
        self.assertEqual(integrations["google_calendar"]["status"], "needs_connection")
        self.assertNotIn("connected", [v["status"] for v in integrations.values()])

    async def test_dashboard_has_readonly_host_view_and_truthful_empty_state(self):
        with patch.dict(os.environ, {}, clear=True):
            result = await self.tool("open_kova_dashboard")
        data = result["result"]["structuredContent"]
        self.assertIn("integrations", data)
        self.assertTrue(data["blockers"])
        self.assertEqual(data["calendar"]["status"], "needs_connection")
        self.assertEqual(
            result["result"]["_meta"]["ui"]["resourceUri"], "ui://kova/dashboard.html"
        )

    async def test_resource_is_owner_protected_and_exposes_no_provider_credentials(
        self,
    ):
        with patch.dict(os.environ, {}, clear=True):
            response = await self.message(
                "resources/read", {"uri": "ui://kova/dashboard.html"}
            )
        content = response.json()["result"]["contents"][0]
        self.assertEqual(content["mimeType"], "text/html;profile=mcp-app")
        self.assertIn("KOVA", content["text"])
        self.assertNotIn("synthetic-owner", content["text"])
        denied = await self.message(
            "resources/read", {"uri": "ui://kova/dashboard.html"}, key=None
        )
        self.assertEqual(denied.status_code, 401)

    async def test_project_lookup_is_limited_to_enabled_registry(self):
        result = await self.tool(
            "get_project_status", {"project_id": "someone/private"}
        )
        self.assertEqual(result["error"]["code"], -32602)
        result = await self.tool("list_kova_projects")
        projects = result["result"]["structuredContent"]["projects"]
        self.assertEqual(
            {p["id"] for p in projects},
            {"Kathrynhiggs21/Kova-ai-SYSTEM", "Kathrynhiggs21/kovaos-site"},
        )

    async def test_invalid_date_and_extra_arguments_are_rejected(self):
        for args in (
            {"date": "not-a-date"},
            {"date": "2026-02-30"},
            {"tenant_id": "other"},
            {"date": True},
        ):
            result = await self.tool("get_daily_digest", args)
            self.assertEqual(result["error"]["code"], -32602)

    async def test_falsey_non_object_arguments_are_rejected(self):
        for args in ([], "", False, 0, None):
            response = await self.message(
                "tools/call", {"name": "get_daily_digest", "arguments": args}
            )
            self.assertEqual(response.json()["error"]["code"], -32602)

    async def test_refresh_cannot_select_arbitrary_provider_or_calendar(self):
        for args in (
            {"integration": "arbitrary"},
            {"integration": {}},
            {"integration": False},
            {"integration": "github", "url": "http://internal"},
            {"integration": "google_calendar", "calendar_id": "other"},
        ):
            result = await self.tool("refresh_integration", args)
            self.assertEqual(result["error"]["code"], -32602)
