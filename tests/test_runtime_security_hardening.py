"""Focused regression tests for KOVA runtime boundary hardening."""

import os
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
