#!/usr/bin/env python3
"""
Configuration Validator for Kova AI Multi-Repository System

Validates kova_repos_config.json structure and content.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple


class Colors:
    """ANSI color codes"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


class ConfigValidator:
    """Validates Kova AI repository configuration"""

    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.errors = []
        self.warnings = []
        self.config = None

    def log(self, message: str, color: str = Colors.RESET):
        """Print colored message"""
        print(f"{color}{message}{Colors.RESET}")

    def error(self, message: str):
        """Log an error"""
        self.errors.append(message)
        self.log(f"  ✗ ERROR: {message}", Colors.RED)

    def warning(self, message: str):
        """Log a warning"""
        self.warnings.append(message)
        self.log(f"  ⚠ WARNING: {message}", Colors.YELLOW)

    def success(self, message: str):
        """Log a success"""
        self.log(f"  ✓ {message}", Colors.GREEN)

    def validate_file_exists(self) -> bool:
        """Check if config file exists"""
        if not self.config_path.exists():
            self.error(f"Config file not found: {self.config_path}")
            return False
        self.success("Config file found")
        return True

    def validate_json_format(self) -> bool:
        """Validate JSON format"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
            self.success("Valid JSON format")
            return True
        except json.JSONDecodeError as e:
            self.error(f"Invalid JSON: {e}")
            return False
        except Exception as e:
            self.error(f"Failed to read file: {e}")
            return False

    def validate_required_fields(self) -> bool:
        """Validate required top-level fields"""
        required_fields = {
            "github_owner": str,
            "repositories": list,
            "sync_settings": dict,
            "discovery_settings": dict,
            "integration_settings": dict
        }

        all_valid = True
        for field, expected_type in required_fields.items():
            if field not in self.config:
                self.error(f"Missing required field: {field}")
                all_valid = False
            elif not isinstance(self.config[field], expected_type):
                self.error(f"Field '{field}' should be {expected_type.__name__}, got {type(self.config[field]).__name__}")
                all_valid = False
            else:
                self.success(f"Field '{field}' present and valid")

        return all_valid

    def validate_github_owner(self) -> bool:
        """Validate GitHub owner field"""
        owner = self.config.get("github_owner", "")
        if not owner or not isinstance(owner, str):
            self.error("github_owner must be a non-empty string")
            return False
        if " " in owner:
            self.error("github_owner should not contain spaces")
            return False
        self.success(f"GitHub owner: {owner}")
        return True

    def validate_repositories(self) -> bool:
        """Validate repositories list"""
        repos = self.config.get("repositories", [])

        if not repos:
            self.warning("No repositories configured")
            return True

        required_repo_fields = ["name", "full_name", "type", "enabled"]
        recommended_repo_fields = ["description", "sync_priority", "features"]
        valid_repo_types = ["core", "service", "frontend", "experimental"]

        all_valid = True
        for i, repo in enumerate(repos):
            self.log(f"\n  Validating repo #{i + 1}: {repo.get('name', 'unknown')}", Colors.BLUE)

            # Check required fields
            for field in required_repo_fields:
                if field not in repo:
                    self.error(f"  Repo '{repo.get('name', 'unknown')}' missing required field: {field}")
                    all_valid = False

            # Check recommended fields
            for field in recommended_repo_fields:
                if field not in repo:
                    self.warning(f"  Repo '{repo.get('name', 'unknown')}' missing recommended field: {field}")

            # Validate repo type
            if "type" in repo and repo["type"] not in valid_repo_types:
                self.warning(f"  Repo type '{repo['type']}' not in standard types: {valid_repo_types}")

            # Validate full_name format
            if "full_name" in repo:
                full_name = repo["full_name"]
                if "/" not in full_name:
                    self.error(f"  Invalid full_name format: {full_name} (should be 'owner/repo')")
                    all_valid = False
                else:
                    owner, name = full_name.split("/", 1)
                    if owner != self.config.get("github_owner"):
                        self.warning(f"  Repo owner '{owner}' doesn't match github_owner '{self.config.get('github_owner')}'")

            # Validate sync_priority
            if "sync_priority" in repo:
                priority = repo["sync_priority"]
                if not isinstance(priority, int) or priority < 1 or priority > 5:
                    self.warning(f"  sync_priority should be between 1-5, got: {priority}")

            # Validate features
            if "features" in repo:
                if not isinstance(repo["features"], list):
                    self.error(f"  'features' should be a list")
                    all_valid = False

        if all_valid:
            self.success(f"All {len(repos)} repositories valid")
        return all_valid

    def validate_sync_settings(self) -> bool:
        """Validate sync settings"""
        settings = self.config.get("sync_settings", {})

        recommended_fields = {
            "auto_sync_enabled": bool,
            "sync_interval_minutes": int,
            "sync_on_push": bool,
            "sync_on_pr": bool,
            "cross_repo_notifications": bool
        }

        all_valid = True
        for field, expected_type in recommended_fields.items():
            if field not in settings:
                self.warning(f"Missing recommended sync setting: {field}")
            elif not isinstance(settings[field], expected_type):
                self.error(f"sync_settings.{field} should be {expected_type.__name__}")
                all_valid = False
            else:
                self.success(f"sync_settings.{field}: {settings[field]}")

        return all_valid

    def validate_discovery_settings(self) -> bool:
        """Validate discovery settings"""
        settings = self.config.get("discovery_settings", {})

        recommended_fields = {
            "auto_discover_new_repos": bool,
            "repo_name_pattern": str,
            "watch_for_new_repos": bool
        }

        all_valid = True
        for field, expected_type in recommended_fields.items():
            if field not in settings:
                self.warning(f"Missing recommended discovery setting: {field}")
            elif not isinstance(settings[field], expected_type):
                self.error(f"discovery_settings.{field} should be {expected_type.__name__}")
                all_valid = False
            else:
                self.success(f"discovery_settings.{field}: {settings[field]}")

        return all_valid

    def validate_integration_settings(self) -> bool:
        """Validate integration settings"""
        settings = self.config.get("integration_settings", {})

        recommended_fields = {
            "claude_api_enabled": bool,
            "github_webhooks_enabled": bool,
            "cross_repo_prs": bool,
            "unified_changelog": bool
        }

        all_valid = True
        for field, expected_type in recommended_fields.items():
            if field not in settings:
                self.warning(f"Missing recommended integration setting: {field}")
            elif not isinstance(settings[field], expected_type):
                self.error(f"integration_settings.{field} should be {expected_type.__name__}")
                all_valid = False
            else:
                self.success(f"integration_settings.{field}: {settings[field]}")

        return all_valid

    def check_duplicates(self) -> bool:
        """Check for duplicate repositories"""
        repos = self.config.get("repositories", [])
        names = [repo.get("name") for repo in repos]
        full_names = [repo.get("full_name") for repo in repos]

        duplicates = []
        seen_names = set()
        seen_full_names = set()

        for name in names:
            if name in seen_names:
                duplicates.append(f"Duplicate name: {name}")
            seen_names.add(name)

        for full_name in full_names:
            if full_name in seen_full_names:
                duplicates.append(f"Duplicate full_name: {full_name}")
            seen_full_names.add(full_name)

        if duplicates:
            for dup in duplicates:
                self.error(dup)
            return False
        else:
            self.success("No duplicate repositories found")
            return True

    def validate_all(self) -> Tuple[bool, Dict[str, Any]]:
        """Run all validations"""
        self.log(f"\n{Colors.BOLD}=== Validating Kova AI Repository Configuration ==={Colors.RESET}\n")
        self.log(f"Config file: {Colors.BLUE}{self.config_path}{Colors.RESET}\n")

        # Run validations
        validations = [
            ("File Existence", self.validate_file_exists),
            ("JSON Format", self.validate_json_format),
        ]

        # Only run these if file exists and is valid JSON
        if self.config:
            validations.extend([
                ("Required Fields", self.validate_required_fields),
                ("GitHub Owner", self.validate_github_owner),
                ("Repositories", self.validate_repositories),
                ("Sync Settings", self.validate_sync_settings),
                ("Discovery Settings", self.validate_discovery_settings),
                ("Integration Settings", self.validate_integration_settings),
                ("Duplicate Check", self.check_duplicates),
            ])

        all_passed = True
        for name, validator in validations:
            self.log(f"\n{Colors.BOLD}{name}:{Colors.RESET}")
            try:
                if not validator():
                    all_passed = False
            except Exception as e:
                self.error(f"Validation failed: {e}")
                all_passed = False

        # Print summary
        self.print_summary(all_passed)

        return all_passed, {
            "errors": self.errors,
            "warnings": self.warnings,
            "config": self.config
        }

    def print_summary(self, passed: bool):
        """Print validation summary"""
        self.log(f"\n{Colors.BOLD}=== Validation Summary ==={Colors.RESET}")
        self.log(f"Errors: {Colors.RED}{len(self.errors)}{Colors.RESET}")
        self.log(f"Warnings: {Colors.YELLOW}{len(self.warnings)}{Colors.RESET}\n")

        if passed and len(self.errors) == 0:
            self.log(f"{Colors.GREEN}{Colors.BOLD}✓ Configuration is valid!{Colors.RESET}\n")
        else:
            self.log(f"{Colors.RED}{Colors.BOLD}✗ Configuration has errors{Colors.RESET}\n")


def main():
    """Main entry point"""
    # Find config file
    config_path = Path(__file__).parent.parent / "kova_repos_config.json"

    if len(sys.argv) > 1:
        config_path = Path(sys.argv[1])

    # Validate
    validator = ConfigValidator(config_path)
    passed, results = validator.validate_all()

    # Exit with appropriate code
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Validation interrupted{Colors.RESET}")
        sys.exit(1)
