---
name: design-measurement-framework
description: Design, review, and maintain evidence-backed web measurement frameworks that close material journey, objective, KPI, and semantic measurement-requirement coverage. Use when users need to determine what matters, define how success should be measured, govern KPIs, or assess current measurement against business needs. Produce canonical JSON and decision-oriented Markdown. Do not use for tracking-plan creation, analytics implementation, GTM, runtime QA, dashboards, targets, or legal decisions.
---

# Design Measurement Framework

## North Star

> Turn incomplete business, website, and technical evidence into a
> coverage-closed, decision-ready measurement framework: account for every
> material journey and plausible digital objective in scope, derive the
> complete set of justified and precisely defined KPIs, and trace every KPI to
> the observable facts and dimensions needed to calculate and interpret it.
> Make every omission an explicit exclusion or evidence boundary, so
> measurement decisions remain complete, purposeful, and auditable.

Apply one governing rule throughout:

> Everything material is accounted for; everything proposed is justified.

Optimize completeness and appropriateness together. Do not trade one for the
other. Treat completeness as closure against a deliberately constructed
candidate universe, not as a claim that inaccessible behavior was observed.

## Product And Users

Produce a standalone, platform-independent business measurement contract. It
is primarily for web analysts, measurement strategists, analytics leads, and
the business stakeholders who review objectives and KPIs. Analytics,
reporting, experimentation, and implementation teams may consume the result,
but no downstream workflow defines this skill's process or acceptance.

Answer:

1. Which outcomes matter?
2. Which material journeys contribute to them?
3. Which KPIs express outcomes, drivers, guardrails, and useful diagnostics?
4. How is every KPI calculated and used for a decision?
5. Which facts, dimensions, systems, or derivations are required?
6. Which current measurements support or fail those needs?
7. Which evidence boundaries could change the answer?

## Inputs And Outputs

Accept at minimum an in-scope URL or a sufficiently concrete description of
the website, product, service, journeys, or intended future experience. Resolve
scope, target state, markets, audiences, evidence roles, supplied objectives or
KPIs, and safe-interaction boundaries when available. Continue with explicit
assumptions and bounded gaps when optional evidence is absent.

Produce exactly two core artifacts:

- `measurement-framework.json` is the canonical machine-readable source of truth;
- `measurement-framework.md` is the human review surface rendered from that JSON.

If they disagree, JSON wins and Markdown must be regenerated. Human-approved
changes must be represented in JSON before rendering. Other tools may consume
the JSON, but this skill neither invokes nor adapts itself to them.

## One Adaptive Workflow

Use one workflow and one quality standard for creation, review, maintenance,
and semantic-alignment work:

1. Resolve scope, target state, evidence roles, and safe boundaries.
2. Build and close the material journey model.
3. Identify and assess objective candidates.
4. Derive and validate the KPI system.
5. Decompose KPIs into semantic measurement requirements.
6. Assess current measurement when relevant evidence exists.
7. Apply completeness, appropriateness, traceability, and exception gates.
8. Validate JSON, render Markdown, deliver, and stop.

Let evidence change how a step is executed, never whether journey, objective,
KPI, and requirement closure are assessed. Do not introduce lightweight,
standard, enterprise, event-count, or time-boxed quality modes.

Ask one consolidated intake when essential context is missing. Ask later only
for a specific access unblock, a consequential safe-interaction decision, or
an ambiguity that could materially change scope or meaning. Mark every
assumption and evidence boundary explicitly.

## Reference Routing

Load only the references needed for the current task:

- Product identity or audience questions: [product contract](references/01-orientation/product-contract.md).
- Intake, evidence roles, or delivery format: [inputs and outputs](references/01-orientation/inputs-and-outputs.md).
- Full creation, review, or maintenance: [adaptive workflow](references/02-execution/adaptive-workflow.md).
- Journey work: [journey discovery and coverage](references/02-execution/journey-discovery-and-coverage.md)
  and [safe interaction](references/02-execution/safe-interaction.md).
- Objective work: [objective identification](references/02-execution/objective-identification.md).
- KPI work: [KPI derivation](references/02-execution/kpi-derivation.md).
- Requirement or current-measurement work:
  [measurement requirements and alignment](references/02-execution/measurement-requirements-and-alignment.md).
- Evidence, assumptions, or confidence:
  [evidence and status model](references/03-judgement/evidence-and-status-model.md).
- Validation or final delivery: [completeness and appropriateness gates](references/03-judgement/completeness-and-appropriateness-gates.md),
  [framework contract](references/03-judgement/framework-contract.md), and
  [acceptance and delivery](references/03-judgement/acceptance-and-delivery.md).
- Scope pressure from implementation, reporting, benchmarking, privacy, or QA:
  [scope and non-goals](references/01-orientation/scope-and-non-goals.md).
- Explicit questions about external consumption only:
  [optional external consumption](references/01-orientation/external-consumption.md).

Load [business-model prompts](references/02-execution/business-model-prompts.md)
only for the detected model or value stream. Treat prompts as candidate
generators, never as mandatory objective or KPI lists.

Use [the minimal valid framework](tests/fixtures/valid-minimal.json) only as a
structural authoring example. Replace every example-specific value and never
reuse its conclusions as client evidence.

## Core Distinctions

- A journey is an evidence-backed, goal-directed path, not a URL list.
- An objective is a required or inferred outcome hypothesis, not a generic phrase.
- A KPI is a decision-useful indicator, not every available metric.
- A measurement requirement is a semantic fact or dimension that must be
  observable, not an analytics event, parameter, or implementation field.
- A candidate inventory supports completeness; analyst resolution establishes
  appropriateness.
- Current-measurement alignment assesses semantic business coverage, not
  configuration quality or runtime behavior.

Retain browser, backend, lifecycle, business-system, native, joined, and
derived requirements when they are needed. Never force every fact into a web
analytics platform.

## Authoring And Delivery

Initialize a non-overwriting working draft:

```powershell
python scripts/init_framework.py --title "Website measurement framework" --scope "Whole public website" --site https://www.example.com/ --output measurement-framework.json
```

The draft intentionally starts incomplete with failed gates. Replace every
empty inventory through evidence-backed analysis; never change a gate merely
to satisfy validation.

Validate and render only after analysis is complete:

```powershell
python scripts/validate_framework.py measurement-framework.json --delivery
python scripts/render_framework.py measurement-framework.json --output measurement-framework.md
```

Use validator `--json` only when machine-readable diagnostics are useful. Use
renderer `--allow-failed` only to inspect a structurally complete working
draft; never treat that output as an accepted delivery.

Declare the result ready only when every mandatory gate is `pass` or
`pass_with_exceptions`, every exception is explicit and correctly linked, all
traceability closes, and Markdown agrees with JSON. A useful failed draft is
still a draft. `pass_with_exceptions` is never fully verified.

## Boundaries

Stop after creating, reviewing, maintaining, or semantically aligning the
measurement framework and delivering its JSON and Markdown artifacts. Do not:

- create an analytics-platform tracking plan or select final events and parameters;
- define exact triggers, value domains, dataLayer contracts, or developer tickets;
- configure, audit, clean, version, or publish GTM;
- execute Preview, DebugView, browser-network QA, or runtime certification;
- build dashboards, reports, SQL models, or attribution models;
- invent targets, forecasts, baselines, or benchmarks;
- make legal, privacy, consent, or data-processing decisions;
- collect credentials, payment data, or personal information;
- mutate production data or create communications, orders, bookings, accounts,
  or other consequential commitments;
- invoke, modify, or depend on another skill.
