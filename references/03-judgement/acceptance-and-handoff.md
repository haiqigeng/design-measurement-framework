# Acceptance And Handoff

## Acceptance States

Use:

- `pass` when every gate passes and no material exception remains;
- `pass_with_exceptions` when every material candidate is resolved or bounded
  and all remaining limitations are explicit;
- `fail` when a material layer remains structurally or silently unresolved.

Do not call `pass_with_exceptions` fully verified. Do not call a useful failed
draft complete.

## Pre-Delivery Review

Confirm:

- declared scope and target state match the request;
- source roles do not overclaim what evidence proves;
- discovery candidates cover top-down expectations and bottom-up evidence;
- material variants and non-UI outcomes were considered;
- objectives are locally evidenced or explicitly client-required;
- KPI formulas, grains, populations, and windows are coherent;
- recommended-core KPIs remain balanced by relevant guardrails;
- all components and dimensions map to semantic requirements;
- current measurement alignment is complete when applicable;
- assumptions, exclusions, and exceptions are visible;
- no sensitive value, credential, or personal-data example is retained;
- no downstream mapping hint is presented as final GA4 semantics;
- schema and cross-reference validation pass;
- rendered Markdown agrees with canonical JSON.

## Human Handoff

Lead with:

1. overall gate status and scope;
2. recommended core;
3. material journey and objective coverage;
4. top missing/partial measurement requirements;
5. exceptions and their decision impact;
6. downstream dependencies.

Keep the full KPI system and requirement inventory available for analyst
review. Do not hide supporting or diagnostic metrics that survived the
appropriateness gates.

## Machine Handoff

Supply the canonical JSON and preserve stable IDs. Bind any rendered Markdown
or downstream manifest to the canonical file hash when a later integration
requires durable provenance.

For the GA4 tracking-plan handoff, treat `measurement_requirements` as the
authoritative inventory of what must be resolved. Treat
`downstream_mapping_hint` as advisory only. Do not require the downstream skill
to send every requirement to GA4; require it to account for every requirement
through the correct collection or derivation mechanism.

## Maintenance Handoff

When superseding a framework, deliver one complete current canonical file.
Preserve stable IDs, note material changes, and retain the prior file as
historical evidence. Do not deliver an addendum as the only source of truth.
