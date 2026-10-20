"""Verify the documented Compose bind mount starts the real API."""

import json
import os
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def read_json(path, key=None):
    headers = {"X-Kova-API-Key": key} if key else {}
    request = Request(f"http://127.0.0.1:{os.environ['PORT']}{path}", headers=headers)
    with urlopen(request, timeout=2) as response:
        return json.load(response)


for attempt in range(60):
    try:
        assert read_json("/health") == {"status": "ok"}
        break
    except (URLError, TimeoutError):
        if attempt == 59:
            raise
        time.sleep(1)

assert Path.cwd() == Path("/app/kova-ai")
assert Path("app/main.py").is_file()
assert os.getuid() == 1001
assert Path("/app/site_final.zip").is_file()
assert Path("/app/images.zip").is_file()
try:
    read_json("/multi-repo/list")
except HTTPError as error:
    assert error.code == 401
else:
    raise AssertionError("Anonymous registry access was accepted")
assert read_json("/multi-repo/list", os.environ["KOVA_OWNER_API_KEY"])["status"] == "success"
print("Compose smoke passed: bind-mounted source, working directory, health and owner access.")
