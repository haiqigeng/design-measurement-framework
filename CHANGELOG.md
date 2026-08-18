# Changelog

## [1.2.0] - 2026-08-18

### Added

- Schema `1.2.0` structured formula fields for calculation type, result unit,
  component symbols, per-component counting units, and component grain.
- Safe formula-expression validation across counts, sums, rates, averages,
  weighted averages, percentiles, cohorts, retention, and composite or index
  calculations.
- Material-journey entry and success closure with bounded journey exceptions.
- Conditional recommended-core guardrail balance when an objective's guardrail
  consideration resolves to a real KPI.
- Non-blocking duplicate-KPI advisories based on calculation, population,
  scope, dimensions, and semantic requirements.

### Compatibility

- Schema `1.0.0` and `1.1.0` artifacts retain their prior acceptance behavior.
- No analytics-platform event, parameter, trigger, dataLayer, or tracking-plan
  contract is included in this release.

## [1.1.2] - 2026-08-18

### Changed

- Rendered Markdown now exposes objective confidence, ownership, rationale,
  and evidence already present in canonical JSON.
- Journey summaries now show entry points and journey-level evidence.
- Coverage evidence now summarizes discovery candidates by type and resolution.
- Objective considerations now include a lens-by-resolution summary without
  treating counts as quality thresholds.

### Compatibility

- No schema, validator, analytical workflow, or acceptance-rule change.
- Schema `1.1.0` and existing `1.0.0` artifact compatibility are preserved.

## [1.1.1] - 2026-08-18

### Changed

- New drafts no longer seed an internal initialization instruction into the
  optional `document.notes` field.
- Rendered Markdown now leads with compact overall quality status, scope,
  strategy, core KPIs, journey and objective coverage, missing needs, and
  evidence requests before presenting the complete quality-gate table.

### Compatibility

- No schema, validator, analytical workflow, or acceptance-rule change.
- Schema `1.1.0` and existing `1.0.0` artifact compatibility are preserved.

## [1.1.0] - 2026-08-18

### Added

- A standalone product contract covering users, inputs, outputs, workflow,
  acceptance gates, and non-goals.
- Additive schema support for applicability, North Star rationale, product
  scope, and gate-linked exceptions.
- Stronger validation for journey variants and states, KPI roles and tiers,
  framework-level core coverage, dimension closure, current-measurement
  alignment, and appropriateness exceptions.
- Decision-oriented Markdown rendering with complete KPI and semantic
  requirement detail.
- Focused unit tests for initialization, validation, rendering, and backward
  compatibility.

### Changed

- The framework is explicitly platform-independent and keeps tracking-plan
  creation outside its workflow.
- JSON is the canonical artifact and Markdown is rendered from it for human
  review.
- External consumers may use the JSON, but the framework does not invoke or
  adapt itself to any downstream skill.

### Compatibility

- The validator accepts existing `1.0.0` framework artifacts.
- New drafts and the schema use version `1.1.0`.
