#!/usr/bin/env python3
"""
Multi-Repository System Test Script

Tests all multi-repo endpoints and validates the system is working correctly.
"""

import asyncio
import httpx
import sys
import os
from pathlib import Path
import json
from datetime import datetime


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


class MultiRepoTester:
    """Test suite for multi-repository management system"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = []
        self.passed = 0
        self.failed = 0

    def log(self, message: str, color: str = Colors.RESET):
        """Print colored log message"""
        print(f"{color}{message}{Colors.RESET}")

    def log_test(self, name: str, passed: bool, details: str = ""):
        """Log test result"""
        status = f"{Colors.GREEN}✓ PASS{Colors.RESET}" if passed else f"{Colors.RED}✗ FAIL{Colors.RESET}"
        self.log(f"  {status} - {name}")
        if details:
            self.log(f"         {details}", Colors.YELLOW)

        self.results.append({"name": name, "passed": passed, "details": details})
        if passed:
            self.passed += 1
        else:
            self.failed += 1

    async def test_health(self) -> bool:
        """Test basic health endpoint"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
        except Exception as e:
            self.log(f"Health check failed: {e}", Colors.RED)
            return False

    async def test_list_repos(self) -> bool:
        """Test listing all repositories"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/multi-repo/list")

                if response.status_code != 200:
                    self.log_test("List Repositories", False, f"Status code: {response.status_code}")
                    return False

                data = response.json()
                if data.get("status") != "success":
                    self.log_test("List Repositories", False, "Response status not success")
                    return False

                repo_count = data.get("data", {}).get("count", 0)
                self.log_test("List Repositories", True, f"Found {repo_count} repositories")
                return True
        except Exception as e:
            self.log_test("List Repositories", False, str(e))
            return False

    async def test_get_status(self) -> bool:
        """Test getting status of all repositories"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.base_url}/multi-repo/status")

                if response.status_code != 200:
                    self.log_test("Get Repo Status", False, f"Status code: {response.status_code}")
                    return False

                data = response.json()
                if data.get("status") != "success":
                    self.log_test("Get Repo Status", False, "Response status not success")
                    return False

                total_repos = data.get("data", {}).get("total_repos", 0)
                self.log_test("Get Repo Status", True, f"Checked {total_repos} repositories")
                return True
        except Exception as e:
            self.log_test("Get Repo Status", False, str(e))
            return False

    async def test_discover_repos(self) -> bool:
        """Test discovering new repositories"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.base_url}/multi-repo/discover")

                if response.status_code != 200:
                    self.log_test("Discover Repos", False, f"Status code: {response.status_code}")
                    return False

                data = response.json()
                new_repo_count = data.get("data", {}).get("count", 0)
                self.log_test("Discover Repos", True, f"Found {new_repo_count} new repositories")
                return True
        except Exception as e:
            self.log_test("Discover Repos", False, str(e))
            return False

    async def test_get_config(self) -> bool:
        """Test getting repository configuration"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/multi-repo/config")

                if response.status_code != 200:
                    self.log_test("Get Config", False, f"Status code: {response.status_code}")
                    return False

                data = response.json()
                config = data.get("data", {})
                owner = config.get("github_owner", "")
                self.log_test("Get Config", True, f"GitHub owner: {owner}")
                return True
        except Exception as e:
            self.log_test("Get Config", False, str(e))
            return False

    async def test_sync_repos(self, include_claude: bool = False) -> bool:
        """Test syncing repositories"""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                payload = {"include_claude": include_claude}
                response = await client.post(
                    f"{self.base_url}/multi-repo/sync",
                    json=payload
                )

                if response.status_code != 200:
                    self.log_test("Sync Repositories", False, f"Status code: {response.status_code}")
                    return False

                data = response.json()
                repos_synced = data.get("data", {}).get("repos_synced", 0)
                test_name = "Sync Repositories (with Claude)" if include_claude else "Sync Repositories"
                self.log_test(test_name, True, f"Synced {repos_synced} repositories")
                return True
        except Exception as e:
            test_name = "Sync Repositories (with Claude)" if include_claude else "Sync Repositories"
            self.log_test(test_name, False, str(e))
            return False

    def validate_config_file(self) -> bool:
        """Validate the kova_repos_config.json file"""
        config_path = Path(__file__).parent.parent / "kova_repos_config.json"

        try:
            if not config_path.exists():
                self.log_test("Validate Config File", False, "Config file not found")
                return False

            with open(config_path, 'r') as f:
                config = json.load(f)

            # Check required fields
            required_fields = ["github_owner", "repositories", "sync_settings"]
            for field in required_fields:
                if field not in config:
                    self.log_test("Validate Config File", False, f"Missing field: {field}")
                    return False

            repo_count = len(config.get("repositories", []))
            self.log_test("Validate Config File", True, f"Config valid with {repo_count} repos")
            return True
        except json.JSONDecodeError as e:
            self.log_test("Validate Config File", False, f"Invalid JSON: {e}")
            return False
        except Exception as e:
            self.log_test("Validate Config File", False, str(e))
            return False

    def validate_env_file(self) -> bool:
        """Validate environment configuration"""
        env_example_path = Path(__file__).parent.parent / "kova-ai" / ".env.example"

        try:
            if not env_example_path.exists():
                self.log_test("Validate .env.example", False, "File not found")
                return False

            with open(env_example_path, 'r') as f:
                content = f.read()

            # Check for required environment variables
            required_vars = ["GITHUB_TOKEN", "ANTHROPIC_API_KEY", "DATABASE_URL"]
            missing_vars = [var for var in required_vars if var not in content]

            if missing_vars:
                self.log_test("Validate .env.example", False, f"Missing: {', '.join(missing_vars)}")
                return False

            self.log_test("Validate .env.example", True, "All required variables present")
            return True
        except Exception as e:
            self.log_test("Validate .env.example", False, str(e))
            return False

    async def run_all_tests(self):
        """Run all tests"""
        self.log(f"\n{Colors.BOLD}=== Kova AI Multi-Repository System Tests ==={Colors.RESET}\n")
        self.log(f"Testing endpoint: {Colors.BLUE}{self.base_url}{Colors.RESET}\n")

        # Configuration tests (don't require API to be running)
        self.log(f"{Colors.BOLD}Configuration Tests:{Colors.RESET}")
        self.validate_config_file()
        self.validate_env_file()

        # API tests (require API to be running)
        self.log(f"\n{Colors.BOLD}API Endpoint Tests:{Colors.RESET}")

        # Check if API is running
        api_running = await self.test_health()
        if not api_running:
            self.log("\n⚠️  API is not running. Start it with:", Colors.YELLOW)
            self.log("   cd kova-ai && docker-compose up -d\n", Colors.YELLOW)
            self.log_test("Health Check", False, "API not responding")
        else:
            self.log_test("Health Check", True, "API is running")

            # Run API tests
            await self.test_list_repos()
            await self.test_get_config()
            await self.test_get_status()
            await self.test_discover_repos()
            await self.test_sync_repos(include_claude=False)

        # Print summary
        return self.print_summary()

    def print_summary(self):
        """Print test summary"""
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0

        self.log(f"\n{Colors.BOLD}=== Test Summary ==={Colors.RESET}")
        self.log(f"Total Tests: {total}")
        self.log(f"Passed: {Colors.GREEN}{self.passed}{Colors.RESET}")
        self.log(f"Failed: {Colors.RED}{self.failed}{Colors.RESET}")
        self.log(f"Pass Rate: {pass_rate:.1f}%\n")

        if self.failed == 0:
            self.log(f"{Colors.GREEN}{Colors.BOLD}✓ All tests passed!{Colors.RESET}\n")
            return 0
        else:
            self.log(f"{Colors.RED}{Colors.BOLD}✗ Some tests failed{Colors.RESET}\n")
            return 1


async def main():
    """Main entry point"""
    tester = MultiRepoTester()
    exit_code = await tester.run_all_tests()
    sys.exit(exit_code)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Tests interrupted by user{Colors.RESET}")
        sys.exit(1)
