# Inputs And Outputs

## Intake

Accept either:

- at least one in-scope URL; or
- a sufficiently concrete description of the site, product, service, and
  journeys when live access is unavailable or the target state is future.

Resolve these fields in one consolidated intake when not already supplied:

- in-scope sites, sections, markets, audiences, and journey subset;
- `as_is`, `to_be`, or `hybrid` target state;
- production and safe non-production environments;
- access constraints and safe-interaction boundaries;
- existing journey maps, objectives, KPI definitions, or measurement frameworks;
- existing tracking plan, dataLayer evidence, GTM export, analytics event list,
  or analytics export;
- business, product, design, technical, CRM, billing, support, or lifecycle evidence;
- client-required objectives, KPIs, targets, or reporting obligations;
- delivery language and downstream consumers.

Do not require the user to possess every answer. Continue with explicit
assumptions and bounded gaps. Do not request credentials, payment details, or
personal information for retention in artifacts. Ask for a specific unblock
only when it changes material coverage.

## Evidence Roles

Classify each source only by what it can prove:

| Source | Typical evidence role |
| --- | --- |
| Rendered live website | Current visible behavior and values |
| Staging/test website | Safely executable flow structure, subject to divergence |
| User or business brief | Required outcomes and intended decisions |
| Design or prototype | Intended future experience |
| Technical, API, CMS, CRM, billing documentation | Data capability and non-UI facts |
| Existing tracking plan, GTM, or dataLayer | Current implementation semantics/configuration |
| Analytics export | Current data usage and observed collection symptoms |
| Prior framework | Historical or approved measurement contract |

Do not let one source claim authority outside its role. Record conflicts and
resolve them according to target state without deleting the disagreement.

## Canonical Output

Produce `measurement-framework.json` conforming to
`schemas/measurement-framework.schema.json`. Treat it as the source of truth.
Include:

- document scope, target state, language, and run identity;
- source inventory;
- journey-discovery candidates and resolutions;
- journey inventory with material states and variants;
- objective-consideration ledger and objective set;
- KPI-consideration ledger and KPI definitions;
- segmentation dimensions;
- semantic measurement requirements;
- optional current-measurement alignment;
- existing measurements not linked to the framework;
- assumptions, exceptions, and quality-gate results.

## Human Output

Render `measurement-framework.md` from the valid canonical JSON. Present:

1. scope, target state, evidence boundaries, and gate status;
2. material journey inventory;
3. objectives and their origin/evidence status;
4. recommended-core KPIs first, then supporting/guardrail/diagnostic metrics;
5. precise KPI definitions and formulas;
6. semantic measurement requirements and source/collection mode;
7. current-measurement alignment when applicable;
8. assumptions, exclusions, unresolved boundaries, and downstream notes.

Keep the human output decision-oriented. Do not expose raw browsing logs,
internal reasoning, schema mechanics, or generic measurement education unless
the user requests them.

## Conditional Alignment Output

When current tracking evidence exists, include one alignment decision for every
measurement requirement:

- `covered`;
- `partial`;
- `missing`; or
- `not_assessable`.

Also classify unlinked current measurements as `justified`,
`needs_justification`, or `out_of_scope`. Treat this as semantic business
alignment, not runtime certification or a full GTM audit.

