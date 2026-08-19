# Adaptive Workflow

## Contents

- [1. Resolve the run](#1-resolve-the-run)
- [2. Build and close the journey model](#2-build-and-close-the-journey-model)
- [3. Identify objectives](#3-identify-objectives)
- [4. Derive KPIs](#4-derive-kpis)
- [5. Decompose measurement requirements](#5-decompose-measurement-requirements)
- [6. Assess current measurement](#6-assess-current-measurement)
- [7. Judge and validate](#7-judge-and-validate)
- [8. Deliver and stop](#8-deliver-and-stop)
- [Maintenance](#maintenance)

Use this workflow for creation, review, maintenance, and semantic-alignment
tasks. Keep the sequence fixed and activate only the evidence and
business-model prompts that apply. The workflow ends with the standalone
framework artifacts.

## 1. Resolve The Run

Create a fresh run identity for a new framework. Before exploration or
normalization, transcribe the requested non-secret targets, scope, and
categorical authorizations into `intake_baseline`. This first record preserves
what was requested; aliases, canonicalizations, exclusions, assumptions, and
representative evidence sources are separate disposition fields rather than
rewrites of the request. Then resolve:

- scope claim: whole site or named journey subset;
- target sites, products, markets, audiences, and language;
- target state: `as_is`, `to_be`, or `hybrid`;
- supplied evidence and the role of each source;
- previous framework and intended change when maintaining;
- current-measurement evidence when semantic alignment is requested or possible;
- safe production and non-production interaction boundaries; and
- client-required objectives, KPIs, targets, and constraints.

Ask one consolidated intake only when the request does not establish these
sufficiently. Accept unknown optional fields and record assumptions. Never
reuse another client's evidence or nearby artifacts merely because they exist
on disk or in session context.

Do not ritualize confirmation. If the resolved production scope is unchanged,
the explicit request evidence is sufficient. If a target is canonicalized,
excluded, assumed, or otherwise materially transformed, obtain user evidence
or retain an exact scope exception. Keep production delivery targets in
`resolved_scope_targets`; connect a UAT, staging, or other investigation source
through `representative_source_ids`. Never store credentials or account values.

Initialize a working draft with `scripts/init_framework.py` after resolving
scope. Treat its empty inventories and failed gates as explicit work remaining,
not as content to preserve or mechanically pass.

Use optional entity applicability only when one framework contains materially
different sites, products, markets, audiences, current or future states, or journey
variants. Do not create a factoring or inheritance model for a simple scope.

## 2. Build And Close The Journey Model

Read `journey-discovery-and-coverage.md` and `safe-interaction.md`.

1. Generate expected journey candidates from detected value streams and the
   applicable business-model prompts.
2. Build the bottom-up candidate universe from every available source.
3. Explore representative route, template, component, state, and funnel
   families interactively when safe and possible.
4. When direct exploration is blocked or partial, continue conditionally with
   available technical routes or capabilities, lifecycle or business-system
   evidence, designs, historical contracts, and credible user descriptions.
   Let these sources confirm or plan mapped journeys without relabeling
   execution as observed.
5. Capture material branches, failures, empty states, re-entry, and
   post-conversion behavior.
6. Resolve every discovery candidate as mapped, merged, excluded, or
   unresolved with a named exception.
7. Build the final journey inventory and record evidence status separately
   from analyst resolution.
8. Record explicit decisions for failure, empty, recovery, re-entry, and
   post-conversion on each material journey. A decision may be covered, merged,
   not applicable, or unresolved; it does not force execution.
9. Run `scripts/candidate_census.py` when useful to expose unresolved material
   candidates, journeys without candidates, state-decision coverage, and
   production targets without representative sources.
10. Review the validator's discovery/evidence diagnostics for unused
    discovery-capable sources, intake-only material candidates, blocked
    journeys without fallback evidence, and environment or locale
    extrapolation.
11. Apply journey completeness and appropriateness gates.

Do not derive objectives from an open, silent material journey gap. Continue
with explicit exceptions when access or evidence cannot be obtained.

## 3. Identify Objectives

Read `objective-identification.md`.

1. Derive value streams and outcomes from the closed journey model and other
   business evidence.
2. Run value-stream, lifecycle, stakeholder, and risk or guardrail sweeps.
3. Record one objective-consideration row for every considered topic.
4. Merge client-required objectives without erasing provenance or conflicts.
5. Deduplicate equivalent statements and retain business vocabulary.
6. Classify each objective as confirmed, hypothesis, unsupported, or outside
   digital measurement scope.
7. Apply objective completeness and appropriateness gates.

Do not present inferred objectives as confirmed corporate strategy.

## 4. Derive KPIs

Read `kpi-derivation.md`.

1. Define outcome KPI candidates for each active objective.
2. Decompose outcomes into mathematically coherent drivers.
3. Consider guardrails for harmful or low-quality optimization.
4. Consider completion, step conversion, friction, and diagnostic metrics for
   every material journey.
5. Record every consideration, including rejected and not-applicable decisions.
6. Specify every accepted KPI precisely and select the recommended core.
7. Check rate numerator and denominator units, grains, eligible populations,
   and subset logic. Review cross-journey aggregation and broad North Star
   comparability rather than assuming unlike tasks can be averaged safely.
8. Apply KPI completeness and appropriateness gates.

Comprehensive means every justified need is considered and resolved. It does
not mean copying every metric from a library. Do not force one core KPI per
objective. Do not force a North Star when balanced outcomes are more honest.

## 5. Decompose Measurement Requirements

Read `measurement-requirements-and-alignment.md`.

1. Decompose each KPI formula into observable or derivable components.
2. Resolve the source and collection mode for every component.
3. Resolve every segmentation dimension independently from transport.
4. Add non-UI, lifecycle, backend, and metric-support facts that formulas need.
5. Link every requirement bidirectionally to the KPIs and dimensions it supports.
6. Keep implementation mapping outside the framework by default.

Do not make a requirement disappear because it cannot be represented by a
manual browser event.

## 6. Assess Current Measurement

Run this stage only when relevant current-measurement evidence exists.

1. Classify every requirement as `covered`, `partial`, `missing`, or
   `not_assessable`.
2. Link every assertion to current implementation or data-usage evidence.
3. Keep configuration, live payload, collected-data, and report-usage evidence
   distinct.
4. Classify every unlinked current measurement as `justified`,
   `needs_justification`, or `out_of_scope`.
5. Record exact gaps and the next evidence or action needed.

A historical framework alone does not prove current coverage. This stage is a
semantic assessment, not a technical audit or runtime certification.

## 7. Judge And Validate

Read the judgement references.

1. Reconcile stable IDs and bidirectional traceability across all inventories.
2. Run every completeness and appropriateness gate.
3. Verify KPI role, tier, core, North Star, formula, and dimension coherence.
4. Resolve failures or create bounded exceptions with affected IDs and impact.
5. Cite each exception from the quality gate it actually affects and from the
   overall gate.
6. Compare resolved delivery scope with the intake baseline and reject any
   unapproved substitution.
7. Resolve or explicitly accept every non-blocking discovery/evidence and KPI
   coherence advisory; a clean structural result is not proof that the
   candidate universe or KPI system is analytically sufficient.
8. Validate `measurement-framework.json` with the supplied validator. Use
   `--json` when reviewers need an artifact-bound hash, computed counts,
   advisories, and gate facts that can be reproduced independently.

Never describe `fail` as complete. Describe `pass_with_exceptions` as
coverage-closed only within its explicitly bounded evidence limitations.

## 8. Deliver And Stop

1. Render Markdown only from valid canonical JSON.
2. Walk the user through the recommended core, material coverage, evidence
   requests, assumptions, exceptions, and measurement dependencies.
3. Deliver `measurement-framework.json` and `measurement-framework.md`.
4. Stop. Do not invoke or continue into another workflow.

The framework remains independently useful. An external user or orchestrator
may later supply its JSON to another authorized workflow, but that is not part
of this skill.

## Maintenance

When a prior framework exists:

1. preserve stable IDs for unchanged entities;
2. capture the maintenance request as the current run's intake baseline and
   preserve the prior framework as historical evidence;
3. compare scope, target state, sources, journeys, objective considerations,
   KPIs, dimensions, requirements, alignment, and exceptions;
4. refresh only affected evidence while rerunning every closure gate;
5. retain client-approved definitions unless new evidence creates a conflict;
6. deliver one complete current canonical file and regenerated Markdown, not
   an addendum as the only source of truth.
