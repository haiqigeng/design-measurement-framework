# Evidence And Status Model

## Contents

- [Separate five questions](#separate-five-questions)
- [Source roles](#source-roles)
- [Evidence eligibility and durability](#evidence-eligibility-and-durability)
- [Target state](#target-state)
- [Journey evidence states](#journey-evidence-states)
- [Evidence maturity](#evidence-maturity)
- [Candidate and consideration resolutions](#candidate-and-consideration-resolutions)
- [Objective and KPI status](#objective-and-kpi-status)
- [Assumptions](#assumptions)
- [Exceptions](#exceptions)

## Separate Five Questions

Never collapse these questions into one status:

1. What source supplied the claim?
2. What can that source prove?
3. Does it describe current, future, or both states?
4. What is the factual evidence state?
5. What did the analyst decide to include, merge, exclude, or leave unresolved?

## Source Roles

Use:

- `live_behavior` for directly rendered or executed current behavior;
- `business_requirement` for intended outcomes, priorities, and decisions;
- `future_design` for planned experience;
- `current_implementation` for tracking or technical configuration;
- `data_capability` for available fields, systems, and source logic;
- `historical_contract` for prior approved definitions;
- `data_usage` for collected-data or reporting evidence.

Current-measurement alignment may use `current_implementation` and
`data_usage` evidence in their respective roles. A `historical_contract`
source may explain intended or prior semantics but cannot by itself establish
present coverage.

Reference evidence as `source_id` or `source_id#locator`. Use a specific source
URL, page, section, sheet/cell, object ID, state label, or other stable locator.
Do not use untraceable prose such as “seen on site.”

## Evidence Eligibility And Durability

For schema 1.3, apply these deterministic boundaries:

| Claim | Minimum eligible support |
| --- | --- |
| `observed` | `live_website` or `test_website`, role `live_behavior`, current-state source, `observed_at`, and a stable source URL or evidence-ref locator |
| `externally_blocked` | Direct live/test evidence in the applicable current or future state, with `observed_at` and a stable locator identifying the attempted boundary |
| `confirmed` | Credible user, business, technical, lifecycle, research, or data-capability evidence whose stated support matches the claim |
| `planned` | Future design or approved requirement evidence |
| `not_tested` | An honest absence of direct execution; do not invent attempt evidence |

Technical, API, route, CMS, CRM, billing, or other data-capability evidence may
confirm that a capability, field, route, or backend outcome exists. It cannot
be rendered as observed browser execution. User input may confirm a described
current state but never becomes direct observation merely because it is
credible.

Evidence eligibility governs maturity, not candidate recall. When direct
execution is blocked, retain candidates supported by credible technical,
lifecycle, business, design, historical, or user evidence and classify them at
the maturity that source can prove. Do not convert `not observed` into `does not
exist`.

Place `observed_at` on the source. When materially different retrieval times
matter, create separate source records. A source URL is sufficient when it is
the stable location of the claim; otherwise use the existing `#locator`
convention. Do not create screenshot or DOM bundles by default.

Test or staging evidence can support production-scoped analysis only through a
recorded representative-source binding, explicit equivalence assumption, or
bounded exception. Apply the same rule when one inspected locale is used for a
broader locale claim.

## Target State

Use:

- `as_is` for the currently evidenced experience;
- `to_be` for intended future measurement;
- `hybrid` when current and future states must remain distinguishable.

Resolve conflicts according to target state, but retain the conflict. Never let
future design prove current behavior or current production behavior erase an
approved future requirement.

## Journey Evidence States

Use:

- `observed`;
- `confirmed`;
- `planned`;
- `partial`;
- `not_tested`;
- `externally_blocked`.

Do not use `blocked` for a sample limit or unattempted work. Do not call user
input observed; classify the user as the source and use confirmed when credible.

## Evidence Maturity

Keep structural closure separate from empirical maturity. The renderer and
validator diagnostics derive status counts for journeys, variants, steps,
objectives, KPIs, and measurement requirements. These counts answer how much
is observed, confirmed, planned, partial, untested, blocked, verified, or
unverified; they are not a new readiness gate and do not replace record-level
evidence review.

Evidence maturity may be low while a framework is honestly coverage-closed
with exceptions. Never let a complete candidate inventory make an inferred
objective look confirmed or an unverified KPI look implemented.

## Candidate And Consideration Resolutions

Keep discovery-candidate resolution separate from factual state. Use:

- journey candidate: `mapped`, `merged`, `excluded`, `unresolved`;
- objective consideration: `objective_proposed`, `covered_by_existing`,
  `none_with_reason`, `out_of_scope`, `unresolved`;
- KPI consideration: `kpi_proposed`, `covered_by_existing`,
  `none_with_reason`, `not_applicable`, `unresolved`.

Require an explicit reason for every exclusion, merge, none, not-applicable, or
unresolved decision. Bind every unresolved material decision to an exception.

## Objective And KPI Status

Keep provenance and confidence orthogonal:

- origin: `client_required` or `inferred`;
- objective status: `confirmed`, `hypothesis`, `unsupported`, or
  `out_of_measurement_scope`;
- confidence: `high`, `medium`, or `low`;
- KPI evidence status: `verified`, `partially_verified`, or `unverified`.

Do not treat a client-required statement as verified merely because it is
mandatory. Do not silently discard an unsupported requirement.

## Assumptions

Create a stable assumption ID for every judgment used in place of evidence.
State the assumption, rationale, affected IDs, evidence references, and status:
`open`, `validated`, or `rejected`.

An open material assumption requires a gate exception. A rejected assumption
must not continue to support an active objective or KPI.

## Exceptions

Use an exception only for a bounded limitation, not to avoid analysis. Record:

- affected stage and IDs;
- applicability when the limitation is narrower than document scope;
- exact missing or conflicting evidence;
- impact on objectives, KPIs, or requirements;
- disposition: `bounded`, `out_of_scope`, or `awaiting_evidence`;
- evidence references.

Require `pass_with_exceptions` for every gate materially affected by an open
exception. The exception stage must match at least one affected entity, it may
affect only its own or downstream gates, and a declared applicability scope
must overlap each scoped entity it claims to affect. Feasibility and
materiality remain analyst judgments; free text is not treated as machine
proof of either.
