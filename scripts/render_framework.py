#!/usr/bin/env python3
"""Render a validated measurement framework JSON artifact as Markdown."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from advisories import review_advisories
from diagnostics import (
    GATE_ORDER,
    discovery_evidence_coverage,
    evidence_maturity,
    gate_facts,
)
from validate_framework import DEFAULT_SCHEMA, validate_framework

TIER_ORDER = {
    "north_star": 0,
    "primary": 1,
    "guardrail": 2,
    "supporting": 3,
    "diagnostic": 4,
}


def _cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, list):
        value = ", ".join(str(item) for item in value)
    text = " ".join(str(value).split())
    return text.replace("|", "\\|")


def _table(headers: list[str], rows: Iterable[Iterable[Any]]) -> list[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend(
        "| " + " | ".join(_cell(value) for value in row) + " |" for row in rows
    )
    return lines


def _join_rules(values: Any) -> str:
    if not isinstance(values, list) or not values:
        return "None specified"
    return "; ".join(str(value) for value in values)


def _format_formula_component(component: dict[str, Any]) -> str:
    attributes = [str(component["role"])]
    for key, label in (
        ("symbol", "symbol"),
        ("counting_unit", "unit"),
        ("grain", "grain"),
    ):
        value = component.get(key)
        if value:
            attributes.append(f"{label}: {value}")
    return f"{component['name']} [{'; '.join(attributes)}] - {component['definition']}"


def _format_applicability(record: dict[str, Any]) -> str:
    applicability = record.get("applicability")
    if not isinstance(applicability, dict) or not applicability:
        return "All declared scope"
    labels = {
        "target_sites": "sites",
        "products": "products",
        "markets": "markets",
        "audiences": "audiences",
        "locales": "locales",
        "states": "states",
        "journey_variant_ids": "variants",
    }
    parts = []
    for key, label in labels.items():
        values = applicability.get(key)
        if isinstance(values, list) and values:
            parts.append(f"{label}: {', '.join(str(value) for value in values)}")
    return "; ".join(parts) or "All declared scope"


def _evidence_roles(
    evidence_refs: Any, sources: dict[str, dict[str, Any]]
) -> list[str]:
    if not isinstance(evidence_refs, list):
        return []
    return sorted(
        {
            str(sources[prefix].get("evidence_role"))
            for reference in evidence_refs
            if isinstance(reference, str)
            for prefix in [reference.split("#", 1)[0]]
            if prefix in sources and sources[prefix].get("evidence_role")
        }
    )


def _ordered_kpis(data: dict[str, Any]) -> list[dict[str, Any]]:
    return sorted(
        data["kpis"],
        key=lambda item: (
            not item["recommended_core"],
            TIER_ORDER.get(item["tier"], 9),
            item["name"].lower(),
        ),
    )


def _evidence_requests(
    data: dict[str, Any], requirements: dict[str, dict[str, Any]]
) -> list[tuple[str, str, str, Any]]:
    requests: list[tuple[str, str, str, Any]] = []
    seen: set[tuple[str, str]] = set()

    for exception in data["exceptions"]:
        if exception["disposition"] != "awaiting_evidence":
            continue
        key = ("Exception", exception["exception_id"])
        if key not in seen:
            seen.add(key)
            requests.append(
                (
                    f"Exception `{exception['exception_id']}`",
                    exception["description"],
                    exception["impact"],
                    exception["affected_ids"],
                )
            )

    for assumption in data["assumptions"]:
        if assumption["status"] != "open":
            continue
        key = ("Assumption", assumption["assumption_id"])
        if key not in seen:
            seen.add(key)
            requests.append(
                (
                    f"Assumption `{assumption['assumption_id']}`",
                    assumption["statement"],
                    assumption["rationale"],
                    assumption["affected_ids"],
                )
            )

    for alignment in data["alignment"]:
        if alignment["status"] == "covered":
            continue
        requirement_id = alignment["requirement_id"]
        key = ("Alignment", requirement_id)
        if key not in seen:
            seen.add(key)
            requests.append(
                (
                    f"Alignment `{requirement_id}`",
                    requirements.get(requirement_id, {}).get("name", requirement_id),
                    alignment["action"],
                    alignment["gaps"],
                )
            )

    return requests


def render_framework(data: dict[str, Any]) -> str:
    document = data["document"]
    sources = {item["source_id"]: item for item in data["sources"]}
    objectives = {item["objective_id"]: item for item in data["objectives"]}
    journeys = {item["journey_id"]: item for item in data["journeys"]}
    dimensions = {item["dimension_id"]: item for item in data["dimensions"]}
    requirements = {
        item["requirement_id"]: item for item in data["measurement_requirements"]
    }
    ordered_kpis = _ordered_kpis(data)
    kpi_names = {item["kpi_id"]: item["name"] for item in ordered_kpis}
    active_objectives = [
        item
        for item in data["objectives"]
        if item["status"] in {"confirmed", "hypothesis"}
    ]
    material_journeys = [item for item in data["journeys"] if item["material"]]
    objective_lenses = {item["lens"] for item in data["objective_considerations"]}
    core_kpis = [item for item in ordered_kpis if item["recommended_core"]]
    core_and_north_star = [
        item
        for item in ordered_kpis
        if item["recommended_core"] or item["tier"] == "north_star"
    ]
    gates = data["quality_gates"]
    overall_gate = gates["overall"]
    advisories = review_advisories(data)
    maturity = evidence_maturity(data)
    discovery_coverage = discovery_evidence_coverage(data)
    computed_gate_facts = gate_facts(data)

    def compact_counts(values: dict[str, int]) -> str:
        return (
            ", ".join(f"{key}={value}" for key, value in sorted(values.items()))
            or "none"
        )

    lines: list[str] = [
        f"# {document['title']}",
        "",
        f"Version: `{document['version']}`  ",
        f"Date: `{document['date']}`  ",
        f"Target state: `{document['target_state']}`  ",
        f"Scope: {document['scope']}  ",
        f"Run: `{document['run_id']}`",
        "",
        "## Quality status",
        "",
        f"- Overall gate: **{overall_gate['status']}**",
        f"- Rationale: {overall_gate['rationale']}",
        "- Exceptions: "
        + (
            ", ".join(f"`{value}`" for value in overall_gate["exception_ids"]) or "None"
        ),
    ]

    lines.extend(
        [
            "",
            "## Measurement strategy summary",
            "",
            f"- Material journeys: **{len(material_journeys)}**",
            f"- Active objectives: **{len(active_objectives)}**",
            "- Objective considerations: "
            f"**{len(data['objective_considerations'])}** across "
            f"**{len(objective_lenses)}** lenses",
            f"- Accepted KPIs: **{len(ordered_kpis)}**; recommended core: **{len(core_kpis)}**",
            f"- Semantic measurement requirements: **{len(data['measurement_requirements'])}**",
            f"- Explicit exceptions: **{len(data['exceptions'])}**",
            f"- Journey evidence maturity: {compact_counts(maturity['journeys'])}",
            f"- Variant evidence maturity: {compact_counts(maturity['variants'])}",
            f"- Step evidence maturity: {compact_counts(maturity['steps'])}",
            f"- Objective evidence maturity: {compact_counts(maturity['objectives'])}",
            f"- KPI evidence maturity: {compact_counts(maturity['kpis'])}",
            "- Requirement evidence maturity: "
            f"{compact_counts(maturity['measurement_requirements'])}",
            "- Active objective(s): "
            + (_cell([item["statement"] for item in active_objectives]) or "None"),
        ]
    )

    intake = data.get("intake_baseline")
    if isinstance(intake, dict):
        lines.extend(["", "## Scope provenance", ""])
        lines.extend(
            [
                f"- Captured: `{intake['captured_at']}`",
                f"- Requested target state: `{intake['target_state']}`",
                f"- Requested scope claim: `{intake['scope_claim']}`",
                f"- Requested scope: {intake['scope_summary']}",
                f"- Resolved production targets: {_cell(document['target_sites']) or 'None'}",
                f"- Products: {_cell(intake['products']) or 'None'}",
                f"- Markets: {_cell(intake['markets']) or 'None'}",
                f"- Audiences: {_cell(intake['audiences']) or 'None'}",
                f"- Locales: {_cell(intake['locales']) or 'None'}",
                f"- Intake evidence: {_cell(intake['source_evidence_refs'])}",
                "",
            ]
        )
        lines.extend(
            _table(
                [
                    "Target ID",
                    "Requested target",
                    "Disposition",
                    "Resolved production scope",
                    "Resolution basis",
                    "Request evidence",
                    "Resolution evidence",
                    "Representative evidence sources",
                    "Exception",
                ],
                (
                    (
                        target["target_id"],
                        target["requested_target"],
                        target["disposition"],
                        target["resolved_scope_targets"],
                        target["resolution_basis"],
                        target["request_evidence_refs"],
                        target["resolution_evidence_refs"],
                        target["representative_source_ids"],
                        target.get("exception_id", ""),
                    )
                    for target in intake["targets"]
                ),
            )
        )
        if intake["authorizations"]:
            lines.extend(["", "### Safe interaction authorizations", ""])
            lines.extend(
                _table(
                    ["Type", "Target(s)", "Constraints", "Evidence"],
                    (
                        (
                            item["authorization_type"],
                            item["target_ids"],
                            item["constraints"],
                            item["evidence_refs"],
                        )
                        for item in intake["authorizations"]
                    ),
                )
            )

    lines.extend(["", "## North Star and recommended core", ""])
    if core_and_north_star:
        lines.extend(
            _table(
                [
                    "KPI",
                    "Role",
                    "Tier",
                    "Formula",
                    "Objective(s)",
                    "Decision use",
                    "North Star rationale",
                    "Applicability",
                ],
                (
                    (
                        item["name"],
                        item["role"],
                        item["tier"],
                        item["formula"]["expression"],
                        [
                            objectives[value]["statement"]
                            for value in item["objective_ids"]
                            if value in objectives
                        ],
                        item["decision_use"],
                        item.get("north_star_rationale", ""),
                        _format_applicability(item),
                    )
                    for item in core_and_north_star
                ),
            )
        )
    else:
        lines.append("No recommended-core KPI is recorded.")

    lines.extend(["", "## Objective and journey coverage", "", "### Objectives", ""])
    lines.extend(
        _table(
            [
                "Objective",
                "Value stream",
                "Origin",
                "Status",
                "Priority",
                "Journey(s)",
                "Applicability",
            ],
            (
                (
                    item["statement"],
                    item["value_stream"],
                    item["origin"],
                    item["status"],
                    item["priority"],
                    [
                        journeys[value]["name"]
                        for value in item["journey_ids"]
                        if value in journeys
                    ],
                    _format_applicability(item),
                )
                for item in data["objectives"]
            ),
        )
    )

    lines.extend(["", "### Objective evidence and rationale", ""])
    lines.extend(
        _table(
            [
                "Objective",
                "Confidence",
                "Owner",
                "Rationale",
                "Evidence",
                "Evidence roles",
            ],
            (
                (
                    item["statement"],
                    item["confidence"],
                    item.get("owner_role", "") or "Not assigned",
                    item["rationale"],
                    item["evidence_refs"],
                    _evidence_roles(item["evidence_refs"], sources),
                )
                for item in data["objectives"]
            ),
        )
    )

    lines.extend(["", "### Journeys", ""])
    lines.extend(
        _table(
            [
                "Journey",
                "Outcome",
                "Material",
                "Status",
                "Value domain(s)",
                "Entry point(s)",
                "Variant(s)",
                "Evidence",
                "Evidence roles",
                "Applicability",
            ],
            (
                (
                    item["name"],
                    item["outcome"],
                    item["material"],
                    item["status"],
                    item["value_domains"],
                    item["entry_points"],
                    [variant["name"] for variant in item["variants"]],
                    item["evidence_refs"],
                    _evidence_roles(item["evidence_refs"], sources),
                    _format_applicability(item),
                )
                for item in data["journeys"]
            ),
        )
    )

    variants = [
        (journey["name"], variant)
        for journey in data["journeys"]
        for variant in journey["variants"]
    ]
    if variants:
        lines.extend(["", "### Journey variants and states", ""])
        lines.extend(
            _table(
                [
                    "Journey",
                    "Variant",
                    "Material",
                    "Status",
                    "States covered",
                    "Evidence",
                    "Evidence roles",
                ],
                (
                    (
                        journey_name,
                        variant["name"],
                        variant["material"],
                        variant["status"],
                        variant["states_covered"],
                        variant["evidence_refs"],
                        _evidence_roles(variant["evidence_refs"], sources),
                    )
                    for journey_name, variant in variants
                ),
            )
        )

    steps = [
        (journey["name"], step)
        for journey in data["journeys"]
        for step in journey["steps"]
    ]
    if steps:
        lines.extend(["", "### Journey steps and evidence states", ""])
        lines.extend(
            _table(
                [
                    "Journey",
                    "Step",
                    "State",
                    "Status",
                    "Evidence",
                    "Evidence roles",
                    "Notes",
                ],
                (
                    (
                        journey_name,
                        step["name"],
                        step["state"],
                        step["status"],
                        step["evidence_refs"],
                        _evidence_roles(step["evidence_refs"], sources),
                        step.get("notes", ""),
                    )
                    for journey_name, step in steps
                ),
            )
        )

    state_decisions = [
        (journey["name"], decision)
        for journey in data["journeys"]
        for decision in journey.get("state_decisions", [])
    ]
    if state_decisions:
        lines.extend(["", "### Material state decisions", ""])
        lines.extend(
            _table(
                [
                    "Journey",
                    "State",
                    "Resolution",
                    "Supporting step(s)",
                    "Reason",
                    "Evidence",
                    "Evidence roles",
                    "Exception",
                ],
                (
                    (
                        journey_name,
                        decision["state"],
                        decision["resolution"],
                        decision["step_ids"],
                        decision["reason"],
                        decision["evidence_refs"],
                        _evidence_roles(decision["evidence_refs"], sources),
                        decision.get("exception_id", ""),
                    )
                    for journey_name, decision in state_decisions
                ),
            )
        )

    lines.extend(["", "## Top missing or partial measurement needs", ""])
    alignment_issues = [
        item for item in data["alignment"] if item["status"] != "covered"
    ]
    if alignment_issues:
        lines.extend(
            _table(
                ["Requirement", "Status", "Gap(s)", "Next action"],
                (
                    (
                        requirements[item["requirement_id"]]["name"],
                        item["status"],
                        item["gaps"],
                        item["action"],
                    )
                    for item in alignment_issues
                ),
            )
        )
    else:
        unverified = [
            item
            for item in data["measurement_requirements"]
            if item["verification_status"] in {"planned", "unverified"}
        ]
        if unverified:
            lines.extend(
                _table(
                    ["Requirement", "Verification", "Source", "Mode", "Priority"],
                    (
                        (
                            item["name"],
                            item["verification_status"],
                            item["source_system"],
                            item["collection_mode"],
                            item["priority"],
                        )
                        for item in unverified
                    ),
                )
            )
        else:
            lines.append(
                "No missing or partial measurement need is recorded in the canonical framework."
            )

    lines.extend(["", "## Evidence requests", ""])
    evidence_requests = _evidence_requests(data, requirements)
    if evidence_requests:
        lines.extend(
            _table(
                ["Type", "Evidence needed", "Impact or action", "Affected"],
                evidence_requests,
            )
        )
    else:
        lines.append("No open evidence request is recorded.")

    lines.extend(["", "## Quality gate detail", ""])
    lines.extend(
        _table(
            ["Gate", "Status", "Rationale", "Computed evidence", "Exceptions"],
            (
                (
                    name,
                    gates[name]["status"],
                    gates[name]["rationale"],
                    computed_gate_facts.get(name, []),
                    gates[name]["exception_ids"],
                )
                for name in [*GATE_ORDER, "overall"]
            ),
        )
    )

    if advisories:
        lines.extend(["", "## Review advisories", ""])
        lines.extend(f"- {advisory}" for advisory in advisories)

    lines.extend(["", "## KPI system", ""])
    lines.extend(
        _table(
            [
                "KPI",
                "Role",
                "Tier",
                "Formula",
                "Core",
                "Owner",
                "Evidence status",
                "Evidence roles",
                "Applicability",
            ],
            (
                (
                    item["name"],
                    item["role"],
                    item["tier"],
                    item["formula"]["expression"],
                    item["recommended_core"],
                    item["owner_role"],
                    item["evidence_status"],
                    _evidence_roles(item["evidence_refs"], sources),
                    _format_applicability(item),
                )
                for item in ordered_kpis
            ),
        )
    )

    applicability_bases = [
        (collection_name, record.get(id_key, ""), record["applicability_basis"])
        for collection_name, id_key, records in (
            ("objective", "objective_id", data["objectives"]),
            ("KPI", "kpi_id", data["kpis"]),
            ("dimension", "dimension_id", data["dimensions"]),
            (
                "measurement requirement",
                "requirement_id",
                data["measurement_requirements"],
            ),
        )
        for record in records
        if isinstance(record.get("applicability_basis"), dict)
    ]
    if applicability_bases:
        lines.extend(["", "### Broader applicability bases", ""])
        lines.extend(
            _table(
                ["Entity type", "Entity ID", "Rationale", "Evidence"],
                (
                    (kind, entity_id, basis["rationale"], basis["evidence_refs"])
                    for kind, entity_id, basis in applicability_bases
                ),
            )
        )

    lines.extend(["", "## KPI definitions", ""])
    for item in ordered_kpis:
        objective_names = [
            objectives[value]["statement"]
            for value in item["objective_ids"]
            if value in objectives
        ]
        journey_names = [
            journeys[value]["name"]
            for value in item["journey_ids"]
            if value in journeys
        ]
        dimension_names = [
            dimensions[value]["name"]
            for value in item["segmentation"]["dimension_ids"]
            if value in dimensions
        ]
        requirement_names = sorted(
            {
                requirements[requirement_id]["name"]
                for component in item["formula"]["components"]
                for requirement_id in component["requirement_ids"]
                if requirement_id in requirements
            }
        )
        lines.extend(
            [
                f"### {item['name']}",
                "",
                f"- ID: `{item['kpi_id']}`",
                f"- Objective(s): {_cell(objective_names)}",
                f"- Journey(s): {_cell(journey_names) or 'Not journey-specific'}",
                f"- Role and tier: {item['role']}; {item['tier']}",
                f"- Decision use: {item['decision_use']}",
                f"- Directionality: {item['directionality']}",
                f"- Owner: {item['owner_role']}",
                f"- Evidence status and references: {item['evidence_status']}; {_cell(item['evidence_refs'])}",
                f"- Formula: `{item['formula']['expression']}`",
                *(
                    [
                        "- Calculation contract: "
                        f"{item['formula']['calculation_type']}; result unit: "
                        f"{item['formula']['result_unit']}"
                    ]
                    if item["formula"].get("calculation_type")
                    and item["formula"].get("result_unit")
                    else []
                ),
                "- Formula components: "
                + "; ".join(
                    _format_formula_component(component)
                    for component in item["formula"]["components"]
                ),
                f"- Counting unit and grain: {item['formula']['counting_unit']}; {item['formula']['grain']}",
                f"- Population and window: {item['formula']['population']}; {item['formula']['reporting_window']}",
                f"- Inclusions: {_join_rules(item['formula']['inclusions'])}",
                f"- Exclusions: {_join_rules(item['formula']['exclusions'])}",
                f"- Dimensions: {_cell(dimension_names) or 'None'} - {item['segmentation']['rationale']}",
                f"- Measurement requirements: {_cell(requirement_names)}",
                f"- Applicability: {_format_applicability(item)}",
                *(
                    [f"- North Star rationale: {item['north_star_rationale']}"]
                    if item.get("north_star_rationale")
                    else []
                ),
                f"- Assumptions: {_cell(item.get('assumption_ids', [])) or 'None'}",
                "",
            ]
        )

    lines.extend(["## Measurement requirements", ""])
    lines.extend(
        _table(
            [
                "Requirement",
                "Semantic fact",
                "Timing or state",
                "Entity and grain",
                "Source and mode",
                "Priority",
                "KPI(s)",
                "Dimension(s)",
                "Status",
                "Applicability",
            ],
            (
                (
                    item["name"],
                    item["semantic_fact"],
                    item["timing_or_state"],
                    f"{item['entity']}; {item['grain']}",
                    f"{item['source_system']}; {item['collection_mode']}",
                    item["priority"],
                    [
                        kpi_names[value]
                        for value in item["kpi_ids"]
                        if value in kpi_names
                    ],
                    [
                        dimensions[value]["name"]
                        for value in item["dimension_ids"]
                        if value in dimensions
                    ],
                    item["verification_status"],
                    _format_applicability(item),
                )
                for item in data["measurement_requirements"]
            ),
        )
    )

    if data["alignment"]:
        lines.extend(["", "## Current-measurement alignment", ""])
        lines.extend(
            _table(
                ["Requirement", "Status", "Current evidence", "Gap(s)", "Action"],
                (
                    (
                        requirements[item["requirement_id"]]["name"],
                        item["status"],
                        item["current_measurement_refs"],
                        item["gaps"],
                        item["action"],
                    )
                    for item in data["alignment"]
                ),
            )
        )

    lines.extend(["", "## Evidence sources", ""])
    lines.extend(
        _table(
            [
                "Source ID",
                "Type",
                "Evidence role",
                "State",
                "Observed at",
                "Reference",
                "Supports",
                "Conflicts",
                "SHA-256",
            ],
            (
                (
                    source["source_id"],
                    source["source_type"],
                    source["evidence_role"],
                    source["state"],
                    source.get("observed_at", ""),
                    source["reference"],
                    source["supports"],
                    source.get("conflicts", []),
                    source.get("sha256", ""),
                )
                for source in data["sources"]
            ),
        )
    )

    resolution_counts = Counter(
        item["resolution"] for item in data["discovery_candidates"]
    )
    candidate_type_counts = Counter(
        (item["candidate_type"], item["resolution"])
        for item in data["discovery_candidates"]
    )
    candidate_type_totals = Counter(
        item["candidate_type"] for item in data["discovery_candidates"]
    )
    candidate_type_material = Counter(
        item["candidate_type"]
        for item in data["discovery_candidates"]
        if item["material"]
    )
    candidate_resolutions = ("mapped", "merged", "excluded", "unresolved")
    lines.extend(
        [
            "",
            "## Coverage evidence",
            "",
            f"Discovery candidates: **{len(data['discovery_candidates'])}**. "
            + ", ".join(
                f"{key}: {value}" for key, value in sorted(resolution_counts.items())
            )
            + ".",
            "",
        ]
    )
    direct_scope = discovery_coverage["direct_evidence_claimed_scope"]
    direct_scope_gaps = discovery_coverage[
        "document_scope_without_attributed_direct_evidence"
    ]
    lines.extend(["### Discovery and evidence diagnostics", ""])
    lines.extend(
        _table(
            ["Diagnostic", "Result"],
            [
                (
                    "Included targets represented by a source",
                    f"{len(discovery_coverage['represented_target_ids'])} / "
                    f"{discovery_coverage['included_target_count']}",
                ),
                (
                    "Direct evidence claimed scope",
                    "; ".join(
                        f"{key}: {len(values)} / "
                        f"{len(values) + len(direct_scope_gaps.get(key, []))}"
                        for key, values in direct_scope.items()
                    ),
                ),
                (
                    "Declared scope without attributable direct evidence",
                    "; ".join(
                        f"{key}: {', '.join(values) or 'none'}"
                        for key, values in direct_scope_gaps.items()
                    ),
                ),
                (
                    "Discovery sources unused by candidate ledger",
                    discovery_coverage[
                        "discovery_source_ids_without_candidate_support"
                    ]
                    or ["None"],
                ),
                (
                    "Material candidates supported only by intake",
                    discovery_coverage[
                        "material_candidate_ids_supported_only_by_intake"
                    ]
                    or ["None"],
                ),
                (
                    "Blocked journeys without alternative source",
                    discovery_coverage[
                        "externally_blocked_journey_ids_without_alternative_source"
                    ]
                    or ["None"],
                ),
                (
                    "Journeys needing environment-equivalence review",
                    [
                        item["journey_id"]
                        for item in discovery_coverage[
                            "journeys_needing_cross_environment_basis"
                        ]
                    ]
                    or ["None"],
                ),
                (
                    "Journeys needing locale-evidence review",
                    [
                        item["journey_id"]
                        for item in discovery_coverage[
                            "journeys_needing_locale_basis"
                        ]
                    ]
                    or ["None"],
                ),
            ],
        )
    )
    lines.append("")
    lines.extend(["### Discovery candidate summary", ""])
    lines.extend(
        _table(
            ["Type", "Total", "Material", *candidate_resolutions],
            (
                (
                    candidate_type,
                    candidate_type_totals[candidate_type],
                    candidate_type_material[candidate_type],
                    *(
                        candidate_type_counts[(candidate_type, resolution)]
                        for resolution in candidate_resolutions
                    ),
                )
                for candidate_type in sorted(candidate_type_totals)
            ),
        )
    )
    lines.extend(["", "### Discovery candidate ledger", ""])
    lines.extend(
        _table(
            [
                "Candidate",
                "Type",
                "Material",
                "Resolution",
                "Journey(s)",
                "Reason",
                "Evidence",
                "Evidence roles",
            ],
            (
                (
                    item["label"],
                    item["candidate_type"],
                    item["material"],
                    item["resolution"],
                    item["journey_ids"],
                    item["reason"],
                    item["evidence_refs"],
                    _evidence_roles(item["evidence_refs"], sources),
                )
                for item in data["discovery_candidates"]
            ),
        )
    )

    objective_resolution_order = (
        "objective_proposed",
        "covered_by_existing",
        "none_with_reason",
        "out_of_scope",
        "unresolved",
    )
    objective_lens_counts = Counter(
        (item["lens"], item["resolution"]) for item in data["objective_considerations"]
    )
    objective_lens_totals = Counter(
        item["lens"] for item in data["objective_considerations"]
    )
    lines.extend(["", "## Objective consideration summary", ""])
    lines.append(
        "Counts expose the recorded sweep depth for human review; they are not quality thresholds."
    )
    lines.append("")
    lines.extend(
        _table(
            ["Lens", "Total", *objective_resolution_order],
            (
                (
                    lens,
                    objective_lens_totals[lens],
                    *(
                        objective_lens_counts[(lens, resolution)]
                        for resolution in objective_resolution_order
                    ),
                )
                for lens in sorted(objective_lens_totals)
            ),
        )
    )

    lines.extend(["", "## Objective consideration ledger", ""])
    lines.extend(
        _table(
            ["Lens", "Topic", "Resolution", "Objective(s)", "Reason"],
            (
                (
                    item["lens"],
                    item["topic"],
                    item["resolution"],
                    item["objective_ids"],
                    item["reason"],
                )
                for item in data["objective_considerations"]
            ),
        )
    )

    lines.extend(["", "## KPI consideration ledger", ""])
    lines.extend(
        _table(
            ["Scope", "Role", "Resolution", "KPI(s)", "Reason"],
            (
                (
                    f"{item['scope_type']}:{item['scope_id']}",
                    item["role"],
                    item["resolution"],
                    item["kpi_ids"],
                    item["reason"],
                )
                for item in data["kpi_considerations"]
            ),
        )
    )

    if data["unlinked_measurements"]:
        lines.extend(["", "## Unlinked current measurements", ""])
        lines.extend(
            _table(
                ["Measurement", "Status", "Justification"],
                (
                    (item["measurement_ref"], item["status"], item["justification"])
                    for item in data["unlinked_measurements"]
                ),
            )
        )

    if data["assumptions"]:
        lines.extend(["", "## Assumptions", ""])
        lines.extend(
            _table(
                ["Assumption", "Status", "Affected IDs", "Rationale"],
                (
                    (
                        item["statement"],
                        item["status"],
                        item["affected_ids"],
                        item["rationale"],
                    )
                    for item in data["assumptions"]
                ),
            )
        )

    if data["exceptions"]:
        lines.extend(["", "## Exceptions and boundaries", ""])
        lines.extend(
            _table(
                [
                    "Exception",
                    "Stage",
                    "Affected gate(s)",
                    "Disposition",
                    "Affected IDs",
                    "Applicability",
                    "Impact",
                ],
                (
                    (
                        item["description"],
                        item["stage"],
                        [
                            gate_name
                            for gate_name in GATE_ORDER
                            if item["exception_id"]
                            in data["quality_gates"][gate_name]["exception_ids"]
                        ],
                        item["disposition"],
                        item["affected_ids"],
                        _format_applicability(item),
                        item["impact"],
                    )
                    for item in data["exceptions"]
                ),
            )
        )

    lines.extend(
        [
            "",
            "## Measurement boundary",
            "",
            "This framework defines what matters, how success is calculated, and what must be observable. It stops before platform-specific event and parameter semantics, exact implementation contracts, configuration, reporting construction, or runtime certification.",
            "",
        ]
    )
    return "\n".join(lines)


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "framework", type=Path, help="Canonical measurement-framework JSON"
    )
    parser.add_argument(
        "--output", "-o", type=Path, required=True, help="Markdown output path"
    )
    parser.add_argument(
        "--schema", type=Path, default=DEFAULT_SCHEMA, help="Override JSON Schema path"
    )
    parser.add_argument(
        "--allow-failed",
        action="store_true",
        help="Render a structurally valid draft whose overall gate is fail",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    try:
        with args.framework.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    errors = validate_framework(data, args.schema, delivery=not args.allow_failed)
    if errors:
        print(f"ERROR: framework is invalid ({len(errors)} issue(s))", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_framework(data) + "\n", encoding="utf-8")
    print(f"WROTE: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
