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

Require two competent analysts using the same sources to calculate the same
number.

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
