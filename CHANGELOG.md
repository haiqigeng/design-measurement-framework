# Changelog

## [Unreleased]

## [1.4.0] - 2026-08-20

### Added

- An evidence-limited discovery protocol that preserves material candidates
  supported by technical, lifecycle, business, design, historical, or credible
  user evidence when direct exploration is blocked or partial, without
  overstating observed execution.
- Computed discovery/evidence diagnostics for representative target coverage,
  candidate use of discovery-capable sources, intake-only material candidates,
  blocked journeys without fallback evidence, attributable direct scope, and
  conditional environment or locale equivalence review.
- Conservative KPI coherence diagnostics for rate counting units and grains,
  cross-journey aggregation, broad North Star scope, and mandatory human review
  of numerator-subset logic.
- A fixed, manifest-driven analytical release evaluator, gated multilingual
  benchmark, and human scorecard that detect material concept loss even when a
  framework remains schema-valid.

### Fixed

- Objective, KPI, dimension, and requirement variant scope now inherits from
  linked journeys or downstream links instead of defaulting to every variant
  in unrelated journeys. Explicit broader scope still requires an
  evidence-backed applicability basis.

### Changed

- Validator diagnostics and rendered Markdown now expose discovery/evidence
  coverage and KPI coherence review signals. Validator version is `1.4.0`;
  canonical framework schema remains `1.3.0` because no new authoring fields
  are required.
- Acceptance guidance now requires explicit handling of UAT-to-production and
  multi-locale extrapolation, and checks coherent rate populations,
  cross-journey aggregation, and North Star mix-shift risk.

### Compatibility

- Schema `1.0.0`, `1.1.0`, `1.2.0`, and `1.3.0` artifacts remain accepted
  under their versioned blocking behavior. New discovery and KPI diagnostics
  are non-blocking review advisories.
- No tracking-plan, GA4 event/parameter, implementation-readiness, mandatory
  technical-mining, fixed-quota, or case-specific journey contract is added.

## [1.3.0] - 2026-08-19

### Added

- Schema `1.3.0` intake baselines that preserve requested non-secret targets,
  resolved production scope, resolution evidence, representative test/live
  sources, locales, and categorical safe-testing authorization.
- Evidence-eligibility checks for `observed` and `externally_blocked` claims,
  including source-level observation time and a stable locator, while retaining
  technical and business-system confirmation for capabilities and backend
  outcomes.
- Relational applicability checks with evidence-backed
  `applicability_basis` overrides, reverse KPI-consideration reciprocity, and
  bounded exception-stage, gate-direction, and scope checks.
- Explicit failure, empty, recovery, re-entry, and post-conversion decisions
  for material journeys without requiring every state to be executed.
- Evidence-maturity rendering, source-role visibility, scope-provenance tables,
  and compact computed facts beside every quality-gate rationale.
- Artifact-bound `--json` validation diagnostics with SHA-256, validator and
  schema versions, candidate census, maturity counts, gate facts, errors, and
  advisories.
- A read-only `scripts/candidate_census.py` helper and conservative advisories
  for anti-circular discovery closure, non-discriminating core selection, and
  contextual uniformity.

### Changed

- New drafts use schema `1.3.0`, initialize an intentionally unresolved intake
  baseline, and accept optional locale declarations.
- Production delivery scope and representative UAT/test evidence are modeled
  separately so evidence-source consolidation cannot silently replace scope.
- Incomplete steps on material journeys require an exact journey exception;
  unresolved material state decisions require a journey-level exception.
- Formula validation remains isolated in `formula_contract.py`; shared
  semantic diagnostics live in `diagnostics.py`, and non-blocking review
  prompts live in `advisories.py`.

### Compatibility

- Schema `1.0.0`, `1.1.0`, and `1.2.0` artifacts retain their prior blocking
  acceptance behavior. Newly detectable evidence, reciprocity, applicability,
  and exception-scope risks are non-blocking legacy advisories.
- No tracking-plan, GA4 event/parameter, implementation-readiness, fixed-quota,
  mandatory execution, or universal evidence-bundle contract is added.

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
