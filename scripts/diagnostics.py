"""Shared semantic diagnostics, maturity facts, and non-blocking advisories."""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from typing import Any, Iterable
from urllib.parse import urlparse

APPLICABILITY_KEYS = (
    "target_sites",
    "products",
    "markets",
    "audiences",
    "locales",
    "states",
    "journey_variant_ids",
)
DIRECT_BEHAVIOR_SOURCE_TYPES = {"live_website", "test_website"}
DISCOVERY_EVIDENCE_ROLES = {"live_behavior", "future_design", "data_capability"}
DIRECT_SCOPE_KEYS = ("target_sites", "markets", "audiences", "locales")
JOURNEY_STATUSES = (
    "observed",
    "confirmed",
    "planned",
    "partial",
    "not_tested",
    "externally_blocked",
)
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
    "scope": {"journey_completeness"},
    "journey": {"journey_completeness"},
    "objective": {"objective_completeness"},
    "kpi": {"kpi_completeness"},
    "measurement_requirement": {"requirement_traceability"},
    "alignment": {"requirement_traceability"},
}
ALLOWED_STAGE_GATES = {
    "scope": set(GATE_ORDER),
    "journey": set(GATE_ORDER),
    "objective": {
        "objective_completeness",
        "objective_appropriateness",
        "kpi_completeness",
        "kpi_appropriateness",
        "requirement_traceability",
    },
    "kpi": {
        "kpi_completeness",
        "kpi_appropriateness",
        "requirement_traceability",
    },
    "measurement_requirement": {"requirement_traceability"},
    "alignment": {"requirement_traceability"},
}


def schema_at_least(data: dict[str, Any], version: tuple[int, int, int]) -> bool:
    value = data.get("schema_version")
    if not isinstance(value, str):
        return False
    try:
        parsed = tuple(int(part) for part in value.split("."))
    except ValueError:
        return False
    return parsed >= version


