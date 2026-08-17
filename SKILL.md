---
name: design-measurement-framework
description: Design, review, and maintain evidence-backed web measurement frameworks that close material journey, objective, KPI, and data-requirement coverage before tracking-plan design. Use when a user asks what to measure, requests website objectives or KPIs, wants a north-star/driver/guardrail framework, needs complete journey-to-KPI traceability, or wants current tracking assessed against business needs. Produce canonical framework JSON and human-readable Markdown, including non-UI facts and downstream measurement requirements. Do not finalize GA4 event or parameter semantics, write dataLayer specifications, configure GTM, perform runtime QA, build dashboards, invent targets, or make legal decisions.
---

# Design Measurement Framework

## North Star

> Turn incomplete website, business, and technical evidence into a
> coverage-closed, decision-ready measurement framework: identify every
> material journey and plausible digital objective in scope, propose the
> complete set of justified and precisely defined KPIs, and trace every KPI
> to the observable facts and dimensions required downstream. Make every
> omission an explicit exclusion or evidence boundary, so the tracking plan
> cannot silently miss a meaningful measurement need or introduce measurement
> without a business purpose.

Apply one governing rule throughout:

> Everything material is accounted for; everything proposed is justified.

Optimize completeness and appropriateness together. Do not trade one for the
other. Treat completeness as closure against a deliberately constructed
candidate universe, not as a claim that inaccessible behavior was observed.

## One Adaptive Workflow

Use one workflow and one quality standard. Let available evidence change how
each step is executed, never whether journey, objective, KPI, and requirement
closure are assessed. Do not introduce lightweight, standard, enterprise,
event-count, or time-boxed quality modes.

Ask one consolidated intake when essential context is missing. Then proceed by
inference. Ask later only for a specific access unblock, a consequential safe-
interaction decision, or an ambiguity that could materially change scope or
meaning. Mark every assumption and evidence boundary explicitly.

## Load References Progressively

Always read:

- [product contract](references/01-orientation/product-contract.md);
- [inputs and outputs](references/01-orientation/inputs-and-outputs.md);
- [adaptive workflow](references/02-execution/adaptive-workflow.md);
- [completeness and appropriateness gates](references/03-judgement/completeness-and-appropriateness-gates.md);
- [framework contract](references/03-judgement/framework-contract.md).

Load immediately before the relevant stage:

- Discover journeys: [journey discovery and coverage](references/02-execution/journey-discovery-and-coverage.md)
  and [safe interaction](references/02-execution/safe-interaction.md).
- Identify objectives: [objective identification](references/02-execution/objective-identification.md).
- Derive KPIs: [KPI derivation](references/02-execution/kpi-derivation.md).
- Decompose requirements or compare existing tracking:
  [measurement requirements and alignment](references/02-execution/measurement-requirements-and-alignment.md).
- Classify evidence, assumptions, gaps, or confidence:
  [evidence and status model](references/03-judgement/evidence-and-status-model.md).
- Deliver or hand off: [acceptance and handoff](references/03-judgement/acceptance-and-handoff.md)
  and [cross-skill handoff](references/01-orientation/cross-skill-handoff.md).

Load [business-model prompts](references/02-execution/business-model-prompts.md)
only for the detected model or value stream. Treat prompts as candidate
generators, never as mandatory objectives or KPI lists.

Use [the minimal valid framework](tests/fixtures/valid-minimal.json) only as a
structural authoring example. Replace every example-specific value and never
reuse its conclusions as client evidence.

## 01 - Orientation

Answer what matters, why it matters, how success is calculated, and what must
be observable. Stop before deciding the final analytics implementation.

Treat the canonical `measurement-framework.json` as the source of truth. Treat
the rendered Markdown as its human review surface. Preserve stable IDs and
source references so downstream skills can consume the framework without
reinterpreting prose.

Keep these distinctions explicit:

- A journey is an evidence-backed, goal-directed path, not a URL list.
- An objective is a required or inferred business outcome hypothesis, not a
  generic library phrase.
- A KPI is a decision-useful performance indicator, not every available
  metric.
- A measurement requirement is a semantic fact or dimension that must be
  observable, not a finalized GA4 event, parameter, or dataLayer field.
- A candidate inventory supports completeness; analyst resolution establishes
  appropriateness.

Read [scope and non-goals](references/01-orientation/scope-and-non-goals.md)
whenever the request approaches tracking-plan, implementation, dashboard,
benchmark, privacy, or runtime-QA work.

## 02 - Execution

For a new framework, initialize a non-overwriting working draft before
authoring the canonical inventories:

```powershell
python scripts/init_framework.py --title "Website measurement framework" --scope "Whole public website" --site https://www.example.com/ --output measurement-framework.json
```

