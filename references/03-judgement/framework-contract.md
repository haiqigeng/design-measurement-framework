# Framework Contract

## Contents

- [Top-level inventories](#top-level-inventories)
- [Stable IDs](#stable-ids)
- [Bidirectional traceability](#bidirectional-traceability)
- [Evidence references](#evidence-references)
- [Consideration ledgers](#consideration-ledgers)
- [Measurement requirements](#measurement-requirements)
- [Gate and exception consistency](#gate-and-exception-consistency)

Use `schemas/measurement-framework.schema.json` as the canonical v1 contract.
Validate with `scripts/validate_framework.py` before rendering or handoff.

## Top-Level Inventories

Maintain these inventories:

1. `document`;
2. `sources`;
3. `discovery_candidates`;
4. `journeys`;
5. `objective_considerations`;
6. `objectives`;
7. `kpi_considerations`;
8. `kpis`;
9. `dimensions`;
10. `measurement_requirements`;
11. `alignment`;
12. `unlinked_measurements`;
13. `assumptions`;
14. `exceptions`;
15. `quality_gates`.

Do not create separately authored human tables. Render every human view from
these canonical objects.

## Stable IDs

Use lowercase ASCII `snake_case` IDs beginning with a letter. Prefix IDs by
entity when helpful, for example:

- `journey_quote`;
- `objective_qualified_demand`;
- `kpi_quote_completion_rate`;
- `dimension_quote_type`;
- `requirement_quote_confirmed`;
- `exception_payment_boundary`.

Preserve stable IDs during maintenance. Never reuse an ID for a different
semantic meaning.

## Bidirectional Traceability

Require:

- discovery candidates → journeys;
- journeys ↔ objectives through objective journey links;
- objective and journey considerations → KPIs;
- KPIs → primary/additional objectives and applicable journeys;
- KPI formula components ↔ measurement requirements;
- KPI segmentation ↔ dimensions;
- dimensions → affected KPIs;
- requirements → KPIs and dimensions;
- current alignment → measurement requirement;
- assumptions/exceptions → affected IDs;
- gates → exception IDs.

Reject dangling, duplicate, or one-way references where the reverse contract is
required.

## Evidence References

Use `source_id` or `source_id#locator`. Ensure the prefix matches a declared
source. Keep at least one evidence reference on every proposed candidate,
journey, objective, KPI, dimension, and requirement.

## Consideration Ledgers

Use consideration rows to prove that completeness was evaluated even when an
objective or KPI was rejected. Never add a low-quality KPI merely to satisfy a
formal role. Record `none_with_reason` or `not_applicable` with evidence and
rationale instead.

Require these objective-level KPI roles for every active objective:

- `outcome`;
- `driver`;
- `guardrail`.

Require these journey-level roles for every material journey:

- `completion`;
- `step_conversion`;
- `friction`.

## Measurement Requirements

Define semantic facts independently of analytics transport. Require one source
system and collection-mode expectation. Keep `downstream_mapping_hint`
optional and `authoritative: false`.

Do not add final event definitions, exact triggers, parameter requiredness,
value-domain contracts, dataLayer paths, or push examples to this schema.

## Gate And Exception Consistency

Require:

- `pass` with no exception IDs;
- `pass_with_exceptions` with at least one valid exception ID;
- no final `fail` for a framework claimed complete;
- overall status equal to the worst component status;
- every open material assumption represented by an exception;
- every unresolved candidate or consideration represented by an exception.

The validator enforces structural closure. The analyst remains responsible for
whether the candidate universe, evidence, materiality, formulas, and judgments
are truthful and sufficient.
