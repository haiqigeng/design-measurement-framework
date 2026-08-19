# Inputs And Outputs

## Minimum Input

Accept either:

- at least one in-scope URL; or
- a sufficiently concrete description of the site, product, service, journeys,
  or intended future experience when live access is unavailable.

Do not require the user to possess every optional input. Continue with explicit
assumptions, evidence requests, and bounded gaps when missing evidence does not
prevent honest progress.

## Intake Context

Resolve these fields in one consolidated intake when not already supplied:

- in-scope sites, sections, products, markets, audiences, and journey subset;
- `as_is`, `to_be`, or `hybrid` target state;
- production and safe non-production environments;
- access constraints and safe-interaction boundaries;
- existing journey maps, objectives, KPI definitions, or frameworks;
- business, product, design, technical, CRM, billing, support, lifecycle, or
  reporting evidence;
- existing tracking plans, dataLayer evidence, GTM exports, analytics event
  lists, or analytics exports when semantic alignment is relevant;
- client-required objectives, KPIs, targets, or reporting obligations; and
- delivery language and known consumers.

An existing tracking plan is optional current-measurement evidence, not a
request to create, update, or execute one. Do not request credentials, payment
details, or personal information for retention in artifacts. Ask for a
specific unblock only when it can materially change scope or meaning.

## Intake Baseline

For schema 1.3, create `intake_baseline` as the first artifact-writing action,
before browsing, aliasing, canonicalization, or exclusion. Preserve each
requested non-secret target and classify its disposition as:

- `included`: retained directly in delivery scope;
- `canonicalized`: represented by one or more equivalent resolved production
  scope targets with an explicit basis;
- `excluded_with_approval`: removed only with user evidence; or
- `unresolved`: retained as a scope exception until resolved.

Keep request evidence separate from resolution evidence. Use
`explicit_in_request`, `user_confirmed`, or `assumed` as the resolution basis;
an assumption requires an exact scope exception. The union of included and
canonicalized `resolved_scope_targets` must equal `document.target_sites` at
delivery.

Use `representative_source_ids` to connect production targets to live, UAT,
staging, document, or user sources used to investigate them. A shared UAT
origin may represent several production targets, but it never becomes the
production delivery scope merely because it is the browsed environment.

Record only categorical authorization, affected target IDs, constraints, and
evidence. Never copy passwords, account identifiers, personal values, tokens,
or other secrets into the baseline. Request user confirmation only for a
material transformation or ambiguity, not when the resolved scope is an
unchanged transcription of the request.

## Evidence Roles

Classify each source only by what it can prove:

| Source | Typical evidence role |
| --- | --- |
| Rendered live website | Current visible behavior and values |
| Staging or test website | Safely executable flow structure, subject to divergence |
| User or business brief | Required outcomes and intended decisions |
| Design or prototype | Intended future experience |
| Technical, API, CMS, CRM, billing documentation | Data capability and non-UI facts |
| Existing tracking plan, GTM, or dataLayer | Current implementation semantics or configuration |
| Analytics export | Observed collection symptoms and current data usage |
| Prior framework | Historical or approved measurement contract |

Do not let one source claim authority outside its role. Record conflicts and
resolve them according to target state without deleting the disagreement.
Directly observed or externally blocked current behavior also requires a
source observation time and a stable URL or evidence-reference locator.

## Canonical Machine Output

Produce `measurement-framework.json` conforming to
`schemas/measurement-framework.schema.json`. It is the sole source of truth and
contains:

- document scope, target state, language, and run identity;
- intake scope provenance, target dispositions, locales, and non-secret
  authorization boundaries;
- source inventory;
- journey-discovery candidates and resolutions;
- journey inventory with material states and variants;
- objective-consideration ledger and objective set;
- KPI-consideration ledger and precise KPI definitions;
- segmentation dimensions;
- semantic measurement requirements;
- optional current-measurement alignment;
- existing measurements not linked to the framework;
- assumptions, exceptions, and quality-gate results; and
- optional entity applicability where one framework covers multiple sites,
  products, markets, audiences, states, or variants.

Stable IDs and explicit relationships make the JSON usable by any authorized
machine consumer without requiring prose interpretation. The framework does
not invoke that consumer or change its own workflow for it.

## Human Output

Render `measurement-framework.md` only from valid canonical JSON. Present:

1. scope, target state, evidence boundaries, and gate status;
2. measurement-strategy and evidence-maturity summary;
3. intake-to-delivery scope provenance;
4. North Star and recommended-core KPIs;
5. material journey and objective coverage;
6. top missing or partial measurement needs;
7. evidence requests;
8. complete KPI definitions;
9. semantic measurement requirements and source or collection mode;
10. current-measurement alignment when applicable; and
11. assumptions, exclusions, unresolved boundaries, and implementation-independent notes.

Keep the Markdown decision-oriented. Do not expose raw browsing logs, internal
reasoning, schema mechanics, or generic measurement education unless requested.

## Authority And Change Rules

- JSON is canonical; Markdown is a derived review surface.
- If they disagree, JSON wins and Markdown must be regenerated.
- Do not maintain human tables independently from canonical objects.
- A human-approved change must be represented in JSON before rendering.
- Machine consumers use JSON rather than treating Markdown prose as a contract.
- The two core artifacts remain useful without any downstream workflow.

## Conditional Alignment Output

When current-measurement evidence exists, include one alignment decision for
every measurement requirement:

- `covered`;
- `partial`;
- `missing`; or
- `not_assessable`.

Also classify unlinked current measurements as `justified`,
`needs_justification`, or `out_of_scope`. Treat this as semantic business
alignment, not runtime certification or a full configuration audit.
