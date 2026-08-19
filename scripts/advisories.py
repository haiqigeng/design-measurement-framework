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
    evidence_eligibility_issues,
    exception_scope_issues,
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


def review_advisories(data: dict[str, Any]) -> list[str]:
    """Return deterministic, non-blocking prompts for human review."""

    if not isinstance(data, dict) or not schema_at_least(data, (1, 2, 0)):
        return []
    advisories = _duplicate_kpi_advisories(data)
    advisories.extend(_core_selection_advisories(data))
    advisories.extend(_uniformity_advisories(data))
    advisories.extend(_anti_circular_advisories(data))
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
