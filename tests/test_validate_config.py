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
    }


class ConfigValidatorTests(unittest.TestCase):
    def validate(self, config):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "kova_repos_config.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")
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


if __name__ == "__main__":
    unittest.main()
