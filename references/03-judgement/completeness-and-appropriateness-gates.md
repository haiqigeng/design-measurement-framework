# Completeness And Appropriateness Gates

## Contents

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

## Journey Completeness

Require all of the following:

- resolve every material top-down and bottom-up discovery candidate;
- map every scanned navigation, CTA, form, template, entry, and endpoint family
  to a journey, merge, exclusion, or exception;
- include every material expected journey or record why it is absent;
- represent material variants separately when their paths or measurement needs differ;
- record decisions for success, failure, empty, re-entry, and post-conversion states;
- link every partial, not-tested, or externally blocked material state to an exception;
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
- identify a recommended core without deleting justified supporting metrics;
- bind every unresolved material consideration to an exception.

Fail when a KPI is omitted because its supporting fact is not visible in the UI.

## KPI Appropriateness

Require every accepted KPI to:

- trace to a primary objective and any additional supported objectives;
- support a plausible decision and action;
- have a coherent owner role;
- use a dimensionally valid formula, grain, population, and time basis;
- avoid vanity, duplicate, and redundant definitions;
- use guardrails where optimizing the KPI can plausibly degrade quality or value;
- distinguish KPI, driver, and diagnostic roles honestly;
- avoid invented targets and unsupported benchmarks;
- state evidence and assumption status.

Fail when two analysts could reasonably calculate different values from the
same written definition.

## Requirement Traceability

Require all of the following:

- map every KPI formula component to a requirement;
- map every requirement back to at least one KPI;
- resolve every required dimension and source/collection mode;
- retain backend, lifecycle, business-system, native, joined, and derived needs;
- prevent a dimension from becoming an event parameter by default;
- keep downstream mapping hints non-authoritative;
- classify every requirement when current tracking evidence exists;
- give every unlinked current measurement an explicit disposition;
- prohibit sensitive fields and flag potential personal-data fields for review.

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