The draft is intentionally incomplete and starts with failed gates. Replace
every empty inventory through evidence-backed analysis; never change a gate to
pass merely to satisfy validation.

### 0. Resolve intake and target state

Resolve scope, sites, markets, target state, available environments, supplied
evidence, existing measurement, client-required objectives or KPIs, language,
and safe-test boundaries. Accept a URL or sufficiently concrete site
description as the minimum starting point. Continue with explicit assumptions
when optional evidence is absent.

### 1. Close journey coverage

Build an expected top-down journey map and a bottom-up candidate census. Use
rendered interaction when available; do not rely on static scraping for
dynamic journeys. Map every material candidate to a journey, merge it into an
equivalent family, exclude it with reason, or bind its unresolved state to an
exception. Cover material entry, progression, success, failure, empty,
re-entry, and post-conversion states when applicable.

Do not start objective or KPI derivation while a material journey candidate is
silently unresolved. Continue with named exceptions when direct closure is not
possible.

### 2. Identify objective candidates

Infer value streams from the journey model and all applicable evidence. Run
value-stream, lifecycle, stakeholder, and risk/guardrail sweeps. Record a
decision for every considered area, including `none_with_reason` and
`out_of_scope`. Preserve client-required objectives even when unsupported;
flag the tension instead of silently correcting the client.

Phrase inferred objectives as evidence-backed hypotheses in the business's own
language. Avoid claiming that a website alone proves corporate strategy.

### 3. Derive the KPI system

For every active objective, consider outcome, driver, and guardrail metrics.
For every material journey, consider completion, step-conversion, friction,
and diagnostic needs. Propose only metrics that survive the appropriateness
tests, while recording rejected or not-applicable considerations so
completeness remains visible.

Specify formula, components, counting unit, grain, population, reporting
window, inclusions, exclusions, segmentation decision, direction, decision
use, owner role, evidence status, and recommended-core status. Validate the
formula dimensionally; do not use a familiar driver identity when its grains
do not reconcile.

### 4. Decompose measurement requirements and align current tracking

Map every KPI formula component and required segmentation dimension to a
semantic measurement requirement. Include browser-visible actions, metric-
support observations, backend outcomes, lifecycle facts, business-system
facts, native analytics context, joins, and derived fields as applicable.

Do not turn every requirement into a manual web event. Do not turn every
dimension into an event parameter. Record the expected source system and
collection mode. Keep any downstream GA4 mapping as a non-authoritative hint.

When current tracking evidence exists, classify each requirement as
`covered`, `partial`, `missing`, or `not_assessable`. Record existing
measurements with no framework link as justified, needing justification, or
out of scope. Do not call configuration evidence runtime proof.

### 5. Judge, validate, and deliver

Apply every completeness and appropriateness gate. Resolve failures or list a
named exception with affected IDs and decision impact. Never label a framework
complete when a gate fails or a material gap is unreported.

Validate the canonical file:

```powershell
python scripts/validate_framework.py measurement-framework.json --delivery
```

Render the human review surface only from a valid canonical file:

```powershell
python scripts/render_framework.py measurement-framework.json --output measurement-framework.md
```

Deliver the canonical JSON, rendered Markdown, and any source evidence that is
safe and useful to retain. Include the alignment section only when existing
measurement was supplied.

## 03 - Judgement

Use deterministic validation for schema, IDs, references, bidirectional
traceability, mandatory consideration rows, unresolved-candidate exceptions,
and gate consistency. Use analyst judgment for materiality, evidence strength,
objective relevance, KPI actionability, formula fitness, and proportional
coverage.

Reject these failure patterns:

- a material journey, objective area, KPI role, or formula component omitted
  without a recorded decision;
- a generic objective or KPI copied from a library without local evidence;
- a KPI that supports no plausible decision or action;
- a KPI formula with incompatible grain, population, or time basis;
- a dimension automatically treated as an event parameter;
- a backend or lifecycle fact silently dropped because it is not visible in
  the UI;
- a current event declared unnecessary merely because it does not support a
  primary KPI;
- a final GA4 event name, parameter contract, or dataLayer specification
  presented as approved by this skill;
- a `pass` gate hiding an exception, assumption, or unobserved material state.

Use `pass_with_exceptions` only when every exception is explicit, bounded, and
linked to affected framework IDs. Use `fail` when a material layer remains
silently or structurally unresolved.

## Boundaries

Stop after creating, reviewing, or maintaining the measurement framework and
its semantic alignment assessment. Do not modify the existing
`ga4-tracking-plan` skill in this version. Do not author the final tracking
plan, implement GTM, certify runtime behavior, build reports, manufacture
benchmarks or targets, or decide legal/privacy acceptability.
