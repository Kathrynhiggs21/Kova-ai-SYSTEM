"""Validate shared contracts without calling a provider or runtime."""

import copy
import json
from pathlib import Path
import re
import unittest

from jsonschema import Draft202012Validator, FormatChecker, ValidationError


ROOT = Path(__file__).resolve().parents[1]


class SecondBrainSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schemas = {}
        cls.validators = {}
        for path in sorted((ROOT / "config/schemas").glob("*.schema.json")):
            schema = json.loads(path.read_text())
            Draft202012Validator.check_schema(schema)
            name = path.name.split(".v1.")[0]
            cls.schemas[name] = schema
            cls.validators[name] = Draft202012Validator(
                schema, format_checker=FormatChecker()
            )

    def capability(self, **changes):
        record = {
            "capability_id": "synthetic.read",
            "provider": "synthetic",
            "operation": "read",
            "access_mode": "READ",
            "risk_class": "LOW",
            "state": "CONFIGURED",
            "requires_confirmation": True,
            "canonical_destination": None,
            "last_verified_at": None,
            "evidence_ref": None,
        }
        record.update(changes)
        return record

    def assert_invalid(self, name, record):
        with self.assertRaises(ValidationError):
            self.validators[name].validate(record)

    def test_all_three_schema_documents_have_distinct_ids(self):
        self.assertEqual(
            set(self.schemas),
            {"capability-registration", "memory-record", "timeline-event"},
        )
        ids = [schema["$id"] for schema in self.schemas.values()]
        self.assertEqual(len(ids), len(set(ids)))

    def test_capability_states_match_canonical_readme_labels(self):
        labels = re.findall(r"^\| `([^`]+)`", (ROOT / "README.md").read_text(), re.M)
        expected = {label.upper().replace(" ", "_") for label in labels}
        self.assertEqual(
            set(self.schemas["capability-registration"]["properties"]["state"]["enum"]),
            expected,
        )

    def test_unverified_states_need_no_live_evidence(self):
        for state in ["CONFIGURED", "NEEDS_CONNECTION", "UNKNOWN"]:
            with self.subTest(state=state):
                self.validators["capability-registration"].validate(
                    self.capability(state=state)
                )

    def test_observed_states_require_timestamp_and_evidence(self):
        for state in ["CONNECTED", "RUNTIME_VERIFIED", "BROKEN"]:
            with self.subTest(state=state):
                record = self.capability(state=state)
                self.assert_invalid("capability-registration", record)
                record["last_verified_at"] = "2026-10-21T20:00:00Z"
                self.assert_invalid("capability-registration", record)
                record["evidence_ref"] = "audit:synthetic-check-1"
                self.validators["capability-registration"].validate(record)
                record["last_verified_at"] = None
                self.assert_invalid("capability-registration", record)

    def test_empty_or_invalid_evidence_is_not_verification(self):
        for state in ["CONNECTED", "RUNTIME_VERIFIED", "BROKEN"]:
            for evidence in ["", " ", "\t\n"]:
                with self.subTest(state=state, evidence=evidence):
                    self.assert_invalid(
                        "capability-registration",
                        self.capability(
                            state=state,
                            last_verified_at="2026-10-21T20:00:00Z",
                            evidence_ref=evidence,
                        ),
                    )
            for timestamp in ["yesterday", "2026-10-21", "2026-99-99T20:00:00Z"]:
                with self.subTest(state=state, timestamp=timestamp):
                    self.assert_invalid(
                        "capability-registration",
                        self.capability(
                            state=state,
                            last_verified_at=timestamp,
                            evidence_ref="audit:synthetic-check-1",
                        ),
                    )

    def test_unknown_cannot_claim_current_verification(self):
        self.assert_invalid(
            "capability-registration",
            self.capability(
                state="UNKNOWN",
                last_verified_at="2026-10-21T20:00:00Z",
                evidence_ref="audit:synthetic-check-1",
            ),
        )

    def test_evidence_metadata_is_a_pair_even_for_configured_state(self):
        for changes in [
            {"last_verified_at": "2026-10-21T20:00:00Z"},
            {"evidence_ref": "audit:configuration-review-1"},
        ]:
            with self.subTest(changes=changes):
                self.assert_invalid("capability-registration", self.capability(**changes))
        self.validators["capability-registration"].validate(
            self.capability(
                last_verified_at="2026-10-21T20:00:00Z",
                evidence_ref="audit:configuration-review-1",
            )
        )

    def test_noncanonical_states_are_rejected_without_automatic_promotion(self):
        for state in ["DEGRADED", "DISABLED", "PLANNED", "LIVE", "Connected"]:
            with self.subTest(state=state):
                self.assert_invalid("capability-registration", self.capability(state=state))

    def test_existing_confirmation_and_required_field_guards_remain(self):
        self.assert_invalid(
            "capability-registration",
            self.capability(risk_class="HIGH", requires_confirmation=False),
        )
        self.validators["capability-registration"].validate(
            self.capability(risk_class="HIGH", requires_confirmation=True)
        )
        for key in self.schemas["capability-registration"]["required"]:
            record = self.capability()
            del record[key]
            with self.subTest(missing=key):
                self.assert_invalid("capability-registration", record)

    def memory(self, **changes):
        record = {
            "memory_id": "synthetic-memory-1",
            "memory_type": "FACT",
            "statement": "Synthetic fixture only.",
            "status": "ACTIVE",
            "sensitivity": "PRIVATE",
            "provenance": {"source": "synthetic", "confidence_score": 1},
        }
        record.update(changes)
        return record

    def test_memory_contract_review_guards_remain(self):
        self.validators["memory-record"].validate(self.memory())
        for field in ["sensitivity", "provenance"]:
            record = self.memory()
            del record[field]
            self.assert_invalid("memory-record", record)
        self.assert_invalid("memory-record", self.memory(memory_type="RELATIONSHIP"))
        edge = {"source_ref": "entity:a", "relationship_type": "links", "target_ref": "entity:b"}
        self.validators["memory-record"].validate(
            self.memory(memory_type="RELATIONSHIP", relationship=edge)
        )
        for field in edge:
            broken_edge = copy.deepcopy(edge)
            del broken_edge[field]
            self.assert_invalid(
                "memory-record", self.memory(memory_type="RELATIONSHIP", relationship=broken_edge)
            )
        self.assert_invalid("memory-record", self.memory(status="SUPERSEDED"))
        self.validators["memory-record"].validate(
            self.memory(status="SUPERSEDED", superseded_by_memory_id="synthetic-memory-2")
        )
        self.assert_invalid("memory-record", self.memory(memory_type="TIMELINE"))
        self.validators["memory-record"].validate(
            self.memory(memory_type="TIMELINE", valid_from="2026-10-21T20:00:00Z")
        )

    def test_correction_event_contract_review_guard_remains(self):
        event = {
            "timestamp": "2026-10-21T20:00:00Z",
            "event_id": "synthetic-event-2",
            "event_type": "CORRECTION",
            "description": "Synthetic correction.",
            "provenance": {"source": "synthetic", "confidence_score": 1},
        }
        self.assert_invalid("timeline-event", event)
        event["supersedes_event_id"] = "synthetic-event-1"
        self.validators["timeline-event"].validate(event)
        event["timestamp"] = "not-a-date"
        self.assert_invalid("timeline-event", event)

    def test_adr_identifiers_are_unique_and_match_file_headings(self):
        identifiers = []
        for path in (ROOT / "docs/architecture").glob("ADR-*.md"):
            identifier = re.match(r"ADR-\d+", path.name).group()
            identifiers.append(identifier)
            self.assertTrue(path.read_text().startswith(f"# {identifier}:"), path.name)
        self.assertEqual(len(identifiers), len(set(identifiers)))


if __name__ == "__main__":
    unittest.main()
