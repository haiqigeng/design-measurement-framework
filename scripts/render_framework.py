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

from validate_framework import DEFAULT_SCHEMA, GATE_ORDER, validate_framework

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


def _format_applicability(record: dict[str, Any]) -> str:
    applicability = record.get("applicability")
    if not isinstance(applicability, dict) or not applicability:
        return "All declared scope"
    labels = {
        "target_sites": "sites",
        "products": "products",
        "markets": "markets",
        "audiences": "audiences",
        "states": "states",
        "journey_variant_ids": "variants",
    }
    parts = []
    for key, label in labels.items():
        values = applicability.get(key)
        if isinstance(values, list) and values:
            parts.append(f"{label}: {', '.join(str(value) for value in values)}")
    return "; ".join(parts) or "All declared scope"


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
    core_kpis = [item for item in ordered_kpis if item["recommended_core"]]
    core_and_north_star = [
        item
        for item in ordered_kpis
        if item["recommended_core"] or item["tier"] == "north_star"
    ]
    gates = data["quality_gates"]
    overall_gate = gates["overall"]

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
            f"- Accepted KPIs: **{len(ordered_kpis)}**; recommended core: **{len(core_kpis)}**",
            f"- Semantic measurement requirements: **{len(data['measurement_requirements'])}**",
            f"- Explicit exceptions: **{len(data['exceptions'])}**",
            "- Active objective(s): "
            + (_cell([item["statement"] for item in active_objectives]) or "None"),
            "",
            "## North Star and recommended core",
            "",
        ]
    )
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

    lines.extend(["", "### Journeys", ""])
    lines.extend(
        _table(
            [
                "Journey",
                "Outcome",
                "Material",
                "Status",
                "Value domain(s)",
                "Variant(s)",
                "Applicability",
            ],
            (
                (
                    item["name"],
                    item["outcome"],
                    item["material"],
                    item["status"],
                    item["value_domains"],
                    [variant["name"] for variant in item["variants"]],
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
                ],
                (
                    (
                        journey_name,
                        variant["name"],
                        variant["material"],
                        variant["status"],
                        variant["states_covered"],
                        variant["evidence_refs"],
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
                ["Journey", "Step", "State", "Status", "Evidence", "Notes"],
                (
                    (
                        journey_name,
                        step["name"],
                        step["state"],
                        step["status"],
                        step["evidence_refs"],
                        step.get("notes", ""),
                    )
                    for journey_name, step in steps
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
            ["Gate", "Status", "Rationale", "Exceptions"],
            (
                (
                    name,
                    gates[name]["status"],
                    gates[name]["rationale"],
                    gates[name]["exception_ids"],
                )
                for name in [*GATE_ORDER, "overall"]
            ),
        )
    )

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
                "Evidence",
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
                    _format_applicability(item),
                )
                for item in ordered_kpis
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
                "- Formula components: "
                + "; ".join(
                    f"{component['name']} [{component['role']}] - {component['definition']}"
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

    resolution_counts = Counter(
        item["resolution"] for item in data["discovery_candidates"]
    )
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
    lines.extend(
        _table(
            ["Candidate", "Type", "Material", "Resolution", "Journey(s)", "Reason"],
            (
                (
                    item["label"],
                    item["candidate_type"],
                    item["material"],
                    item["resolution"],
                    item["journey_ids"],
                    item["reason"],
                )
                for item in data["discovery_candidates"]
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
