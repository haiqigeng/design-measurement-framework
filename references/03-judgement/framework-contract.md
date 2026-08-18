# Framework Contract

## Contents

- [Top-level inventories](#top-level-inventories)
- [Stable IDs](#stable-ids)
- [Bidirectional traceability](#bidirectional-traceability)
- [Evidence references](#evidence-references)
- [Consideration ledgers](#consideration-ledgers)
- [Measurement requirements](#measurement-requirements)
- [Gate and exception consistency](#gate-and-exception-consistency)

Use `schemas/measurement-framework.schema.json` as the canonical v1.2
contract. It accepts v1.0 and v1.1 artifacts for backward compatibility. New
drafts use `schema_version: 1.2.0`. Validate with
`scripts/validate_framework.py` before rendering or delivery. Version-specific
analytical safeguards apply only to v1.2 artifacts, so validation of an older
artifact does not silently change its prior acceptance contract.

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

## Artifact Authority

Treat `measurement-framework.json` as canonical and
`measurement-framework.md` as its generated human review surface. If they
disagree, JSON wins and Markdown must be regenerated. Human-approved changes
must be represented in JSON before rendering.

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

## Optional Applicability

Use the optional `applicability` object only when an entity is limited to
specific target sites, products, markets, audiences, `as_is` or `to_be` states, or
journey variants within the document scope. It may appear on journeys,
objectives, KPIs, dimensions, and measurement requirements.

Omit it for a simple scope. Do not build inheritance, factoring, market caches,
or split outputs around this field. Multiple North Stars require explicit,
non-overlapping applicability and a rationale.

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

## Structured Formula Contract

For schema `1.2.0`, require `calculation_type` and `result_unit` on every KPI
formula and `symbol`, `counting_unit`, and `grain` on every formula component.
The existing expression uses only declared component symbols, numeric constants,
bounded arithmetic, and approved semantic functions. Every numerator,
denominator, and input component must occur in the expression. Filters and
outputs may remain declarative when they do not participate in arithmetic.

The validator checks expression syntax, symbol reconciliation, specialized
rate, percentile, and weighted-average shapes, and component metadata. Human
review remains responsible for whether the declared units, grain, population,
window, and identity are substantively correct.

## Measurement Requirements

Define semantic facts independently of analytics transport. Require one source
system and collection-mode expectation. The legacy `downstream_mapping_hint`
remains optional for v1 compatibility, must be `authoritative: false`, and
should be omitted from new frameworks.

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

An exception may declare `gate_ids` when it affects an appropriateness gate or
more than one component gate. When omitted, the validator applies the
backward-compatible default gate for the exception stage. Every exception must
be cited by each declared gate and by `overall`.

The validator enforces structural closure. The analyst remains responsible for
whether the candidate universe, evidence, materiality, formulas, and judgments
are truthful and sufficient.
