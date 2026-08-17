from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from render_framework import render_framework  # noqa: E402
from init_framework import build_draft  # noqa: E402
from validate_framework import validate_framework  # noqa: E402


FIXTURE = ROOT / "tests" / "fixtures" / "valid-minimal.json"


class MeasurementFrameworkValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.framework = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_valid_minimal_framework_passes(self) -> None:
        self.assertEqual(validate_framework(self.framework, delivery=True), [])

    def test_initializer_creates_explicit_incomplete_working_state(self) -> None:
        draft = build_draft(
            title="Draft",
            scope="Whole site",
            language="en",
            target_state="as_is",
            scope_claim="whole_site",
            target_sites=["https://example.com/"],
            markets=[],
            audiences=[],
            source_reference="Test brief",
        )
        self.assertRegex(draft["document"]["run_id"], r"^run_[a-f0-9]{32}$")
        self.assertEqual(draft["journeys"], [])
        self.assertTrue(all(gate["status"] == "fail" for gate in draft["quality_gates"].values()))

    def test_unresolved_candidate_requires_exception(self) -> None:
        changed = copy.deepcopy(self.framework)
        candidate = changed["discovery_candidates"][0]
        candidate["resolution"] = "unresolved"
        candidate["journey_ids"] = []
        errors = validate_framework(changed)
        self.assertTrue(any("unresolved candidate requires a linked exception" in error for error in errors))

    def test_bounded_exception_must_be_visible_in_stage_and_overall_gates(self) -> None:
        changed = copy.deepcopy(self.framework)
        candidate = changed["discovery_candidates"][0]
        candidate["resolution"] = "unresolved"
        candidate["journey_ids"] = []
        changed["exceptions"] = [
            {
                "exception_id": "exception_quote_access",
                "stage": "journey",
                "description": "The quote route is awaiting safe test access.",
                "affected_ids": ["candidate_quote_form"],
                "impact": "Journey coverage remains provisional.",
                "disposition": "awaiting_evidence",
                "evidence_refs": ["source_site#quote-form"]
            }
        ]
        changed["quality_gates"]["overall"]["status"] = "pass_with_exceptions"
        changed["quality_gates"]["overall"]["exception_ids"] = ["exception_quote_access"]
        errors = validate_framework(changed)
        self.assertTrue(any("must be cited by its stage gate" in error for error in errors))

        changed["quality_gates"]["journey_completeness"]["status"] = "pass_with_exceptions"
        changed["quality_gates"]["journey_completeness"]["exception_ids"] = ["exception_quote_access"]
        self.assertEqual(validate_framework(changed), [])

    def test_active_objective_requires_every_kpi_role_consideration(self) -> None:
        changed = copy.deepcopy(self.framework)
        changed["kpi_considerations"] = [
            item
            for item in changed["kpi_considerations"]
            if item["consideration_id"] != "kpicon_objective_guardrail"
        ]
        errors = validate_framework(changed)
        self.assertTrue(any("lacks required 'guardrail' consideration" in error for error in errors))

    def test_current_tracking_requires_alignment_for_every_requirement(self) -> None:
        changed = copy.deepcopy(self.framework)
        changed["sources"].append(
            {
                "source_id": "source_tracking",
                "source_type": "current_tracking",
                "reference": "Current event inventory",
                "evidence_role": "current_implementation",
                "state": "as_is",
                "supports": ["Existing analytics event names"]
            }
        )
        errors = validate_framework(changed)
        self.assertTrue(any("requirements lack alignment" in error for error in errors))

    def test_requirement_and_formula_links_are_bidirectional(self) -> None:
        changed = copy.deepcopy(self.framework)
        changed["measurement_requirements"][0]["kpi_ids"] = ["kpi_quote_completion_rate"]
        errors = validate_framework(changed)
        self.assertTrue(any("bidirectional KPI links" in error for error in errors))

    def test_prohibited_dimension_is_rejected(self) -> None:
        changed = copy.deepcopy(self.framework)
        changed["dimensions"][0]["sensitivity_review"] = "prohibited"
        errors = validate_framework(changed)
        self.assertTrue(any("prohibited dimension cannot be recommended" in error for error in errors))

    def test_renderer_includes_core_contract_sections(self) -> None:
        markdown = render_framework(self.framework)
        self.assertIn("## Quality status", markdown)
        self.assertIn("## Journey inventory", markdown)
        self.assertIn("## KPI definitions", markdown)
        self.assertIn("## Measurement requirements", markdown)
        self.assertIn("This framework defines what must be measurable and why", markdown)


if __name__ == "__main__":
    unittest.main()
