"""Regression tests for the KOVA repository configuration validator."""

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_config import ConfigValidator


def valid_config():
    return {
        "github_owner": "Kathrynhiggs21",
        "repositories": [
            {
                "name": "Kova-ai-SYSTEM",
                "full_name": "Kathrynhiggs21/Kova-ai-SYSTEM",
                "description": "Canonical orchestrator",
                "type": "core",
                "enabled": True,
                "sync_priority": 1,
                "features": ["orchestration"],
            }
        ],
        "worlds": [],
        "excluded_repositories": [],
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
            "claude_api_enabled": False,
            "github_webhooks_enabled": False,
            "cross_repo_prs": False,
            "unified_changelog": False,
        },
        "architecture_mode": "modular_two_repository_system",
        "repository_creation_policy": {
            "description": "Canonical split policy",
            "split_policy_file": "config/core_modules.v1.json",
        },
    }


def valid_architecture_policy():
    return {
        "schema_version": 1,
        "architecture": "modular_two_repository_system",
        "modules": [
            {
                "id": "orchestration",
                "repository": "Kathrynhiggs21/Kova-ai-SYSTEM",
                "current_paths": ["kova-ai/app/main.py"],
                "responsibility": "runtime composition",
                "separate_repository": False,
            }
        ],
        "split_policy": {
            "default": "keep_as_module",
            "requires_owner_approval": True,
            "required_controls": [
                "migration_plan",
                "ci",
                "deployment_ownership",
                "versioned_interfaces",
                "rollback",
                "registry_update",
            ],
            "qualifying_boundaries": [
                "independent_deployment",
                "distinct_security_or_secrets_boundary",
                "independent_scaling_profile",
                "independent_release_cycle",
                "external_team_or_product_ownership",
            ],
            "non_qualifying_reasons": [
                "category_name_only",
                "future_idea_only",
                "temporary_experiment",
                "visual_neatness",
            ],
        },
    }


