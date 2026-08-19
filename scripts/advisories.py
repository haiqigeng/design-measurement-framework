"""Non-blocking human-review advisories for measurement frameworks."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from typing import Any

from diagnostics import (
    _eligible_direct_source,
    _records,
    consideration_reciprocity_issues,
    discovery_evidence_coverage,
    evidence_eligibility_issues,
    exception_scope_issues,
    kpi_coherence_diagnostics,
    relational_applicability_issues,
    schema_at_least,
)


def _normalized_text(value: Any) -> str:
    return " ".join(str(value or "").lower().split())


def _duplicate_fingerprint(kpi: dict[str, Any]) -> str:
    formula = kpi.get("formula", {})
    if not isinstance(formula, dict):
        formula = {}
    components = formula.get("components", [])
    records = (
        [component for component in components if isinstance(component, dict)]
        if isinstance(components, list)
        else []
    )
    signatures = []
    for component in records:
        signature = {
            "role": component.get("role"),
            "requirement_ids": sorted(component.get("requirement_ids", [])),
            "counting_unit": _normalized_text(component.get("counting_unit")),
            "grain": _normalized_text(component.get("grain")),
        }
        signatures.append((component, signature))
    signatures.sort(
        key=lambda item: (
            json.dumps(item[1], sort_keys=True),
            str(item[0].get("symbol", "")),
        )
    )
    expression = _normalized_text(formula.get("expression"))
    for index, (component, _) in enumerate(signatures):
        symbol = component.get("symbol")
        if isinstance(symbol, str) and symbol:
            expression = re.sub(
                rf"\b{re.escape(symbol.lower())}\b", f"component_{index}", expression
            )
    signature = {
        "role": kpi.get("role"),
        "expression": expression,
        "calculation_type": formula.get("calculation_type"),
        "result_unit": _normalized_text(formula.get("result_unit")),
        "counting_unit": _normalized_text(formula.get("counting_unit")),
        "grain": _normalized_text(formula.get("grain")),
        "population": _normalized_text(formula.get("population")),
        "reporting_window": _normalized_text(formula.get("reporting_window")),
        "inclusions": sorted(
            _normalized_text(value) for value in formula.get("inclusions", [])
        ),
        "exclusions": sorted(
            _normalized_text(value) for value in formula.get("exclusions", [])
        ),
        "components": [value for _, value in signatures],
        "objective_ids": sorted(kpi.get("objective_ids", [])),
        "journey_ids": sorted(kpi.get("journey_ids", [])),
        "dimension_ids": sorted(
            kpi.get("segmentation", {}).get("dimension_ids", [])
            if isinstance(kpi.get("segmentation"), dict)
            else []
        ),
        "applicability": kpi.get("applicability", {}),
    }
    return json.dumps(signature, sort_keys=True, separators=(",", ":"))


def _duplicate_kpi_advisories(data: dict[str, Any]) -> list[str]:
    fingerprints: dict[str, list[str]] = defaultdict(list)
    for kpi in _records(data, "kpis"):
        kpi_id = kpi.get("kpi_id")
        if isinstance(kpi_id, str) and kpi_id:
            fingerprints[_duplicate_fingerprint(kpi)].append(kpi_id)
    return [
        "Possible duplicate KPIs "
        + ", ".join(repr(kpi_id) for kpi_id in sorted(kpi_ids))
        + " share the same calculation, population, scope, dimensions, and "
        "measurement requirements; retain both only when their distinct "
        "decision use is evidenced."
        for kpi_ids in fingerprints.values()
        if len(kpi_ids) > 1
    ]


def _core_selection_advisories(data: dict[str, Any]) -> list[str]:
    kpis = _records(data, "kpis")
    if not kpis or not all(kpi.get("recommended_core") is True for kpi in kpis):
        return []
    tiers = {str(kpi.get("tier")) for kpi in kpis}
    if "diagnostic" not in tiers:
        return []
    return [
        "Every accepted KPI, including at least one diagnostic KPI, is recommended "
        "core; recheck decision criticality, actionability, balance, feasibility, "
        "and each KPI's distinct contribution. No fixed core count is implied."
    ]


def _uniformity_advisories(data: dict[str, Any]) -> list[str]:
    advisories: list[str] = []
    objectives = [
        item
        for item in _records(data, "objectives")
        if item.get("status") in {"confirmed", "hypothesis"}
    ]
    by_stream: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for objective in objectives:
        by_stream[str(objective.get("value_stream", ""))].append(objective)
    for stream, records in by_stream.items():
        if len(records) > 1 and all(
            record.get("priority") == "primary" for record in records
        ):
            advisories.append(
                f"All active objectives in value stream {stream!r} are primary; "
                "recheck whether priority meaningfully distinguishes decisions."
            )

    owners = {
        _normalized_text(item.get("owner_role"))
        for item in objectives
        if _normalized_text(item.get("owner_role"))
    }
    streams = {
        _normalized_text(item.get("value_stream"))
        for item in objectives
        if _normalized_text(item.get("value_stream"))
    }
    if len(objectives) > 1 and len(streams) > 1 and len(owners) == 1:
        advisories.append(
            "One owner role is assigned across materially different objective value "
            "streams; verify that governance ownership is intentional."
        )

    kpis = _records(data, "kpis")
    formula_pairs = {
        (
            _normalized_text(kpi.get("formula", {}).get("grain")),
            _normalized_text(kpi.get("formula", {}).get("reporting_window")),
        )
        for kpi in kpis
        if isinstance(kpi.get("formula"), dict)
    }
    calculation_types = {
        str(kpi.get("formula", {}).get("calculation_type"))
        for kpi in kpis
        if isinstance(kpi.get("formula"), dict)
    }
    roles = {str(kpi.get("role")) for kpi in kpis}
    if (
        len(kpis) > 1
        and len(formula_pairs) == 1
        and (len(calculation_types) > 1 or len(roles) > 2)
    ):
        advisories.append(
            "Heterogeneous KPIs share identical grain and reporting-window text; "
            "verify that the common definition is substantive rather than templated."
        )
    return advisories


def _anti_circular_advisories(data: dict[str, Any]) -> list[str]:
    document = data.get("document", {})
    if not isinstance(document, dict) or not (
        document.get("target_state") == "as_is"
        and document.get("scope_claim") == "whole_site"
    ):
        return []
    material_journeys = [
        item for item in _records(data, "journeys") if item.get("material") is True
    ]
    if not material_journeys:
        return []
    sources = {str(item.get("source_id")): item for item in _records(data, "sources")}
    refs = [
        reference
        for candidate in _records(data, "discovery_candidates")
        if candidate.get("material") is True
        for reference in candidate.get("evidence_refs", [])
        if isinstance(reference, str)
    ]
    has_rendered_discovery = any(
        _eligible_direct_source(reference, sources) is not None for reference in refs
    )
    journey_refs = [
        reference
        for journey in material_journeys
        for record in [
            journey,
            *[item for item in journey.get("steps", []) if isinstance(item, dict)],
            *[item for item in journey.get("variants", []) if isinstance(item, dict)],
        ]
        for reference in record.get("evidence_refs", [])
        if isinstance(reference, str)
    ]
    has_rendered_journey = any(
        _eligible_direct_source(reference, sources) is not None
        for reference in journey_refs
    )
    if has_rendered_discovery or has_rendered_journey:
        return []
    return [
        "The as-is whole-site candidate universe closes without rendered discovery "
        "evidence for a material family; confirm that access constraints or other "
        "evidence justify the residual coverage boundary."
    ]


def _discovery_evidence_advisories(data: dict[str, Any]) -> list[str]:
    coverage = discovery_evidence_coverage(data)
    advisories: list[str] = []

    missing_targets = coverage["included_targets_without_representative_sources"]
    if missing_targets:
        advisories.append(
            "Included production targets lack representative evidence sources: "
            + ", ".join(repr(value) for value in missing_targets)
            + ". Bind a relevant source or retain an explicit scope boundary."
        )

    unused_sources = coverage["discovery_source_ids_without_candidate_support"]
    if unused_sources:
        advisories.append(
            "Discovery-capable sources are not cited by any discovery candidate: "
            + ", ".join(repr(value) for value in unused_sources)
            + ". Confirm that they produced no material candidate or connect the "
            "candidate ledger to their findings."
        )

    intake_only = coverage["material_candidate_ids_supported_only_by_intake"]
    if intake_only:
        advisories.append(
            "Resolved material candidates rely only on intake-source evidence: "
            + ", ".join(repr(value) for value in intake_only)
            + ". Confirm that the intake contains specific support or seek an "
            "independent behavioral, technical, lifecycle, or design source."
        )

    blocked = coverage["externally_blocked_journey_ids_without_alternative_source"]
    if blocked:
        advisories.append(
            "Externally blocked journeys have no linked alternative discovery "
            "source: "
            + ", ".join(repr(value) for value in blocked)
            + ". Check available technical, lifecycle, business, design, historical, "
            "or credible user evidence before treating the boundary as the end of "
            "discovery."
        )

    cross_environment = coverage["journeys_needing_cross_environment_basis"]
    if cross_environment:
        advisories.append(
            "Test-environment evidence supports production-scoped journeys without "
            "a representative-source mapping, explicit assumption, or scoped "
            "exception: "
            + ", ".join(
                repr(item["journey_id"]) for item in cross_environment
            )
            + ". Verify environment equivalence or bound the claim."
        )

    locale_reviews = coverage["journeys_needing_locale_basis"]
    if locale_reviews:
        advisories.append(
            "Multi-locale journey scope has fewer attributable direct sources or "
            "evidenced variants than declared locales, without an explicit basis: "
            + ", ".join(repr(item["journey_id"]) for item in locale_reviews)
            + ". Inspect each material locale difference or record the justified "
            "equivalence and residual limitation."
        )
    return advisories


def _kpi_coherence_advisories(data: dict[str, Any]) -> list[str]:
    diagnostics = kpi_coherence_diagnostics(data)
    advisories: list[str] = []
    unit_mismatches = diagnostics["rate_counting_unit_mismatch_ids"]
    if unit_mismatches:
        advisories.append(
            "Rate or ratio KPIs use different numerator and denominator counting "
            "units: "
            + ", ".join(repr(value) for value in unit_mismatches)
            + ". Align the counted entity or explain a mathematically valid unit "
            "conversion."
        )
    grain_mismatches = diagnostics["rate_grain_mismatch_ids"]
    if grain_mismatches:
        advisories.append(
            "Rate or ratio KPIs appear to mix numerator and denominator entity "
            "grains: "
            + ", ".join(repr(value) for value in grain_mismatches)
            + ". Confirm a shared entity key, deduplication rule, and eligible "
            "population."
        )
    cross_journey = diagnostics["cross_journey_aggregate_review_ids"]
    if cross_journey:
        advisories.append(
            "Cross-journey KPIs combine disjoint value domains or counting units "
            "without a differentiating dimension: "
            + ", ".join(repr(value) for value in cross_journey)
            + ". Establish one coherent shared unit, add the interpretation dimension, "
            "or split the KPI."
        )
    missing_rationale = diagnostics["north_star_ids_missing_scope_rationale"]
    if missing_rationale:
        advisories.append(
            "Broad-scope North Star KPIs lack a scope and aggregation rationale: "
            + ", ".join(repr(value) for value in missing_rationale)
            + ". Explain comparability and mix-shift risk, or use a balanced set "
            "instead of one North Star."
        )
    reviewed_north_stars = sorted(
        set(diagnostics["north_star_scope_review_ids"]) - set(missing_rationale)
    )
    if reviewed_north_stars:
        advisories.append(
            "Broad-scope North Star KPIs require human confirmation that their "
            "aggregation remains comparable across roles, value streams, and journey "
            "types: "
            + ", ".join(repr(value) for value in reviewed_north_stars)
            + "."
        )
    return advisories


def review_advisories(data: dict[str, Any]) -> list[str]:
    """Return deterministic, non-blocking prompts for human review."""

    if not isinstance(data, dict) or not schema_at_least(data, (1, 2, 0)):
        return []
    advisories = _duplicate_kpi_advisories(data)
    advisories.extend(_core_selection_advisories(data))
    advisories.extend(_uniformity_advisories(data))
    advisories.extend(_anti_circular_advisories(data))
    advisories.extend(_discovery_evidence_advisories(data))
    advisories.extend(_kpi_coherence_advisories(data))
    if not schema_at_least(data, (1, 3, 0)):
        advisories.extend(
            "Legacy evidence advisory: " + issue
            for issue in evidence_eligibility_issues(data, require_durability=False)
        )
        advisories.extend(
            "Legacy relational advisory: " + issue
            for issue in relational_applicability_issues(data)
        )
        advisories.extend(
            "Legacy reciprocity advisory: " + issue
            for issue in consideration_reciprocity_issues(data)
        )
        advisories.extend(
            "Legacy exception advisory: " + issue
            for issue in exception_scope_issues(data)
        )
    return sorted(set(advisories))
