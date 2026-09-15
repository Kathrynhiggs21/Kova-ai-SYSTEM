#!/usr/bin/env python3
"""
Configuration Validator for Kova AI Multi-Repository System

Validates kova_repos_config.json structure and content.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "kova-ai"))

from app.core.repository_registry import (  # noqa: E402
    is_safe_github_owner,
    parse_github_repository,
    repository_key,
)


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

    def get_repository_root(self) -> Path:
        """Resolve the repository root for the current config path."""
        config_root = self.config_path.parent.resolve()
        for candidate in (config_root, *config_root.parents):
            if (candidate / ".git").exists():
                return candidate
        if self.config_path.resolve().is_relative_to(PROJECT_ROOT):
            return PROJECT_ROOT
        return config_root

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
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            if not isinstance(self.config, dict):
                self.error("Top-level JSON value must be an object")
                return False
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
            "worlds": list,
            "excluded_repositories": list,
            "sync_settings": dict,
            "discovery_settings": dict,
            "integration_settings": dict,
            "architecture_mode": str,
            "repository_creation_policy": dict,
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
        if not is_safe_github_owner(owner):
            self.error("github_owner must be a URL-safe GitHub owner name")
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
            if not isinstance(repo, dict):
                self.error(f"Repository entry #{i + 1} must be an object")
                all_valid = False
                continue

            self.log(
                f"\n  Validating repo #{i + 1}: {repo.get('name', 'unknown')}",
                Colors.BLUE,
            )

            # Check required fields
            required_repo_types = {
                "name": str,
                "full_name": str,
                "type": str,
                "enabled": bool,
            }
            for field in required_repo_fields:
                if field not in repo:
                    self.error(f"  Repo '{repo.get('name', 'unknown')}' missing required field: {field}")
                    all_valid = False
                elif not isinstance(repo[field], required_repo_types[field]):
                    self.error(
                        f"  Repo '{repo.get('name', 'unknown')}' field '{field}' "
                        f"should be {required_repo_types[field].__name__}"
                    )
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
                parsed_repository = parse_github_repository(full_name)
                if parsed_repository is None:
                    self.error(
                        f"  Invalid GitHub repository coordinate: {full_name} "
                        "(should be a URL-safe 'owner/repo')"
                    )
                    all_valid = False
                else:
                    owner, name = parsed_repository
                    if owner.casefold() != str(
                        self.config.get("github_owner", "")
                    ).casefold():
                        self.error(
                            f"  Repo owner '{owner}' doesn't match github_owner "
                            f"'{self.config.get('github_owner')}'"
                        )
                        all_valid = False
                    if repo.get("name") != name:
                        self.error(
                            f"  Repo name '{repo.get('name')}' does not match "
                            f"full_name repository '{name}'"
                        )
                        all_valid = False

            # Validate sync_priority
            if "sync_priority" in repo:
                priority = repo["sync_priority"]
                if (
                    not isinstance(priority, int)
                    or isinstance(priority, bool)
                    or priority < 1
                    or priority > 5
                ):
                    self.error(f"  sync_priority should be an integer between 1-5, got: {priority}")
                    all_valid = False

            # Validate features
            if "features" in repo:
                if not isinstance(repo["features"], list):
                    self.error(f"  'features' should be a list")
                    all_valid = False
                elif not all(isinstance(feature, str) for feature in repo["features"]):
                    self.error("  'features' entries should all be strings")
                    all_valid = False

        if all_valid:
            self.success(f"All {len(repos)} repositories valid")
        return all_valid

    def validate_sync_settings(self) -> bool:
        """Validate sync settings"""
        settings = self.config.get("sync_settings", {})
        if not isinstance(settings, dict):
            return False

        required_fields = {
            "auto_sync_enabled": bool,
            "sync_interval_minutes": int,
            "sync_on_push": bool,
            "sync_on_pr": bool,
            "cross_repo_notifications": bool
        }

        all_valid = True
        for field, expected_type in required_fields.items():
            if field not in settings:
                self.error(f"Missing required sync setting: {field}")
                all_valid = False
            elif type(settings[field]) is not expected_type:
                self.error(f"sync_settings.{field} should be {expected_type.__name__}")
                all_valid = False
            elif field == "sync_interval_minutes" and settings[field] <= 0:
                self.error("sync_settings.sync_interval_minutes must be positive")
                all_valid = False
            else:
                self.success(f"sync_settings.{field}: {settings[field]}")

        return all_valid

    def validate_discovery_settings(self) -> bool:
        """Validate discovery settings"""
        settings = self.config.get("discovery_settings", {})
        if not isinstance(settings, dict):
            return False

        required_fields = {
            "auto_discover_new_repos": bool,
            "repo_name_pattern": str,
            "watch_for_new_repos": bool
        }

        all_valid = True
        for field, expected_type in required_fields.items():
            if field not in settings:
                self.error(f"Missing required discovery setting: {field}")
                all_valid = False
            elif type(settings[field]) is not expected_type:
                self.error(f"discovery_settings.{field} should be {expected_type.__name__}")
                all_valid = False
            elif field == "repo_name_pattern" and not settings[field].strip():
                self.error("discovery_settings.repo_name_pattern cannot be empty")
                all_valid = False
            else:
                self.success(f"discovery_settings.{field}: {settings[field]}")

        return all_valid

    def validate_integration_settings(self) -> bool:
        """Validate integration settings"""
        settings = self.config.get("integration_settings", {})
        if not isinstance(settings, dict):
            return False

        required_fields = {
            "claude_api_enabled": bool,
            "github_webhooks_enabled": bool,
            "cross_repo_prs": bool,
            "unified_changelog": bool
        }

        all_valid = True
        for field, expected_type in required_fields.items():
            if field not in settings:
                self.error(f"Missing required integration setting: {field}")
                all_valid = False
            elif type(settings[field]) is not expected_type:
                self.error(f"integration_settings.{field} should be {expected_type.__name__}")
                all_valid = False
            else:
                self.success(f"integration_settings.{field}: {settings[field]}")

        return all_valid

    def validate_catalog_collections(self) -> bool:
        """Validate disabled World and excluded repository catalog entries."""
        all_valid = True
        for index, world in enumerate(self.config.get("worlds", []), start=1):
            if not isinstance(world, dict):
                self.error(f"World entry #{index} must be an object")
                all_valid = False
                continue
            required = {
                "name": str,
                "full_name": str,
                "type": str,
                "enabled": bool,
                "relationship": str,
                "lifecycle": str,
            }
            for field, expected_type in required.items():
                if type(world.get(field)) is not expected_type:
                    self.error(
                        f"World entry #{index} field '{field}' should be "
                        f"{expected_type.__name__}"
                    )
                    all_valid = False
            parsed_repository = parse_github_repository(world.get("full_name"))
            if parsed_repository is None:
                self.error(f"World entry #{index} has an invalid repository coordinate")
                all_valid = False
            else:
                if parsed_repository[0].casefold() != self.config.get(
                    "github_owner", ""
                ).casefold():
                    self.error(f"World entry #{index} owner does not match github_owner")
                    all_valid = False
                if world.get("name") != parsed_repository[1]:
                    self.error(f"World entry #{index} name does not match full_name")
                    all_valid = False
            if world.get("type") != "world":
                self.error(f"World entry #{index} type must be world")
                all_valid = False
            if world.get("enabled") is not False:
                self.error(
                    f"World entry #{index} must remain disabled in the Core registry"
                )
                all_valid = False
            if world.get("lifecycle") not in {
                "active",
                "final",
                "review",
                "archive",
                "unreviewed",
            }:
                self.error(f"World entry #{index} has an invalid lifecycle")
                all_valid = False

        for index, repository in enumerate(
            self.config.get("excluded_repositories", []), start=1
        ):
            if not isinstance(repository, dict):
                self.error(f"Excluded repository entry #{index} must be an object")
                all_valid = False
                continue
            if parse_github_repository(repository.get("full_name")) is None:
                self.error(
                    f"Excluded repository entry #{index} has an invalid coordinate"
                )
                all_valid = False
            if not isinstance(repository.get("reason"), str) or not repository[
                "reason"
            ].strip():
                self.error(f"Excluded repository entry #{index} needs a reason")
                all_valid = False
            if repository.get("enabled") is not False:
                self.error(f"Excluded repository entry #{index} must be disabled")
                all_valid = False

        if all_valid:
            self.success("World and excluded repository catalogs valid")
        return all_valid

    def validate_repository_creation_policy(self) -> bool:
        """Validate the canonical repository-split policy and its local paths."""
        policy_pointer = self.config.get("repository_creation_policy")
        if not isinstance(policy_pointer, dict):
            self.error("repository_creation_policy must be an object")
            return False

        description = policy_pointer.get("description")
        policy_reference = policy_pointer.get("split_policy_file")
        if not isinstance(description, str) or not description.strip():
            self.error("repository_creation_policy.description must be non-empty")
            return False
        if not isinstance(policy_reference, str) or not policy_reference.strip():
            self.error(
                "repository_creation_policy.split_policy_file must be a non-empty "
                "repository-root-relative path"
            )
            return False

        relative_policy_path = Path(policy_reference)
        repository_root = self.get_repository_root()
        if relative_policy_path.is_absolute():
            self.error("split_policy_file must be repository-root-relative")
            return False

        policy_path = (repository_root / relative_policy_path).resolve()
        if not policy_path.is_relative_to(repository_root):
            self.error("split_policy_file must stay within the repository root")
            return False
        if not policy_path.is_file():
            self.error(f"split_policy_file not found: {policy_reference}")
            return False

        resolved_policy_path = policy_path.resolve(strict=False)
        if not resolved_policy_path.is_relative_to(repository_root):
            self.error("split_policy_file must stay within the repository root")
            return False

        try:
            with open(resolved_policy_path, "r", encoding="utf-8") as file_handle:
                policy = json.load(file_handle)
        except json.JSONDecodeError as e:
            self.error(f"split_policy_file contains invalid JSON: {e}")
            return False
        except OSError as e:
            self.error(f"Failed to read split_policy_file: {e}")
            return False

        if not isinstance(policy, dict):
            self.error("split_policy_file top-level JSON value must be an object")
            return False

        if "active_repositories" in policy:
            self.error(
                "split_policy_file must not duplicate the active repository set; "
                "use repositories[].enabled"
            )
            return False

        all_valid = True
        required_policy_fields = {
            "schema_version": int,
            "architecture": str,
            "modules": list,
            "split_policy": dict,
        }
        for field, expected_type in required_policy_fields.items():
            if field not in policy:
                self.error(f"split_policy_file missing required field: {field}")
                all_valid = False
            elif type(policy[field]) is not expected_type:
                self.error(
                    "split_policy_file field "
                    f"'{field}' should be {expected_type.__name__}"
                )
                all_valid = False

        modules = policy.get("modules", [])
        if isinstance(modules, list):
            registry_repositories = {
                repository.get("full_name", "").casefold(): repository
                for repository in self.config.get("repositories", [])
                if isinstance(repository, dict)
                and isinstance(repository.get("full_name"), str)
            }
            core_repositories = {
                full_name
                for full_name, repository in registry_repositories.items()
                if repository.get("type") == "core" and repository.get("enabled") is True
            }
            seen_module_ids = set()
            required_module_fields = {
                "id": str,
                "repository": str,
                "current_paths": list,
                "responsibility": str,
                "separate_repository": bool,
            }
            for index, module in enumerate(modules, start=1):
                if not isinstance(module, dict):
                    self.error(
                        f"split_policy_file module #{index} must be an object"
                    )
                    all_valid = False
                    continue
                for field, expected_type in required_module_fields.items():
                    if field not in module:
                        self.error(
                            "split_policy_file module "
                            f"#{index} missing required field: {field}"
                        )
                        all_valid = False
                    elif type(module[field]) is not expected_type:
                        self.error(
                            "split_policy_file module "
                            f"#{index} field '{field}' should be "
                            f"{expected_type.__name__}"
                        )
                        all_valid = False

                module_id = module.get("id")
                if isinstance(module_id, str):
                    normalized_module_id = module_id.casefold()
                    if normalized_module_id in seen_module_ids:
                        self.error(f"split_policy_file duplicate module id: {module_id}")
                        all_valid = False
                    seen_module_ids.add(normalized_module_id)

                module_repository = module.get("repository")
                normalized_repository = (
                    module_repository.casefold()
                    if isinstance(module_repository, str)
                    else ""
                )
                if normalized_repository not in registry_repositories:
                    self.error(
                        "split_policy_file module "
                        f"#{index} references an unregistered repository: "
                        f"{module_repository}"
                    )
                    all_valid = False

                if "current_paths" in module and (
                    not isinstance(module["current_paths"], list)
                    or not all(
                        isinstance(path, str) and path
                        for path in module["current_paths"]
                    )
                ):
                    self.error(
                        "split_policy_file module "
                        f"#{index} current_paths must contain non-empty strings"
                    )
                    all_valid = False

                if normalized_repository in core_repositories:
                    for field in ("current_paths", "excluded_paths"):
                        for current_path in module.get(field, []):
                            if not isinstance(current_path, str) or not current_path:
                                continue
                            relative_path = Path(current_path)
                            resolved_path = (repository_root / relative_path).resolve()
                            if relative_path.is_absolute() or not resolved_path.is_relative_to(
                                repository_root
                            ):
                                self.error(
                                    "split_policy_file module "
                                    f"#{index} {field} contains an unsafe path: "
                                    f"{current_path}"
                                )
                                all_valid = False
                            elif not resolved_path.exists():
                                self.error(
                                    "split_policy_file module "
                                    f"#{index} {field} path not found: {current_path}"
                                )
                                all_valid = False
                excluded_paths = module.get("excluded_paths")
                if excluded_paths is not None and (
                    not isinstance(excluded_paths, list)
                    or not all(
                        isinstance(path, str) and path for path in excluded_paths
                    )
                ):
                    self.error(
                        "split_policy_file module "
                        f"#{index} excluded_paths must contain non-empty strings"
                    )
                    all_valid = False

        split_policy = policy.get("split_policy")
        if isinstance(split_policy, dict):
            required_split_policy_fields = {
                "default": str,
                "requires_owner_approval": bool,
                "required_controls": list,
                "qualifying_boundaries": list,
                "non_qualifying_reasons": list,
            }
            for field, expected_type in required_split_policy_fields.items():
                if field not in split_policy:
                    self.error(
                        "split_policy_file split_policy missing required field: "
                        f"{field}"
                    )
                    all_valid = False
                elif type(split_policy[field]) is not expected_type:
                    self.error(
                        "split_policy_file split_policy field "
                        f"'{field}' should be {expected_type.__name__}"
                    )
                    all_valid = False
            for field in (
                "required_controls",
                "qualifying_boundaries",
                "non_qualifying_reasons",
            ):
                values = split_policy.get(field)
                if isinstance(values, list) and not all(
                    isinstance(value, str) and value for value in values
                ):
                    self.error(
                        "split_policy_file split_policy "
                        f"{field} must contain non-empty strings"
                    )
                    all_valid = False

            required_values = {
                "required_controls": {
                    "migration_plan",
                    "ci",
                    "deployment_ownership",
                    "versioned_interfaces",
                    "rollback",
                    "registry_update",
                },
                "qualifying_boundaries": {
                    "independent_deployment",
                    "distinct_security_or_secrets_boundary",
                    "independent_scaling_profile",
                    "independent_release_cycle",
                    "external_team_or_product_ownership",
                },
                "non_qualifying_reasons": {
                    "category_name_only",
                    "future_idea_only",
                    "temporary_experiment",
                    "visual_neatness",
                },
            }
            if split_policy.get("default") != "keep_as_module":
                self.error("split_policy_file default must be keep_as_module")
                all_valid = False
            if split_policy.get("requires_owner_approval") is not True:
                self.error("split_policy_file must require owner approval")
                all_valid = False
            for field, required in required_values.items():
                values = split_policy.get(field)
                if isinstance(values, list):
                    missing = sorted(required.difference(values))
                    if missing:
                        self.error(
                            f"split_policy_file {field} missing required values: "
                            + ", ".join(missing)
                        )
                        all_valid = False

        if all_valid:
            self.success(f"repository split policy valid: {policy_reference}")
        return all_valid

    def check_duplicates(self) -> bool:
        """Check for duplicate repositories"""
        repos = []
        for collection in ("repositories", "worlds", "excluded_repositories"):
            repos.extend(
                repo
                for repo in self.config.get(collection, [])
                if isinstance(repo, dict)
            )
        names = [
            repo.get("name")
            for repo in repos
            if isinstance(repo.get("name"), str) and repo.get("name")
        ]
        full_names = [
            repo.get("full_name")
            for repo in repos
            if isinstance(repo.get("full_name"), str) and repo.get("full_name")
        ]

        duplicates = []
        seen_names = set()
        seen_full_names = set()

        for name in names:
            normalized_name = name.casefold() if isinstance(name, str) else name
            if normalized_name in seen_names:
                duplicates.append(f"Duplicate name: {name}")
            seen_names.add(normalized_name)

        for full_name in full_names:
            normalized_full_name = repository_key(full_name)
            if normalized_full_name in seen_full_names:
                duplicates.append(f"Duplicate full_name: {full_name}")
            seen_full_names.add(normalized_full_name)

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

        all_passed = True

        def run_validation(name, validator):
            nonlocal all_passed
            self.log(f"\n{Colors.BOLD}{name}:{Colors.RESET}")
            try:
                if not validator():
                    all_passed = False
                    return False
            except Exception as e:
                self.error(f"Validation failed: {e}")
                all_passed = False
                return False
            return True

        file_exists = run_validation("File Existence", self.validate_file_exists)
        json_valid = False
        if file_exists:
            json_valid = run_validation("JSON Format", self.validate_json_format)

        if json_valid:
            validations = [
                ("Required Fields", self.validate_required_fields),
                ("GitHub Owner", self.validate_github_owner),
                ("Repositories", self.validate_repositories),
                ("Sync Settings", self.validate_sync_settings),
                ("Discovery Settings", self.validate_discovery_settings),
                ("Integration Settings", self.validate_integration_settings),
                ("Repository Catalogs", self.validate_catalog_collections),
                ("Repository Creation Policy", self.validate_repository_creation_policy),
                ("Duplicate Check", self.check_duplicates),
            ]
            for name, validator in validations:
                run_validation(name, validator)

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
