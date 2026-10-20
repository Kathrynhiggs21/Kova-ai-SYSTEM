"""Smoke-test the built Core container without calling external services."""

import json
import os
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def read_json(path, *, key=None):
    headers = {"X-Kova-API-Key": key} if key else {}
    request = Request(f"http://127.0.0.1:{os.environ['PORT']}{path}", headers=headers)
    with urlopen(request, timeout=2) as response:
        assert response.status == 200, response.status
        return json.load(response)


for attempt in range(60):
    try:
        assert read_json("/health") == {"status": "ok"}
        break
    except (URLError, TimeoutError):
        if attempt == 59:
            raise
        time.sleep(1)

assert os.getuid() == 1001, "Core must run as the non-root app user"
assert not any(Path("/app").rglob(".env*")), "Local environment files must not enter the image"
assert Path("/app/kova_repos_config.json").is_file(), "Canonical registry is missing"

for archive in ("site", "images"):
    with urlopen(f"http://127.0.0.1:{os.environ['PORT']}/api/export/{archive}", timeout=2) as response:
        assert response.status == 200
        assert response.read(4) == b"PK\x03\x04", "Published archive is not a ZIP"

try:
    request = Request(f"http://127.0.0.1:{os.environ['PORT']}/api/export/gdrive-upload",
                      headers={"X-Kova-API-Key": os.environ["KOVA_OWNER_API_KEY"]}, method="POST")
    urlopen(request, timeout=2)
except HTTPError as error:
    assert error.code == 404, "Minimal image must not expose the local upload workflow"
else:
    raise AssertionError("Local upload workflow is exposed")

try:
    read_json("/multi-repo/list")
except HTTPError as error:
    assert error.code == 401, error.code
else:
    raise AssertionError("Anonymous registry access was accepted")

request = Request(
    f"http://127.0.0.1:{os.environ['PORT']}/mcp",
    data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                     "params": {"name": "kova_export_status", "arguments": {}}}).encode(),
    headers={"Content-Type": "application/json", "X-Kova-API-Key": os.environ["KOVA_OWNER_API_KEY"]},
)
with urlopen(request, timeout=2) as response:
    status = json.loads(json.load(response)["result"]["content"][0]["text"])
    assert status["site"]["compiled"] and status["images"]["compiled"]

owner_key = os.environ["KOVA_OWNER_API_KEY"]
repositories = read_json("/multi-repo/list", key=owner_key)
assert repositories["status"] == "success"
assert set(repositories["data"]["repositories"]) == {
    "Kathrynhiggs21/Kova-ai-SYSTEM",
    "Kathrynhiggs21/kovaos-site",
}
config = read_json("/multi-repo/config", key=owner_key)["data"]
donor = next(repo for repo in config["repositories"] if repo["name"] == "kova-ai-dash")
assert donor["enabled"] is False, "Disabled donor must remain disabled"
print("Container smoke passed: configured port, health JSON, non-root user, owner access, canonical registry, published archives, local upload disabled.")
