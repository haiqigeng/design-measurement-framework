# Completeness And Appropriateness Gates

## Contents

- [Scope fidelity](#scope-fidelity)
- [Journey completeness](#journey-completeness)
- [Journey appropriateness](#journey-appropriateness)
- [Objective completeness](#objective-completeness)
- [Objective appropriateness](#objective-appropriateness)
- [KPI completeness](#kpi-completeness)
- [KPI appropriateness](#kpi-appropriateness)
- [Requirement traceability](#requirement-traceability)
- [Overall gate](#overall-gate)

Apply every gate. Use `pass`, `pass_with_exceptions`, or `fail`. A gate may pass
with exceptions only when each exception is explicit, bounded, and linked to
affected IDs. Never use an exception to hide an unperformed but feasible core
analysis step.

## Scope Fidelity

Before judging analytical layers, require:

- every requested non-secret target has an intake disposition;
- included and canonicalized resolved production targets exactly match
  `document.target_sites`;
- canonicalization or exclusion is supported by user evidence;
- every assumed or unresolved target has an exact scope exception;
- products, markets, audiences, locales, target state, and scope claim agree
  between the intake baseline and resolved document; and
- representative test or staging sources remain evidence bindings rather than
  silent production-scope substitutions.

Fail delivery on an unapproved scope substitution. Do not fail merely because
several production targets share one representative test source.

## Journey Completeness

Require all of the following:

- resolve every material top-down and bottom-up discovery candidate;
- map every scanned navigation, CTA, form, template, entry, and endpoint family
  to a journey, merge, exclusion, or exception;
- include every material expected journey or record why it is absent;
- give every material journey a declared entry point plus explicit entry and
  success steps, allowing non-UI outcome evidence or a bounded exception;
- represent material variants separately when their paths or measurement needs differ;
- record explicit covered, merged, not-applicable, or unresolved decisions for
  failure, empty, recovery, re-entry, and post-conversion states on every
  material journey;
- link every partial, not-tested, or externally blocked material state to an exception;
- require timestamped direct live/test evidence with a stable locator for
  every `observed` claim and every claimed external boundary;
- after a direct access boundary, inspect available technical, lifecycle,
  business, design, historical, or credible user evidence before concluding
  discovery, and preserve every supported material candidate at its honest
  maturity;
- review discovery-capable sources that support no candidate, material
  candidates supported only by intake, and blocked journeys without an
  alternative source;
- state the downstream impact of every residual gap.

Fail when a material candidate is silently absent or an unresolved candidate has
no exception.

## Journey Appropriateness

Require every included journey to:

- have a concrete user intent and defined outcome;
- be material to an evidenced value stream or required scope;
- avoid duplicate naming of the same goal;
- group equivalent variants without collapsing materially different ones;
- exclude aimless paths and page/click inventories;
- use evidence and target state consistently;
- keep production scope distinct from test evidence and support environment or
  locale extrapolation with a representative-source binding, explicit
  assumption, or bounded exception;
- apply a proportional coverage strategy to large or combinatorial spaces.

Fail when journey quantity substitutes for goal/outcome reasoning.

## Objective Completeness

Require all of the following:

- record a decision for every material value stream;
- record applicable lifecycle-stage decisions, including `none_with_reason`;
- record decisions for relevant stakeholder lenses;
- record risk/guardrail considerations, not only growth outcomes;
- map every material included journey to at least one active objective;
- preserve every client-required objective and any evidence tension;
- bind every unresolved material consideration to an exception.

Fail when a material journey or value stream has no objective-level decision.

## Objective Appropriateness

Require every active objective to:

- cite local evidence or be explicitly client-required;
- describe an outcome rather than an implementation;
- be distinct from other objectives;
- fit the declared scope, target state, business model, and maturity;
- use recognizable business vocabulary;
- support a plausible decision;
- identify its digital or linked business-system measurability boundary;
- preserve hypothesis status when strategy is inferred rather than confirmed.

Fail when generic library content is presented as a site-specific objective.

## KPI Completeness

Require all of the following:

- record outcome, driver, and guardrail considerations for every active objective;
- record completion, step-conversion, and friction considerations for every
  material journey;
- retain at least one outcome KPI per active objective unless a named exception
  establishes why measurement is currently impossible;
- specify every accepted KPI completely;
- map every formula component to at least one measurement requirement;
- make every segmentation decision explicit;
- require each proposed or covering KPI consideration to link back from the
  referenced KPI to the consideration's objective or journey;
- identify a recommended core for the framework without mechanically forcing
  one core KPI per objective;
- bind every unresolved material consideration to an exception.

Fail when a KPI is omitted because its supporting fact is not visible in the UI.

## KPI Appropriateness

Require every accepted KPI to:

- trace to a primary objective and any additional supported objectives;
- support a plausible decision and action;
- have a coherent owner role;
- use a dimensionally valid formula, grain, population, and time basis;
- make rate numerators conceptual subsets of compatible denominators, with the
  same counting unit, entity grain, eligibility, deduplication, and time basis
  unless a valid conversion is explicit;
- combine multiple journeys only through a coherent shared unit, a required
  differentiating dimension, or separate KPIs;
- avoid vanity, duplicate, and redundant definitions;
- use guardrails where optimizing the KPI can plausibly degrade quality or value;
- balance core outcome or driver KPIs with their explicitly proposed guardrail
  KPIs, or cite a KPI-appropriateness exception;
- keep tier and role coherent, including guardrail and diagnostic assignments;
- distinguish outcome, driver, guardrail, and diagnostic roles honestly;
- use a North Star only when one durable metric can represent its declared
  scope without hiding essential counter-outcomes;
- require a broad North Star to explain comparability, aggregation, and
  mix-shift risk across roles, value streams, or task types;
- give multiple North Stars explicit, non-overlapping applicability and rationale;
- avoid invented targets and unsupported benchmarks;
- state evidence and assumption status;
- keep claimed KPI applicability within linked journey or objective scope, or
  provide an evidence-backed `applicability_basis` for an intentionally broader
  business definition.

Fail when two analysts could reasonably calculate different values from the
same written definition.

## Requirement Traceability

Require all of the following:

- map every KPI formula component to a requirement;
- map every requirement back to at least one KPI;
- resolve every required dimension through at least one measurement requirement
  for each affected KPI and name its source or collection mode;
- retain backend, lifecycle, business-system, native, joined, and derived needs;
- prevent a dimension from becoming an event parameter by default;
- keep downstream mapping hints non-authoritative;
- classify every requirement when current implementation or data-usage evidence exists;
- use current evidence for every alignment assertion and never let a historical
  framework alone prove present coverage;
- give every unlinked current measurement an explicit disposition;
- prohibit sensitive fields and flag potential personal-data fields for review;
- keep dimension and requirement applicability within the linked KPI or
  journey scope, or provide an evidence-backed basis for intentional breadth.

Fail when a KPI cannot be calculated from the declared requirements or when a
material dependency is silent.

## Overall Gate

Set `overall` to:

- `pass` only when every component gate passes without exceptions;
- `pass_with_exceptions` when no component fails and at least one component has
  an explicit exception;
- `fail` when any component fails.

Do not deliver a failed framework as complete. A draft may still be useful, but
state the exact failed gates and required next evidence.

Treat computed gate facts as a check on the analyst-authored rationale, not a
replacement for it. Render candidate, maturity, reciprocity, applicability,
scope-diff, and exception counts beside the gate. Resolve any contradiction
before delivery; never parse persuasive prose as proof.