class ConfigValidatorTests(unittest.TestCase):
    def validate(self, config, extra_files=None):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "kova_repos_config.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            policy_pointer = (
                config.get("repository_creation_policy", {})
                if isinstance(config, dict)
                else {}
            )
            if policy_pointer.get("split_policy_file") == "config/core_modules.v1.json":
                default_policy_path = Path(temp_dir) / "config/core_modules.v1.json"
                default_policy_path.parent.mkdir(parents=True, exist_ok=True)
                policy = valid_architecture_policy()
                default_policy_path.write_text(
                    json.dumps(policy), encoding="utf-8"
                )
                for module in policy["modules"]:
                    if module["repository"] != "Kathrynhiggs21/Kova-ai-SYSTEM":
                        continue
                    for current_path in module.get("current_paths", []):
                        local_path = Path(temp_dir) / current_path
                        local_path.parent.mkdir(parents=True, exist_ok=True)
                        local_path.touch()
            for relative_path, content in (extra_files or {}).items():
                file_path = Path(temp_dir) / relative_path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content, encoding="utf-8")
            validator = ConfigValidator(config_path)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                passed, results = validator.validate_all()
            return passed, results, output.getvalue()

    def test_valid_config_runs_semantic_checks(self):
        passed, results, output = self.validate(valid_config())

        self.assertTrue(passed)
        self.assertEqual(results["errors"], [])
        self.assertIn("Required Fields", output)
        self.assertIn("Duplicate Check", output)

    def test_empty_object_fails_required_field_checks(self):
        passed, results, output = self.validate({})

        self.assertFalse(passed)
        self.assertIn("Missing required field: github_owner", results["errors"])
        self.assertIn("Required Fields", output)

    def test_top_level_array_is_rejected(self):
        passed, results, output = self.validate([])

        self.assertFalse(passed)
        self.assertIn("Top-level JSON value must be an object", results["errors"])
        self.assertNotIn("Required Fields", output)

    def test_repository_name_must_match_full_name(self):
        config = valid_config()
        config["repositories"][0]["name"] = "different-name"

        passed, results, _ = self.validate(config)

        self.assertFalse(passed)
        self.assertTrue(
            any("does not match full_name" in error for error in results["errors"])
        )

    def test_duplicate_repositories_are_case_insensitive(self):
        config = valid_config()
        duplicate = dict(config["repositories"][0])
        duplicate["name"] = "kova-AI-system"
        duplicate["full_name"] = "kathrynhiggs21/kova-AI-system"
        config["repositories"].append(duplicate)

        passed, results, _ = self.validate(config)

        self.assertFalse(passed)
        self.assertTrue(any("Duplicate name" in error for error in results["errors"]))
        self.assertTrue(
            any("Duplicate full_name" in error for error in results["errors"])
        )

    def test_unhashable_repository_fields_report_schema_errors(self):
        config = valid_config()
        config["repositories"][0]["name"] = ["Kova-ai-SYSTEM"]
        config["repositories"][0]["full_name"] = {
            "owner": "Kathrynhiggs21",
            "repo": "Kova-ai-SYSTEM",
        }

        passed, results, output = self.validate(config)

        self.assertFalse(passed)
        self.assertTrue(any("field 'name' should be str" in e for e in results["errors"]))
        self.assertTrue(
            any("field 'full_name' should be str" in e for e in results["errors"])
        )
        self.assertNotIn("Validation failed", output)

    def test_url_fragment_repository_alias_is_rejected(self):
        config = valid_config()
        config["repositories"][0]["name"] = "Repo#shadow"
        config["repositories"][0]["full_name"] = "Kathrynhiggs21/Repo#shadow"

        passed, results, _ = self.validate(config)

        self.assertFalse(passed)
        self.assertTrue(
            any("Invalid GitHub repository coordinate" in e for e in results["errors"])
        )

    def test_parent_segment_repository_coordinate_is_rejected(self):
        config = valid_config()
        config["repositories"][0]["name"] = "user"
        config["repositories"][0]["full_name"] = "../user"

        passed, results, _ = self.validate(config)

        self.assertFalse(passed)
        self.assertTrue(
            any("Invalid GitHub repository coordinate" in e for e in results["errors"])
        )

    def test_boolean_sync_interval_is_rejected(self):
        config = valid_config()
        config["sync_settings"]["sync_interval_minutes"] = True

        passed, results, _ = self.validate(config)

        self.assertFalse(passed)
        self.assertIn(
            "sync_settings.sync_interval_minutes should be int", results["errors"]
        )

    def test_missing_nested_setting_is_rejected(self):
        config = valid_config()
        del config["integration_settings"]["unified_changelog"]

        passed, results, _ = self.validate(config)

        self.assertFalse(passed)
        self.assertIn(
            "Missing required integration setting: unified_changelog",
            results["errors"],
        )

    def test_nonpositive_sync_interval_is_rejected(self):
        config = valid_config()
        config["sync_settings"]["sync_interval_minutes"] = 0

        passed, results, _ = self.validate(config)

        self.assertFalse(passed)
        self.assertIn(
            "sync_settings.sync_interval_minutes must be positive", results["errors"]
        )

    def test_blank_discovery_pattern_is_rejected(self):
        config = valid_config()
        config["discovery_settings"]["repo_name_pattern"] = "  "

        passed, results, _ = self.validate(config)

        self.assertFalse(passed)
        self.assertIn(
            "discovery_settings.repo_name_pattern cannot be empty", results["errors"]
        )

    def test_missing_split_policy_file_is_rejected(self):
        config = valid_config()
        config["repository_creation_policy"]["split_policy_file"] = (
            "config/missing.json"
        )

        passed, results, _ = self.validate(config)

        self.assertFalse(passed)
        self.assertIn(
            "split_policy_file not found: config/missing.json",
            results["errors"],
        )

    def test_malformed_split_policy_file_is_rejected(self):
        config = valid_config()

        passed, results, _ = self.validate(
            config,
            extra_files={"config/core_modules.v1.json": '{"schema_version": 1'},
        )

        self.assertFalse(passed)
        self.assertTrue(
            any(
                "split_policy_file contains invalid JSON" in error
                for error in results["errors"]
            )
        )

    def test_split_policy_file_cannot_escape_repository_root(self):
        config = valid_config()
        config["repository_creation_policy"]["split_policy_file"] = "../outside.json"

        passed, results, _ = self.validate(config)

        self.assertFalse(passed)
        self.assertIn(
            "split_policy_file must stay within the repository root",
            results["errors"],
        )

    def test_split_policy_file_requires_all_controls(self):
        policy = valid_architecture_policy()
        policy["split_policy"]["required_controls"].remove("rollback")

        passed, results, _ = self.validate(
            valid_config(),
            extra_files={"config/core_modules.v1.json": json.dumps(policy)},
        )

        self.assertFalse(passed)
        self.assertTrue(
            any("required_controls missing required values: rollback" in e for e in results["errors"])
        )

    def test_split_policy_symlink_outside_repo_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config = valid_config()
            config_path = temp_path / "kova_repos_config.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")

            outside_policy_path = temp_path.parent / f"{temp_path.name}-outside.json"
            try:
                outside_policy_path.write_text(
                    json.dumps(valid_architecture_policy()), encoding="utf-8"
                )
                policy_path = temp_path / "config" / "core_modules.v1.json"
                policy_path.parent.mkdir(parents=True, exist_ok=True)
                policy_path.symlink_to(outside_policy_path)

                validator = ConfigValidator(config_path)
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    passed, results = validator.validate_all()

                self.assertFalse(passed)
                self.assertIn(
                    "split_policy_file must stay within the repository root",
                    results["errors"],
                )
            finally:
                outside_policy_path.unlink(missing_ok=True)

    def test_duplicate_active_repository_list_is_rejected(self):
        policy = valid_architecture_policy()
        policy["active_repositories"] = {"core": "duplicate"}

        passed, results, _ = self.validate(
            valid_config(),
            extra_files={"config/core_modules.v1.json": json.dumps(policy)},
        )

        self.assertFalse(passed)
        self.assertTrue(
            any("must not duplicate the active repository set" in e for e in results["errors"])
        )

    def test_policy_must_require_owner_approval(self):
        policy = valid_architecture_policy()
        policy["split_policy"]["requires_owner_approval"] = False

        passed, results, _ = self.validate(
            valid_config(),
            extra_files={"config/core_modules.v1.json": json.dumps(policy)},
        )

        self.assertFalse(passed)
        self.assertIn(
            "split_policy_file must require owner approval", results["errors"]
        )

    def test_policy_rejects_missing_core_path(self):
        policy = valid_architecture_policy()
        policy["modules"][0]["current_paths"] = ["missing/module.py"]

        passed, results, _ = self.validate(
            valid_config(),
            extra_files={"config/core_modules.v1.json": json.dumps(policy)},
        )

        self.assertFalse(passed)
        self.assertTrue(any("path not found" in e for e in results["errors"]))

    def test_world_cannot_be_enabled_in_core_registry(self):
        config = valid_config()
        config["worlds"] = [
            {
                "name": "Scribbles-Zoo-Project",
                "full_name": "Kathrynhiggs21/Scribbles-Zoo-Project",
                "type": "world",
                "enabled": True,
                "relationship": "independent-domain-repository",
                "lifecycle": "review",
            }
        ]

        passed, results, _ = self.validate(config)

        self.assertFalse(passed)
        self.assertTrue(
            any("must remain disabled in the Core registry" in e for e in results["errors"])
        )


if __name__ == "__main__":
    unittest.main()
