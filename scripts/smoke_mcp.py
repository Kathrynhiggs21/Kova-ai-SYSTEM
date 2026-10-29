"""Read-only acceptance for the built Core MCP endpoint; no secret output."""

import json
import os
from urllib.error import HTTPError
from urllib.request import Request, urlopen

url = "http://127.0.0.1:" + os.environ.get("PORT", "8000") + "/mcp"
key = os.environ["KOVA_OWNER_API_KEY"]


def message(method, params=None, owner_key=key):
    headers = {"Content-Type": "application/json"}
    if owner_key:
        headers["X-Kova-API-Key"] = owner_key
    request = Request(
        url,
        data=json.dumps(
            {"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}}
        ).encode(),
        headers=headers,
    )
    with urlopen(request, timeout=35) as response:
        assert response.status == 200
        return json.load(response)


for supplied in (None, "synthetic-wrong-owner"):
    try:
        message("tools/list", owner_key=supplied)
    except HTTPError as error:
        assert error.code == 401
    else:
        raise AssertionError("Unauthorized MCP discovery succeeded")

capabilities = message("initialize")["result"]["capabilities"]
assert "tools" in capabilities and "resources" in capabilities
names = {tool["name"] for tool in message("tools/list")["result"]["tools"]}
assert {
    "kova_health",
    "open_kova_dashboard",
    "get_daily_digest",
    "get_calendar_events",
    "get_project_status",
} <= names
legacy = message("tools/call", {"name": "kova_health"})["result"]["structuredContent"]
assert legacy == {"status": "ok"}
dashboard = message("tools/call", {"name": "open_kova_dashboard"})["result"]
assert {"calendar", "projects", "integrations", "blockers", "next_actions"} <= set(
    dashboard["structuredContent"]
)
uri = dashboard["_meta"]["ui"]["resourceUri"]
resource = message("resources/read", {"uri": uri})["result"]["contents"][0]
assert resource["mimeType"] == "text/html;profile=mcp-app"
assert "<main>" in resource["text"] and "<script" not in resource["text"]
assert key not in json.dumps(dashboard) and key not in resource["text"]
print(
    "MCP smoke passed: owner boundary, initialize, tool discovery, legacy call, dashboard and resource read."
)
