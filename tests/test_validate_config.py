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
        "architecture_policy_file": "config/core_modules.v1.json",
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
            "qualifying_boundaries": ["independent_deployment"],
            "non_qualifying_reasons": ["future_idea_only"],
        },
    }


class ConfigValidatorTests(unittest.TestCase):
    def validate(self, config, extra_files=None):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "kova_repos_config.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            if (
                isinstance(config, dict)
                and config.get("architecture_policy_file") == "config/core_modules.v1.json"
            ):
                default_policy_path = Path(temp_dir) / "config/core_modules.v1.json"
                default_policy_path.parent.mkdir(parents=True, exist_ok=True)
                default_policy_path.write_text(
                    json.dumps(valid_architecture_policy()), encoding="utf-8"
                )
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

    def test_missing_architecture_policy_file_is_rejected(self):
        config = valid_config()
        config["architecture_policy_file"] = "config/missing.json"

        passed, results, _ = self.validate(config)

        self.assertFalse(passed)
        self.assertIn(
            "architecture_policy_file not found: config/missing.json",
            results["errors"],
        )

    def test_malformed_architecture_policy_file_is_rejected(self):
        config = valid_config()

        passed, results, _ = self.validate(
            config,
            extra_files={"config/core_modules.v1.json": '{"schema_version": 1'},
        )

        self.assertFalse(passed)
        self.assertTrue(
            any(
                "architecture_policy_file contains invalid JSON" in error
                for error in results["errors"]
            )
        )


if __name__ == "__main__":
    unittest.main()