def _records(data: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = data.get(key, [])
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _source_prefix(reference: Any) -> str | None:
    if not isinstance(reference, str) or not reference:
        return None
    return reference.split("#", 1)[0]


def _string_set(value: Any) -> set[str]:
    if not isinstance(value, list):
        return set()
    return {item for item in value if isinstance(item, str)}


def _explicit_applicability_values(
    record: dict[str, Any], key: str
) -> set[str] | None:
    applicability = record.get("applicability")
    if not isinstance(applicability, dict):
        return None
    values = applicability.get(key)
    if not isinstance(values, list) or not values:
        return None
    return {value for value in values if isinstance(value, str)}


def _status_counts(records: Iterable[dict[str, Any]], key: str) -> dict[str, int]:
    counts = Counter(
        str(record.get(key)) for record in records if isinstance(record.get(key), str)
    )
    return {name: counts[name] for name in sorted(counts)}


def evidence_maturity(data: dict[str, Any]) -> dict[str, dict[str, int]]:
    journeys = _records(data, "journeys")
    variants = [
        variant
        for journey in journeys
        for variant in journey.get("variants", [])
        if isinstance(variant, dict)
    ]
    steps = [
        step
        for journey in journeys
        for step in journey.get("steps", [])
        if isinstance(step, dict)
    ]
    return {
        "journeys": _status_counts(journeys, "status"),
        "variants": _status_counts(variants, "status"),
        "steps": _status_counts(steps, "status"),
        "objectives": _status_counts(_records(data, "objectives"), "status"),
        "kpis": _status_counts(_records(data, "kpis"), "evidence_status"),
        "measurement_requirements": _status_counts(
            _records(data, "measurement_requirements"), "verification_status"
        ),
    }


def candidate_census(data: dict[str, Any]) -> dict[str, Any]:
    candidates = _records(data, "discovery_candidates")
    journeys = _records(data, "journeys")
    by_type: dict[str, Counter[str]] = defaultdict(Counter)
    journey_candidate_ids: set[str] = set()
    unresolved_material: list[str] = []
    for candidate in candidates:
        candidate_type = str(candidate.get("candidate_type", "unknown"))
        resolution = str(candidate.get("resolution", "unknown"))
        by_type[candidate_type][resolution] += 1
        by_type[candidate_type]["total"] += 1
        if candidate.get("material") is True:
            by_type[candidate_type]["material"] += 1
            if resolution == "unresolved":
                unresolved_material.append(str(candidate.get("candidate_id", "")))
        journey_candidate_ids.update(
            value
            for value in candidate.get("journey_ids", [])
            if isinstance(value, str)
        )

    state_resolutions = Counter(
        str(decision.get("resolution", "unknown"))
        for journey in journeys
        for decision in journey.get("state_decisions", [])
        if isinstance(decision, dict)
    )
    intake = data.get("intake_baseline", {})
    intake_present = isinstance(intake, dict) and schema_at_least(data, (1, 3, 0))
    targets = intake.get("targets", []) if intake_present else []
    targets_without_evidence = [
        str(target.get("target_id", ""))
        for target in targets
        if isinstance(target, dict)
        and target.get("disposition") in {"included", "canonicalized"}
        and not target.get("representative_source_ids", [])
    ]
    return {
        "candidate_total": len(candidates),
        "material_candidate_total": sum(
            1 for candidate in candidates if candidate.get("material") is True
        ),
        "by_type": {
            name: {key: values[key] for key in sorted(values)}
            for name, values in sorted(by_type.items())
        },
        "unresolved_material_candidate_ids": sorted(
            value for value in unresolved_material if value
        ),
        "journeys_without_discovery_candidates": sorted(
            str(journey.get("journey_id", ""))
            for journey in journeys
            if str(journey.get("journey_id", "")) not in journey_candidate_ids
        ),
        "intake_baseline_present": intake_present,
        "included_targets_without_representative_sources": sorted(
            value for value in targets_without_evidence if value
        ),
        "state_decision_resolutions": {
            key: state_resolutions[key] for key in sorted(state_resolutions)
        },
    }


def _document_scope(data: dict[str, Any]) -> dict[str, set[str]]:
    document = data.get("document", {})
    if not isinstance(document, dict):
        document = {}
    target_state = document.get("target_state")
    states = {
        "as_is": {"as_is"},
        "to_be": {"to_be"},
        "hybrid": {"as_is", "to_be"},
    }.get(target_state, set())
    variants = {
        str(variant.get("variant_id"))
        for journey in _records(data, "journeys")
        for variant in journey.get("variants", [])
        if isinstance(variant, dict) and isinstance(variant.get("variant_id"), str)
    }
    return {
        "target_sites": _string_set(document.get("target_sites", [])),
        "products": _string_set(document.get("products", [])),
        "markets": _string_set(document.get("markets", [])),
        "audiences": _string_set(document.get("audiences", [])),
        "locales": _string_set(document.get("locales", [])),
        "states": states,
        "journey_variant_ids": variants,
    }


def _derived_variant_scopes(
    data: dict[str, Any], document_scope: dict[str, set[str]]
) -> dict[int, set[str]]:
    """Resolve variant scope through the documented journey-link inheritance."""

    by_record: dict[int, set[str]] = {}
    journeys = {
        str(record.get("journey_id")): record for record in _records(data, "journeys")
    }
    objectives = {
        str(record.get("objective_id")): record
        for record in _records(data, "objectives")
    }
    kpis = {str(record.get("kpi_id")): record for record in _records(data, "kpis")}

    def declared_or(record: dict[str, Any], fallback: set[str]) -> set[str]:
        declared = _explicit_applicability_values(record, "journey_variant_ids")
        return set(declared) if declared is not None else set(fallback)

    for journey in journeys.values():
        own_variants = {
            str(variant.get("variant_id"))
            for variant in journey.get("variants", [])
            if isinstance(variant, dict)
            and isinstance(variant.get("variant_id"), str)
        }
        by_record[id(journey)] = declared_or(journey, own_variants)

    for objective in objectives.values():
        linked = [
            journeys[value]
            for value in objective.get("journey_ids", [])
            if value in journeys
        ]
        inherited = (
            set().union(*(by_record[id(record)] for record in linked))
            if linked
            else set(document_scope.get("journey_variant_ids", set()))
        )
        by_record[id(objective)] = declared_or(objective, inherited)

    for kpi in kpis.values():
        linked_journeys = [
            journeys[value] for value in kpi.get("journey_ids", []) if value in journeys
        ]
        linked_objectives = [
            objectives[value]
            for value in kpi.get("objective_ids", [])
            if value in objectives
        ]
        supporting = linked_journeys or linked_objectives
        inherited = (
            set().union(*(by_record[id(record)] for record in supporting))
            if supporting
            else set(document_scope.get("journey_variant_ids", set()))
        )
        by_record[id(kpi)] = declared_or(kpi, inherited)

    for dimension in _records(data, "dimensions"):
        linked = [
            kpis[value] for value in dimension.get("kpi_ids", []) if value in kpis
        ]
        inherited = (
            set().union(*(by_record[id(record)] for record in linked))
            if linked
            else set(document_scope.get("journey_variant_ids", set()))
        )
        by_record[id(dimension)] = declared_or(dimension, inherited)

    for requirement in _records(data, "measurement_requirements"):
        linked_journeys = [
            journeys[value]
            for value in requirement.get("journey_ids", [])
            if value in journeys
        ]
        linked_kpis = [
            kpis[value]
            for value in requirement.get("kpi_ids", [])
            if value in kpis
        ]
        supporting = linked_journeys or linked_kpis
        inherited = (
            set().union(*(by_record[id(record)] for record in supporting))
            if supporting
            else set(document_scope.get("journey_variant_ids", set()))
        )
        by_record[id(requirement)] = declared_or(requirement, inherited)

    return by_record


def _effective_scope(
    record: dict[str, Any],
    document_scope: dict[str, set[str]],
    variant_scopes: dict[int, set[str]] | None = None,
) -> dict[str, set[str]]:
    applicability = record.get("applicability")
    if not isinstance(applicability, dict):
        applicability = {}
    result: dict[str, set[str]] = {}
    for key in APPLICABILITY_KEYS:
        values = applicability.get(key)
        if isinstance(values, list) and values:
            result[key] = {value for value in values if isinstance(value, str)}
        elif key == "journey_variant_ids" and variant_scopes is not None:
            result[key] = set(
                variant_scopes.get(
                    id(record), document_scope.get("journey_variant_ids", set())
                )
            )
        elif key == "journey_variant_ids" and isinstance(record.get("journey_id"), str):
            result[key] = {
                str(variant.get("variant_id"))
                for variant in record.get("variants", [])
                if isinstance(variant, dict)
                and isinstance(variant.get("variant_id"), str)
            }
        else:
            result[key] = set(document_scope.get(key, set()))
    return result


def _union_scope(
    records: Iterable[dict[str, Any]],
    document_scope: dict[str, set[str]],
    variant_scopes: dict[int, set[str]] | None = None,
) -> dict[str, set[str]]:
    result = {key: set() for key in APPLICABILITY_KEYS}
    for record in records:
        scope = _effective_scope(record, document_scope, variant_scopes)
        for key in APPLICABILITY_KEYS:
            result[key].update(scope[key])
    return result


def relational_applicability_issues(data: dict[str, Any]) -> list[str]:
    """Return unsupported scope-expansion issues across linked entities."""

    document_scope = _document_scope(data)
    variant_scopes = _derived_variant_scopes(data, document_scope)
    journeys = {
        str(item.get("journey_id")): item for item in _records(data, "journeys")
    }
    objectives = {
        str(item.get("objective_id")): item for item in _records(data, "objectives")
    }
    kpis = {str(item.get("kpi_id")): item for item in _records(data, "kpis")}
    collections: list[tuple[str, str, list[dict[str, Any]], Any]] = [
        (
            "objectives",
            "objective_id",
            _records(data, "objectives"),
            lambda item: [
                journeys[value]
                for value in item.get("journey_ids", [])
                if value in journeys
            ],
        ),
        (
            "kpis",
            "kpi_id",
            _records(data, "kpis"),
            lambda item: (
                [
                    journeys[value]
                    for value in item.get("journey_ids", [])
                    if value in journeys
                ]
                if item.get("journey_ids", [])
                else [
                    objectives[value]
                    for value in item.get("objective_ids", [])
                    if value in objectives
                ]
            ),
        ),
        (
            "dimensions",
            "dimension_id",
            _records(data, "dimensions"),
            lambda item: [
                kpis[value] for value in item.get("kpi_ids", []) if value in kpis
            ],
        ),
        (
            "measurement_requirements",
            "requirement_id",
            _records(data, "measurement_requirements"),
            lambda item: (
                [
                    journeys[value]
                    for value in item.get("journey_ids", [])
                    if value in journeys
                ]
                if item.get("journey_ids", [])
                else [kpis[value] for value in item.get("kpi_ids", []) if value in kpis]
            ),
        ),
    ]
    issues: list[str] = []
    for collection_name, id_key, records, linked_records in collections:
        for record in records:
            supporting = linked_records(record)
            if not supporting:
                continue
            claimed = _effective_scope(record, document_scope, variant_scopes)
            supported = _union_scope(supporting, document_scope, variant_scopes)
            overreach = {
                key: sorted(claimed[key] - supported[key])
                for key in APPLICABILITY_KEYS
                if claimed[key] - supported[key]
            }
            if not overreach:
                continue
            basis = record.get("applicability_basis")
            if (
                isinstance(basis, dict)
                and basis.get("rationale")
                and basis.get("evidence_refs")
            ):
                continue
            record_id = str(record.get(id_key, ""))
            details = ", ".join(
                f"{key}={values!r}" for key, values in sorted(overreach.items())
            )
            issues.append(
                f"$.{collection_name}[{record_id!r}].applicability: claimed scope "
                f"exceeds linked-entity scope ({details}); add a supported "
                "applicability_basis only when the broader business scope is intentional"
            )
    return sorted(set(issues))


def consideration_reciprocity_issues(data: dict[str, Any]) -> list[str]:
    kpis = {str(item.get("kpi_id")): item for item in _records(data, "kpis")}
    issues: list[str] = []
    for index, consideration in enumerate(_records(data, "kpi_considerations")):
        if consideration.get("resolution") not in {
            "kpi_proposed",
            "covered_by_existing",
        }:
            continue
        scope_type = consideration.get("scope_type")
        scope_id = consideration.get("scope_id")
        reverse_key = "objective_ids" if scope_type == "objective" else "journey_ids"
        for kpi_id in consideration.get("kpi_ids", []):
            kpi = kpis.get(str(kpi_id))
            if kpi is not None and scope_id not in kpi.get(reverse_key, []):
                issues.append(
                    f"$.kpi_considerations[{index}].kpi_ids: KPI {kpi_id!r} "
                    f"does not link back to {scope_type} {scope_id!r}"
                )
    return sorted(set(issues))


def _exception_entities(
    data: dict[str, Any],
) -> dict[str, tuple[str, dict[str, Any] | None]]:
    entities: dict[str, tuple[str, dict[str, Any] | None]] = {}

    def add(records: Iterable[dict[str, Any]], id_key: str, stage: str) -> None:
        for record in records:
            entity_id = record.get(id_key)
            if isinstance(entity_id, str):
                entities[entity_id] = (stage, record)

    intake = data.get("intake_baseline", {})
    targets = intake.get("targets", []) if isinstance(intake, dict) else []
    add(
        [item for item in targets if isinstance(item, dict)],
        "target_id",
        "scope",
    )
    add(_records(data, "discovery_candidates"), "candidate_id", "journey")
    add(_records(data, "objective_considerations"), "consideration_id", "objective")
    add(_records(data, "objectives"), "objective_id", "objective")
    add(_records(data, "kpi_considerations"), "consideration_id", "kpi")
    add(_records(data, "kpis"), "kpi_id", "kpi")
    add(_records(data, "dimensions"), "dimension_id", "measurement_requirement")
    add(
        _records(data, "measurement_requirements"),
        "requirement_id",
        "measurement_requirement",
    )
    for journey in _records(data, "journeys"):
        journey_id = journey.get("journey_id")
        if isinstance(journey_id, str):
            entities[journey_id] = ("journey", journey)
        for nested_key, id_key in (("steps", "step_id"), ("variants", "variant_id")):
            for record in journey.get(nested_key, []):
                if isinstance(record, dict) and isinstance(record.get(id_key), str):
                    entities[str(record[id_key])] = ("journey", journey)
    return entities


def _scope_overlap(left: dict[str, Any], right: dict[str, Any]) -> bool:
    for key in APPLICABILITY_KEYS:
        left_values = left.get(key, [])
        right_values = right.get(key, [])
        left_set = _string_set(left_values)
        right_set = _string_set(right_values)
        if left_set and right_set and left_set.isdisjoint(right_set):
            return False
    return True


def exception_scope_issues(data: dict[str, Any]) -> list[str]:
    """Return deterministic exception-stage, gate-direction, and scope issues."""

    entities = _exception_entities(data)
    issues: list[str] = []
    for index, exception in enumerate(_records(data, "exceptions")):
        stage = str(exception.get("stage", ""))
        affected_ids = [
            value
            for value in exception.get("affected_ids", [])
            if isinstance(value, str)
        ]
        compatible_stages = (
            {"measurement_requirement"} if stage == "alignment" else {stage}
        )
        if not any(
            entity_id in entities and entities[entity_id][0] in compatible_stages
            for entity_id in affected_ids
        ):
            issues.append(
                f"$.exceptions[{index}].affected_ids: stage {stage!r} requires at "
                "least one affected entity from that stage"
            )

        gate_ids = exception.get("gate_ids")
        effective_gates = (
            {value for value in gate_ids if isinstance(value, str)}
            if isinstance(gate_ids, list) and gate_ids
            else DEFAULT_STAGE_GATES.get(stage, set())
        )
        invalid_gates = sorted(effective_gates - ALLOWED_STAGE_GATES.get(stage, set()))
        if invalid_gates:
            issues.append(
                f"$.exceptions[{index}].gate_ids: stage {stage!r} cannot affect "
                f"upstream gates {invalid_gates}"
            )

        exception_scope = exception.get("applicability")
        if not isinstance(exception_scope, dict):
            continue
        for affected_id in affected_ids:
            entity = entities.get(affected_id)
            if entity is None:
                continue
            record = entity[1]
            if not isinstance(record, dict):
                continue
            record_scope = record.get("applicability")
            if entity[0] == "scope" and not isinstance(record_scope, dict):
                resolved = record.get("resolved_scope_targets", [])
                if isinstance(resolved, list) and resolved:
                    record_scope = {"target_sites": resolved}
            if isinstance(record_scope, dict) and not _scope_overlap(
                exception_scope, record_scope
            ):
                issues.append(
                    f"$.exceptions[{index}].applicability: scope is disjoint from "
                    f"affected entity {affected_id!r}"
                )
    return sorted(set(issues))


def _eligible_direct_source(
    reference: Any,
    sources: dict[str, dict[str, Any]],
    *,
    allowed_states: set[str] | None = None,
) -> tuple[str, dict[str, Any]] | None:
    states = allowed_states or {"as_is", "both"}
    prefix = _source_prefix(reference)
    source = sources.get(prefix or "")
    if source is None or not (
        source.get("source_type") in DIRECT_BEHAVIOR_SOURCE_TYPES
        and source.get("evidence_role") == "live_behavior"
        and source.get("state") in states
    ):
        return None
    return str(prefix), source


def _has_stable_locator(reference: str, source: dict[str, Any]) -> bool:
    if "#" in reference:
        return True
    parsed = urlparse(str(source.get("reference", "")))
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _web_origin(value: Any) -> tuple[str, str] | None:
    parsed = urlparse(str(value or ""))
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    return parsed.scheme, parsed.netloc


def evidence_eligibility_issues(
    data: dict[str, Any], *, require_durability: bool = True
) -> list[str]:
    sources = {str(item.get("source_id")): item for item in _records(data, "sources")}
    issues: list[str] = []
    for source_id, source in sources.items():
        if (
            source.get("evidence_role") == "live_behavior"
            and source.get("source_type") not in DIRECT_BEHAVIOR_SOURCE_TYPES
        ):
            issues.append(
                f"$.sources[{source_id!r}]: live_behavior requires a live_website "
                "or test_website source"
            )

    status_records: list[tuple[str, dict[str, Any]]] = []
    for journey_index, journey in enumerate(_records(data, "journeys")):
        status_records.append((f"$.journeys[{journey_index}]", journey))
        for step_index, step in enumerate(journey.get("steps", [])):
            if isinstance(step, dict):
                status_records.append(
                    (f"$.journeys[{journey_index}].steps[{step_index}]", step)
                )
        for variant_index, variant in enumerate(journey.get("variants", [])):
            if isinstance(variant, dict):
                status_records.append(
                    (f"$.journeys[{journey_index}].variants[{variant_index}]", variant)
                )

    durable_source_ids: set[str] = set()
    for path, record in status_records:
        status = record.get("status")
        if status not in {"observed", "externally_blocked"}:
            continue
        refs = record.get("evidence_refs", [])
        eligible_refs: list[str] = []
        for reference in refs if isinstance(refs, list) else []:
            allowed_states = (
                {"as_is", "both"}
                if status == "observed"
                else {"as_is", "to_be", "both"}
            )
            eligible = _eligible_direct_source(
                reference, sources, allowed_states=allowed_states
            )
            if eligible is None:
                continue
            source_id, source = eligible
            eligible_refs.append(str(reference))
            durable_source_ids.add(source_id)
            if require_durability and not _has_stable_locator(str(reference), source):
                issues.append(
                    f"{path}.evidence_refs: {status} evidence {reference!r} "
                    "needs a stable source URL or an evidence-ref locator"
                )
        if not eligible_refs:
            requirement = (
                "observed status requires direct live/test behavior evidence"
                if status == "observed"
                else "externally_blocked status requires direct live/test evidence of the attempted boundary"
            )
            issues.append(f"{path}: {requirement}")

    for source_id in sorted(durable_source_ids):
        if require_durability and not sources[source_id].get("observed_at"):
            issues.append(
                f"$.sources[{source_id!r}].observed_at: required when the source "
                "supports an observed or externally-blocked claim"
            )
    return sorted(set(issues))


def _journey_evidence_refs(journey: dict[str, Any]) -> list[str]:
    refs: list[str] = []
    records = [
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
    for record in records:
        refs.extend(
            reference
            for reference in record.get("evidence_refs", [])
            if isinstance(reference, str)
        )
    return refs


def _semantic_key(value: Any) -> str:
    tokens = re.findall(r"[a-z0-9]+", str(value or "").lower())
    normalized: list[str] = []
    for token in tokens:
        if len(token) > 3 and token.endswith("ies"):
            token = token[:-3] + "y"
        elif len(token) > 3 and token.endswith("s") and not token.endswith("ss"):
            token = token[:-1]
        normalized.append(token)
    return " ".join(normalized)


def _grain_entity_tokens(value: Any) -> set[str]:
    stopwords = {
        "a",
        "an",
        "the",
        "one",
        "record",
        "row",
        "distinct",
        "unique",
        "per",
        "identifier",
        "id",
        "eligible",
        "accepted",
        "completed",
        "started",
        "first",
        "final",
        "with",
        "without",
        "each",
    }
    return {
        token
        for token in _semantic_key(value).split()
        if token and token not in stopwords
    }


def _rate_formula_diagnostics(
    formula: dict[str, Any], components: list[dict[str, Any]]
) -> tuple[bool, bool, bool]:
    """Return rate presence, counting-unit mismatch, and grain mismatch."""

    if formula.get("calculation_type") not in {"rate", "ratio", "retention"}:
        return False, False, False
    numerators = [item for item in components if item.get("role") == "numerator"]
    denominators = [
        item for item in components if item.get("role") == "denominator"
    ]
    if not numerators or not denominators:
        return False, False, False

    numerator_units = {
        _semantic_key(item.get("counting_unit")) for item in numerators
    } - {""}
    denominator_units = {
        _semantic_key(item.get("counting_unit")) for item in denominators
    } - {""}
    unit_mismatch = bool(
        numerator_units
        and denominator_units
        and numerator_units != denominator_units
    )
    numerator_grains = set().union(
        *(_grain_entity_tokens(item.get("grain")) for item in numerators)
    )
    denominator_grains = set().union(
        *(_grain_entity_tokens(item.get("grain")) for item in denominators)
    )
    grain_mismatch = bool(
        numerator_grains
        and denominator_grains
        and numerator_grains.isdisjoint(denominator_grains)
    )
    return True, unit_mismatch, grain_mismatch


def _cross_journey_aggregation_context(
    kpi: dict[str, Any],
    linked_journeys: list[dict[str, Any]],
    components: list[dict[str, Any]],
) -> tuple[list[set[str]], bool, bool]:
    """Return value-domain context and whether an aggregate needs review."""

    segmentation = kpi.get("segmentation", {})
    dimension_ids = (
        _string_set(segmentation.get("dimension_ids", []))
        if isinstance(segmentation, dict)
        else set()
    )
    domain_sets = [
        _string_set(journey.get("value_domains", []))
        for journey in linked_journeys
        if _string_set(journey.get("value_domains", []))
    ]
    shared_domains = (
        set(domain_sets[0]).intersection(*domain_sets[1:]) if domain_sets else set()
    )
    aggregate_units = {
        _semantic_key(item.get("counting_unit"))
        for item in components
        if item.get("role") in {"numerator", "denominator", "input"}
        and _semantic_key(item.get("counting_unit"))
    }
    needs_review = bool(
        len(linked_journeys) > 1
        and not dimension_ids
        and (
            (len(domain_sets) > 1 and not shared_domains)
            or len(aggregate_units) > 1
        )
    )
    return domain_sets, bool(shared_domains), needs_review


def _north_star_scope_diagnostics(
    kpi: dict[str, Any],
    linked_journeys: list[dict[str, Any]],
    domain_sets: list[set[str]],
    has_shared_domain: bool,
    objectives: dict[str, dict[str, Any]],
    document_scope: dict[str, set[str]],
) -> tuple[bool, bool]:
    """Return broad-scope and missing-rationale signals for a North Star."""

    if kpi.get("tier") != "north_star":
        return False, False
    streams = {
        _semantic_key(objectives[value].get("value_stream"))
        for value in kpi.get("objective_ids", [])
        if value in objectives
        and _semantic_key(objectives[value].get("value_stream"))
    }
    audiences: set[str] = set()
    for journey in linked_journeys:
        declared = _explicit_applicability_values(journey, "audiences")
        audiences.update(
            declared
            if declared is not None
            else document_scope.get("audiences", set())
        )
    broad_scope = bool(
        len(streams) > 1
        or len(audiences) > 1
        or (len(domain_sets) > 1 and not has_shared_domain)
    )
    missing_rationale = broad_scope and not str(
        kpi.get("north_star_rationale", "")
    ).strip()
    return broad_scope, missing_rationale


def kpi_coherence_diagnostics(data: dict[str, Any]) -> dict[str, list[str]]:
    """Return conservative, review-oriented formula and aggregation diagnostics."""

    document_scope = _document_scope(data)
    journeys = {
        str(item.get("journey_id")): item for item in _records(data, "journeys")
    }
    objectives = {
        str(item.get("objective_id")): item
        for item in _records(data, "objectives")
    }
    rate_ids: list[str] = []
    unit_mismatches: list[str] = []
    grain_mismatches: list[str] = []
    cross_journey_reviews: list[str] = []
    north_star_reviews: list[str] = []
    missing_north_star_rationale: list[str] = []

    for kpi in _records(data, "kpis"):
        kpi_id = str(kpi.get("kpi_id", ""))
        formula = kpi.get("formula", {})
        if not isinstance(formula, dict):
            formula = {}
        components = [
            item
            for item in formula.get("components", [])
            if isinstance(item, dict)
        ]
        is_rate, unit_mismatch, grain_mismatch = _rate_formula_diagnostics(
            formula, components
        )
        if is_rate:
            rate_ids.append(kpi_id)
            if unit_mismatch:
                unit_mismatches.append(kpi_id)
            if grain_mismatch:
                grain_mismatches.append(kpi_id)

        linked_journeys = [
            journeys[value]
            for value in kpi.get("journey_ids", [])
            if value in journeys
        ]
        domain_sets, has_shared_domain, aggregate_review = (
            _cross_journey_aggregation_context(kpi, linked_journeys, components)
        )
        if aggregate_review:
            cross_journey_reviews.append(kpi_id)

        broad_north_star, missing_rationale = _north_star_scope_diagnostics(
            kpi,
            linked_journeys,
            domain_sets,
            has_shared_domain,
            objectives,
            document_scope,
        )
        if broad_north_star:
            north_star_reviews.append(kpi_id)
        if missing_rationale:
            missing_north_star_rationale.append(kpi_id)

    return {
        "rate_population_subset_review_ids": sorted(set(rate_ids)),
        "rate_counting_unit_mismatch_ids": sorted(set(unit_mismatches)),
        "rate_grain_mismatch_ids": sorted(set(grain_mismatches)),
        "cross_journey_aggregate_review_ids": sorted(set(cross_journey_reviews)),
        "north_star_scope_review_ids": sorted(set(north_star_reviews)),
        "north_star_ids_missing_scope_rationale": sorted(
            set(missing_north_star_rationale)
        ),
    }


def _source_ids_from_refs(
    references: Any, sources: dict[str, dict[str, Any]] | None = None
) -> set[str]:
    refs = references if isinstance(references, list) else []
    source_ids = {
        prefix
        for reference in refs
        for prefix in [_source_prefix(reference)]
        if prefix
    }
    return source_ids.intersection(sources) if sources is not None else source_ids


def _intake_coverage_facts(
    data: dict[str, Any], sources: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    intake = data.get("intake_baseline", {})
    has_intake = isinstance(intake, dict) and schema_at_least(data, (1, 3, 0))
    raw_targets = intake.get("targets", []) if has_intake else []
    targets = [
        item
        for item in (raw_targets if isinstance(raw_targets, list) else [])
        if isinstance(item, dict)
        and item.get("disposition") in {"included", "canonicalized"}
    ]
    intake_refs = list(intake.get("source_evidence_refs", [])) if has_intake else []
    represented: list[str] = []
    direct: list[str] = []
    test_only: list[str] = []
    targets_by_site: dict[str, dict[str, Any]] = {}
    for target in targets:
        intake_refs.extend(target.get("request_evidence_refs", []))
        intake_refs.extend(target.get("resolution_evidence_refs", []))
        target_id = str(target.get("target_id", ""))
        representative_ids = _string_set(target.get("representative_source_ids", []))
        declared_ids = representative_ids.intersection(sources)
        if declared_ids:
            represented.append(target_id)
        if any(
            sources[source_id].get("source_type") in DIRECT_BEHAVIOR_SOURCE_TYPES
            and sources[source_id].get("evidence_role") == "live_behavior"
            for source_id in declared_ids
        ):
            direct.append(target_id)
        if declared_ids and all(
            sources[source_id].get("source_type") == "test_website"
            for source_id in declared_ids
        ):
            test_only.append(target_id)
        for site in target.get("resolved_scope_targets", []):
            if isinstance(site, str):
                targets_by_site[site] = target
    return {
        "has_intake": has_intake,
        "targets": targets,
        "targets_by_site": targets_by_site,
        "intake_source_ids": {
            source_id
            for source_id in _source_ids_from_refs(intake_refs, sources)
            if sources[source_id].get("source_type") == "user_input"
        },
        "represented_target_ids": represented,
        "directly_represented_target_ids": direct,
        "test_only_represented_target_ids": test_only,
    }


def _candidate_coverage_facts(
    candidates: list[dict[str, Any]],
    sources: dict[str, dict[str, Any]],
    intake_source_ids: set[str],
) -> dict[str, list[str]]:
    cited_source_ids = {
        source_id
        for candidate in candidates
        for source_id in _source_ids_from_refs(candidate.get("evidence_refs", []))
    }
    discovery_source_ids = {
        source_id
        for source_id, source in sources.items()
        if source.get("evidence_role") in DISCOVERY_EVIDENCE_ROLES
    }
    intake_only = []
    for candidate in candidates:
        source_ids = _source_ids_from_refs(candidate.get("evidence_refs", []))
        if (
            candidate.get("material") is True
            and candidate.get("resolution") in {"mapped", "merged"}
            and source_ids
            and source_ids.issubset(intake_source_ids)
        ):
            intake_only.append(str(candidate.get("candidate_id", "")))
    return {
        "discovery_source_ids_without_candidate_support": sorted(
            discovery_source_ids - cited_source_ids
        ),
        "material_candidate_ids_supported_only_by_intake": sorted(
            value for value in intake_only if value
        ),
    }


def _scoped_exception_exists(
    data: dict[str, Any],
    journey_id: str,
    scope_key: str,
    scope_values: set[str],
    test_source_ids: set[str],
) -> bool:
    for exception in _records(data, "exceptions"):
        if journey_id not in exception.get("affected_ids", []):
            continue
        applicability = exception.get("applicability")
        if not isinstance(applicability, dict):
            continue
        declared = _string_set(applicability.get(scope_key, []))
        exception_sources = _source_ids_from_refs(exception.get("evidence_refs", []))
        if (
            declared
            and not declared.isdisjoint(scope_values)
            and not exception_sources.isdisjoint(test_source_ids)
        ):
            return True
    return False


def _journey_evidence_facts(
    journey: dict[str, Any],
    candidates: list[dict[str, Any]],
    sources: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    journey_id = str(journey.get("journey_id", ""))
    refs = _journey_evidence_refs(journey)
    source_ids = _source_ids_from_refs(refs, sources)
    direct_source_ids = {
        prefix
        for reference in refs
        for prefix in [_source_prefix(reference)]
        if prefix and _eligible_direct_source(reference, sources) is not None
    }
    records = [
        journey,
        *[item for item in journey.get("steps", []) if isinstance(item, dict)],
        *[item for item in journey.get("variants", []) if isinstance(item, dict)],
    ]
    candidate_source_ids = {
        source_id
        for candidate in candidates
        if journey_id in candidate.get("journey_ids", [])
        for source_id in _source_ids_from_refs(candidate.get("evidence_refs", []), sources)
    }
    alternative_ids = {
        source_id
        for source_id in source_ids.union(candidate_source_ids)
        if sources[source_id].get("evidence_role")
        in {
            "business_requirement",
            "future_design",
            "data_capability",
            "historical_contract",
        }
    }
    return {
        "journey_id": journey_id,
        "direct_source_ids": direct_source_ids,
        "test_source_ids": {
            source_id
            for source_id in direct_source_ids
            if sources[source_id].get("source_type") == "test_website"
        },
        "blocked_without_fallback": any(
            record.get("status") == "externally_blocked" for record in records
        )
        and not alternative_ids,
    }


def _missing_target_mappings(
    journey: dict[str, Any],
    test_source_ids: set[str],
    sources: dict[str, dict[str, Any]],
    document_scope: dict[str, set[str]],
    targets_by_site: dict[str, dict[str, Any]],
) -> list[str]:
    journey_sites = _explicit_applicability_values(journey, "target_sites")
    if journey_sites is None:
        journey_sites = set(document_scope.get("target_sites", set()))
    test_origins = {
        origin
        for source_id in test_source_ids
        for origin in [_web_origin(sources[source_id].get("reference", ""))]
        if origin is not None
    }
    missing: list[str] = []
    for site in sorted(journey_sites):
        if _web_origin(site) in test_origins:
            continue
        target = targets_by_site.get(site)
        representative_ids = (
            _string_set(target.get("representative_source_ids", []))
            if isinstance(target, dict)
            else set()
        )
        representative_origins = {
            origin
            for source_id in representative_ids.intersection(sources)
            if sources[source_id].get("source_type") == "test_website"
            and sources[source_id].get("evidence_role") == "live_behavior"
            for origin in [_web_origin(sources[source_id].get("reference", ""))]
            if origin is not None
        }
        if representative_ids.isdisjoint(
            test_source_ids
        ) and representative_origins.isdisjoint(test_origins):
            missing.append(site)
    return missing


def _locale_review(
    journey: dict[str, Any],
    journey_id: str,
    direct_source_ids: set[str],
    document_scope: dict[str, set[str]],
) -> dict[str, Any] | None:
    locales = _explicit_applicability_values(journey, "locales")
    if locales is None:
        locales = set(document_scope.get("locales", set()))
    evidenced_variants = sum(
        1
        for variant in journey.get("variants", [])
        if isinstance(variant, dict)
        and variant.get("status") in {"observed", "confirmed"}
        and variant.get("evidence_refs")
    )
    if len(locales) <= 1 or max(len(direct_source_ids), evidenced_variants) >= len(
        locales
    ):
        return None
    return {
        "journey_id": journey_id,
        "locales": sorted(locales),
        "direct_source_ids": sorted(direct_source_ids),
    }


def discovery_evidence_coverage(data: dict[str, Any]) -> dict[str, Any]:
    """Compute evidence-coverage signals from existing framework fields only."""

    sources = {str(item.get("source_id")): item for item in _records(data, "sources")}
    candidates = _records(data, "discovery_candidates")
    document_scope = _document_scope(data)
    intake_facts = _intake_coverage_facts(data, sources)
    candidate_facts = _candidate_coverage_facts(
        candidates, sources, intake_facts["intake_source_ids"]
    )
    direct_scope = {key: set() for key in DIRECT_SCOPE_KEYS}
    blocked_without_fallback: list[str] = []
    cross_environment_reviews: list[dict[str, Any]] = []
    locale_reviews: list[dict[str, Any]] = []
    assumptions_by_entity = {
        affected_id
        for assumption in _records(data, "assumptions")
        if assumption.get("status") in {"open", "validated"}
        for affected_id in assumption.get("affected_ids", [])
        if isinstance(affected_id, str)
    }

    for journey in _records(data, "journeys"):
        facts = _journey_evidence_facts(journey, candidates, sources)
        journey_id = facts["journey_id"]
        direct_source_ids = facts["direct_source_ids"]
        test_source_ids = facts["test_source_ids"]
        if journey.get("material") is True and direct_source_ids:
            for key in DIRECT_SCOPE_KEYS:
                declared = _explicit_applicability_values(journey, key)
                if declared is not None:
                    direct_scope[key].update(declared)
                elif len(document_scope.get(key, set())) == 1:
                    direct_scope[key].update(document_scope[key])
        if facts["blocked_without_fallback"]:
            blocked_without_fallback.append(journey_id)
        if not intake_facts["has_intake"] or not test_source_ids:
            continue

        missing_targets = _missing_target_mappings(
            journey,
            test_source_ids,
            sources,
            document_scope,
            intake_facts["targets_by_site"],
        )
        scope_basis = journey_id in assumptions_by_entity or _scoped_exception_exists(
            data, journey_id, "target_sites", set(missing_targets), test_source_ids
        )
        if missing_targets and not scope_basis:
            cross_environment_reviews.append(
                {
                    "journey_id": journey_id,
                    "target_sites": missing_targets,
                    "test_source_ids": sorted(test_source_ids),
                }
            )

        locale_review = _locale_review(
            journey, journey_id, direct_source_ids, document_scope
        )
        locale_values = set(locale_review["locales"]) if locale_review else set()
        locale_basis = journey_id in assumptions_by_entity or _scoped_exception_exists(
            data, journey_id, "locales", locale_values, test_source_ids
        )
        if locale_review and not locale_basis:
            locale_reviews.append(locale_review)

    targets = intake_facts["targets"]
    represented = intake_facts["represented_target_ids"]
    return {
        "included_target_count": len(targets),
        "represented_target_ids": sorted(set(represented)),
        "included_targets_without_representative_sources": sorted(
            str(target.get("target_id", ""))
            for target in targets
            if str(target.get("target_id", "")) not in represented
        ),
        "directly_represented_target_ids": sorted(
            set(intake_facts["directly_represented_target_ids"])
        ),
        "test_only_represented_target_ids": sorted(
            set(intake_facts["test_only_represented_target_ids"])
        ),
        "direct_evidence_claimed_scope": {
            key: sorted(values) for key, values in direct_scope.items()
        },
        "document_scope_without_attributed_direct_evidence": {
            key: sorted(document_scope.get(key, set()) - direct_scope[key])
            for key in DIRECT_SCOPE_KEYS
        },
        **candidate_facts,
        "externally_blocked_journey_ids_without_alternative_source": sorted(
            value for value in blocked_without_fallback if value
        ),
        "journeys_needing_cross_environment_basis": sorted(
            cross_environment_reviews, key=lambda item: item["journey_id"]
        ),
        "journeys_needing_locale_basis": sorted(
            locale_reviews, key=lambda item: item["journey_id"]
        ),
    }


def gate_facts(data: dict[str, Any]) -> dict[str, list[str]]:
    maturity = evidence_maturity(data)
    census = candidate_census(data)
    discovery_coverage = discovery_evidence_coverage(data)
    kpi_coherence = kpi_coherence_diagnostics(data)
    evidence_issues = evidence_eligibility_issues(
        data, require_durability=schema_at_least(data, (1, 3, 0))
    )
    relational_issues = relational_applicability_issues(data)
    reciprocity_issues = consideration_reciprocity_issues(data)
    exception_issues = exception_scope_issues(data)
    objective_considerations = _records(data, "objective_considerations")
    kpi_considerations = _records(data, "kpi_considerations")
    exceptions = _records(data, "exceptions")
    by_stage = Counter(str(item.get("stage")) for item in exceptions)
    intake = data.get("intake_baseline", {})
    has_intake = isinstance(intake, dict) and schema_at_least(data, (1, 3, 0))
    intake_targets = intake.get("targets", []) if has_intake else []
    target_dispositions = Counter(
        str(item.get("disposition"))
        for item in intake_targets
        if isinstance(item, dict)
    )
    resolved_scope = {
        value
        for item in intake_targets
        if isinstance(item, dict)
        and item.get("disposition") in {"included", "canonicalized"}
        for value in item.get("resolved_scope_targets", [])
        if isinstance(value, str)
    }
    document = data.get("document", {})
    document_sites = (
        _string_set(document.get("target_sites", []))
        if isinstance(document, dict)
        else set()
    )
    scope_diff_count = len(resolved_scope.symmetric_difference(document_sites))

    def compact(counts: dict[str, int]) -> str:
        return (
            ", ".join(f"{key}={value}" for key, value in sorted(counts.items()))
            or "none"
        )

    overall_facts = [
        f"exceptions={len(exceptions)}",
        f"exception scope issues={len(exception_issues)}",
    ]
    if has_intake:
        overall_facts.extend(
            [
                "included targets without representative sources="
                f"{len(census['included_targets_without_representative_sources'])}",
                f"intake target dispositions: {compact(target_dispositions)}",
                f"delivery scope diff items={scope_diff_count}",
            ]
        )
    else:
        overall_facts.append("intake scope provenance=not available in legacy schema")

    return {
        "journey_completeness": [
            f"material candidates={census['material_candidate_total']}",
            f"material unresolved={len(census['unresolved_material_candidate_ids'])}",
            f"journey statuses: {compact(maturity['journeys'])}",
            f"state decisions: {compact(census['state_decision_resolutions'])}",
            f"evidence eligibility issues={len(evidence_issues)}",
            "discovery sources without candidate support="
            f"{len(discovery_coverage['discovery_source_ids_without_candidate_support'])}",
            "blocked journeys without alternative evidence="
            f"{len(discovery_coverage['externally_blocked_journey_ids_without_alternative_source'])}",
            "material candidates supported only by intake="
            f"{len(discovery_coverage['material_candidate_ids_supported_only_by_intake'])}",
        ],
        "journey_appropriateness": [
            f"material journeys={sum(1 for item in _records(data, 'journeys') if item.get('material') is True)}",
            f"journey exceptions={by_stage['journey']}",
            "cross-environment basis reviews="
            f"{len(discovery_coverage['journeys_needing_cross_environment_basis'])}",
            "locale basis reviews="
            f"{len(discovery_coverage['journeys_needing_locale_basis'])}",
        ],
        "objective_completeness": [
            f"objective considerations={len(objective_considerations)}",
            f"active objectives={sum(maturity['objectives'].get(key, 0) for key in ('confirmed', 'hypothesis'))}",
            f"objective exceptions={by_stage['objective']}",
        ],
        "objective_appropriateness": [
            f"objective statuses: {compact(maturity['objectives'])}",
            "objective applicability issues="
            f"{sum(1 for item in relational_issues if item.startswith('$.objectives'))}",
        ],
        "kpi_completeness": [
            f"KPI considerations={len(kpi_considerations)}",
            f"accepted KPIs={len(_records(data, 'kpis'))}",
            f"recommended core={sum(1 for item in _records(data, 'kpis') if item.get('recommended_core') is True)}",
            f"KPI exceptions={by_stage['kpi']}",
            f"consideration reciprocity issues={len(reciprocity_issues)}",
        ],
        "kpi_appropriateness": [
            f"KPI evidence: {compact(maturity['kpis'])}",
            "KPI applicability issues="
            f"{sum(1 for item in relational_issues if item.startswith('$.kpis'))}",
            "rate unit/grain issues="
            f"{len(kpi_coherence['rate_counting_unit_mismatch_ids']) + len(kpi_coherence['rate_grain_mismatch_ids'])}",
            "cross-journey aggregation reviews="
            f"{len(kpi_coherence['cross_journey_aggregate_review_ids'])}",
            "broad North Star reviews="
            f"{len(kpi_coherence['north_star_scope_review_ids'])}",
        ],
        "requirement_traceability": [
            f"requirements={len(_records(data, 'measurement_requirements'))}",
            f"requirement evidence: {compact(maturity['measurement_requirements'])}",
            "requirement/alignment exceptions="
            f"{by_stage['measurement_requirement'] + by_stage['alignment']}",
            "dimension/requirement applicability issues="
            f"{sum(1 for item in relational_issues if item.startswith(('$.dimensions', '$.measurement_requirements')))}",
        ],
        "overall": overall_facts,
    }
