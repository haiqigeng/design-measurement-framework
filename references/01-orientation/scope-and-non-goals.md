# Scope And Non-Goals

## In Scope

Create, review, update, or compare a web measurement framework covering:

- material user and customer journeys;
- current, planned, or hybrid digital outcomes;
- client-required and evidence-inferred objective hypotheses;
- north-star candidates when appropriate;
- outcome, driver, guardrail, supporting, and diagnostic metrics;
- precise KPI calculation contracts;
- browser, backend, lifecycle, business-system, native, joined, and derived
  measurement requirements;
- semantic alignment of current measurement with those requirements;
- explicit assumptions, exclusions, and evidence boundaries.

Treat web and adjacent backend/business-system facts as in scope when they are
needed to evaluate web outcomes. Do not silently force every fact into GA4.

## Out Of Scope

Do not:

- select or approve final GA4 event and parameter semantics;
- verify current Google documentation for final event implementation;
- author event-level dataLayer contracts or developer tickets;
- configure, audit, clean, version, or publish GTM;
- execute GTM Preview, browser-network recette, DebugView, or runtime certification;
- build dashboards, reports, SQL models, or attribution models;
- invent targets, forecasts, baselines, or industry benchmarks;
- treat a benchmark as comparable without current source and methodology review;
- decide legal basis, consent validity, or privacy acceptability;
- collect or retain credentials, payment data, or personal information;
- mutate production data, send real communications, place orders, book
  appointments, or create consequential commitments;
- invoke, modify, redesign, or depend on another skill.

## Boundary Decisions

This skill ends after delivering the validated framework JSON and its rendered
Markdown. If the user also requested implementation or another analytics
artifact, treat that as separate work outside this skill. Do not add routing,
invocation, or downstream execution to the framework workflow.

When the user supplies an approved, current framework, review its scope and
freshness instead of rebuilding it automatically. Refresh only the affected
journeys, objectives, KPIs, or requirements when the business or product has
materially changed.

When a requested KPI depends primarily on another platform or offline process,
retain it when it expresses a relevant web outcome. Identify the external
source and join or derivation dependency rather than excluding it merely
because a web analytics platform cannot calculate it alone.
