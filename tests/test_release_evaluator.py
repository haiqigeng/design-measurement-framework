from __future__ import annotations

import copy
import sys
import unittest

from helpers import ROOT, load_framework, upgrade_to_v1_3

sys.path.insert(0, str(ROOT / "scripts"))

from evaluate_release import evaluate_framework  # noqa: E402


class MeasurementFrameworkReleaseEvaluatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.framework = load_framework()
        upgrade_to_v1_3(self.framework)
        self.benchmark = {
            "benchmark_id": "synthetic_quote",
            "expectations": [
                {
                    "concept_id": "candidate_quote",
                    "layer": "discovery_candidates",
                    "match_any": ["quote request form"],
                    "material": True,
                },
                {
                    "concept_id": "journey_quote",
                    "layer": "journeys",
                    "match_any": ["request a quote"],
                    "material": True,
                },
                {
                    "concept_id": "objective_demand",
                    "layer": "objectives",
                    "match_any": ["qualified demand"],
                },
                {
                    "concept_id": "kpi_completion",
                    "layer": "kpis",
                    "match_any": ["quote completion"],
                    "allowed_roles": ["outcome"],
                },
            ],
            "thresholds": {
                "min_candidate_recall": 1.0,
                "min_journey_recall": 1.0,
                "min_objective_recall": 1.0,
                "min_kpi_recall": 1.0,
                "min_evidence_traceability_rate": 1.0,
                "min_formula_specificity_rate": 1.0,
                "min_requirement_specificity_rate": 1.0,
                "max_observed_claim_issue_rate": 0.0,
                "max_intake_only_material_candidate_rate": 0.0,
            },
        }

    def test_complete_artifact_passes_fixed_expectations(self) -> None:
        report = evaluate_framework(self.framework, self.benchmark)
        self.assertTrue(report["passed"], report)
        self.assertEqual(report["missing_concepts"], [])
        self.assertEqual(report["metrics"]["candidate_recall"], 1.0)

    def test_candidate_loss_fails_even_when_schema_remains_valid(self) -> None:
        regressed = copy.deepcopy(self.framework)
        regressed["discovery_candidates"][0]["label"] = "Generic interaction"
        regressed["discovery_candidates"][0]["reason"] = "Generic interaction"
        report = evaluate_framework(regressed, self.benchmark)
        self.assertFalse(report["passed"])
        self.assertIn("candidate_quote", report["missing_concepts"])
        self.assertTrue(report["structurally_valid"])


if __name__ == "__main__":
    unittest.main()
