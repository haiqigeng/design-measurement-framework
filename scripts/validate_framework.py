#!/usr/bin/env python3
"""Validate a design-measurement-framework canonical JSON artifact."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from formula_contract import (
    review_advisories,
    uses_v1_2_contract,
    validate_structured_formula,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = ROOT / "schemas" / "measurement-framework.schema.json"

CURRENT_ALIGNMENT_ROLES = {"current_implementation", "data_usage"}
INCOMPLETE_JOURNEY_STATUSES = {"partial", "not_tested", "externally_blocked"}
GATE_ORDER = (
    "journey_completeness",
    "journey_appropriateness",
    "objective_completeness",
    "objective_appropriateness",
    "kpi_completeness",
    "kpi_appropriateness",
    "requirement_traceability",
)
DEFAULT_STAGE_GATES = {
    "journey": {"journey_completeness"},
    "objective": {"objective_completeness"},
    "kpi": {"kpi_completeness"},
    "measurement_requirement": {"requirement_traceability"},
    "alignment": {"requirement_traceability"},
}
APPLICABILITY_KEYS = (
    "target_sites",
    "products",
    "markets",
    "audiences",
    "states",
    "journey_variant_ids",
)


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
            errors.append(
                f"{path}: duplicate global ID {value!r}; first declared at {registry[value]}"
            )
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
            path = (
                f"$.{collection}[{parent_index}].{nested_key}[{nested_index}].{id_key}"
            )
            if value in registry:
                errors.append(
                    f"{path}: duplicate global ID {value!r}; first declared at {registry[value]}"
                )
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
            if key in {"evidence_refs", "current_measurement_refs"} and isinstance(
                value, list
            ):
                for index, ref in enumerate(value):
                    if not isinstance(ref, str):
                        continue
                    prefix = ref.split("#", 1)[0]
                    if prefix not in source_ids:
                        errors.append(
                            f"{child_path}[{index}]: evidence source {prefix!r} is not declared"
                        )
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
        entity_id in item.get("affected_ids", [])
        and (stage is None or item.get("stage") == stage)
        for item in exceptions.values()
    )


def _active_objective(record: dict[str, Any]) -> bool:
    return record.get("status") in {"confirmed", "hypothesis"}


def _source_prefix(reference: Any) -> str | None:
    if not isinstance(reference, str) or not reference:
        return None
    return reference.split("#", 1)[0]


def _is_current_alignment_source(source: dict[str, Any]) -> bool:
    return (
        source.get("source_type") != "previous_framework"
        and source.get("evidence_role") in CURRENT_ALIGNMENT_ROLES
        and source.get("state") in {"as_is", "both"}
    )


def _exception_gate_names(exception: dict[str, Any]) -> set[str]:
    explicit = exception.get("gate_ids")
    if isinstance(explicit, list) and explicit:
        return {value for value in explicit if isinstance(value, str)}
    return set(DEFAULT_STAGE_GATES.get(str(exception.get("stage")), set()))


def _has_gate_exception(
    entity_ids: set[str],
    exceptions: dict[str, dict[str, Any]],
    stage: str,
    gate_name: str,
) -> bool:
    return any(
        exception.get("stage") == stage
        and bool(entity_ids & set(exception.get("affected_ids", [])))
        and gate_name in _exception_gate_names(exception)
        for exception in exceptions.values()
    )


def _validate_applicability(
    record: dict[str, Any],
    path: str,
    document: dict[str, Any],
    variant_ids: set[str],
    errors: list[str],
) -> None:
    applicability = record.get("applicability")
    if not isinstance(applicability, dict):
        return

    scoped_values = {
        "target_sites": set(document.get("target_sites", []))
        if isinstance(document.get("target_sites"), list)
        else set(),
        "products": set(document.get("products", []))
        if isinstance(document.get("products"), list)
        else set(),
        "markets": set(document.get("markets", []))
        if isinstance(document.get("markets"), list)
        else set(),
        "audiences": set(document.get("audiences", []))
        if isinstance(document.get("audiences"), list)
        else set(),
    }
    for key, declared_scope in scoped_values.items():
        values = applicability.get(key, [])
        if not isinstance(values, list) or not values:
            continue
        if not declared_scope:
            errors.append(
                f"{path}.applicability.{key}: values require a corresponding document.{key} scope declaration"
            )
            continue
        outside = sorted(
            value
            for value in values
            if isinstance(value, str) and value not in declared_scope
        )
        if outside:
            errors.append(
                f"{path}.applicability.{key}: values fall outside document scope: {outside}"
            )

    allowed_states = {
        "as_is": {"as_is"},
        "to_be": {"to_be"},
        "hybrid": {"as_is", "to_be"},
    }.get(document.get("target_state"), set())
    states = applicability.get("states", [])
    if isinstance(states, list) and allowed_states:
        outside_states = sorted(
            value
            for value in states
            if isinstance(value, str) and value not in allowed_states
        )
        if outside_states:
            errors.append(
                f"{path}.applicability.states: states conflict with document target state: {outside_states}"
            )

    _require_refs(
        applicability.get("journey_variant_ids", []),
        variant_ids,
        f"{path}.applicability.journey_variant_ids",
        "journey variant ID",
        errors,
    )


def _applicability_overlaps(left: dict[str, Any], right: dict[str, Any]) -> bool:
    """Return True when two applicability declarations can describe the same scope."""

    for key in APPLICABILITY_KEYS:
        left_values = left.get(key, [])
        right_values = right.get(key, [])
        left_set = (
            {value for value in left_values if isinstance(value, str)}
            if isinstance(left_values, list)
            else set()
        )
        right_set = (
            {value for value in right_values if isinstance(value, str)}
            if isinstance(right_values, list)
            else set()
        )
        if left_set and right_set and left_set.isdisjoint(right_set):
            return False
    return True


@dataclass(frozen=True)
class FrameworkIndex:
    registry: dict[str, str]
    sources: dict[str, dict[str, Any]]
    journeys: dict[str, dict[str, Any]]
    objectives: dict[str, dict[str, Any]]
    kpis: dict[str, dict[str, Any]]
    dimensions: dict[str, dict[str, Any]]
    requirements: dict[str, dict[str, Any]]
    assumptions: dict[str, dict[str, Any]]
    exceptions: dict[str, dict[str, Any]]
    journey_records: list[dict[str, Any]]
    kpi_records: list[dict[str, Any]]
    variant_ids: set[str]


@dataclass(frozen=True)
class KpiLinks:
    requirement_kpis: dict[str, set[str]]
    dimension_kpis: dict[str, set[str]]


def _index_framework(data: dict[str, Any], errors: list[str]) -> FrameworkIndex:
    registry: dict[str, str] = {}
    sources = _register_ids(
        _records(data, "sources"), "source_id", "sources", registry, errors
    )
    _register_ids(
        _records(data, "discovery_candidates"),
        "candidate_id",
        "discovery_candidates",
        registry,
        errors,
    )
    journeys = _register_ids(
        _records(data, "journeys"), "journey_id", "journeys", registry, errors
    )
    _register_ids(
        _records(data, "objective_considerations"),
        "consideration_id",
        "objective_considerations",
        registry,
        errors,
    )
    objectives = _register_ids(
        _records(data, "objectives"), "objective_id", "objectives", registry, errors
    )
    _register_ids(
        _records(data, "kpi_considerations"),
        "consideration_id",
        "kpi_considerations",
        registry,
        errors,
    )
    kpis = _register_ids(_records(data, "kpis"), "kpi_id", "kpis", registry, errors)
    dimensions = _register_ids(
        _records(data, "dimensions"), "dimension_id", "dimensions", registry, errors
    )
    requirements = _register_ids(
        _records(data, "measurement_requirements"),
        "requirement_id",
        "measurement_requirements",
        registry,
        errors,
    )
    assumptions = _register_ids(
        _records(data, "assumptions"), "assumption_id", "assumptions", registry, errors
    )
    exceptions = _register_ids(
        _records(data, "exceptions"), "exception_id", "exceptions", registry, errors
    )

    journey_records = _records(data, "journeys")
    kpi_records = _records(data, "kpis")
    _add_nested_ids(journey_records, "journeys", "steps", "step_id", registry, errors)
    _add_nested_ids(
        journey_records, "journeys", "variants", "variant_id", registry, errors
    )
    variant_ids = {
        str(variant.get("variant_id"))
        for journey in journey_records
        for variant in journey.get("variants", [])
        if isinstance(variant, dict) and isinstance(variant.get("variant_id"), str)
    }
    for kpi_index, kpi in enumerate(kpi_records):
        components = (
            kpi.get("formula", {}).get("components", [])
            if isinstance(kpi.get("formula"), dict)
            else []
        )
        if not isinstance(components, list):
            continue
        for component_index, component in enumerate(components):
            if not isinstance(component, dict):
                continue
            value = component.get("component_id")
            if not isinstance(value, str) or not value:
                continue
            path = f"$.kpis[{kpi_index}].formula.components[{component_index}].component_id"
            if value in registry:
                errors.append(
                    f"{path}: duplicate global ID {value!r}; first declared at {registry[value]}"
                )
            else:
                registry[value] = path

    return FrameworkIndex(
        registry=registry,
        sources=sources,
        journeys=journeys,
        objectives=objectives,
        kpis=kpis,
        dimensions=dimensions,
        requirements=requirements,
        assumptions=assumptions,
        exceptions=exceptions,
        journey_records=journey_records,
        kpi_records=kpi_records,
        variant_ids=variant_ids,
    )


def _validate_evidence_and_applicability(
    data: dict[str, Any], index: FrameworkIndex, errors: list[str]
) -> None:
    _walk_evidence_refs(data, set(index.sources), errors)
    document = (
        data.get("document", {}) if isinstance(data.get("document"), dict) else {}
    )
    applicable_collections = (
        ("journeys", index.journey_records),
        ("objectives", _records(data, "objectives")),
        ("kpis", index.kpi_records),
        ("dimensions", _records(data, "dimensions")),
        ("measurement_requirements", _records(data, "measurement_requirements")),
    )
    for collection_name, records in applicable_collections:
        for record_index, record in enumerate(records):
            _validate_applicability(
                record,
                f"$.{collection_name}[{record_index}]",
                document,
                index.variant_ids,
                errors,
            )


def _validate_journey_layer(
    data: dict[str, Any], index: FrameworkIndex, errors: list[str]
) -> set[str]:
    journey_ids = set(index.journeys)
    for candidate_index, candidate in enumerate(_records(data, "discovery_candidates")):
        candidate_id = candidate.get("candidate_id", "")
        resolution = candidate.get("resolution")
        linked = candidate.get("journey_ids", [])
        _require_refs(
            linked,
            journey_ids,
            f"$.discovery_candidates[{candidate_index}].journey_ids",
            "journey ID",
            errors,
        )
        if resolution in {"mapped", "merged"} and not linked:
            errors.append(
                f"$.discovery_candidates[{candidate_index}]: {resolution} requires at least one journey_id"
            )
        if resolution == "excluded" and linked:
            errors.append(
                f"$.discovery_candidates[{candidate_index}]: excluded candidate must not retain journey_ids"
            )
        if resolution == "unresolved" and not _has_exception(
            str(candidate_id), index.exceptions, "journey"
        ):
            errors.append(
                f"$.discovery_candidates[{candidate_index}]: unresolved candidate requires a linked exception"
            )

    material_journey_ids: set[str] = set()
    for journey_index, journey in enumerate(index.journey_records):
        journey_id = str(journey.get("journey_id", ""))
        if journey.get("material") is True:
            material_journey_ids.add(journey_id)
            if journey.get(
                "status"
            ) in INCOMPLETE_JOURNEY_STATUSES and not _has_exception(
                journey_id, index.exceptions, "journey"
            ):
                errors.append(
                    f"$.journeys[{journey_index}]: material journey with status "
                    f"{journey.get('status')!r} requires a linked exception"
                )
        steps = journey.get("steps", [])
        if journey.get("material") is True and uses_v1_2_contract(data):
            represented_states = {
                step.get("state")
                for step in steps
                if isinstance(steps, list) and isinstance(step, dict)
            }
            closure_gaps: list[str] = []
            if not journey.get("entry_points"):
                closure_gaps.append("a declared entry point")
            if "entry" not in represented_states:
                closure_gaps.append("an entry-state step")
            if "success" not in represented_states:
                closure_gaps.append("a success-state step")
            if closure_gaps and not _has_exception(
                journey_id, index.exceptions, "journey"
            ):
                errors.append(
                    f"$.journeys[{journey_index}]: material journey requires "
                    + ", ".join(closure_gaps)
                    + " or a linked journey exception"
                )
        for step_index, step in enumerate(steps if isinstance(steps, list) else []):
            if not isinstance(step, dict):
                continue
            if (
                journey.get("material") is True
                and step.get("status") in INCOMPLETE_JOURNEY_STATUSES
                and journey.get("status") not in INCOMPLETE_JOURNEY_STATUSES
            ):
                errors.append(
                    f"$.journeys[{journey_index}].steps[{step_index}]: incomplete step status "
                    "must be reflected by the parent material journey status"
                )

        variants = journey.get("variants", [])
        for variant_index, variant in enumerate(
            variants if isinstance(variants, list) else []
        ):
            if not isinstance(variant, dict) or variant.get("material") is not True:
                continue
            variant_id = str(variant.get("variant_id", ""))
            if not variant.get("states_covered"):
                errors.append(
                    f"$.journeys[{journey_index}].variants[{variant_index}]: "
                    "material variant requires at least one covered state"
                )
            if variant.get(
                "status"
            ) in INCOMPLETE_JOURNEY_STATUSES and not _has_exception(
                variant_id, index.exceptions, "journey"
            ):
                errors.append(
                    f"$.journeys[{journey_index}].variants[{variant_index}]: "
                    f"material variant with status {variant.get('status')!r} "
                    "requires a linked exception"
                )
    return material_journey_ids


def _validate_objective_layer(
    data: dict[str, Any],
    index: FrameworkIndex,
    material_journey_ids: set[str],
    errors: list[str],
) -> set[str]:
    required_lenses = {"value_stream", "lifecycle", "stakeholder", "risk_guardrail"}
    present_lenses = {
        str(item.get("lens"))
        for item in _records(data, "objective_considerations")
        if item.get("lens")
    }
    for lens in sorted(required_lenses - present_lenses):
        errors.append(
            f"$.objective_considerations: missing required {lens!r} sweep decision"
        )

    objective_ids = set(index.objectives)
    for consideration_index, item in enumerate(
        _records(data, "objective_considerations")
    ):
        consideration_id = str(item.get("consideration_id", ""))
        linked = item.get("objective_ids", [])
        _require_refs(
            linked,
            objective_ids,
            f"$.objective_considerations[{consideration_index}].objective_ids",
            "objective ID",
            errors,
        )
        resolution = item.get("resolution")
        if resolution in {"objective_proposed", "covered_by_existing"} and not linked:
            errors.append(
                f"$.objective_considerations[{consideration_index}]: "
                f"{resolution} requires objective_ids"
            )
        if resolution in {"none_with_reason", "out_of_scope"} and linked:
            errors.append(
                f"$.objective_considerations[{consideration_index}]: "
                f"{resolution} must not retain objective_ids"
            )
        if resolution == "unresolved" and not _has_exception(
            consideration_id, index.exceptions, "objective"
        ):
            errors.append(
                f"$.objective_considerations[{consideration_index}]: "
                "unresolved consideration requires a linked exception"
            )

    active_objective_ids = {
        key for key, value in index.objectives.items() if _active_objective(value)
    }
    objective_journeys: dict[str, set[str]] = {}
    value_streams: dict[str, list[dict[str, Any]]] = {}
    for objective_index, objective in enumerate(_records(data, "objectives")):
        objective_id = str(objective.get("objective_id", ""))
        linked_journeys = (
            set(objective.get("journey_ids", []))
            if isinstance(objective.get("journey_ids"), list)
            else set()
        )
        objective_journeys[objective_id] = linked_journeys
        _require_refs(
            list(linked_journeys),
            set(index.journeys),
            f"$.objectives[{objective_index}].journey_ids",
            "journey ID",
            errors,
        )
        if _active_objective(objective):
            value_streams.setdefault(str(objective.get("value_stream", "")), []).append(
                objective
            )

    for journey_id in sorted(material_journey_ids):
        if not any(
            journey_id in objective_journeys.get(objective_id, set())
            for objective_id in active_objective_ids
        ):
            errors.append(
                f"$.journeys[{journey_id!r}]: material journey has no active objective link"
            )

    for value_stream, records in value_streams.items():
        if value_stream and not any(
            record.get("priority") == "primary" for record in records
        ):
            errors.append(
                f"$.objectives: active value stream {value_stream!r} has no primary objective"
            )
    return active_objective_ids


def _validate_kpi_considerations(
    data: dict[str, Any],
    index: FrameworkIndex,
    active_objective_ids: set[str],
    material_journey_ids: set[str],
    errors: list[str],
) -> None:
    objective_ids = set(index.objectives)
    journey_ids = set(index.journeys)
    kpi_ids = set(index.kpis)
    consideration_records = _records(data, "kpi_considerations")
    for consideration_index, item in enumerate(consideration_records):
        consideration_id = str(item.get("consideration_id", ""))
        scope_type = item.get("scope_type")
        scope_id = item.get("scope_id")
        if scope_type == "objective" and scope_id not in objective_ids:
            errors.append(
                f"$.kpi_considerations[{consideration_index}].scope_id: "
                f"unknown objective ID {scope_id!r}"
            )
        if scope_type == "journey" and scope_id not in journey_ids:
            errors.append(
                f"$.kpi_considerations[{consideration_index}].scope_id: "
                f"unknown journey ID {scope_id!r}"
            )
        linked = item.get("kpi_ids", [])
        _require_refs(
            linked,
            kpi_ids,
            f"$.kpi_considerations[{consideration_index}].kpi_ids",
            "KPI ID",
            errors,
        )
        resolution = item.get("resolution")
        if resolution in {"kpi_proposed", "covered_by_existing"} and not linked:
            errors.append(
                f"$.kpi_considerations[{consideration_index}]: "
                f"{resolution} requires kpi_ids"
            )
        if resolution in {"none_with_reason", "not_applicable"} and linked:
            errors.append(
                f"$.kpi_considerations[{consideration_index}]: "
                f"{resolution} must not retain kpi_ids"
            )
        if resolution == "unresolved" and not _has_exception(
            consideration_id, index.exceptions, "kpi"
        ):
            errors.append(
                f"$.kpi_considerations[{consideration_index}]: "
                "unresolved consideration requires a linked exception"
            )
        if scope_type == "objective" and item.get("role") in {
            "outcome",
            "driver",
            "guardrail",
        }:
            expected_role = item.get("role")
            for kpi_id in linked if isinstance(linked, list) else []:
                if (
                    kpi_id in index.kpis
                    and index.kpis[kpi_id].get("role") != expected_role
                ):
                    errors.append(
                        f"$.kpi_considerations[{consideration_index}].kpi_ids: "
                        f"{expected_role!r} consideration references KPI {kpi_id!r} "
                        f"with role {index.kpis[kpi_id].get('role')!r}"
                    )

    for objective_id in sorted(active_objective_ids):
        roles = {
            item.get("role")
            for item in consideration_records
            if item.get("scope_type") == "objective"
            and item.get("scope_id") == objective_id
        }
        for role in sorted({"outcome", "driver", "guardrail"} - roles):
            errors.append(
                f"$.kpi_considerations: objective {objective_id!r} "
                f"lacks required {role!r} consideration"
            )
    for journey_id in sorted(material_journey_ids):
        roles = {
            item.get("role")
            for item in consideration_records
            if item.get("scope_type") == "journey"
            and item.get("scope_id") == journey_id
        }
        for role in sorted({"completion", "step_conversion", "friction"} - roles):
            errors.append(
                f"$.kpi_considerations: journey {journey_id!r} "
                f"lacks required {role!r} consideration"
            )


def _validate_kpi_records(
    data: dict[str, Any], index: FrameworkIndex, errors: list[str]
) -> KpiLinks:
    objective_ids = set(index.objectives)
    journey_ids = set(index.journeys)
    dimension_ids = set(index.dimensions)
    requirement_ids = set(index.requirements)
    assumption_ids = set(index.assumptions)
    requirement_kpis: dict[str, set[str]] = {
        requirement_id: set() for requirement_id in requirement_ids
    }
    dimension_kpis: dict[str, set[str]] = {
        dimension_id: set() for dimension_id in dimension_ids
    }

    for kpi_index, kpi in enumerate(index.kpi_records):
        kpi_id = str(kpi.get("kpi_id", ""))
        role = kpi.get("role")
        tier = kpi.get("tier")
        if tier == "north_star" and role != "outcome":
            errors.append(f"$.kpis[{kpi_index}]: north_star tier requires outcome role")
        if tier == "guardrail" and role != "guardrail":
            errors.append(
                f"$.kpis[{kpi_index}]: guardrail tier requires guardrail role"
            )
        if role == "guardrail" and tier != "guardrail":
            errors.append(
                f"$.kpis[{kpi_index}]: guardrail role requires guardrail tier"
            )
        if tier == "diagnostic" and role != "diagnostic":
            errors.append(
                f"$.kpis[{kpi_index}]: diagnostic tier requires diagnostic role"
            )
        if role == "diagnostic" and tier != "diagnostic":
            errors.append(
                f"$.kpis[{kpi_index}]: diagnostic role requires diagnostic tier"
            )

        linked_objectives = kpi.get("objective_ids", [])
        _require_refs(
            linked_objectives,
            objective_ids,
            f"$.kpis[{kpi_index}].objective_ids",
            "objective ID",
            errors,
        )
        primary = kpi.get("primary_objective_id")
        if primary not in objective_ids:
            errors.append(
                f"$.kpis[{kpi_index}].primary_objective_id: unknown objective ID {primary!r}"
            )
        elif primary not in linked_objectives:
            errors.append(
                f"$.kpis[{kpi_index}]: primary_objective_id must also appear in objective_ids"
            )
        elif not _active_objective(index.objectives[primary]):
            errors.append(
                f"$.kpis[{kpi_index}]: primary objective {primary!r} is not active"
            )
        _require_refs(
            kpi.get("journey_ids", []),
            journey_ids,
            f"$.kpis[{kpi_index}].journey_ids",
            "journey ID",
            errors,
        )

        segmentation = kpi.get("segmentation", {})
        linked_dimensions = (
            segmentation.get("dimension_ids", [])
            if isinstance(segmentation, dict)
            else []
        )
        _require_refs(
            linked_dimensions,
            dimension_ids,
            f"$.kpis[{kpi_index}].segmentation.dimension_ids",
            "dimension ID",
            errors,
        )
        for dimension_id in linked_dimensions:
            if dimension_id in dimension_kpis:
                dimension_kpis[dimension_id].add(kpi_id)

        formula = kpi.get("formula", {})
        if uses_v1_2_contract(data):
            errors.extend(validate_structured_formula(kpi, kpi_index))
        components = formula.get("components", []) if isinstance(formula, dict) else []
        for component_index, component in enumerate(
            components if isinstance(components, list) else []
        ):
            if not isinstance(component, dict):
                continue
            linked_requirements = component.get("requirement_ids", [])
            _require_refs(
                linked_requirements,
                requirement_ids,
                f"$.kpis[{kpi_index}].formula.components[{component_index}].requirement_ids",
                "measurement requirement ID",
                errors,
            )
            for requirement_id in linked_requirements:
                if requirement_id in requirement_kpis:
                    requirement_kpis[requirement_id].add(kpi_id)

        linked_assumptions = kpi.get("assumption_ids", [])
        _require_refs(
            linked_assumptions,
            assumption_ids,
            f"$.kpis[{kpi_index}].assumption_ids",
            "assumption ID",
            errors,
        )
        for assumption_id in (
            linked_assumptions if isinstance(linked_assumptions, list) else []
        ):
            if (
                assumption_id in index.assumptions
                and index.assumptions[assumption_id].get("status") == "rejected"
            ):
                errors.append(
                    f"$.kpis[{kpi_index}]: KPI relies on rejected assumption {assumption_id!r}"
                )
        if (
            kpi.get("recommended_core") is True
            and kpi.get("evidence_status") == "unverified"
            and not _has_exception(kpi_id, index.exceptions, "kpi")
        ):
            errors.append(
                f"$.kpis[{kpi_index}]: unverified recommended-core KPI requires a linked exception"
            )
    return KpiLinks(requirement_kpis=requirement_kpis, dimension_kpis=dimension_kpis)


def _validate_kpi_selection(
    data: dict[str, Any],
    index: FrameworkIndex,
    active_objective_ids: set[str],
    errors: list[str],
) -> None:
    north_stars = [
        item for item in index.kpi_records if item.get("tier") == "north_star"
    ]
    if len(north_stars) > 1:
        for item in north_stars:
            kpi_id = str(item.get("kpi_id", ""))
            if not isinstance(item.get("applicability"), dict):
                errors.append(
                    f"$.kpis[{kpi_id!r}]: multiple North Stars require explicit applicability"
                )
            if (
                not isinstance(item.get("north_star_rationale"), str)
                or not item.get("north_star_rationale", "").strip()
            ):
                errors.append(
                    f"$.kpis[{kpi_id!r}]: multiple North Stars require north_star_rationale"
                )
        for left_index, left in enumerate(north_stars):
            left_scope = left.get("applicability")
            if not isinstance(left_scope, dict):
                continue
            for right in north_stars[left_index + 1 :]:
                right_scope = right.get("applicability")
                if isinstance(right_scope, dict) and _applicability_overlaps(
                    left_scope, right_scope
                ):
                    errors.append(
                        f"$.kpis: North Stars {left.get('kpi_id')!r} and "
                        f"{right.get('kpi_id')!r} have overlapping applicability"
                    )

    for objective_id in sorted(active_objective_ids):
        outcome_kpis = [
            item
            for item in index.kpi_records
            if item.get("role") == "outcome"
            and objective_id in item.get("objective_ids", [])
        ]
        if not outcome_kpis and not _has_exception(
            objective_id, index.exceptions, "kpi"
        ):
            errors.append(
                f"$.objectives[{objective_id!r}]: active objective has no outcome KPI or linked exception"
            )
    core_kpis = [
        item for item in index.kpi_records if item.get("recommended_core") is True
    ]
    if (
        active_objective_ids
        and not core_kpis
        and not all(
            _has_exception(objective_id, index.exceptions, "kpi")
            for objective_id in active_objective_ids
        )
    ):
        errors.append(
            "$.kpis: framework has no recommended-core KPI or complete set of linked objective exceptions"
        )
    if core_kpis and not any(item.get("role") == "outcome" for item in core_kpis):
        errors.append("$.kpis: recommended core must include at least one outcome KPI")

    if not uses_v1_2_contract(data):
        return

    objective_guardrail_considerations: dict[str, list[dict[str, Any]]] = {}
    for consideration in _records(data, "kpi_considerations"):
        if (
            consideration.get("scope_type") == "objective"
            and consideration.get("role") == "guardrail"
            and consideration.get("resolution")
            in {"kpi_proposed", "covered_by_existing"}
        ):
            objective_guardrail_considerations.setdefault(
                str(consideration.get("scope_id", "")), []
            ).append(consideration)

    for objective_id in sorted(active_objective_ids):
        core_growth_kpis = [
            item
            for item in core_kpis
            if item.get("role") in {"outcome", "driver"}
            and objective_id in item.get("objective_ids", [])
        ]
        relevant_considerations = objective_guardrail_considerations.get(
            objective_id, []
        )
        if not core_growth_kpis or not relevant_considerations:
            continue

        cited_guardrail_ids = {
            kpi_id
            for consideration in relevant_considerations
            for kpi_id in consideration.get("kpi_ids", [])
            if isinstance(kpi_id, str)
        }
        core_guardrail_ids = {
            kpi_id
            for kpi_id in cited_guardrail_ids
            if kpi_id in index.kpis
            and index.kpis[kpi_id].get("role") == "guardrail"
            and index.kpis[kpi_id].get("recommended_core") is True
            and objective_id in index.kpis[kpi_id].get("objective_ids", [])
        }
        if core_guardrail_ids:
            continue

        exception_targets = {
            objective_id,
            *(
                str(item.get("consideration_id", ""))
                for item in relevant_considerations
            ),
            *(str(item.get("kpi_id", "")) for item in core_growth_kpis),
            *cited_guardrail_ids,
        }
        if _has_gate_exception(
            exception_targets,
            index.exceptions,
            "kpi",
            "kpi_appropriateness",
        ):
            continue
        errors.append(
            f"$.objectives[{objective_id!r}]: recommended-core outcome or driver "
            "KPIs have a proposed guardrail, but no cited guardrail KPI is in the "
            "recommended core and no KPI-appropriateness exception is linked"
        )


def _validate_requirement_layer(
    data: dict[str, Any],
    index: FrameworkIndex,
    kpi_links: KpiLinks,
    errors: list[str],
) -> None:
    kpi_ids = set(index.kpis)
    journey_ids = set(index.journeys)
    dimension_ids = set(index.dimensions)
    dimension_requirement_links: dict[str, set[str]] = {
        dimension_id: set() for dimension_id in dimension_ids
    }
    for requirement in _records(data, "measurement_requirements"):
        linked_kpis = requirement.get("kpi_ids", [])
        linked_dimensions = requirement.get("dimension_ids", [])
        if not isinstance(linked_kpis, list) or not isinstance(linked_dimensions, list):
            continue
        for dimension_id in linked_dimensions:
            if dimension_id in dimension_requirement_links:
                dimension_requirement_links[dimension_id].update(
                    kpi_id for kpi_id in linked_kpis if isinstance(kpi_id, str)
                )

    for dimension_index, dimension in enumerate(_records(data, "dimensions")):
        dimension_id = str(dimension.get("dimension_id", ""))
        linked_kpis = (
            set(dimension.get("kpi_ids", []))
            if isinstance(dimension.get("kpi_ids"), list)
            else set()
        )
        _require_refs(
            list(linked_kpis),
            kpi_ids,
            f"$.dimensions[{dimension_index}].kpi_ids",
            "KPI ID",
            errors,
        )
        if linked_kpis != kpi_links.dimension_kpis.get(dimension_id, set()):
            errors.append(
                f"$.dimensions[{dimension_index}].kpi_ids: bidirectional KPI links "
                "do not match KPI segmentation references"
            )
        missing_requirement_links = linked_kpis - dimension_requirement_links.get(
            dimension_id, set()
        )
        if missing_requirement_links:
            errors.append(
                f"$.dimensions[{dimension_index}]: dimension is not carried by a "
                f"measurement requirement for KPIs {sorted(missing_requirement_links)}"
            )
        if dimension.get("sensitivity_review") == "prohibited":
            errors.append(
                f"$.dimensions[{dimension_index}]: prohibited dimension cannot be recommended"
            )

    for requirement_index, requirement in enumerate(
        _records(data, "measurement_requirements")
    ):
        requirement_id = str(requirement.get("requirement_id", ""))
        linked_kpis = (
            set(requirement.get("kpi_ids", []))
            if isinstance(requirement.get("kpi_ids"), list)
            else set()
        )
        _require_refs(
            list(linked_kpis),
            kpi_ids,
            f"$.measurement_requirements[{requirement_index}].kpi_ids",
            "KPI ID",
            errors,
        )
        if linked_kpis != kpi_links.requirement_kpis.get(requirement_id, set()):
            errors.append(
                f"$.measurement_requirements[{requirement_index}].kpi_ids: "
                "bidirectional KPI links do not match formula component references"
            )
        _require_refs(
            requirement.get("journey_ids", []),
            journey_ids,
            f"$.measurement_requirements[{requirement_index}].journey_ids",
            "journey ID",
            errors,
        )
        _require_refs(
            requirement.get("dimension_ids", []),
            dimension_ids,
            f"$.measurement_requirements[{requirement_index}].dimension_ids",
            "dimension ID",
            errors,
        )
        linked_dimensions = (
            requirement.get("dimension_ids", [])
            if isinstance(requirement.get("dimension_ids"), list)
            else []
        )
        for dimension_id in linked_dimensions:
            if dimension_id not in index.dimensions:
                continue
            affected_kpis = set(index.dimensions[dimension_id].get("kpi_ids", []))
            if linked_kpis.isdisjoint(affected_kpis):
                errors.append(
                    f"$.measurement_requirements[{requirement_index}].dimension_ids: "
                    f"dimension {dimension_id!r} does not apply to any KPI linked "
                    "by this requirement"
                )
        if requirement.get("collection_mode") == "unknown" and not _has_exception(
            requirement_id, index.exceptions, "measurement_requirement"
        ):
            errors.append(
                f"$.measurement_requirements[{requirement_index}]: unknown collection "
                "mode requires a linked exception"
            )


def _validate_alignment_layer(
    data: dict[str, Any], index: FrameworkIndex, errors: list[str]
) -> None:
    requirement_ids = set(index.requirements)
    alignment_records = _records(data, "alignment")
    alignment_ids: set[str] = set()
    current_alignment_source_ids = {
        source_id
        for source_id, source in index.sources.items()
        if _is_current_alignment_source(source)
    }
    for alignment_index, item in enumerate(alignment_records):
        requirement_id = item.get("requirement_id")
        if requirement_id not in requirement_ids:
            errors.append(
                f"$.alignment[{alignment_index}].requirement_id: unknown measurement "
                f"requirement {requirement_id!r}"
            )
        if requirement_id in alignment_ids:
            errors.append(
                f"$.alignment[{alignment_index}].requirement_id: duplicate alignment "
                f"row for {requirement_id!r}"
            )
        if isinstance(requirement_id, str):
            alignment_ids.add(requirement_id)
        gaps = item.get("gaps", [])
        if item.get("status") == "covered" and gaps:
            errors.append(
                f"$.alignment[{alignment_index}]: covered alignment must not retain gaps"
            )
        if item.get("status") in {"partial", "missing", "not_assessable"} and not gaps:
            errors.append(
                f"$.alignment[{alignment_index}]: {item.get('status')} alignment "
                "requires at least one gap"
            )
        current_refs = item.get("current_measurement_refs", [])
        if item.get("status") in {"covered", "partial"} and not current_refs:
            errors.append(
                f"$.alignment[{alignment_index}]: {item.get('status')} alignment "
                "requires current evidence references"
            )
        for ref_index, reference in enumerate(
            current_refs if isinstance(current_refs, list) else []
        ):
            prefix = _source_prefix(reference)
            if prefix is not None and prefix not in current_alignment_source_ids:
                errors.append(
                    f"$.alignment[{alignment_index}].current_measurement_refs[{ref_index}]: "
                    f"source {prefix!r} is not current implementation or data-usage evidence"
                )

    has_current_measurement_evidence = bool(current_alignment_source_ids)
    if has_current_measurement_evidence:
        missing_alignment = requirement_ids - alignment_ids
        extra_alignment = alignment_ids - requirement_ids
        if missing_alignment:
            errors.append(
                "$.alignment: current measurement evidence supplied but requirements "
                f"lack alignment: {sorted(missing_alignment)}"
            )
        if extra_alignment:
            errors.append(
                f"$.alignment: alignment contains unknown requirements: {sorted(extra_alignment)}"
            )
    elif alignment_records:
        errors.append(
            "$.alignment: alignment rows require current implementation or data-usage "
            "evidence in an as-is state"
        )

    unlinked_records = _records(data, "unlinked_measurements")
    if unlinked_records and not has_current_measurement_evidence:
        errors.append(
            "$.unlinked_measurements: rows require current implementation or data-usage "
            "evidence in an as-is state"
        )
    for unlinked_index, item in enumerate(unlinked_records):
        evidence_refs = item.get("evidence_refs", [])
        for ref_index, reference in enumerate(
            evidence_refs if isinstance(evidence_refs, list) else []
        ):
            prefix = _source_prefix(reference)
            if prefix is not None and prefix not in current_alignment_source_ids:
                errors.append(
                    f"$.unlinked_measurements[{unlinked_index}].evidence_refs[{ref_index}]: "
                    f"source {prefix!r} is not current implementation or data-usage evidence"
                )


def _validate_assumptions_and_exceptions(
    data: dict[str, Any], index: FrameworkIndex, errors: list[str]
) -> None:
    known_ids = set(index.registry)
    for assumption_index, assumption in enumerate(_records(data, "assumptions")):
        _require_refs(
            assumption.get("affected_ids", []),
            known_ids,
            f"$.assumptions[{assumption_index}].affected_ids",
            "affected ID",
            errors,
        )
        assumption_id = str(assumption.get("assumption_id", ""))
        if assumption.get("status") == "open" and not _has_exception(
            assumption_id, index.exceptions
        ):
            errors.append(
                f"$.assumptions[{assumption_index}]: open assumption requires a linked exception"
            )

    for exception_index, exception in enumerate(_records(data, "exceptions")):
        _require_refs(
            exception.get("affected_ids", []),
            known_ids,
            f"$.exceptions[{exception_index}].affected_ids",
            "affected ID",
            errors,
        )


def _validate_quality_gates(
    data: dict[str, Any],
    index: FrameworkIndex,
    delivery: bool,
    errors: list[str],
) -> None:
    exception_ids = set(index.exceptions)
    quality_gates = data.get("quality_gates", {})
    referenced_exception_ids: set[str] = set()
    component_statuses: list[str] = []
    if isinstance(quality_gates, dict):
        for gate_name in [*GATE_ORDER, "overall"]:
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
                referenced_exception_ids.update(
                    value for value in exception_refs if isinstance(value, str)
                )
            if status == "pass" and exception_refs:
                errors.append(
                    f"$.quality_gates.{gate_name}: pass must not cite exceptions"
                )
            if status == "pass_with_exceptions" and not exception_refs:
                errors.append(
                    f"$.quality_gates.{gate_name}: pass_with_exceptions requires exception_ids"
                )
            if gate_name != "overall" and isinstance(status, str):
                component_statuses.append(status)

        overall_exception_refs = set(
            quality_gates.get("overall", {}).get("exception_ids", [])
            if isinstance(quality_gates.get("overall"), dict)
            else []
        )
        for exception_id, exception in index.exceptions.items():
            for gate_name in sorted(_exception_gate_names(exception)):
                gate = quality_gates.get(gate_name, {})
                gate_exception_refs = (
                    set(gate.get("exception_ids", []))
                    if isinstance(gate, dict)
                    else set()
                )
                if exception_id not in gate_exception_refs:
                    errors.append(
                        f"$.exceptions[{exception_id!r}]: exception must be cited by "
                        f"affected gate {gate_name!r}"
                    )
            if exception_id not in overall_exception_refs:
                errors.append(
                    f"$.exceptions[{exception_id!r}]: exception must be cited by the overall gate"
                )

        severity = {"pass": 0, "pass_with_exceptions": 1, "fail": 2}
        if component_statuses and isinstance(quality_gates.get("overall"), dict):
            expected = max(
                component_statuses, key=lambda value: severity.get(value, -1)
            )
            actual = quality_gates["overall"].get("status")
            if actual != expected:
                errors.append(
                    f"$.quality_gates.overall.status: expected {expected!r} from "
                    f"component gates, got {actual!r}"
                )
            if delivery and actual == "fail":
                errors.append(
                    "$.quality_gates.overall.status: delivery cannot be marked "
                    "complete while overall is fail"
                )

    for exception_id in sorted(exception_ids - referenced_exception_ids):
        errors.append(
            f"$.exceptions[{exception_id!r}]: exception is not cited by any quality gate"
        )


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

    index = _index_framework(data, errors)
    _validate_evidence_and_applicability(data, index, errors)

    material_journey_ids = _validate_journey_layer(data, index, errors)

    active_objective_ids = _validate_objective_layer(
        data, index, material_journey_ids, errors
    )

    _validate_kpi_considerations(
        data, index, active_objective_ids, material_journey_ids, errors
    )

    kpi_links = _validate_kpi_records(data, index, errors)
    _validate_kpi_selection(data, index, active_objective_ids, errors)

    _validate_requirement_layer(data, index, kpi_links, errors)

    _validate_alignment_layer(data, index, errors)

    _validate_assumptions_and_exceptions(data, index, errors)
    _validate_quality_gates(data, index, delivery, errors)

    return sorted(set(errors))


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "framework", type=Path, help="Canonical measurement-framework JSON"
    )
    parser.add_argument(
        "--schema", type=Path, default=DEFAULT_SCHEMA, help="Override JSON Schema path"
    )
    parser.add_argument(
        "--delivery",
        action="store_true",
        help="Reject an overall fail gate for final delivery",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Emit a JSON validation report",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    warnings: list[str] = []
    try:
        with args.framework.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        errors = [f"{args.framework}: {exc}"]
    else:
        errors = validate_framework(data, args.schema, delivery=args.delivery)
        warnings = review_advisories(data) if not errors else []

    if args.json_output:
        print(
            json.dumps(
                {"valid": not errors, "errors": errors, "warnings": warnings},
                indent=2,
                ensure_ascii=False,
            )
        )
    elif errors:
        print(f"INVALID: {len(errors)} error(s)")
        for error in errors:
            print(f"- {error}")
    else:
        print("VALID: measurement framework is structurally and traceably closed")
        if warnings:
            print(f"ADVISORIES: {len(warnings)} non-blocking review item(s)")
            for warning in warnings:
                print(f"- {warning}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
