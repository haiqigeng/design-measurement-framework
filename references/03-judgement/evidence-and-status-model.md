# Evidence And Status Model

## Contents

- [Separate five questions](#separate-five-questions)
- [Source roles](#source-roles)
- [Target state](#target-state)
- [Journey evidence states](#journey-evidence-states)
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

Reference evidence as `source_id` or `source_id#locator`. Use a URL, page,
section, sheet/cell, object ID, or other stable locator after `#`. Do not use
untraceable prose such as “seen on site.”

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
- exact missing or conflicting evidence;
- impact on objectives, KPIs, or requirements;
- disposition: `bounded`, `out_of_scope`, or `awaiting_evidence`;
- evidence references.

Require `pass_with_exceptions` for every gate materially affected by an open
exception.
