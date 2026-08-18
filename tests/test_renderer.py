from __future__ import annotations

import sys
import unittest

from helpers import (
    ROOT,
    add_duplicate_kpi,
    add_exception,
    add_second_north_star,
    load_framework,
)

sys.path.insert(0, str(ROOT / "scripts"))

from render_framework import render_framework  # noqa: E402


class MeasurementFrameworkRendererTests(unittest.TestCase):
    def setUp(self) -> None:
        self.framework = load_framework()

    def test_render_is_deterministic(self) -> None:
        first = render_framework(self.framework)
        second = render_framework(self.framework)
        self.assertEqual(first, second)

    def test_decision_first_sections_are_present_and_ordered(self) -> None:
        rendered = render_framework(self.framework)
        headings = [
            "## Quality status",
            "## Measurement strategy summary",
            "## North Star and recommended core",
            "## Objective and journey coverage",
            "## Top missing or partial measurement needs",
            "## Evidence requests",
            "## Quality gate detail",
            "## KPI system",
            "## Measurement requirements",
            "## Coverage evidence",
            "## Measurement boundary",
        ]
        positions = [rendered.index(heading) for heading in headings]
        self.assertEqual(positions, sorted(positions))

    def test_compact_status_leads_and_detailed_gates_remain_visible(self) -> None:
        rendered = render_framework(self.framework)
        summary_end = rendered.index("## Measurement strategy summary")
        summary = rendered[:summary_end]
        self.assertIn("- Overall gate: **pass**", summary)
        self.assertNotIn("| Gate | Status | Rationale | Exceptions |", summary)

        detail_start = rendered.index("## Quality gate detail")
        detail_end = rendered.index("## KPI system")
        detail = rendered[detail_start:detail_end]
        for gate_name in self.framework["quality_gates"]:
            self.assertIn(f"| {gate_name} |", detail)

    def test_material_variant_coverage_is_visible(self) -> None:
        rendered = render_framework(self.framework)
        self.assertIn("### Journey variants and states", rendered)
        self.assertIn("Standard public quote form", rendered)
        self.assertIn("entry, progression, success, failure", rendered)
        self.assertIn("### Journey steps and evidence states", rendered)
        self.assertIn("Open quote form", rendered)

    def test_objective_and_journey_evidence_is_human_visible(self) -> None:
        rendered = render_framework(self.framework)
        self.assertIn("### Objective evidence and rationale", rendered)
        self.assertIn(
            "| Objective | Confidence | Owner | Rationale | Evidence |", rendered
        )
        self.assertIn("Sales and marketing", rendered)
        self.assertIn("source_business#qualified-demand", rendered)
        self.assertIn("Entry point(s)", rendered)
        self.assertIn("/quote", rendered)
        self.assertIn("source_business#accepted-request", rendered)

    def test_coverage_summaries_expose_type_and_lens_resolutions(self) -> None:
        rendered = render_framework(self.framework)
        self.assertIn("### Discovery candidate summary", rendered)
        self.assertIn(
            "| Type | Total | Material | mapped | merged | excluded | unresolved |",
            rendered,
        )
        self.assertIn("| form | 1 | 1 | 1 | 0 | 0 | 0 |", rendered)
        self.assertIn("## Objective consideration summary", rendered)
        self.assertIn(
            "Counts expose the recorded sweep depth for human review; they are not quality thresholds.",
            rendered,
        )
        self.assertIn("| risk_guardrail | 1 | 0 | 1 | 0 | 0 | 0 |", rendered)

    def test_open_exception_becomes_an_evidence_request(self) -> None:
        add_exception(
            self.framework,
            exception_id="exception_variant_access",
            stage="journey",
            affected_ids=["variant_quote_standard"],
        )
        rendered = render_framework(self.framework)
        self.assertIn("- Overall gate: **pass_with_exceptions**", rendered)
        self.assertIn("- Exceptions: `exception_variant_access`", rendered)
        self.assertIn("## Evidence requests", rendered)
        self.assertIn("Exception `exception_variant_access`", rendered)
        self.assertIn("Additional evidence is required", rendered)

    def test_complete_kpi_and_requirement_contract_is_human_visible(self) -> None:
        rendered = render_framework(self.framework)
        self.assertIn("- Directionality:", rendered)
        self.assertIn("- Formula components:", rendered)
        self.assertIn("Distinct quote journeys accepted", rendered)
        self.assertIn("- Evidence status and references:", rendered)
        self.assertIn("Timing or state", rendered)
        self.assertIn("Entity and grain", rendered)
        self.assertIn("Dimension(s)", rendered)

    def test_structured_formula_contract_is_human_visible(self) -> None:
        rendered = render_framework(self.framework)
        self.assertIn("- Calculation contract: rate; result unit: proportion", rendered)
        self.assertIn("symbol: accepted_quote_requests", rendered)
        self.assertIn("unit: quote journey", rendered)
        self.assertIn("grain: one record per quote journey identifier", rendered)

    def test_duplicate_kpi_advisory_is_human_visible(self) -> None:
        duplicate = add_duplicate_kpi(self.framework)
        rendered = render_framework(self.framework)
        self.assertIn("## Review advisories", rendered)
        self.assertIn("Possible duplicate KPIs", rendered)
        self.assertIn(duplicate["kpi_id"], rendered)

    def test_multiple_north_star_rationales_are_human_visible(self) -> None:
        add_second_north_star(self.framework)
        rendered = render_framework(self.framework)
        self.assertIn("North Star rationale", rendered)
        self.assertIn(
            "Represents accepted quote value for the French journey scope.", rendered
        )
        self.assertIn(
            "Represents accepted quote value for the Belgian journey scope.", rendered
        )

    def test_output_keeps_a_platform_neutral_boundary(self) -> None:
        rendered = render_framework(self.framework).lower()
        self.assertNotIn("tracking plan", rendered)
        self.assertNotIn("ga4", rendered)
        self.assertNotIn("datalayer", rendered)
        self.assertIn("platform-specific event and parameter semantics", rendered)


if __name__ == "__main__":
    unittest.main()
