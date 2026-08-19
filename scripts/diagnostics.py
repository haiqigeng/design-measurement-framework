"""Shared semantic diagnostics, maturity facts, and non-blocking advisories."""

from __future__ import annotations

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


def _effective_scope(
    record: dict[str, Any], document_scope: dict[str, set[str]]
) -> dict[str, set[str]]:
    applicability = record.get("applicability")
    if not isinstance(applicability, dict):
        applicability = {}
    result: dict[str, set[str]] = {}
    for key in APPLICABILITY_KEYS:
        values = applicability.get(key)
        if isinstance(values, list) and values:
            result[key] = {value for value in values if isinstance(value, str)}
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
    records: Iterable[dict[str, Any]], document_scope: dict[str, set[str]]
) -> dict[str, set[str]]:
    result = {key: set() for key in APPLICABILITY_KEYS}
    for record in records:
        scope = _effective_scope(record, document_scope)
        for key in APPLICABILITY_KEYS:
            result[key].update(scope[key])
    return result


def relational_applicability_issues(data: dict[str, Any]) -> list[str]:
    """Return unsupported scope-expansion issues across linked entities."""

    document_scope = _document_scope(data)
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
            claimed = _effective_scope(record, document_scope)
            supported = _union_scope(supporting, document_scope)
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


def gate_facts(data: dict[str, Any]) -> dict[str, list[str]]:
    maturity = evidence_maturity(data)
    census = candidate_census(data)
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
        ],
        "journey_appropriateness": [
            f"material journeys={sum(1 for item in _records(data, 'journeys') if item.get('material') is True)}",
            f"journey exceptions={by_stage['journey']}",
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
