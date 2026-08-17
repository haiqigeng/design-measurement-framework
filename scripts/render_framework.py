#!/usr/bin/env python3
"""Render a validated measurement framework JSON artifact as Markdown."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from validate_framework import DEFAULT_SCHEMA, validate_framework


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
    lines.extend("| " + " | ".join(_cell(value) for value in row) + " |" for row in rows)
    return lines


def _join_rules(values: Any) -> str:
    if not isinstance(values, list) or not values:
        return "None specified"
    return "; ".join(str(value) for value in values)


def render_framework(data: dict[str, Any]) -> str:
    document = data["document"]
    objectives = {item["objective_id"]: item for item in data["objectives"]}
    journeys = {item["journey_id"]: item for item in data["journeys"]}
    dimensions = {item["dimension_id"]: item for item in data["dimensions"]}
    requirements = {item["requirement_id"]: item for item in data["measurement_requirements"]}

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
    ]

    gates = data["quality_gates"]
    lines.extend(
        _table(
            ["Gate", "Status", "Rationale", "Exceptions"],
            (
                (name, gate["status"], gate["rationale"], gate["exception_ids"])
                for name, gate in gates.items()
            ),
        )
    )

    resolution_counts = Counter(item["resolution"] for item in data["discovery_candidates"])
    lines.extend(
        [
            "",
            "## Coverage summary",
            "",
            f"Discovery candidates: **{len(data['discovery_candidates'])}**. "
            + ", ".join(f"{key}: {value}" for key, value in sorted(resolution_counts.items()))
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

    lines.extend(["", "## Journey inventory", ""])
    lines.extend(
        _table(
            ["Journey", "Outcome", "Material", "Status", "Value domain(s)", "Entry point(s)"],
            (
                (
                    item["name"],
                    item["outcome"],
                    item["material"],
                    item["status"],
                    item["value_domains"],
                    item["entry_points"],
                )
                for item in data["journeys"]
            ),
        )
    )

    lines.extend(["", "## Objective consideration ledger", ""])
    lines.extend(
        _table(
            ["Lens", "Topic", "Resolution", "Objective(s)", "Reason"],
            (
                (item["lens"], item["topic"], item["resolution"], item["objective_ids"], item["reason"])
                for item in data["objective_considerations"]
            ),
        )
    )

    lines.extend(["", "## Objectives", ""])
    lines.extend(
        _table(
            ["Objective", "Value stream", "Origin", "Status", "Priority", "Journey(s)", "Confidence"],
            (
                (
                    item["statement"],
                    item["value_stream"],
                    item["origin"],
                    item["status"],
                    item["priority"],
                    item["journey_ids"],
                    item["confidence"],
                )
                for item in data["objectives"]
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

    ordered_kpis = sorted(
        data["kpis"],
        key=lambda item: (
            not item["recommended_core"],
            {"north_star": 0, "primary": 1, "guardrail": 2, "supporting": 3, "diagnostic": 4}.get(
                item["tier"], 9
            ),
            item["name"].lower(),
        ),
    )
    lines.extend(["", "## KPI system", ""])
    lines.extend(
        _table(
            ["KPI", "Role", "Tier", "Formula", "Core", "Owner", "Evidence"],
            (
                (
                    item["name"],
                    item["role"],
                    item["tier"],
                    item["formula"]["expression"],
                    item["recommended_core"],
                    item["owner_role"],
                    item["evidence_status"],
                )
                for item in ordered_kpis
            ),
        )
    )

    lines.extend(["", "## KPI definitions", ""])
    for item in ordered_kpis:
        objective_names = [objectives[value]["statement"] for value in item["objective_ids"] if value in objectives]
        journey_names = [journeys[value]["name"] for value in item["journey_ids"] if value in journeys]
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
                f"- Decision use: {item['decision_use']}",
                f"- Formula: `{item['formula']['expression']}`",
                f"- Counting unit and grain: {item['formula']['counting_unit']}; {item['formula']['grain']}",
                f"- Population and window: {item['formula']['population']}; {item['formula']['reporting_window']}",
                f"- Inclusions: {_join_rules(item['formula']['inclusions'])}",
                f"- Exclusions: {_join_rules(item['formula']['exclusions'])}",
                f"- Dimensions: {_cell(dimension_names) or 'None'} — {item['segmentation']['rationale']}",
                f"- Measurement requirements: {_cell(requirement_names)}",
                "",
            ]
        )

    lines.extend(["## Measurement requirements", ""])
    lines.extend(
        _table(
            ["Requirement", "Semantic fact", "Mode", "Source", "Priority", "KPI(s)", "Status"],
            (
                (
                    item["name"],
                    item["semantic_fact"],
                    item["collection_mode"],
                    item["source_system"],
                    item["priority"],
                    [data_item["name"] for data_item in ordered_kpis if data_item["kpi_id"] in item["kpi_ids"]],
                    item["verification_status"],
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
                    (item["statement"], item["status"], item["affected_ids"], item["rationale"])
                    for item in data["assumptions"]
                ),
            )
        )

    if data["exceptions"]:
        lines.extend(["", "## Exceptions and boundaries", ""])
        lines.extend(
            _table(
                ["Exception", "Stage", "Disposition", "Affected IDs", "Impact"],
                (
                    (
                        item["description"],
                        item["stage"],
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
            "## Downstream boundary",
            "",
            "This framework defines what must be measurable and why. Final GA4 event and parameter semantics, exact triggers, dataLayer paths, and implementation examples belong to the downstream tracking-plan workflow.",
            "",
        ]
    )
    return "\n".join(lines)


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("framework", type=Path, help="Canonical measurement-framework JSON")
    parser.add_argument("--output", "-o", type=Path, required=True, help="Markdown output path")
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA, help="Override JSON Schema path")
    parser.add_argument("--allow-failed", action="store_true", help="Render a structurally valid draft whose overall gate is fail")
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
    args.output.write_text(render_framework(data), encoding="utf-8")
    print(f"WROTE: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
