"""Focused regression tests for KOVA runtime boundary hardening."""

import os
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "kova-ai"))

from fastapi import HTTPException

from app.api.multi_repo_endpoints import RepoAddRequest, add_repository
from app.api.webhooks import handle_push_event, handle_workflow_run_event
from app.database import session as database_session


class DatabaseRuntimeHardeningTests(unittest.TestCase):
    def test_import_uses_explicit_database_url_without_component_password(self):
        env = os.environ.copy()
        env.update(
            {
                "DATABASE_URL": "postgresql+asyncpg://owner@db:5432/kova",
                "POSTGRES_PASSWORD": "",
            }
        )
        package_path = str(Path(__file__).resolve().parents[1] / "kova-ai")
        env["PYTHONPATH"] = os.pathsep.join(
            filter(None, (package_path, env.get("PYTHONPATH", "")))
        )
        result = subprocess.run(
            [sys.executable, "-c", "import app.database.session"],
            cwd=Path(__file__).resolve().parents[1],
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_empty_database_url_uses_component_settings(self):
        with patch.dict(
            os.environ,
            {
                "DATABASE_URL": "",
                "POSTGRES_USER": "owner",
                "POSTGRES_PASSWORD": "pw",
                "POSTGRES_HOST": "postgres.internal",
                "POSTGRES_PORT": "6543",
                "POSTGRES_DB": "kova_core",
            },
            clear=False,
        ):
            self.assertEqual(
                database_session.resolve_database_url(),
                "postgresql+asyncpg://owner:pw@postgres.internal:6543/kova_core",
            )

    def test_database_components_escape_reserved_characters(self):
        with patch.dict(
            os.environ,
            {
                "DATABASE_URL": "",
                "POSTGRES_USER": "owner",
                "POSTGRES_PASSWORD": "p/ss@word",
                "POSTGRES_HOST": "db.internal",
                "POSTGRES_PORT": "5432",
                "POSTGRES_DB": "kova",
            },
            clear=False,
        ):
            url = database_session.build_default_database_url()

        self.assertIn("owner:p%2Fss%40word@db.internal:5432/kova", url)

    def test_template_database_url_is_not_used_as_a_real_dsn(self):
        with patch.dict(
            os.environ,
            {
                "DATABASE_URL": (
                    "postgresql+asyncpg://<db-user>:<db-password>"
                    "@localhost:5432/<db-name>"
                ),
                "POSTGRES_USER": "owner",
                "POSTGRES_PASSWORD": "pw",
                "POSTGRES_HOST": "db",
                "POSTGRES_PORT": "5432",
                "POSTGRES_DB": "kova",
            },
            clear=False,
        ):
            self.assertEqual(
                database_session.resolve_database_url(),
                "postgresql+asyncpg://owner:pw@db:5432/kova",
            )

    def test_blank_component_password_fails_closed(self):
        for password in ("", "   "):
            with self.subTest(password=repr(password)):
                with patch.dict(
                    os.environ,
                    {"DATABASE_URL": "", "POSTGRES_PASSWORD": password},
                    clear=False,
                ):
                    with self.assertRaisesRegex(ValueError, "POSTGRES_PASSWORD"):
                        database_session.resolve_database_url()

    def test_blank_password_rejects_template_dsn_fallback(self):
        with patch.dict(
            os.environ,
            {
                "DATABASE_URL": "postgresql+asyncpg://<user>:<password>@db:5432/kova",
                "POSTGRES_PASSWORD": "",
            },
            clear=False,
        ):
            with self.assertRaisesRegex(ValueError, "POSTGRES_PASSWORD"):
                database_session.resolve_database_url()

    def test_railway_postgres_urls_use_async_driver_without_changing_credentials(self):
        for scheme in ("postgresql", "postgres"):
            with self.subTest(scheme=scheme):
                dsn = f"{scheme}://owner:p%2Fss%40word@postgres.internal:5432/kova?application_name=kova"
                with patch.dict(os.environ, {"DATABASE_URL": dsn}):
                    resolved = database_session.resolve_database_url()
                    self.assertEqual(resolved, "postgresql+asyncpg" + dsn[len(scheme):])
                    engine = database_session.create_database_engine()
                    self.assertTrue(engine.dialect.is_async)
                    self.assertEqual(engine.url.password, "p/ss@word")

    def test_explicit_async_database_url_is_preserved(self):
        dsn = "postgresql+asyncpg://owner:pw@db.internal/kova"
        with patch.dict(os.environ, {"DATABASE_URL": dsn}):
            self.assertEqual(database_session.resolve_database_url(), dsn)

    def test_sqlalchemy_echo_is_off_unless_explicitly_enabled(self):
        with patch.dict(os.environ, {"SQLALCHEMY_ECHO": ""}, clear=False):
            self.assertFalse(database_session.is_sqlalchemy_echo_enabled())

        with patch.dict(os.environ, {"SQLALCHEMY_ECHO": "true"}, clear=False):
            self.assertTrue(database_session.is_sqlalchemy_echo_enabled())


class CanonicalRepositoryMutationTests(unittest.IsolatedAsyncioTestCase):
    async def test_add_rejects_noncanonical_repository(self):
        with self.assertRaises(HTTPException) as raised:
            await add_repository(
                RepoAddRequest(
                    repo_full_name="Kathrynhiggs21/kova-ai-site",
                    repo_type="legacy",
                )
            )

        self.assertEqual(raised.exception.status_code, 422)

    async def test_add_normalizes_case_variant_canonical_repository(self):
        request = RepoAddRequest(
            repo_full_name="kathrynhiggs21/KOVAOS-SITE",
            repo_type="frontend",
        )
        with patch(
            "app.api.multi_repo_endpoints.MultiRepoSyncService.add_repo_to_config",
            new=AsyncMock(return_value=True),
        ) as add_repo:
            response = await add_repository(request)

        self.assertEqual(response.status, "success")
        self.assertEqual(response.data["repo"], "Kathrynhiggs21/kovaos-site")
        add_repo.assert_awaited_once_with("Kathrynhiggs21/kovaos-site", "frontend")



    async def test_readding_case_variant_preserves_saved_registry(self):
        import json
        import tempfile
        from services.multi_repo_sync_service import MultiRepoSyncService

        with tempfile.TemporaryDirectory() as directory:
            config_path = Path(directory) / "registry.json"
            with patch.dict(os.environ, {"KOVA_REPOS_CONFIG": str(config_path)}):
                service = MultiRepoSyncService()
                config = service._get_default_config()
                config["repositories"][0]["name"] = "kova-ai-system"
                config["repositories"][0]["full_name"] = "kathrynhiggs21/kova-ai-system"
                config["integration_settings"]["github_webhooks_enabled"] = True
                config_path.write_text(json.dumps(config))
                original = config_path.read_bytes()
                with patch("services.multi_repo_sync_service.httpx.AsyncClient") as client:
                    response = client.return_value.__aenter__.return_value.get
                    response.return_value.status_code = 200
                    response.return_value.json = lambda: {"name": "Kova-ai-SYSTEM"}
                    result = await service.add_repo_to_config(
                        "Kathrynhiggs21/Kova-ai-SYSTEM", "core"
                    )
                self.assertTrue(result)
                self.assertEqual(config_path.read_bytes(), original)
                reloaded = MultiRepoSyncService()
                self.assertEqual(len(reloaded.config["repositories"]), 2)
                self.assertTrue(reloaded.is_integration_enabled("github_webhooks_enabled"))


class CanonicalWebhookScopeTests(unittest.IsolatedAsyncioTestCase):
    async def test_noncanonical_push_is_ignored_before_ai_forwarding(self):
        payload = {
            "repository": {"full_name": "Kathrynhiggs21/kova-ai-site"},
            "ref": "refs/heads/main",
            "commits": [{"message": "legacy change"}],
        }
        with patch(
            "app.api.webhooks.forward_to_claude",
            new=AsyncMock(),
        ) as forward:
            await handle_push_event(payload)

        forward.assert_not_awaited()

    async def test_case_variant_canonical_workflow_is_forwarded(self):
        payload = {
            "repository": {"full_name": "kathrynhiggs21/kova-ai-system"},
            "workflow_run": {
                "name": "CI",
                "status": "completed",
                "conclusion": "success",
                "run_number": 1,
            },
        }
        with patch(
            "app.api.webhooks.forward_to_claude",
            new=AsyncMock(),
        ) as forward:
            await handle_workflow_run_event(payload)

        forward.assert_awaited_once()


if __name__ == "__main__":
    unittest.main()
