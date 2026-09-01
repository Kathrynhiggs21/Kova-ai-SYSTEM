"""Runtime regression tests for the canonical KOVA repository registry."""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "kova-ai"))

from fastapi import HTTPException

from app.api.ai_endpoints import load_kova_repos_from_config
from app.api.multi_repo_endpoints import RepoSyncRequest, sync_repositories
from app.services.multi_repo_sync_service import MultiRepoSyncService


CANONICAL_REPOSITORIES = [
    "Kathrynhiggs21/Kova-ai-SYSTEM",
    "Kathrynhiggs21/kova-ai-dash",
]


def write_config(path: Path, *, claude_enabled: bool = False) -> None:
    path.write_text(
        json.dumps(
            {
                "github_owner": "Kathrynhiggs21",
                "repositories": [
                    {
                        "name": "Kova-ai-SYSTEM",
                        "full_name": CANONICAL_REPOSITORIES[0],
                        "description": "Canonical KOVA OS orchestrator",
                        "type": "core",
                        "enabled": True,
                        "sync_priority": 1,
                        "features": ["orchestration"],
                    },
                    {
                        "name": "kova-ai-dash",
                        "full_name": CANONICAL_REPOSITORIES[1],
                        "description": "KOVA OS command center",
                        "type": "frontend",
                        "enabled": True,
                        "sync_priority": 1,
                        "features": ["dashboard"],
                    },
                    {
                        "name": "disabled",
                        "full_name": "Kathrynhiggs21/disabled",
                        "description": "Disabled test repository",
                        "type": "service",
                        "enabled": False,
                        "sync_priority": 5,
                        "features": [],
                    },
                ],
                "sync_settings": {
                    "auto_sync_enabled": False,
                    "sync_interval_minutes": 30,
                    "sync_on_push": False,
                    "sync_on_pr": False,
                    "cross_repo_notifications": False,
                },
                "discovery_settings": {
                    "auto_discover_new_repos": False,
                    "repo_name_pattern": "kova-ai-",
                    "watch_for_new_repos": False,
                },
                "integration_settings": {
                    "claude_api_enabled": claude_enabled,
                    "github_webhooks_enabled": False,
                    "cross_repo_prs": False,
                    "unified_changelog": False,
                },
            }
        ),
        encoding="utf-8",
    )


class RepositoryRegistryRuntimeTests(unittest.IsolatedAsyncioTestCase):
    async def test_ai_loader_uses_registry_and_excludes_disabled_repositories(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "kova_repos_config.json"
            write_config(config_path)
            with patch.dict(os.environ, {"KOVA_REPOS_CONFIG": str(config_path)}):
                repositories = await load_kova_repos_from_config()

        self.assertEqual(repositories, CANONICAL_REPOSITORIES)

    async def test_missing_registry_falls_back_to_canonical_repositories(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            missing_path = Path(temp_dir) / "missing.json"
            with patch.dict(os.environ, {"KOVA_REPOS_CONFIG": str(missing_path)}):
                service = MultiRepoSyncService()

        self.assertEqual(service.get_enabled_repos(), CANONICAL_REPOSITORIES)

    async def test_non_object_registry_falls_back_to_canonical_repositories(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "kova_repos_config.json"
            config_path.write_text("[]", encoding="utf-8")
            with patch.dict(os.environ, {"KOVA_REPOS_CONFIG": str(config_path)}):
                service = MultiRepoSyncService()

        self.assertEqual(service.get_enabled_repos(), CANONICAL_REPOSITORIES)

    async def test_malformed_repository_falls_back_to_canonical_repositories(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "kova_repos_config.json"
            config_path.write_text(
                json.dumps(
                    {
                        "github_owner": "Kathrynhiggs21",
                        "repositories": [{"full_name": [], "enabled": True}],
                    }
                ),
                encoding="utf-8",
            )
            with patch.dict(os.environ, {"KOVA_REPOS_CONFIG": str(config_path)}):
                service = MultiRepoSyncService()

        self.assertEqual(service.get_enabled_repos(), CANONICAL_REPOSITORIES)

    async def test_claude_service_stays_disabled_even_when_key_exists(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "kova_repos_config.json"
            write_config(config_path, claude_enabled=False)
            with patch.dict(os.environ, {"KOVA_REPOS_CONFIG": str(config_path)}):
                service = MultiRepoSyncService(claude_api_key="configured-key")
                with patch(
                    "app.services.multi_repo_sync_service.httpx.AsyncClient"
                ) as http_client:
                    result = await service.sync_with_claude({"name": "KOVA"})

        self.assertEqual(result["status"], "disabled")
        http_client.assert_not_called()

    async def test_enabled_claude_service_reports_missing_key_consistently(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "kova_repos_config.json"
            write_config(config_path, claude_enabled=True)
            with patch.dict(
                os.environ,
                {
                    "KOVA_REPOS_CONFIG": str(config_path),
                    "ANTHROPIC_API_KEY": "",
                },
            ):
                service = MultiRepoSyncService(claude_api_key="")
                with patch(
                    "app.services.multi_repo_sync_service.httpx.AsyncClient"
                ) as http_client:
                    result = await service.sync_with_claude({"name": "KOVA"})

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"], "Claude API key not configured")
        http_client.assert_not_called()

    async def test_sync_endpoint_rejects_disabled_claude_request(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "kova_repos_config.json"
            write_config(config_path, claude_enabled=False)
            with patch.dict(os.environ, {"KOVA_REPOS_CONFIG": str(config_path)}):
                with patch(
                    "app.api.multi_repo_endpoints.MultiRepoSyncService.sync_all_repositories",
                    new=AsyncMock(return_value={}),
                ):
                    with self.assertRaises(HTTPException) as raised:
                        await sync_repositories(RepoSyncRequest(include_claude=True))

        self.assertEqual(raised.exception.status_code, 409)


if __name__ == "__main__":
    unittest.main()
