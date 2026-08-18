from __future__ import annotations

import copy
import sys
import unittest

from helpers import (
    ROOT,
    add_alignment_source,
    add_duplicate_kpi,
    add_exception,
    add_second_north_star,
    add_secondary_objective_without_core,
    downgrade_formula_contract,
    load_framework,
)

sys.path.insert(0, str(ROOT / "scripts"))

from formula_contract import review_advisories  # noqa: E402
from validate_framework import validate_framework  # noqa: E402


class MeasurementFrameworkValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.framework = load_framework()

    def assert_has_error(self, errors: list[str], text: str) -> None:
        self.assertTrue(any(text in error for error in errors), errors)

    def test_valid_minimal_framework_passes(self) -> None:
        self.assertEqual(validate_framework(self.framework, delivery=True), [])

    def test_v1_schema_version_remains_compatible(self) -> None:
        downgrade_formula_contract(self.framework, schema_version="1.0.0")
        self.assertEqual(validate_framework(self.framework, delivery=True), [])

    def test_v1_1_schema_version_remains_compatible(self) -> None:
        downgrade_formula_contract(self.framework, schema_version="1.1.0")
        self.assertEqual(validate_framework(self.framework, delivery=True), [])

    def test_material_journey_requires_entry_and_success_closure(self) -> None:
        journey = self.framework["journeys"][0]
        journey["steps"] = [
            step for step in journey["steps"] if step["state"] != "success"
        ]
        errors = validate_framework(self.framework)
        self.assert_has_error(errors, "a success-state step")

    def test_material_journey_requires_a_declared_entry_point(self) -> None:
        self.framework["journeys"][0]["entry_points"] = []
        errors = validate_framework(self.framework)
        self.assert_has_error(errors, "a declared entry point")

    def test_material_journey_closure_can_be_bounded_by_exception(self) -> None:
        journey = self.framework["journeys"][0]
        journey["steps"] = [
            step for step in journey["steps"] if step["state"] != "success"
        ]
        add_exception(
            self.framework,
            exception_id="exception_backend_outcome_evidence",
            stage="journey",
            affected_ids=[journey["journey_id"]],
        )
        self.assertEqual(validate_framework(self.framework), [])

    def test_legacy_journey_shape_keeps_prior_acceptance_behavior(self) -> None:
        downgrade_formula_contract(self.framework, schema_version="1.1.0")
        journey = self.framework["journeys"][0]
        journey["steps"] = [
            step for step in journey["steps"] if step["state"] != "success"
        ]
        self.assertEqual(validate_framework(self.framework), [])

    def test_unresolved_candidate_requires_exception(self) -> None:
        candidate = self.framework["discovery_candidates"][0]
        candidate["resolution"] = "unresolved"
        candidate["journey_ids"] = []
        self.assert_has_error(
            validate_framework(self.framework),
            "unresolved candidate requires a linked exception",
        )

    def test_default_stage_exception_must_be_visible_in_stage_and_overall_gates(
        self,
    ) -> None:
        candidate = self.framework["discovery_candidates"][0]
        candidate["resolution"] = "unresolved"
        candidate["journey_ids"] = []
        add_exception(
            self.framework,
            exception_id="exception_quote_access",
            stage="journey",
            affected_ids=["candidate_quote_form"],
        )
        self.framework["quality_gates"]["journey_completeness"]["exception_ids"] = []
        self.framework["quality_gates"]["journey_completeness"]["status"] = "pass"
        errors = validate_framework(self.framework)
        self.assert_has_error(
            errors, "must be cited by affected gate 'journey_completeness'"
        )

    def test_material_variant_requires_exception_when_not_tested(self) -> None:
        self.framework["journeys"][0]["variants"][0]["status"] = "not_tested"
        errors = validate_framework(self.framework)
        self.assert_has_error(
            errors,
            "material variant with status 'not_tested' requires a linked exception",
        )

    def test_material_variant_with_bounded_exception_passes(self) -> None:
        variant = self.framework["journeys"][0]["variants"][0]
        variant["status"] = "not_tested"
        add_exception(
            self.framework,
            exception_id="exception_variant_access",
            stage="journey",
            affected_ids=[variant["variant_id"]],
        )
        self.assertEqual(validate_framework(self.framework), [])

    def test_material_variant_requires_a_covered_state(self) -> None:
        self.framework["journeys"][0]["variants"][0]["states_covered"] = []
        errors = validate_framework(self.framework)
        self.assert_has_error(
            errors, "material variant requires at least one covered state"
        )

    def test_incomplete_step_must_be_reflected_by_material_journey_status(self) -> None:
        self.framework["journeys"][0]["steps"][0]["status"] = "not_tested"
        errors = validate_framework(self.framework)
        self.assert_has_error(
            errors, "must be reflected by the parent material journey status"
        )

    def test_active_objective_requires_every_kpi_role_consideration(self) -> None:
        self.framework["kpi_considerations"] = [
            item
            for item in self.framework["kpi_considerations"]
            if item["consideration_id"] != "kpicon_objective_guardrail"
        ]
        errors = validate_framework(self.framework)
        self.assert_has_error(errors, "lacks required 'guardrail' consideration")

    def test_objective_guardrail_consideration_requires_guardrail_kpi(self) -> None:
        consideration = next(
            item
            for item in self.framework["kpi_considerations"]
            if item["consideration_id"] == "kpicon_objective_guardrail"
        )
        consideration["kpi_ids"] = ["kpi_quote_completion_rate"]
        errors = validate_framework(self.framework)
        self.assert_has_error(errors, "'guardrail' consideration references KPI")

    def test_current_tracking_requires_alignment_for_every_requirement(self) -> None:
        add_alignment_source(self.framework)
        self.framework["alignment"].pop()
        errors = validate_framework(self.framework)
        self.assert_has_error(errors, "requirements lack alignment")

    def test_analytics_export_can_support_alignment_by_evidence_role(self) -> None:
        add_alignment_source(
            self.framework,
            source_type="analytics_export",
            evidence_role="data_usage",
        )
        self.assertEqual(validate_framework(self.framework), [])

    def test_previous_framework_cannot_prove_current_alignment(self) -> None:
        add_alignment_source(
            self.framework,
            source_type="previous_framework",
            evidence_role="current_implementation",
        )
        errors = validate_framework(self.framework)
        self.assert_has_error(
            errors, "require current implementation or data-usage evidence"
        )

    def test_alignment_refs_must_use_current_measurement_evidence(self) -> None:
        add_alignment_source(self.framework)
        self.framework["alignment"][0]["current_measurement_refs"] = [
            "source_business#brief"
        ]
        errors = validate_framework(self.framework)
        self.assert_has_error(
            errors, "is not current implementation or data-usage evidence"
        )

    def test_covered_and_partial_alignment_require_current_refs(self) -> None:
        add_alignment_source(self.framework)
        row = self.framework["alignment"][0]
        row["status"] = "partial"
        row["current_measurement_refs"] = []
        errors = validate_framework(self.framework)
        self.assert_has_error(
            errors, "partial alignment requires current evidence references"
        )

    def test_requirement_and_formula_links_are_bidirectional(self) -> None:
        self.framework["measurement_requirements"][0]["kpi_ids"] = [
            "kpi_quote_completion_rate"
        ]
        errors = validate_framework(self.framework)
        self.assert_has_error(errors, "bidirectional KPI links")

    def test_each_dimension_closes_into_requirements_for_affected_kpis(self) -> None:
        for requirement in self.framework["measurement_requirements"]:
            requirement["dimension_ids"] = []
        errors = validate_framework(self.framework)
        self.assert_has_error(
            errors, "dimension is not carried by a measurement requirement"
        )

    def test_requirement_dimension_must_apply_to_a_linked_kpi(self) -> None:
        extra = copy.deepcopy(self.framework["dimensions"][0])
        extra["dimension_id"] = "dimension_sales_region"
        extra["name"] = "Sales region"
        extra["kpi_ids"] = ["kpi_qualified_quote_rate"]
        self.framework["dimensions"].append(extra)
        requirement = next(
            item
            for item in self.framework["measurement_requirements"]
            if item["requirement_id"] == "requirement_quote_validation_error"
        )
        requirement["dimension_ids"].append(extra["dimension_id"])
        errors = validate_framework(self.framework)
        self.assert_has_error(
            errors, "does not apply to any KPI linked by this requirement"
        )

    def test_prohibited_dimension_is_rejected(self) -> None:
        self.framework["dimensions"][0]["sensitivity_review"] = "prohibited"
        errors = validate_framework(self.framework)
        self.assert_has_error(errors, "prohibited dimension cannot be recommended")

    def test_kpi_tier_and_role_must_be_coherent(self) -> None:
        self.framework["kpis"][0]["tier"] = "guardrail"
        errors = validate_framework(self.framework)
        self.assert_has_error(errors, "guardrail tier requires guardrail role")

    def test_multiple_north_stars_pass_with_non_overlapping_applicability(self) -> None:
        add_second_north_star(self.framework)
        self.assertEqual(validate_framework(self.framework), [])

    def test_multiple_north_stars_reject_overlapping_applicability(self) -> None:
        duplicate = add_second_north_star(self.framework)
        duplicate["applicability"] = {"markets": ["France"]}
        errors = validate_framework(self.framework)
        self.assert_has_error(errors, "have overlapping applicability")

    def test_framework_requires_a_recommended_core_not_one_per_objective(self) -> None:
        for kpi in self.framework["kpis"]:
            kpi["recommended_core"] = False
        errors = validate_framework(self.framework)
        self.assert_has_error(errors, "framework has no recommended-core KPI")

    def test_relevant_guardrail_must_balance_core_growth_kpis(self) -> None:
        guardrail = next(
            item for item in self.framework["kpis"] if item["role"] == "guardrail"
        )
        guardrail["recommended_core"] = False
        errors = validate_framework(self.framework)
        self.assert_has_error(
            errors, "no cited guardrail KPI is in the recommended core"
        )

    def test_core_guardrail_balance_can_use_appropriateness_exception(self) -> None:
        guardrail = next(
            item for item in self.framework["kpis"] if item["role"] == "guardrail"
        )
        guardrail["recommended_core"] = False
        add_exception(
            self.framework,
            exception_id="exception_core_guardrail_scope",
            stage="kpi",
            affected_ids=["objective_qualified_demand"],
            gate_ids=["kpi_appropriateness"],
        )
        self.assertEqual(validate_framework(self.framework), [])

    def test_core_guardrail_is_not_forced_when_consideration_rejects_it(self) -> None:
        guardrail = next(
            item for item in self.framework["kpis"] if item["role"] == "guardrail"
        )
        guardrail["recommended_core"] = False
        consideration = next(
            item
            for item in self.framework["kpi_considerations"]
            if item["consideration_id"] == "kpicon_objective_guardrail"
        )
        consideration["resolution"] = "none_with_reason"
        consideration["kpi_ids"] = []
        consideration["reason"] = (
            "No distinct objective-level guardrail is justified by the evidence."
        )
        self.assertEqual(validate_framework(self.framework), [])

    def test_legacy_core_selection_keeps_prior_acceptance_behavior(self) -> None:
        downgrade_formula_contract(self.framework, schema_version="1.1.0")
        guardrail = next(
            item for item in self.framework["kpis"] if item["role"] == "guardrail"
        )
        guardrail["recommended_core"] = False
        self.assertEqual(validate_framework(self.framework), [])

    def test_secondary_objective_does_not_require_its_own_core_kpi(self) -> None:
        add_secondary_objective_without_core(self.framework)
        self.assertEqual(validate_framework(self.framework), [])

    def test_structured_formula_supports_major_calculation_families(self) -> None:
        cases = {
            "count": "distinct_count(accepted_quote_requests)",
            "sum": "sum(accepted_quote_requests)",
            "ratio": "accepted_quote_requests / started_quote_journeys",
            "rate": "rate(accepted_quote_requests, started_quote_journeys)",
            "average": "average(accepted_quote_requests)",
            "weighted_average": (
                "weighted_average(accepted_quote_requests, started_quote_journeys)"
            ),
            "percentile": "percentile(accepted_quote_requests, 0.9)",
            "cohort": "cohort_rate(accepted_quote_requests, started_quote_journeys)",
            "retention": (
                "retention_rate(accepted_quote_requests, started_quote_journeys)"
            ),
            "composite": (
                "0.5 * accepted_quote_requests + 0.5 * started_quote_journeys"
            ),
            "index": "index_value(accepted_quote_requests, started_quote_journeys)",
            "other": "accepted_quote_requests + started_quote_journeys",
        }
        one_input_types = {"count", "sum", "average", "percentile"}
        general_input_types = {
            "weighted_average",
            "composite",
            "index",
            "other",
        }
        for calculation_type, expression in cases.items():
            with self.subTest(calculation_type=calculation_type):
                framework = copy.deepcopy(self.framework)
                formula = framework["kpis"][0]["formula"]
                formula["calculation_type"] = calculation_type
                formula["expression"] = expression
                if calculation_type in one_input_types:
                    formula["components"][0]["role"] = "input"
                    formula["components"][1]["role"] = "filter"
                elif calculation_type in general_input_types:
                    for component in formula["components"]:
                        component["role"] = "input"
                self.assertEqual(validate_framework(framework), [])

    def test_structured_formula_rejects_undeclared_or_unused_components(self) -> None:
        formula = self.framework["kpis"][0]["formula"]
        formula["expression"] = "unrelated_value / another_value"
        errors = validate_framework(self.framework)
        self.assert_has_error(errors, "undeclared component symbol 'unrelated_value'")
        self.assert_has_error(
            errors, "component symbol 'accepted_quote_requests' is not used"
        )

    def test_structured_formula_requires_component_units_and_grain(self) -> None:
        component = self.framework["kpis"][0]["formula"]["components"][0]
        component.pop("counting_unit")
        component.pop("grain")
        errors = validate_framework(self.framework)
        self.assert_has_error(errors, ".counting_unit: required for schema 1.2.0")
        self.assert_has_error(errors, ".grain: required for schema 1.2.0")

    def test_structured_formula_type_must_match_specialized_function(self) -> None:
        formula = self.framework["kpis"][0]["formula"]
        formula["calculation_type"] = "percentile"
        errors = validate_framework(self.framework)
        self.assert_has_error(errors, "'percentile' requires percentile(...)")

    def test_structured_formula_function_arity_is_checked(self) -> None:
        formula = self.framework["kpis"][0]["formula"]
        formula["expression"] = "rate(accepted_quote_requests)"
        errors = validate_framework(self.framework)
        self.assert_has_error(errors, "function 'rate' requires 2 argument(s)")

    def test_duplicate_kpi_is_an_advisory_not_a_validation_error(self) -> None:
        duplicate = add_duplicate_kpi(self.framework)
        self.assertEqual(validate_framework(self.framework), [])
        advisories = review_advisories(self.framework)
        self.assertEqual(len(advisories), 1)
        self.assertIn(duplicate["kpi_id"], advisories[0])

    def test_distinct_population_is_not_flagged_as_duplicate(self) -> None:
        duplicate = add_duplicate_kpi(self.framework)
        duplicate["formula"]["population"] = "Returning quote journeys only"
        self.assertEqual(review_advisories(self.framework), [])

    def test_appropriateness_exception_can_target_appropriateness_gate(self) -> None:
        add_exception(
            self.framework,
            exception_id="exception_kpi_appropriateness",
            stage="kpi",
            affected_ids=["kpi_quote_completion_rate"],
            gate_ids=["kpi_appropriateness"],
        )
        self.assertEqual(validate_framework(self.framework), [])

    def test_in_scope_applicability_passes(self) -> None:
        self.framework["journeys"][0]["applicability"] = {
            "products": ["Quote service"],
            "markets": ["France"],
            "states": ["as_is"],
            "journey_variant_ids": ["variant_quote_standard"],
        }
        self.assertEqual(validate_framework(self.framework), [])

    def test_applicability_requires_a_declared_document_scope(self) -> None:
        self.framework["document"]["products"] = []
        self.framework["kpis"][0]["applicability"] = {"products": ["Quote service"]}
        errors = validate_framework(self.framework)
        self.assert_has_error(
            errors, "require a corresponding document.products scope declaration"
        )

    def test_out_of_scope_applicability_is_rejected(self) -> None:
        self.framework["journeys"][0]["applicability"] = {"markets": ["Belgium"]}
        errors = validate_framework(self.framework)
        self.assert_has_error(errors, "values fall outside document scope")

    def test_unknown_applicability_variant_is_rejected(self) -> None:
        self.framework["kpis"][0]["applicability"] = {
            "journey_variant_ids": ["variant_unknown"]
        }
        errors = validate_framework(self.framework)
        self.assert_has_error(errors, "unknown journey variant ID")


if __name__ == "__main__":
    unittest.main()
