# Framework Contract

## Contents

- [Top-level inventories](#top-level-inventories)
- [Intake and scope provenance](#intake-and-scope-provenance)
- [Artifact authority](#artifact-authority)
- [Stable IDs](#stable-ids)
- [Optional applicability](#optional-applicability)
- [Bidirectional traceability](#bidirectional-traceability)
- [Evidence references](#evidence-references)
- [Material state decisions](#material-state-decisions)
- [Consideration ledgers](#consideration-ledgers)
- [Structured formula contract](#structured-formula-contract)
- [Measurement requirements](#measurement-requirements)
- [Gate and exception consistency](#gate-and-exception-consistency)

Use `schemas/measurement-framework.schema.json` as the canonical v1.3
contract. It accepts v1.0, v1.1, and v1.2 artifacts for backward compatibility.
New drafts use `schema_version: 1.3.0`. Validate with
`scripts/validate_framework.py` before rendering or delivery. Version-specific
blocking safeguards apply only to the schema that introduced them; newly
detectable semantic risks remain advisories for legacy artifacts.

## Top-Level Inventories

Maintain these inventories:

1. `document`;
2. `intake_baseline` for v1.3;
3. `sources`;
4. `discovery_candidates`;
5. `journeys`;
6. `objective_considerations`;
7. `objectives`;
8. `kpi_considerations`;
9. `kpis`;
10. `dimensions`;
11. `measurement_requirements`;
12. `alignment`;
13. `unlinked_measurements`;
14. `assumptions`;
15. `exceptions`;
16. `quality_gates`.

Do not create separately authored human tables. Render every human view from
these canonical objects.

## Intake And Scope Provenance

Capture `intake_baseline` before exploration. Each target preserves the
requested non-secret value, disposition, resolved production targets,
resolution basis, request and resolution evidence, representative source IDs,
and optional exception. Included and canonicalized resolved targets must equal
`document.target_sites`; excluded and unresolved targets must not leak into
delivery scope.

The baseline also mirrors target state, scope claim, products, markets,
audiences, and locales. Record safe-testing authorization categorically with
target IDs and constraints. Never retain a credential or test account value.

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
specific target sites, products, markets, audiences, locales, `as_is` or
`to_be` states, or journey variants within the document scope. It may appear
on journeys, objectives, KPIs, dimensions, measurement requirements, and
exceptions.

Omit it for a simple scope. Do not build inheritance, factoring, market caches,
or split outputs around this field. Multiple North Stars require explicit,
non-overlapping applicability and a rationale.

For v1.3, an objective, KPI, dimension, or requirement must not silently claim
scope broader than the union of the entities that support it. Add
`applicability_basis` with rationale and evidence only when the broader
business definition is intentional; it is not a generic bypass.

Journey-variant scope is inherited through links: an objective derives it from
linked journeys; a KPI from linked journeys or, when none are linked, its
objectives; a dimension from linked KPIs; and a requirement from linked
journeys or KPIs. Omission of `applicability.journey_variant_ids` therefore
does not mean every variant in an unrelated journey. Declare the field only to
narrow or intentionally broaden the inherited scope; intentional breadth still
requires `applicability_basis`.

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

For v1.3, every KPI cited by a proposed or covering KPI consideration must
also link back to that consideration's objective or journey.

## Evidence References

Use `source_id` or `source_id#locator`. Ensure the prefix matches a declared
source. Keep at least one evidence reference on every proposed candidate,
journey, objective, KPI, dimension, and requirement.

An `observed` record requires direct current-state live/test behavior evidence.
An `externally_blocked` record requires direct live/test evidence of the
attempted boundary in the applicable current or future state. Its supporting
source requires `observed_at`, and the source URL or evidence reference must
provide a stable locator. Technical evidence may still confirm capabilities
and backend outcomes.

## Material State Decisions

For each material v1.3 journey, record exactly one decision for failure, empty,
recovery, re-entry, and post-conversion. Use `covered`, `merged`,
`not_applicable`, or `unresolved`. Covered decisions link to a matching state
step; merged decisions link to the supporting step; unresolved decisions link
to a journey exception. Non-material journeys need no decision ledger.

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

For schema `1.2.0` and later, require `calculation_type` and `result_unit` on
every KPI formula and `symbol`, `counting_unit`, and `grain` on every formula
component.
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

For v1.3, the stage must match at least one affected entity, gate impact may
flow only from that stage to the same or downstream stages, and declared
exception applicability must overlap scoped affected entities. These are
structural checks; the validator does not pretend to prove feasibility or
materiality from prose.

Validator `--json` emits an artifact-bound diagnostic view with SHA-256,
versions, evidence maturity, candidate census, discovery/evidence coverage,
KPI coherence checks, computed gate facts, errors, and advisories. It is
reproducible review output, not a third canonical artifact.

The validator enforces structural closure. The analyst remains responsible for
whether the candidate universe, evidence, materiality, formulas, and judgments
are truthful and sufficient.
