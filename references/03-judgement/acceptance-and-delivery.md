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

- every requested non-secret target has an intake disposition and the resolved
  production delivery scope exactly matches included and canonicalized targets;
- target state, scope claim, products, markets, audiences, and locales agree
  between the intake baseline and resolved document;
- representative UAT or staging sources have not replaced production scope;
- source roles do not overclaim what evidence proves;
- every `observed` or `externally_blocked` claim has eligible direct evidence,
  source observation time, and a stable locator;
- discovery candidates cover top-down expectations and bottom-up evidence;
- a direct access failure did not stop available technical, lifecycle,
  business, design, historical, or credible user discovery, and every supported
  material family remains visible at an honest maturity;
- discovery/evidence diagnostics for unused sources, intake-only candidates,
  blocked paths, direct-scope attribution, environment equivalence, and locale
  equivalence were reviewed;
- material journeys, variants, states, and non-UI outcomes were considered;
- every material journey explicitly resolves failure, empty, recovery,
  re-entry, and post-conversion states;
- objectives are locally evidenced or explicitly client-required;
- objective and journey KPI-role considerations are complete;
- KPI roles, tiers, North Star choices, formulas, grains, populations, and
  windows are coherent;
- rate numerator and denominator units, grains, eligible populations, and
  subset logic are coherent, and cross-journey aggregates do not hide unlike
  task or value mixes;
- a broad North Star has a defensible aggregation and mix-shift rationale, or
  the framework honestly uses no North Star;
- recommended-core KPIs remain balanced by relevant guardrails;
- all components and required dimensions map to semantic requirements;
- current-measurement alignment is complete when applicable;
- assumptions, exclusions, evidence requests, and exceptions are visible;
- applicability overreach has an evidence-backed basis and consideration-to-KPI
  links are reciprocal;
- every exception is cited by the gate it affects and by the overall gate;
- exception stage, gate direction, and declared applicability are structurally
  compatible with affected entities;
- no sensitive value, credential, or personal-data example is retained;
- no platform-specific implementation decision is presented as approved;
- schema and cross-reference validation pass; and
- rendered Markdown agrees with canonical JSON.

## Human Delivery

Lead with:

1. overall gate status and scope;
2. measurement-strategy and evidence-maturity summary;
3. intake-to-delivery scope provenance;
4. North Star and recommended core;
5. material journey and objective coverage;
6. top missing or partial measurement needs;
7. evidence requests and exceptions; and
8. the full KPI and requirement inventories for detailed review.

Do not hide supporting, guardrail, or diagnostic metrics that survived the
appropriateness gates.

## Machine Delivery

Supply the canonical JSON with stable IDs. JSON is authoritative; Markdown is
a generated human view. A machine consumer must use the JSON rather than infer
the contract from prose.

When reproducible review is needed, also run validator `--json`. Its artifact
hash, versions, maturity counts, candidate census, gate facts, errors, and
advisories must be generated from the delivered JSON. This diagnostic output
is not a third core artifact and does not supersede canonical JSON.

The framework does not require a consumer-specific manifest. Bind a rendered
view or external manifest to the canonical file hash only when a later,
separate integration genuinely requires durable provenance.

## Maintenance Delivery

When superseding a framework, deliver one complete current canonical file and
regenerated Markdown. Preserve stable IDs, capture the maintenance request as
the current run's intake baseline, note material scope and semantic changes,
and retain the prior file as historical evidence. Do not deliver an addendum
as the only source of truth.
