#!/usr/bin/env python3
"""Validate a design-measurement-framework canonical JSON artifact."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = ROOT / "schemas" / "measurement-framework.schema.json"


def _json_path(parts: Iterable[Any]) -> str:
    path = "$"
    for part in parts:
        if isinstance(part, int):
            path += f"[{part}]"
        else:
            path += f".{part}"
    return path


def _records(data: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = data.get(key, [])
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _register_ids(
    records: list[dict[str, Any]],
    key: str,
    collection: str,
    registry: dict[str, str],
    errors: list[str],
) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for index, record in enumerate(records):
        value = record.get(key)
        if not isinstance(value, str) or not value:
            continue
        path = f"$.{collection}[{index}].{key}"
        if value in registry:
            errors.append(f"{path}: duplicate global ID {value!r}; first declared at {registry[value]}")
        else:
            registry[value] = path
        if value in indexed:
            errors.append(f"{path}: duplicate {collection} ID {value!r}")
        indexed[value] = record
    return indexed


def _add_nested_ids(
    parent_records: list[dict[str, Any]],
    collection: str,
    nested_key: str,
    id_key: str,
    registry: dict[str, str],
    errors: list[str],
) -> None:
    for parent_index, parent in enumerate(parent_records):
        nested = parent.get(nested_key, [])
        if not isinstance(nested, list):
            continue
        for nested_index, record in enumerate(nested):
            if not isinstance(record, dict):
                continue
            value = record.get(id_key)
            if not isinstance(value, str) or not value:
                continue
            path = f"$.{collection}[{parent_index}].{nested_key}[{nested_index}].{id_key}"
            if value in registry:
                errors.append(f"{path}: duplicate global ID {value!r}; first declared at {registry[value]}")
            else:
                registry[value] = path


def _require_refs(
    values: Any,
    valid: set[str],
    path: str,
    label: str,
    errors: list[str],
) -> None:
    if not isinstance(values, list):
        return
    for index, value in enumerate(values):
        if isinstance(value, str) and value not in valid:
            errors.append(f"{path}[{index}]: unknown {label} {value!r}")


def _walk_evidence_refs(
    node: Any,
    source_ids: set[str],
    errors: list[str],
    path: str = "$",
) -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            child_path = f"{path}.{key}"
            if key in {"evidence_refs", "current_measurement_refs"} and isinstance(value, list):
                for index, ref in enumerate(value):
                    if not isinstance(ref, str):
                        continue
                    prefix = ref.split("#", 1)[0]
                    if prefix not in source_ids:
                        errors.append(f"{child_path}[{index}]: evidence source {prefix!r} is not declared")
            else:
                _walk_evidence_refs(value, source_ids, errors, child_path)
    elif isinstance(node, list):
        for index, value in enumerate(node):
            _walk_evidence_refs(value, source_ids, errors, f"{path}[{index}]")


def _has_exception(
    entity_id: str,
    exceptions: dict[str, dict[str, Any]],
    stage: str | None = None,
) -> bool:
    return any(
        entity_id in item.get("affected_ids", []) and (stage is None or item.get("stage") == stage)
        for item in exceptions.values()
    )


def _active_objective(record: dict[str, Any]) -> bool:
    return record.get("status") in {"confirmed", "hypothesis"}


def validate_framework(
    data: dict[str, Any],
    schema_path: Path | None = None,
    *,
    delivery: bool = False,
) -> list[str]:
    """Return human-readable validation errors; return an empty list when valid."""

    errors: list[str] = []
    selected_schema = schema_path or DEFAULT_SCHEMA
    with selected_schema.open("r", encoding="utf-8") as handle:
        schema = json.load(handle)

    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    schema_errors = sorted(
        validator.iter_errors(data),
        key=lambda error: _json_path(error.absolute_path),
    )
    for error in schema_errors:
        errors.append(f"{_json_path(error.absolute_path)}: {error.message}")

    if not isinstance(data, dict):
        return errors

    registry: dict[str, str] = {}
    sources = _register_ids(_records(data, "sources"), "source_id", "sources", registry, errors)
    candidates = _register_ids(
        _records(data, "discovery_candidates"),
        "candidate_id",
        "discovery_candidates",
        registry,
        errors,
    )
    journeys = _register_ids(_records(data, "journeys"), "journey_id", "journeys", registry, errors)
    objective_considerations = _register_ids(
        _records(data, "objective_considerations"),
        "consideration_id",
        "objective_considerations",
        registry,
        errors,
    )
    objectives = _register_ids(_records(data, "objectives"), "objective_id", "objectives", registry, errors)
    kpi_considerations = _register_ids(
        _records(data, "kpi_considerations"),
        "consideration_id",
        "kpi_considerations",
        registry,
        errors,
    )
    kpis = _register_ids(_records(data, "kpis"), "kpi_id", "kpis", registry, errors)
    dimensions = _register_ids(_records(data, "dimensions"), "dimension_id", "dimensions", registry, errors)
    requirements = _register_ids(
        _records(data, "measurement_requirements"),
        "requirement_id",
        "measurement_requirements",
        registry,
        errors,
    )
    assumptions = _register_ids(_records(data, "assumptions"), "assumption_id", "assumptions", registry, errors)
    exceptions = _register_ids(_records(data, "exceptions"), "exception_id", "exceptions", registry, errors)

    journey_records = _records(data, "journeys")
    kpi_records = _records(data, "kpis")
    _add_nested_ids(journey_records, "journeys", "steps", "step_id", registry, errors)
    _add_nested_ids(journey_records, "journeys", "variants", "variant_id", registry, errors)
    for kpi_index, kpi in enumerate(kpi_records):
        components = kpi.get("formula", {}).get("components", []) if isinstance(kpi.get("formula"), dict) else []
        if isinstance(components, list):
            for component_index, component in enumerate(components):
                if not isinstance(component, dict):
                    continue
                value = component.get("component_id")
                if not isinstance(value, str) or not value:
                    continue
                path = f"$.kpis[{kpi_index}].formula.components[{component_index}].component_id"
                if value in registry:
                    errors.append(f"{path}: duplicate global ID {value!r}; first declared at {registry[value]}")
                else:
                    registry[value] = path

    source_ids = set(sources)
    journey_ids = set(journeys)
    objective_ids = set(objectives)
    kpi_ids = set(kpis)
    dimension_ids = set(dimensions)
    requirement_ids = set(requirements)
    assumption_ids = set(assumptions)
    exception_ids = set(exceptions)
    known_ids = set(registry)

    _walk_evidence_refs(data, source_ids, errors)

    for index, candidate in enumerate(_records(data, "discovery_candidates")):
        candidate_id = candidate.get("candidate_id", "")
        resolution = candidate.get("resolution")
        linked = candidate.get("journey_ids", [])
        _require_refs(linked, journey_ids, f"$.discovery_candidates[{index}].journey_ids", "journey ID", errors)
        if resolution in {"mapped", "merged"} and not linked:
            errors.append(f"$.discovery_candidates[{index}]: {resolution} requires at least one journey_id")
        if resolution == "excluded" and linked:
            errors.append(f"$.discovery_candidates[{index}]: excluded candidate must not retain journey_ids")
        if resolution == "unresolved" and not _has_exception(str(candidate_id), exceptions, "journey"):
            errors.append(f"$.discovery_candidates[{index}]: unresolved candidate requires a linked exception")

    material_journey_ids: set[str] = set()
    for index, journey in enumerate(journey_records):
        journey_id = str(journey.get("journey_id", ""))
        if journey.get("material") is True:
            material_journey_ids.add(journey_id)
            if journey.get("status") in {"partial", "not_tested", "externally_blocked"} and not _has_exception(
                journey_id, exceptions, "journey"
            ):
                errors.append(
                    f"$.journeys[{index}]: material journey with status {journey.get('status')!r} requires a linked exception"
                )

    required_lenses = {"value_stream", "lifecycle", "stakeholder", "risk_guardrail"}
    present_lenses = {
        str(item.get("lens")) for item in _records(data, "objective_considerations") if item.get("lens")
    }
    for lens in sorted(required_lenses - present_lenses):
        errors.append(f"$.objective_considerations: missing required {lens!r} sweep decision")

    for index, item in enumerate(_records(data, "objective_considerations")):
        consideration_id = str(item.get("consideration_id", ""))
        linked = item.get("objective_ids", [])
        _require_refs(
            linked,
            objective_ids,
            f"$.objective_considerations[{index}].objective_ids",
            "objective ID",
            errors,
        )
        resolution = item.get("resolution")
        if resolution in {"objective_proposed", "covered_by_existing"} and not linked:
            errors.append(f"$.objective_considerations[{index}]: {resolution} requires objective_ids")
        if resolution in {"none_with_reason", "out_of_scope"} and linked:
            errors.append(f"$.objective_considerations[{index}]: {resolution} must not retain objective_ids")
        if resolution == "unresolved" and not _has_exception(consideration_id, exceptions, "objective"):
            errors.append(f"$.objective_considerations[{index}]: unresolved consideration requires a linked exception")

    active_objective_ids = {key for key, value in objectives.items() if _active_objective(value)}
    objective_journeys: dict[str, set[str]] = {}
    value_streams: dict[str, list[dict[str, Any]]] = {}
    for index, objective in enumerate(_records(data, "objectives")):
        objective_id = str(objective.get("objective_id", ""))
        linked_journeys = set(objective.get("journey_ids", [])) if isinstance(objective.get("journey_ids"), list) else set()
        objective_journeys[objective_id] = linked_journeys
        _require_refs(
            list(linked_journeys),
            journey_ids,
            f"$.objectives[{index}].journey_ids",
            "journey ID",
            errors,
        )
        if _active_objective(objective):
            value_streams.setdefault(str(objective.get("value_stream", "")), []).append(objective)

    for journey_id in sorted(material_journey_ids):
        if not any(journey_id in objective_journeys.get(objective_id, set()) for objective_id in active_objective_ids):
            errors.append(f"$.journeys[{journey_id!r}]: material journey has no active objective link")

    for value_stream, records in value_streams.items():
        if value_stream and not any(record.get("priority") == "primary" for record in records):
            errors.append(f"$.objectives: active value stream {value_stream!r} has no primary objective")

    for index, item in enumerate(_records(data, "kpi_considerations")):
        consideration_id = str(item.get("consideration_id", ""))
        scope_type = item.get("scope_type")
        scope_id = item.get("scope_id")
        if scope_type == "objective" and scope_id not in objective_ids:
            errors.append(f"$.kpi_considerations[{index}].scope_id: unknown objective ID {scope_id!r}")
        if scope_type == "journey" and scope_id not in journey_ids:
            errors.append(f"$.kpi_considerations[{index}].scope_id: unknown journey ID {scope_id!r}")
        linked = item.get("kpi_ids", [])
        _require_refs(linked, kpi_ids, f"$.kpi_considerations[{index}].kpi_ids", "KPI ID", errors)
        resolution = item.get("resolution")
        if resolution in {"kpi_proposed", "covered_by_existing"} and not linked:
            errors.append(f"$.kpi_considerations[{index}]: {resolution} requires kpi_ids")
        if resolution in {"none_with_reason", "not_applicable"} and linked:
            errors.append(f"$.kpi_considerations[{index}]: {resolution} must not retain kpi_ids")
        if resolution == "unresolved" and not _has_exception(consideration_id, exceptions, "kpi"):
            errors.append(f"$.kpi_considerations[{index}]: unresolved consideration requires a linked exception")

    consideration_records = _records(data, "kpi_considerations")
    for objective_id in sorted(active_objective_ids):
        roles = {
            item.get("role")
            for item in consideration_records
            if item.get("scope_type") == "objective" and item.get("scope_id") == objective_id
        }
        for role in sorted({"outcome", "driver", "guardrail"} - roles):
            errors.append(f"$.kpi_considerations: objective {objective_id!r} lacks required {role!r} consideration")
    for journey_id in sorted(material_journey_ids):
        roles = {
            item.get("role")
            for item in consideration_records
            if item.get("scope_type") == "journey" and item.get("scope_id") == journey_id
        }
        for role in sorted({"completion", "step_conversion", "friction"} - roles):
            errors.append(f"$.kpi_considerations: journey {journey_id!r} lacks required {role!r} consideration")

    component_requirement_links: dict[str, set[str]] = {requirement_id: set() for requirement_id in requirement_ids}
    kpi_dimension_links: dict[str, set[str]] = {dimension_id: set() for dimension_id in dimension_ids}
    for index, kpi in enumerate(kpi_records):
        kpi_id = str(kpi.get("kpi_id", ""))
        linked_objectives = kpi.get("objective_ids", [])
        _require_refs(linked_objectives, objective_ids, f"$.kpis[{index}].objective_ids", "objective ID", errors)
        primary = kpi.get("primary_objective_id")
        if primary not in objective_ids:
            errors.append(f"$.kpis[{index}].primary_objective_id: unknown objective ID {primary!r}")
        elif primary not in linked_objectives:
            errors.append(f"$.kpis[{index}]: primary_objective_id must also appear in objective_ids")
        elif not _active_objective(objectives[primary]):
            errors.append(f"$.kpis[{index}]: primary objective {primary!r} is not active")
        _require_refs(kpi.get("journey_ids", []), journey_ids, f"$.kpis[{index}].journey_ids", "journey ID", errors)
        segmentation = kpi.get("segmentation", {})
        linked_dimensions = segmentation.get("dimension_ids", []) if isinstance(segmentation, dict) else []
        _require_refs(linked_dimensions, dimension_ids, f"$.kpis[{index}].segmentation.dimension_ids", "dimension ID", errors)
        for dimension_id in linked_dimensions:
            if dimension_id in kpi_dimension_links:
                kpi_dimension_links[dimension_id].add(kpi_id)
        formula = kpi.get("formula", {})
        components = formula.get("components", []) if isinstance(formula, dict) else []
        for component_index, component in enumerate(components if isinstance(components, list) else []):
            if not isinstance(component, dict):
                continue
            linked_requirements = component.get("requirement_ids", [])
            _require_refs(
                linked_requirements,
                requirement_ids,
                f"$.kpis[{index}].formula.components[{component_index}].requirement_ids",
                "measurement requirement ID",
                errors,
            )
            for requirement_id in linked_requirements:
                if requirement_id in component_requirement_links:
                    component_requirement_links[requirement_id].add(kpi_id)
        linked_assumptions = kpi.get("assumption_ids", [])
        _require_refs(linked_assumptions, assumption_ids, f"$.kpis[{index}].assumption_ids", "assumption ID", errors)
        for assumption_id in linked_assumptions if isinstance(linked_assumptions, list) else []:
            if assumption_id in assumptions and assumptions[assumption_id].get("status") == "rejected":
                errors.append(f"$.kpis[{index}]: KPI relies on rejected assumption {assumption_id!r}")
        if kpi.get("recommended_core") is True and kpi.get("evidence_status") == "unverified" and not _has_exception(
            kpi_id, exceptions, "kpi"
        ):
            errors.append(f"$.kpis[{index}]: unverified recommended-core KPI requires a linked exception")

    for objective_id in sorted(active_objective_ids):
        outcome_kpis = [
            item
            for item in kpi_records
            if item.get("role") == "outcome" and objective_id in item.get("objective_ids", [])
        ]
        if not outcome_kpis and not _has_exception(objective_id, exceptions, "kpi"):
            errors.append(f"$.objectives[{objective_id!r}]: active objective has no outcome KPI or linked exception")
        core_kpis = [
            item
            for item in kpi_records
            if item.get("recommended_core") is True and objective_id in item.get("objective_ids", [])
        ]
        if not core_kpis and not _has_exception(objective_id, exceptions, "kpi"):
            errors.append(f"$.objectives[{objective_id!r}]: active objective has no recommended-core KPI or linked exception")

    for index, dimension in enumerate(_records(data, "dimensions")):
        dimension_id = str(dimension.get("dimension_id", ""))
        linked_kpis = set(dimension.get("kpi_ids", [])) if isinstance(dimension.get("kpi_ids"), list) else set()
        _require_refs(list(linked_kpis), kpi_ids, f"$.dimensions[{index}].kpi_ids", "KPI ID", errors)
        if linked_kpis != kpi_dimension_links.get(dimension_id, set()):
            errors.append(
                f"$.dimensions[{index}].kpi_ids: bidirectional KPI links do not match KPI segmentation references"
            )
        if dimension.get("sensitivity_review") == "prohibited":
            errors.append(f"$.dimensions[{index}]: prohibited dimension cannot be recommended")

    for index, requirement in enumerate(_records(data, "measurement_requirements")):
        requirement_id = str(requirement.get("requirement_id", ""))
        linked_kpis = set(requirement.get("kpi_ids", [])) if isinstance(requirement.get("kpi_ids"), list) else set()
        _require_refs(list(linked_kpis), kpi_ids, f"$.measurement_requirements[{index}].kpi_ids", "KPI ID", errors)
        if linked_kpis != component_requirement_links.get(requirement_id, set()):
            errors.append(
                f"$.measurement_requirements[{index}].kpi_ids: bidirectional KPI links do not match formula component references"
            )
        _require_refs(
            requirement.get("journey_ids", []),
            journey_ids,
            f"$.measurement_requirements[{index}].journey_ids",
            "journey ID",
            errors,
        )
        _require_refs(
            requirement.get("dimension_ids", []),
            dimension_ids,
            f"$.measurement_requirements[{index}].dimension_ids",
            "dimension ID",
            errors,
        )
        if requirement.get("collection_mode") == "unknown" and not _has_exception(
            requirement_id, exceptions, "measurement_requirement"
        ):
            errors.append(f"$.measurement_requirements[{index}]: unknown collection mode requires a linked exception")

    alignment_records = _records(data, "alignment")
    alignment_ids: set[str] = set()
    for index, item in enumerate(alignment_records):
        requirement_id = item.get("requirement_id")
        if requirement_id not in requirement_ids:
            errors.append(f"$.alignment[{index}].requirement_id: unknown measurement requirement {requirement_id!r}")
        if requirement_id in alignment_ids:
            errors.append(f"$.alignment[{index}].requirement_id: duplicate alignment row for {requirement_id!r}")
        if isinstance(requirement_id, str):
            alignment_ids.add(requirement_id)
        gaps = item.get("gaps", [])
        if item.get("status") == "covered" and gaps:
            errors.append(f"$.alignment[{index}]: covered alignment must not retain gaps")
        if item.get("status") in {"partial", "missing", "not_assessable"} and not gaps:
            errors.append(f"$.alignment[{index}]: {item.get('status')} alignment requires at least one gap")

    has_current_tracking = any(source.get("source_type") == "current_tracking" for source in sources.values())
    if has_current_tracking:
        missing_alignment = requirement_ids - alignment_ids
        extra_alignment = alignment_ids - requirement_ids
        if missing_alignment:
            errors.append(f"$.alignment: current tracking supplied but requirements lack alignment: {sorted(missing_alignment)}")
        if extra_alignment:
            errors.append(f"$.alignment: alignment contains unknown requirements: {sorted(extra_alignment)}")
    elif alignment_records:
        errors.append("$.alignment: alignment rows require a declared current_tracking source")
    if _records(data, "unlinked_measurements") and not has_current_tracking:
        errors.append("$.unlinked_measurements: rows require a declared current_tracking source")

    for index, assumption in enumerate(_records(data, "assumptions")):
        _require_refs(
            assumption.get("affected_ids", []),
            known_ids,
            f"$.assumptions[{index}].affected_ids",
            "affected ID",
            errors,
        )
        assumption_id = str(assumption.get("assumption_id", ""))
        if assumption.get("status") == "open" and not _has_exception(assumption_id, exceptions):
            errors.append(f"$.assumptions[{index}]: open assumption requires a linked exception")

    for index, exception in enumerate(_records(data, "exceptions")):
        _require_refs(
            exception.get("affected_ids", []),
            known_ids,
            f"$.exceptions[{index}].affected_ids",
            "affected ID",
            errors,
        )

    quality_gates = data.get("quality_gates", {})
    referenced_exception_ids: set[str] = set()
    component_statuses: list[str] = []
    gate_order = [
        "journey_completeness",
        "journey_appropriateness",
        "objective_completeness",
        "objective_appropriateness",
        "kpi_completeness",
        "kpi_appropriateness",
        "requirement_traceability",
    ]
    if isinstance(quality_gates, dict):
        for gate_name in gate_order + ["overall"]:
            gate = quality_gates.get(gate_name)
            if not isinstance(gate, dict):
                continue
            status = gate.get("status")
            exception_refs = gate.get("exception_ids", [])
            _require_refs(
                exception_refs,
                exception_ids,
                f"$.quality_gates.{gate_name}.exception_ids",
                "exception ID",
                errors,
            )
            if isinstance(exception_refs, list):
                referenced_exception_ids.update(value for value in exception_refs if isinstance(value, str))
            if status == "pass" and exception_refs:
                errors.append(f"$.quality_gates.{gate_name}: pass must not cite exceptions")
            if status == "pass_with_exceptions" and not exception_refs:
                errors.append(f"$.quality_gates.{gate_name}: pass_with_exceptions requires exception_ids")
            if gate_name != "overall" and isinstance(status, str):
                component_statuses.append(status)

        stage_gate = {
            "journey": "journey_completeness",
            "objective": "objective_completeness",
            "kpi": "kpi_completeness",
            "measurement_requirement": "requirement_traceability",
            "alignment": "requirement_traceability",
        }
        overall_exception_refs = set(
            quality_gates.get("overall", {}).get("exception_ids", [])
            if isinstance(quality_gates.get("overall"), dict)
            else []
        )
        for exception_id, exception in exceptions.items():
            gate_name = stage_gate.get(str(exception.get("stage")))
            gate = quality_gates.get(gate_name, {}) if gate_name else {}
            gate_exception_refs = set(gate.get("exception_ids", [])) if isinstance(gate, dict) else set()
            if exception_id not in gate_exception_refs:
                errors.append(
                    f"$.exceptions[{exception_id!r}]: exception must be cited by its stage gate {gate_name!r}"
                )
            if exception_id not in overall_exception_refs:
                errors.append(f"$.exceptions[{exception_id!r}]: exception must be cited by the overall gate")

        severity = {"pass": 0, "pass_with_exceptions": 1, "fail": 2}
        if component_statuses and isinstance(quality_gates.get("overall"), dict):
            expected = max(component_statuses, key=lambda value: severity.get(value, -1))
            actual = quality_gates["overall"].get("status")
            if actual != expected:
                errors.append(f"$.quality_gates.overall.status: expected {expected!r} from component gates, got {actual!r}")
            if delivery and actual == "fail":
                errors.append("$.quality_gates.overall.status: delivery cannot be marked complete while overall is fail")

    for exception_id in sorted(exception_ids - referenced_exception_ids):
        errors.append(f"$.exceptions[{exception_id!r}]: exception is not cited by any quality gate")

    return sorted(set(errors))


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("framework", type=Path, help="Canonical measurement-framework JSON")
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA, help="Override JSON Schema path")
    parser.add_argument("--delivery", action="store_true", help="Reject an overall fail gate for final delivery")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Emit a JSON validation report")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    try:
        with args.framework.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        errors = [f"{args.framework}: {exc}"]
    else:
        errors = validate_framework(data, args.schema, delivery=args.delivery)

    if args.json_output:
        print(json.dumps({"valid": not errors, "errors": errors}, indent=2, ensure_ascii=False))
    elif errors:
        print(f"INVALID: {len(errors)} error(s)")
        for error in errors:
            print(f"- {error}")
    else:
        print("VALID: measurement framework is structurally and traceably closed")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
