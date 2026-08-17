# Cross-Skill Handoff

## GA4 Tracking Plan

Hand off the valid `measurement-framework.json` as the upstream business
measurement contract. Preserve:

- framework, journey, objective, KPI, dimension, and requirement IDs;
- target state and scope;
- source and evidence references;
- semantic facts and timing/state requirements;
- source-system and collection-mode expectations;
- non-authoritative GA4 mapping hints when present;
- assumptions and exceptions that can change implementation.

Require the downstream tracking-plan workflow to resolve every measurement
requirement as one of:

- a manual GA4 event or parameter;
- native analytics context;
- backend or server-side measurement;
- CRM, billing, support, or warehouse fact;
- joined or reporting-time derivation;
- an explicit exclusion with reason; or
- an unresolved implementation dependency.

Do not treat a `downstream_mapping_hint` as approved semantics. Let the
tracking-plan workflow check current official documentation, select official or
custom events, define exact triggers and fields, and author the dataLayer.

For this first version, do not modify the existing `ga4-tracking-plan` skill.
Treat direct machine ingestion as the next integration phase after this
contract has been forward-tested.

## GTM Preview Recette

Provide journey IDs, material variants, outcome/failure states, and explicit
coverage boundaries as test-scenario guidance. Do not provide expected runtime
events directly from this framework. Let the approved tracking plan remain the
event-level acceptance authority.

## Guided Analytics

Provide KPI IDs, formulas, grains, populations, windows, dimensions, source
systems, assumptions, and evidence status as the calculation contract. Do not
let downstream analysis silently redefine a KPI.

## GTM Audit Or Current Measurement Evidence

Consume read-only inventories as current-implementation evidence. Use them to
assess semantic coverage, not to infer that configured tags fired correctly or
that vendor reporting received the data.

## Privacy Or Consent Review

Flag a dimension or requirement as `review_required` or `prohibited` when
potential personal or sensitive data is detected. Do not make the legal
decision. Never recommend a prohibited field as a downstream measurement input.
