# Measurement Requirements And Alignment

## Contents

- [Decompose KPIs into semantic needs](#decompose-kpis-into-semantic-needs)
- [Classify the collection mode](#classify-the-collection-mode)
- [Treat dimensions independently](#treat-dimensions-independently)
- [Keep implementation outside the framework](#keep-implementation-outside-the-framework)
- [Align existing measurement](#align-existing-measurement)
- [Traceability closure](#traceability-closure)

## Decompose KPIs Into Semantic Needs

For each KPI formula component, identify the fact, state, count, amount,
dimension, or relationship that must be available. Define the need before
choosing an analytics implementation.

Examples:

- product-list exposure and product selection for list click-through rate;
- first meaningful form progression and confirmed completion for completion rate;
- backend-qualified lead and rejected lead for lead-quality rate;
- confirmed order, refund, and returned amount for net revenue;
- trial start, conversion, renewal, downgrade, and churn for subscription metrics;
- search execution and zero-result outcome for search failure rate;
- support-content use and subsequent support contact for deflection analysis.

Include invisible requirements that rendered exploration cannot prove:

- backend-confirmed outcomes;
- CRM qualification or sales acceptance;
- refunds, returns, cancellations, and chargebacks;
- trial, renewal, upgrade, downgrade, pause, and churn states;
- fulfilment and service outcomes;
- payment and server failures;
- metric-support exposures, eligible populations, and denominators;
- finance, support, operations, or mission facts required for outcomes.

## Classify The Collection Mode

Use one expected mode per requirement:

- `manual_web_event`;
- `native_analytics`;
- `backend_event`;
- `business_system_fact`;
- `join`;
- `derived`; or
- `unknown`.

Name the expected source system separately. Do not make `unknown` disappear;
link it to an assumption or exception when material.

## Treat Dimensions Independently

Define each segmentation dimension once. Record its business meaning, purpose,
source hint, collection-mode hint, sensitivity review, and linked KPIs.

Do not automatically convert a dimension into an analytics parameter. Preserve
native platform context, business-system fields, lookup dimensions, and derived
cohorts in their correct roles.

Mark potential personal or sensitive data as `review_required`. Mark a field as
`prohibited` when the available evidence establishes that it must not be
recommended. Never place raw personal or sensitive examples in the framework.

## Keep Implementation Outside The Framework

Semantic requirements are the implementation-independent contract. Do not add
platform event names, fields, exact triggers, requiredness, value domains,
dataLayer paths, or push examples during ordinary framework authoring.

The schema accepts the legacy optional `downstream_mapping_hint` only for v1
compatibility. Omit it by default. If maintaining an existing framework that
already contains one, keep `authoritative: false` and treat it as historical,
unapproved context rather than a current implementation decision.

## Align Existing Measurement

When current measurement evidence exists, create exactly one alignment row per
measurement requirement:

- `covered`: evidence represents the complete semantic need;
- `partial`: some facts, dimensions, timing, or confirmation are missing;
- `missing`: no supplied current measurement supports the need;
- `not_assessable`: supplied evidence cannot establish coverage.

Record current-measurement references, exact gaps, and the recommended next
action. Use only current implementation or data-usage evidence for alignment;
a prior framework alone cannot prove current coverage. Distinguish
configuration, live payload, collected analytics data, and report usage
evidence. Never let one evidence layer prove another.

Classify current measurements with no requirement link as:

- `justified` when they support a concrete diagnostic, operational, activation,
  experimentation, or other legitimate decision;
- `needs_justification` when no use is established;
- `out_of_scope` when the current framework intentionally does not assess them.

Do not call an unlinked measurement redundant solely because it does not map to
a primary KPI.

## Traceability Closure

Close requirement traceability only when:

1. every KPI formula component names at least one requirement;
2. every KPI segmentation decision is explicit;
3. every requirement links back to at least one KPI;
4. every linked dimension exists and links back to its KPIs;
5. every material non-UI dependency has a source and mode or named exception;
6. every supplied-current-tracking requirement has an alignment result;
7. every unlinked current measurement has a visible disposition;
8. no legacy downstream mapping hint is marked authoritative.
