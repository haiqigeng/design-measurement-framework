# Adaptive Workflow

## Contents

- [0. Resolve the run](#0-resolve-the-run)
- [1. Build and close the journey model](#1-build-and-close-the-journey-model)
- [2. Identify objectives](#2-identify-objectives)
- [3. Derive KPIs](#3-derive-kpis)
- [4. Decompose measurement requirements](#4-decompose-measurement-requirements)
- [5. Judge and deliver](#5-judge-and-deliver)
- [Maintenance](#maintenance)

Use this workflow for creation, review, maintenance, and alignment tasks. Keep
the sequence fixed and activate only the evidence and business-model prompts
that apply.

## 0. Resolve The Run

Create a fresh run identity for a new framework. Resolve:

- scope claim: whole site or named journey subset;
- target sites, markets, audiences, and language;
- target state: `as_is`, `to_be`, or `hybrid`;
- supplied evidence and its role;
- previous framework and intended change when maintaining;
- current measurement evidence when alignment is requested or possible;
- safe production and non-production interaction boundaries;
- client-required objectives, KPIs, targets, and constraints.

Ask one consolidated intake only when the available request does not establish
these sufficiently. Accept unknown optional fields and record assumptions.
Never reuse another client's evidence or nearby artifacts merely because they
exist on disk or in session context.

Initialize a working draft with `scripts/init_framework.py` after resolving
scope. Treat its empty inventories and failed gates as explicit work remaining,
not as content to preserve or mechanically pass.

## 1. Build And Close The Journey Model

Read `journey-discovery-and-coverage.md` and `safe-interaction.md`.

1. Generate expected journey candidates from detected value streams and the
   applicable business-model prompts.
2. Build the bottom-up candidate universe from every available source.
3. Explore representative route, template, component, state, and funnel
   families interactively when safe and possible.
4. Capture material branches, failures, empty states, re-entry, and
   post-conversion behavior.
5. Resolve every discovery candidate as mapped, merged, excluded, or
   unresolved with a named exception.
6. Build the final journey inventory and record evidence status separately
   from analyst resolution.
7. Apply the journey completeness and appropriateness gates.

Do not derive objectives from an open, silent material journey gap. Continue
with explicit exceptions when access or evidence cannot be obtained.

## 2. Identify Objectives

Read `objective-identification.md`.

1. Derive value streams and outcomes from the closed journey model and other
   business evidence.
2. Run the value-stream, lifecycle, stakeholder, and risk/guardrail sweeps.
3. Record one objective-consideration row for every considered topic.
4. Merge client-required objectives without erasing provenance or conflicts.
5. Deduplicate equivalent statements and retain the business vocabulary.
6. Classify each objective as confirmed, hypothesis, unsupported, or outside
   digital measurement scope.
7. Apply the objective completeness and appropriateness gates.

Do not present inferred objectives as confirmed corporate strategy.

## 3. Derive KPIs

Read `kpi-derivation.md`.

1. Define the outcome KPI candidates for each active objective.
2. Decompose outcomes into mathematically coherent drivers.
3. Consider guardrails for harmful or low-quality optimization.
4. Consider completion, step conversion, friction, and diagnostic metrics for
   every material journey.
5. Record every consideration, including rejected and not-applicable decisions.
6. Specify every accepted KPI precisely and select the recommended core.
7. Apply the KPI completeness and appropriateness gates.

Comprehensive means every justified need is considered and resolved. It does
not mean copying every metric from a library.

## 4. Decompose Measurement Requirements

Read `measurement-requirements-and-alignment.md`.

1. Decompose each KPI formula into observable or derivable components.
2. Resolve the source and collection mode for every component.
3. Resolve every segmentation dimension independently from transport.
4. Add non-UI, lifecycle, backend, and metric-support facts that formulas need.
5. Link every requirement bidirectionally to the KPIs it supports.
6. Add only non-authoritative downstream mapping hints.
7. When current tracking exists, classify every requirement and every unlinked
   current measurement.

Do not make a requirement disappear because it cannot be represented by a
manual browser event.

## 5. Judge And Deliver

Read the judgement references.

1. Reconcile IDs and traceability across all inventories.
2. Run every completeness and appropriateness gate.
3. Resolve failures or create bounded exceptions with affected IDs and impact.
4. Validate `measurement-framework.json` with the supplied validator.
5. Render Markdown from the valid canonical JSON.
6. Walk the user through the recommended core, assumptions, exceptions,
   alignment risks, and downstream dependencies.

Never describe `fail` as complete. Describe `pass_with_exceptions` as
coverage-closed only within its explicitly bounded evidence limitations.

## Maintenance

When a prior framework exists:

1. preserve stable IDs for unchanged entities;
2. compare scope, target state, sources, journeys, objective considerations,
   KPIs, dimensions, requirements, and exceptions;
3. refresh only affected evidence while rerunning all closure gates;
4. retain client-approved definitions unless new evidence creates a conflict;
5. deliver a complete current framework, not an addendum as the only source of truth.
