# Changelog

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
