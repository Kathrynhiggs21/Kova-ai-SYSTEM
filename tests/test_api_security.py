"""Security regression tests for KOVA's owner-only API boundary."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

import httpx
from fastapi import HTTPException

from app.api import export_endpoints
from app.api.ai_endpoints import validate_repository_path
from app.main import app, parse_allowed_origins


OWNER_KEY = "test-owner-api-key"
ENV_EXAMPLE = Path(__file__).resolve().parents[1] / "kova-ai" / ".env.example"


class SecureConfigurationDefaultsTests(unittest.TestCase):
    def test_owner_api_key_sample_is_empty(self):
        assignments = {
            line.partition("=")[0]: line.partition("=")[2]
            for line in ENV_EXAMPLE.read_text(encoding="utf-8").splitlines()
            if "=" in line and not line.lstrip().startswith("#")
        }

        self.assertIn("KOVA_OWNER_API_KEY", assignments)
        self.assertEqual(assignments["KOVA_OWNER_API_KEY"], "")


class OwnerApiBoundaryTests(unittest.IsolatedAsyncioTestCase):
    async def request(self, method: str, path: str, owner_key=None, **kwargs):
        headers = dict(kwargs.pop("headers", {}))
        if owner_key is not None:
            headers["X-Kova-API-Key"] = owner_key

        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        ) as client:
            return await client.request(method, path, headers=headers, **kwargs)

    async def test_health_remains_public(self):
        with patch.dict(os.environ, {"KOVA_OWNER_API_KEY": ""}):
            response = await self.request("GET", "/health")

        self.assertEqual(response.status_code, 200)

    async def test_unconfigured_authentication_fails_closed(self):
        with patch.dict(os.environ, {"KOVA_OWNER_API_KEY": ""}):
            response = await self.request("GET", "/multi-repo/list")

        self.assertEqual(response.status_code, 503)

    async def test_whitespace_only_authentication_fails_closed(self):
        with patch.dict(os.environ, {"KOVA_OWNER_API_KEY": "   "}):
            response = await self.request("GET", "/multi-repo/list")

        self.assertEqual(response.status_code, 503)

    async def test_owner_routes_reject_missing_key(self):
        protected_requests = [
            ("POST", "/ai/command", {"json": {"command": "status"}}),
            ("GET", "/multi-repo/list", {}),
            ("GET", "/artifacts/types", {}),
            ("POST", "/api/export/gdrive-upload", {}),
            ("GET", "/webhooks/status", {}),
        ]

        with patch.dict(os.environ, {"KOVA_OWNER_API_KEY": OWNER_KEY}):
            for method, path, kwargs in protected_requests:
                with self.subTest(path=path):
                    response = await self.request(method, path, **kwargs)
                    self.assertEqual(response.status_code, 401)

    async def test_owner_routes_reject_wrong_key(self):
        with patch.dict(os.environ, {"KOVA_OWNER_API_KEY": OWNER_KEY}):
            response = await self.request(
                "GET", "/multi-repo/list", owner_key="wrong-key"
            )

        self.assertEqual(response.status_code, 401)

    async def test_valid_owner_key_allows_safe_route(self):
        with patch.dict(os.environ, {"KOVA_OWNER_API_KEY": OWNER_KEY}):
            response = await self.request(
                "GET", "/multi-repo/list", owner_key=OWNER_KEY
            )

        self.assertEqual(response.status_code, 200)

    async def test_noncanonical_repository_is_denied_before_github_access(self):
        with patch.dict(os.environ, {"KOVA_OWNER_API_KEY": OWNER_KEY}):
            response = await self.request(
                "POST",
                "/ai/command",
                owner_key=OWNER_KEY,
                json={
                    "command": "read",
                    "action": "analyze",
                    "repository": "someone/private-repository",
                    "file_path": "README.md",
                },
            )

        self.assertEqual(response.status_code, 403)

    async def test_ai_errors_do_not_leak_internal_details(self):
        with patch.dict(os.environ, {"KOVA_OWNER_API_KEY": OWNER_KEY}):
            with patch(
                "app.api.ai_endpoints.execute_general_command",
                new=AsyncMock(side_effect=RuntimeError("secret-marker")),
            ):
                with patch("app.api.ai_endpoints.logger.exception") as log_exception:
                    response = await self.request(
                        "POST",
                        "/ai/command",
                        owner_key=OWNER_KEY,
                        json={"command": "status", "action": "unexpected"},
                    )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["detail"], "Internal server error")
        self.assertNotIn("secret-marker", response.text)
        log_exception.assert_called_once_with("Unexpected /ai/command failure")


class PublishedExportBoundaryTests(unittest.IsolatedAsyncioTestCase):
    async def request(self, method: str, path: str, **kwargs):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        ) as client:
            return await client.request(method, path, **kwargs)

    async def test_published_export_status_is_public(self):
        with patch.dict(os.environ, {"KOVA_OWNER_API_KEY": ""}):
            response = await self.request("GET", "/api/export/status")

        self.assertEqual(response.status_code, 200)

    async def test_existing_published_site_archive_is_public(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            archive = Path(temp_dir) / "site_final.zip"
            archive.write_bytes(b"published-archive")
            with patch.object(export_endpoints, "SITE_ZIP", archive):
                response = await self.request("GET", "/api/export/site")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"published-archive")

    async def test_missing_published_archive_does_not_trigger_compilation(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            missing_archive = Path(temp_dir) / "missing.zip"
            with patch.object(export_endpoints, "SITE_ZIP", missing_archive):
                with patch.object(export_endpoints.subprocess, "run") as run:
                    response = await self.request("GET", "/api/export/site")

        self.assertEqual(response.status_code, 404)
        run.assert_not_called()

    async def test_upload_mutation_requires_owner_auth_before_subprocess(self):
        with patch.dict(os.environ, {"KOVA_OWNER_API_KEY": OWNER_KEY}):
            with patch.object(export_endpoints.subprocess, "run") as run:
                response = await self.request("POST", "/api/export/gdrive-upload")

        self.assertEqual(response.status_code, 401)
        run.assert_not_called()


class RepositoryPathTests(unittest.TestCase):
    def test_safe_path_is_url_encoded(self):
        self.assertEqual(
            validate_repository_path("docs/KOVA OS.md"),
            "docs/KOVA%20OS.md",
        )

    def test_unsafe_paths_are_rejected(self):
        unsafe_paths = [
            "../secret",
            "/absolute/path",
            "docs\\secret",
            "README.md?ref=other",
            "README.md#fragment",
            "encoded%2Fpath",
        ]

        for file_path in unsafe_paths:
            with self.subTest(file_path=file_path):
                with self.assertRaises(HTTPException) as raised:
                    validate_repository_path(file_path)
                self.assertEqual(raised.exception.status_code, 400)


class CorsConfigurationTests(unittest.TestCase):
    def test_origins_are_trimmed_and_deduplicated(self):
        self.assertEqual(
            parse_allowed_origins(" https://kova.example,https://kova.example "),
            ["https://kova.example"],
        )

    def test_wildcard_origin_is_rejected(self):
        with self.assertRaises(RuntimeError):
            parse_allowed_origins("*")


if __name__ == "__main__":
    unittest.main()
