from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "valid-minimal.json"


def load_framework() -> dict[str, Any]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def add_alignment_source(
    framework: dict[str, Any],
    *,
    source_id: str = "source_measurement",
    source_type: str = "current_tracking",
    evidence_role: str = "current_implementation",
    state: str = "as_is",
) -> None:
    framework["sources"].append(
        {
            "source_id": source_id,
            "source_type": source_type,
            "reference": "Current measurement evidence",
            "evidence_role": evidence_role,
            "state": state,
            "supports": ["Current semantic measurement assessment"],
        }
    )
    framework["alignment"] = [
        {
            "requirement_id": requirement["requirement_id"],
            "status": "not_assessable",
            "current_measurement_refs": [f"{source_id}#inventory"],
            "gaps": [
                "The supplied evidence does not prove complete semantic coverage."
            ],
            "action": "Obtain the missing evidence layer before claiming coverage.",
        }
        for requirement in framework["measurement_requirements"]
    ]


def add_exception(
    framework: dict[str, Any],
    *,
    exception_id: str,
    stage: str,
    affected_ids: list[str],
    gate_ids: list[str] | None = None,
) -> None:
    exception: dict[str, Any] = {
        "exception_id": exception_id,
        "stage": stage,
        "description": "Additional evidence is required to close this bounded limitation.",
        "affected_ids": affected_ids,
        "impact": "The affected conclusion remains provisional.",
        "disposition": "awaiting_evidence",
        "evidence_refs": ["source_business#evidence-boundary"],
    }
    if gate_ids:
        exception["gate_ids"] = gate_ids
    framework["exceptions"].append(exception)

    default_gate = {
        "journey": "journey_completeness",
        "objective": "objective_completeness",
        "kpi": "kpi_completeness",
        "measurement_requirement": "requirement_traceability",
        "alignment": "requirement_traceability",
    }[stage]
    affected_gates = gate_ids or [default_gate]
    for gate_name in affected_gates:
        framework["quality_gates"][gate_name]["status"] = "pass_with_exceptions"
        framework["quality_gates"][gate_name]["exception_ids"].append(exception_id)
    framework["quality_gates"]["overall"]["status"] = "pass_with_exceptions"
    framework["quality_gates"]["overall"]["exception_ids"].append(exception_id)


def add_second_north_star(framework: dict[str, Any]) -> dict[str, Any]:
    framework["document"]["markets"] = ["France", "Belgium"]
    original = next(
        item
        for item in framework["kpis"]
        if item["kpi_id"] == "kpi_quote_completion_rate"
    )
    original["tier"] = "north_star"
    original["applicability"] = {"markets": ["France"]}
    original["north_star_rationale"] = (
        "Represents accepted quote value for the French journey scope."
    )

    duplicate = copy.deepcopy(original)
    duplicate["kpi_id"] = "kpi_quote_completion_rate_belgium"
    duplicate["name"] = "Belgium quote completion rate"
    duplicate["applicability"] = {"markets": ["Belgium"]}
    duplicate["north_star_rationale"] = (
        "Represents accepted quote value for the Belgian journey scope."
    )
    for component in duplicate["formula"]["components"]:
        component["component_id"] += "_belgium"
    framework["kpis"].append(duplicate)

    for requirement in framework["measurement_requirements"]:
        if requirement["requirement_id"] in {
            requirement_id
            for component in duplicate["formula"]["components"]
            for requirement_id in component["requirement_ids"]
        }:
            requirement["kpi_ids"].append(duplicate["kpi_id"])
    for dimension in framework["dimensions"]:
        if dimension["dimension_id"] in duplicate["segmentation"]["dimension_ids"]:
            dimension["kpi_ids"].append(duplicate["kpi_id"])
    for consideration in framework["kpi_considerations"]:
        if original["kpi_id"] in consideration["kpi_ids"]:
            consideration["kpi_ids"].append(duplicate["kpi_id"])
    return duplicate


def add_secondary_objective_without_core(framework: dict[str, Any]) -> None:
    objective = copy.deepcopy(framework["objectives"][0])
    objective["objective_id"] = "objective_secondary_quality"
    objective["statement"] = "Improve the quality of accepted quote demand"
    objective["priority"] = "secondary"
    framework["objectives"].append(objective)
    framework["objective_considerations"][0]["objective_ids"].append(
        objective["objective_id"]
    )

    kpi = copy.deepcopy(
        next(
            item
            for item in framework["kpis"]
            if item["kpi_id"] == "kpi_quote_completion_rate"
        )
    )
    kpi["kpi_id"] = "kpi_secondary_quality_outcome"
    kpi["name"] = "Secondary quality outcome"
    kpi["primary_objective_id"] = objective["objective_id"]
    kpi["objective_ids"] = [objective["objective_id"]]
    kpi["tier"] = "supporting"
    kpi["recommended_core"] = False
    for component in kpi["formula"]["components"]:
        component["component_id"] += "_secondary"
    framework["kpis"].append(kpi)

    linked_requirement_ids = {
        requirement_id
        for component in kpi["formula"]["components"]
        for requirement_id in component["requirement_ids"]
    }
    for requirement in framework["measurement_requirements"]:
        if requirement["requirement_id"] in linked_requirement_ids:
            requirement["kpi_ids"].append(kpi["kpi_id"])
    for dimension in framework["dimensions"]:
        if dimension["dimension_id"] in kpi["segmentation"]["dimension_ids"]:
            dimension["kpi_ids"].append(kpi["kpi_id"])

    template_by_role = {
        item["role"]: item
        for item in framework["kpi_considerations"]
        if item["scope_type"] == "objective"
        and item["scope_id"] == "objective_qualified_demand"
    }
    for role in ("outcome", "driver", "guardrail"):
        consideration = copy.deepcopy(template_by_role[role])
        consideration["consideration_id"] = f"kpicon_secondary_{role}"
        consideration["scope_id"] = objective["objective_id"]
        if role == "outcome":
            consideration["kpi_ids"] = [kpi["kpi_id"]]
            consideration["reason"] = (
                "The supporting outcome directly represents the secondary objective."
            )
        else:
            consideration["resolution"] = "none_with_reason"
            consideration["kpi_ids"] = []
            consideration["reason"] = (
                f"No distinct {role} KPI is justified beyond the framework core."
            )
        framework["kpi_considerations"].append(consideration)
