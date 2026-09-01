"""Regression tests for the owner-authenticated multi-repo test client."""

import os
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from scripts.test_multi_repo import MultiRepoTester, load_owner_api_key


OWNER_KEY = "test-client-owner-key"


class MultiRepoClientAuthenticationTests(unittest.IsolatedAsyncioTestCase):
    async def test_protected_request_attaches_owner_header(self):
        response = MagicMock(status_code=200)
        response.json.return_value = {
            "status": "success",
            "data": {"repositories": [], "count": 0},
        }
        client = MagicMock()
        client.get = AsyncMock(return_value=response)

        context = MagicMock()
        context.__aenter__ = AsyncMock(return_value=client)
        context.__aexit__ = AsyncMock(return_value=None)

        tester = MultiRepoTester(owner_api_key=OWNER_KEY)
        with patch(
            "scripts.test_multi_repo.httpx.AsyncClient",
            return_value=context,
        ) as client_class:
            self.assertTrue(await tester.test_list_repos())

        client_class.assert_called_once_with(
            timeout=10.0,
            headers={"X-Kova-API-Key": OWNER_KEY},
        )

    async def test_missing_key_stops_before_protected_requests(self):
        tester = MultiRepoTester(owner_api_key="")
        tester.test_health = AsyncMock(return_value=True)
        tester.test_list_repos = AsyncMock()
        tester.test_get_config = AsyncMock()
        tester.test_get_status = AsyncMock()
        tester.test_discover_repos = AsyncMock()
        tester.test_sync_repos = AsyncMock()

        with patch.object(tester, "log") as log:
            exit_code = await tester.run_all_tests()

        self.assertEqual(exit_code, 1)
        tester.test_list_repos.assert_not_awaited()
        tester.test_get_config.assert_not_awaited()
        tester.test_get_status.assert_not_awaited()
        tester.test_discover_repos.assert_not_awaited()
        tester.test_sync_repos.assert_not_awaited()
        rendered_log = "\n".join(
            str(call.args[0]) for call in log.call_args_list if call.args
        )
        self.assertNotIn(OWNER_KEY, rendered_log)

    def test_process_owner_key_is_loaded_without_transformation(self):
        with patch.dict(os.environ, {"KOVA_OWNER_API_KEY": OWNER_KEY}):
            self.assertEqual(load_owner_api_key(), OWNER_KEY)


if __name__ == "__main__":
    unittest.main()
