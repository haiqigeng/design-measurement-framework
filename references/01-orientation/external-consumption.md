# Optional External Consumption

Read this reference only when the user explicitly asks how another workflow
may consume a completed framework. External consumption is not a stage of the
measurement-framework workflow and creates no dependency on another skill.

## Canonical Contract

Supply the valid `measurement-framework.json`. Preserve:

- framework, journey, variant, objective, KPI, dimension, and requirement IDs;
- target state, scope, and optional applicability;
- source and evidence references;
- KPI formulas, grains, populations, windows, and decision uses;
- semantic facts and timing or state requirements;
- source-system and collection-mode expectations; and
- assumptions and exceptions that could affect another decision.

The Markdown is the human review surface, not the machine contract. If JSON and
Markdown disagree, JSON is authoritative and Markdown must be regenerated.

## Consumer Responsibilities

An external consumer must:

- validate the JSON and inspect its quality status before use;
- preserve stable IDs when retaining traceability;
- respect evidence boundaries, prohibited data, and safe-interaction limits;
- avoid silently redefining journeys, objectives, KPIs, formulas, or semantic
  requirements; and
- surface any newly discovered business-meaning conflict for human review.

The consumer decides how to represent or implement a semantic requirement. It
must not assume that every requirement belongs in a web analytics platform.

## Examples Of Independent Use

- Reporting or analysis consumes KPI IDs, formulas, grains, populations,
  windows, dimensions, sources, and assumptions as a calculation contract.
- Experiment design consumes objectives, KPI roles, guardrails, and applicable
  journeys as decision context.
- Current-measurement review consumes semantic requirements and alignment rows
  without treating configuration evidence as runtime proof.
- Analytics implementation may consume semantic requirements as business
  input while independently selecting platform semantics and technical design.

## Non-Integration Rule

This skill does not invoke, configure, modify, validate, or wait for an
external consumer. Do not add consumer-specific files, schemas, resolution
ledgers, or acceptance dependencies to the framework package.
