# KPI Derivation

## Contents

- [Distinguish metric roles](#distinguish-metric-roles)
- [Build outcome and driver trees](#build-outcome-and-driver-trees)
- [Specify the formula precisely](#specify-the-formula-precisely)
- [Validate grain and identities](#validate-grain-and-identities)
- [Resolve segmentation](#resolve-segmentation)
- [Prevent metric bloat](#prevent-metric-bloat)

## Distinguish Metric Roles

Use:

- `outcome` for the result that expresses objective achievement;
- `driver` for a factor that explains or influences an outcome;
- `guardrail` for a counter-metric that detects harmful optimization;
- `diagnostic` for a metric that helps locate a problem without itself
  representing success.

Use tiers independently:

- `north_star` only when one durable metric can represent a coherent value
  stream without hiding essential counter-outcomes;
- `primary` for decision-critical outcome or driver KPIs;
- `supporting` for useful but secondary indicators;
- `guardrail` for required counter-metrics;
- `diagnostic` for investigation metrics.

Do not force a north star for a site or value stream that needs balanced or
multiple outcomes.

When more than one North Star is justified in one framework, require explicit,
non-overlapping applicability and a rationale for each. Do not use multiple
North Stars as a substitute for prioritization within the same scope.

## Build Outcome And Driver Trees

For every active objective:

1. define at least one outcome consideration;
2. decompose the outcome into causal or arithmetic drivers;
3. distinguish true identities from explanatory relationships;
4. add guardrail considerations;
5. record rejected or not-applicable candidates.

For every material journey, consider:

- completion;
- major step conversion;
- observed or strongly expected friction;
- outcome quality or backend confirmation;
- diagnostics that support a plausible action.

Do not promote every step or driver into a KPI. Retain a KPI only when an owner
can use it to decide or act. Record the consideration decision so rejection
does not become a completeness gap.

When a consideration resolves to `kpi_proposed` or `covered_by_existing`, each
referenced KPI must link back to that consideration's objective or journey.
This reciprocity proves that the recorded decision and the accepted KPI still
describe the same scope.

## Specify The Formula Precisely

Record for every KPI:

- human-readable expression;
- named formula components;
- numerator, denominator, input, output, and filter roles;
- counting unit;
- grain;
- eligible population;
- reporting window;
- inclusion and exclusion rules;
- deduplication or confirmation rule when relevant;
- directionality;
- segmentation decision and rationale;
- decision use and owner role;
- objective and journey links;
- recommended-core status;
- evidence and assumption status.

When a KPI has journey links, its effective applicability normally derives
from those journeys; otherwise it derives from its linked objectives. A
legitimate cross-journey business KPI may be broader, but it must carry an
`applicability_basis` with rationale and evidence. Do not duplicate or narrow a
sound business KPI solely to avoid an explicit basis.

Require two competent analysts using the same sources to calculate the same
number.

For schema `1.2.0` and later, make the existing `formula.expression` both
readable and machine-checkable:

- write it with stable lowercase `snake_case` component symbols;
- declare `calculation_type` and `result_unit`;
- give every component its symbol, counting unit, grain, role, definition, and
  measurement-requirement links;
- use arithmetic operators or the validator's bounded functions for counts,
  sums, rates, averages, weighted averages, percentiles, cohorts, retention,
  and composite or index calculations; and
- reference every numerator, denominator, and input component in the expression.

Filters and declared outputs may remain outside the arithmetic expression when
their role is eligibility or result description. The expression is a semantic
calculation contract, not SQL, analytics-platform syntax, or executable client
code. If the calculation cannot be represented without ambiguity, retain an
explicit exception instead of writing unrelated prose in the expression.

## Validate Grain And Identities

Check units on both sides of every arithmetic identity. Do not accept
`revenue = sessions × conversion rate × average order value` unless conversion
rate and transaction frequency make the identity valid for the selected grain.
Prefer explicit components such as:

`revenue = sessions × transactions_per_session × revenue_per_transaction`

State whether a rate is event-, session-, user-, account-, lead-, order-, item-,
or time-based. State the cohort and time relationship for retention, churn,
renewal, and lifetime metrics.

## Resolve Segmentation

List dimensions needed to interpret or act on the KPI. For each dimension,
state its business definition, segmentation purpose, source, and expected
collection mode.

Do not assume that device, channel, market, authentication, customer status, or
another dimension must be sent as an event parameter. It may be native,
configured, backend-provided, joined, or derived. If no segmentation is needed,
record that decision and rationale explicitly.

## Prevent Metric Bloat

Reject or demote:

- raw traffic volume as a primary success measure without value or rate context;
- duplicate names for the same calculation;
- metrics that necessarily duplicate another definition without a distinct use;
- metrics with no owner, decision, or plausible action;
- metrics whose source cannot be defined even as an explicit dependency;
- generic library KPIs unsupported by local evidence;
- targets or benchmarks without a current, comparable, cited source.

Produce the complete justified set, then highlight the recommended core. Keep
lower-tier candidates only when they retain a distinct decision or diagnostic
purpose.

Treat duplicate-definition detection as a review advisory. Similar calculations
may remain distinct when their population, applicability, objective, decision,
or required interpretation differs. Never delete or merge a KPI from a
fingerprint alone.

Select the recommended core at framework level. Every active objective still
needs an appropriate outcome KPI or named exception, but it does not need its
own mechanically designated core KPI. When a core outcome or driver has a
guardrail consideration resolved to a real guardrail KPI, include a cited
guardrail for that objective in the core or record a KPI-appropriateness
exception. Do not manufacture a guardrail when the consideration is explicitly
and credibly `none_with_reason` or `not_applicable`.

Treat a non-discriminating core or suspiciously uniform priority, ownership,
grain, or reporting-window pattern as a review prompt, never a quota. Resolve
the advisory through evidence and decision usefulness; do not mechanically
change counts or wording to silence it.
