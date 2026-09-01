"""Runtime regression tests for the canonical KOVA repository registry."""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

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
                    {"full_name": CANONICAL_REPOSITORIES[0], "enabled": True},
                    {"full_name": CANONICAL_REPOSITORIES[1], "enabled": True},
                    {"full_name": "example/disabled", "enabled": False},
                ],
                "integration_settings": {
                    "claude_api_enabled": claude_enabled,
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

    async def test_claude_service_stays_disabled_even_when_key_exists(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "kova_repos_config.json"
            write_config(config_path, claude_enabled=False)
            with patch.dict(os.environ, {"KOVA_REPOS_CONFIG": str(config_path)}):
                service = MultiRepoSyncService(claude_api_key="configured-key")
                result = await service.sync_with_claude({"name": "KOVA"})

        self.assertEqual(result["status"], "disabled")

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
