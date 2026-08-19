#!/usr/bin/env python3
"""Evaluate a framework against a fixed analytical benchmark and optional baseline."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from diagnostics import discovery_evidence_coverage, evidence_eligibility_issues
from validate_framework import validate_framework

SUPPORTED_LAYERS = {
    "discovery_candidates",
    "journeys",
    "objectives",
    "kpis",
}


def _records(data: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = data.get(key, [])
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _normalize(value: Any) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", str(value or "").lower()))


def _record_text(layer: str, record: dict[str, Any]) -> str:
    fields: list[Any]
    if layer == "discovery_candidates":
        fields = [
            record.get("candidate_type"),
            record.get("label"),
            record.get("reason"),
        ]
    elif layer == "journeys":
        fields = [
            record.get("name"),
            record.get("outcome"),
            record.get("value_domains"),
            record.get("entry_points"),
        ]
    elif layer == "objectives":
        fields = [
            record.get("statement"),
            record.get("value_stream"),
            record.get("rationale"),
        ]
    else:
        formula = record.get("formula", {})
        components = (
            formula.get("components", []) if isinstance(formula, dict) else []
        )
        fields = [
            record.get("name"),
            record.get("role"),
            record.get("tier"),
            record.get("decision_use"),
            formula.get("population") if isinstance(formula, dict) else None,
            [
                [component.get("name"), component.get("definition")]
                for component in components
                if isinstance(component, dict)
            ],
        ]
    return _normalize(json.dumps(fields, ensure_ascii=False, sort_keys=True))


def _matches_expectation(
    layer: str, record: dict[str, Any], expectation: dict[str, Any]
) -> bool:
    if "material" in expectation and record.get("material") is not expectation["material"]:
        return False
    allowed_roles = expectation.get("allowed_roles")
    if isinstance(allowed_roles, list) and record.get("role") not in allowed_roles:
        return False
    allowed_statuses = expectation.get("allowed_statuses")
    status = record.get("status", record.get("evidence_status"))
    if isinstance(allowed_statuses, list) and status not in allowed_statuses:
        return False

    text = _record_text(layer, record)
    match_any = [
        _normalize(value)
        for value in expectation.get("match_any", [])
        if _normalize(value)
    ]
    required_terms = [
        _normalize(value)
        for value in expectation.get("required_terms", [])
        if _normalize(value)
    ]
    return (not match_any or any(value in text for value in match_any)) and all(
        value in text for value in required_terms
    )


def _concept_matches(
    data: dict[str, Any], benchmark: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    matches: dict[str, dict[str, Any]] = {}
    for expectation in benchmark.get("expectations", []):
        if not isinstance(expectation, dict):
            continue
        concept_id = str(expectation.get("concept_id", ""))
        layer = str(expectation.get("layer", ""))
        if not concept_id or layer not in SUPPORTED_LAYERS:
            continue
        id_key = {
            "discovery_candidates": "candidate_id",
            "journeys": "journey_id",
            "objectives": "objective_id",
            "kpis": "kpi_id",
        }[layer]
        record_ids = sorted(
            str(record.get(id_key, ""))
            for record in _records(data, layer)
            if _matches_expectation(layer, record, expectation)
        )
        matches[concept_id] = {
            "layer": layer,
            "matched": bool(record_ids),
            "record_ids": [value for value in record_ids if value],
        }
    return matches


def _traceability_rate(data: dict[str, Any]) -> float:
    source_ids = {
        str(source.get("source_id")) for source in _records(data, "sources")
    }
    records = [
        *[
            item
            for item in _records(data, "discovery_candidates")
            if item.get("material") is True
        ],
        *[
            item for item in _records(data, "journeys") if item.get("material") is True
        ],
        *[
            item
            for item in _records(data, "objectives")
            if item.get("status") in {"confirmed", "hypothesis"}
        ],
        *_records(data, "kpis"),
        *_records(data, "measurement_requirements"),
    ]
    if not records:
        return 0.0
    traced = 0
    for record in records:
        refs = record.get("evidence_refs", [])
        if isinstance(refs, list) and refs and all(
            isinstance(reference, str)
            and reference.split("#", 1)[0] in source_ids
            for reference in refs
        ):
            traced += 1
    return traced / len(records)


def _formula_specificity_rate(data: dict[str, Any]) -> float:
    kpis = _records(data, "kpis")
    if not kpis:
        return 0.0
    specific = 0
    for kpi in kpis:
        formula = kpi.get("formula", {})
        components = formula.get("components", []) if isinstance(formula, dict) else []
        if (
            isinstance(formula, dict)
            and all(
                str(formula.get(key, "")).strip()
                for key in (
                    "expression",
                    "counting_unit",
                    "grain",
                    "population",
                    "reporting_window",
                )
            )
            and isinstance(components, list)
            and components
            and all(
                isinstance(component, dict)
                and all(
                    str(component.get(key, "")).strip()
                    for key in ("symbol", "counting_unit", "grain")
                )
                and bool(component.get("requirement_ids"))
                for component in components
            )
        ):
            specific += 1
    return specific / len(kpis)


def _requirement_specificity_rate(data: dict[str, Any]) -> float:
    requirements = _records(data, "measurement_requirements")
    if not requirements:
        return 0.0
    specific = sum(
        1
        for requirement in requirements
        if all(
            str(requirement.get(key, "")).strip()
            for key in (
                "semantic_fact",
                "timing_or_state",
                "entity",
                "grain",
                "source_system",
                "collection_mode",
            )
        )
    )
    return specific / len(requirements)


def _recall_by_layer(
    matches: dict[str, dict[str, Any]], layer: str
) -> float:
    layer_matches = [item for item in matches.values() if item["layer"] == layer]
    if not layer_matches:
        return 1.0
    return sum(1 for item in layer_matches if item["matched"]) / len(layer_matches)


def evaluate_framework(
    data: dict[str, Any], benchmark: dict[str, Any]
) -> dict[str, Any]:
    validation_errors = validate_framework(data, delivery=True)
    concept_matches = _concept_matches(data, benchmark)
    coverage = discovery_evidence_coverage(data)
    material_candidate_total = sum(
        1
        for item in _records(data, "discovery_candidates")
        if item.get("material") is True
    )
    direct_claim_count = sum(
        1
        for journey in _records(data, "journeys")
        for record in [
            journey,
            *[
                item
                for item in journey.get("steps", [])
                if isinstance(item, dict)
            ],
            *[
                item
                for item in journey.get("variants", [])
                if isinstance(item, dict)
            ],
        ]
        if record.get("status") in {"observed", "externally_blocked"}
    )
    eligibility_issues = evidence_eligibility_issues(data)
    metrics = {
        "candidate_recall": _recall_by_layer(
            concept_matches, "discovery_candidates"
        ),
        "journey_recall": _recall_by_layer(concept_matches, "journeys"),
        "objective_recall": _recall_by_layer(concept_matches, "objectives"),
        "kpi_recall": _recall_by_layer(concept_matches, "kpis"),
        "evidence_traceability_rate": _traceability_rate(data),
        "formula_specificity_rate": _formula_specificity_rate(data),
        "requirement_specificity_rate": _requirement_specificity_rate(data),
        "observed_claim_issue_rate": len(eligibility_issues)
        / max(1, direct_claim_count),
        "intake_only_material_candidate_rate": len(
            coverage["material_candidate_ids_supported_only_by_intake"]
        )
        / max(1, material_candidate_total),
    }
    threshold_failures: list[str] = []
    for threshold_name, expected in benchmark.get("thresholds", {}).items():
        if not isinstance(expected, (int, float)):
            continue
        if threshold_name.startswith("min_"):
            metric_name = threshold_name[4:]
            actual = metrics.get(metric_name)
            if actual is None or actual < expected:
                threshold_failures.append(
                    f"{metric_name}={actual!r} is below minimum {expected!r}"
                )
        elif threshold_name.startswith("max_"):
            metric_name = threshold_name[4:]
            actual = metrics.get(metric_name)
            if actual is None or actual > expected:
                threshold_failures.append(
                    f"{metric_name}={actual!r} exceeds maximum {expected!r}"
                )

    missing_concepts = sorted(
        concept_id
        for concept_id, match in concept_matches.items()
        if not match["matched"]
    )
    passed = not validation_errors and not threshold_failures and not missing_concepts
    return {
        "passed": passed,
        "benchmark_id": benchmark.get("benchmark_id"),
        "structurally_valid": not validation_errors,
        "validation_errors": validation_errors,
        "concept_matches": concept_matches,
        "missing_concepts": missing_concepts,
        "metrics": metrics,
        "threshold_failures": sorted(threshold_failures),
        "diagnostics": {
            "discovery_evidence_coverage": coverage,
            "evidence_eligibility_issues": eligibility_issues,
        },
        "human_review_questions": benchmark.get("human_review_questions", []),
    }


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return value


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("framework", type=Path, help="Framework JSON to evaluate")
    parser.add_argument("--benchmark", required=True, type=Path)
    parser.add_argument(
        "--baseline",
        type=Path,
        help="Optional prior framework evaluated against the same benchmark",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    try:
        framework = _load_json(args.framework)
        benchmark = _load_json(args.benchmark)
        report = evaluate_framework(framework, benchmark)
        if args.baseline:
            baseline = evaluate_framework(_load_json(args.baseline), benchmark)
            current_matches = report["concept_matches"]
            baseline_matches = baseline["concept_matches"]
            lost_concepts = sorted(
                concept_id
                for concept_id, match in baseline_matches.items()
                if match["matched"]
                and not current_matches.get(concept_id, {}).get("matched", False)
            )
            metric_deltas = {
                key: report["metrics"][key] - baseline["metrics"].get(key, 0.0)
                for key in report["metrics"]
            }
            report["baseline_comparison"] = {
                "baseline_passed": baseline["passed"],
                "lost_concepts": lost_concepts,
                "gained_concepts": sorted(
                    concept_id
                    for concept_id, match in current_matches.items()
                    if match["matched"]
                    and not baseline_matches.get(concept_id, {}).get("matched", False)
                ),
                "metric_deltas": metric_deltas,
            }
            if benchmark.get("fail_on_baseline_concept_regression") and lost_concepts:
                report["passed"] = False
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"passed": False, "error": str(exc)}, indent=2))
        return 1
    print(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
