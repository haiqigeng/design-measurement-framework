# Acceptance And Delivery

## Acceptance States

Use:

- `pass` when every gate passes and no material exception remains;
- `pass_with_exceptions` when every material candidate is resolved or bounded
  and all remaining limitations are explicit; and
- `fail` when a material layer remains structurally or silently unresolved.

Do not call `pass_with_exceptions` fully verified. Do not call a useful failed
draft complete.

## Pre-Delivery Review

Confirm:

- declared scope and target state match the request;
- source roles do not overclaim what evidence proves;
- discovery candidates cover top-down expectations and bottom-up evidence;
- material journeys, variants, states, and non-UI outcomes were considered;
- objectives are locally evidenced or explicitly client-required;
- objective and journey KPI-role considerations are complete;
- KPI roles, tiers, North Star choices, formulas, grains, populations, and
  windows are coherent;
- recommended-core KPIs remain balanced by relevant guardrails;
- all components and required dimensions map to semantic requirements;
- current-measurement alignment is complete when applicable;
- assumptions, exclusions, evidence requests, and exceptions are visible;
- every exception is cited by the gate it affects and by the overall gate;
- no sensitive value, credential, or personal-data example is retained;
- no platform-specific implementation decision is presented as approved;
- schema and cross-reference validation pass; and
- rendered Markdown agrees with canonical JSON.

## Human Delivery

Lead with:

1. overall gate status and scope;
2. measurement-strategy summary;
3. North Star and recommended core;
4. material journey and objective coverage;
5. top missing or partial measurement needs;
6. evidence requests and exceptions; and
7. the full KPI and requirement inventories for detailed review.

Do not hide supporting, guardrail, or diagnostic metrics that survived the
appropriateness gates.

## Machine Delivery

Supply the canonical JSON with stable IDs. JSON is authoritative; Markdown is
a generated human view. A machine consumer must use the JSON rather than infer
the contract from prose.

The framework does not require a consumer-specific manifest. Bind a rendered
view or external manifest to the canonical file hash only when a later,
separate integration genuinely requires durable provenance.

## Maintenance Delivery

When superseding a framework, deliver one complete current canonical file and
regenerated Markdown. Preserve stable IDs, note material changes, and retain
the prior file as historical evidence. Do not deliver an addendum as the only
source of truth.
