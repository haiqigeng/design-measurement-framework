# Product Contract

## North Star

Turn incomplete website, business, and technical evidence into a
coverage-closed, decision-ready measurement framework: identify every material
journey and plausible digital objective in scope, propose the complete set of
justified and precisely defined KPIs, and trace every KPI to the observable
facts and dimensions required downstream. Make every omission an explicit
exclusion or evidence boundary, so the tracking plan cannot silently miss a
meaningful measurement need or introduce measurement without a business
purpose.

Apply one governing rule:

> Everything material is accounted for; everything proposed is justified.

## Product Identity

Produce the business measurement contract upstream of analytics implementation.
Answer:

1. Which outcomes matter?
2. Which journeys contribute to them?
3. Which KPIs express outcomes, drivers, and risks?
4. Which observable facts and dimensions are needed to calculate them?
5. Which current measurements support or fail those needs?
6. Which evidence boundaries could change the answer?

Do not optimize for the number of journeys, objectives, KPIs, requirements, or
events. Optimize for closed decision coverage with no unsupported proposal.

## Coverage-Closed Meaning

Treat coverage as closed only when every candidate generated from available
top-down and bottom-up evidence has one explicit resolution:

- mapped to an included entity;
- merged into an equivalent family;
- excluded with a concrete reason;
- marked not applicable with a concrete reason; or
- retained as unresolved and linked to a named exception and impact.

Do not equate coverage closure with universal observability. Preserve
inaccessible, untested, planned, or externally blocked states as factual
boundaries. Never convert an explicit boundary into a silent assumption.

## Completeness And Appropriateness

Apply both qualities at every layer:

| Layer | Completeness | Appropriateness |
| --- | --- | --- |
| Journeys | Resolve every material journey, variant, outcome, and discovered family | Keep goal-directed, material, deduplicated, proportional journeys |
| Objectives | Record a decision for every applicable value stream and strategic lens | Keep evidence-backed, distinct, recognizable, digitally relevant objectives |
| KPIs | Cover outcomes, drivers, guardrails, journey success, and material friction | Keep actionable, precise, feasible, non-vanity, non-redundant KPIs |
| Requirements | Map every KPI component and segmentation need to an observable source | Keep only decision-useful facts and use the correct collection mechanism |

Completeness without appropriateness creates inventories and bloat.
Appropriateness without completeness creates elegant blind spots.

## Primary Users

- Enable web analysts to challenge, approve, revise, and maintain the framework.
- Enable business, product, marketing, sales, finance, support, operations, and
  mission owners to recognize their intended outcomes and decisions.
- Enable tracking-plan designers to consume explicit measurement needs without
  reconstructing strategy from website controls.
- Enable analytics practitioners to calculate the same KPI from the same
  definition.

## One Quality Standard

Use one adaptive workflow. Activate relevant business-model, alignment,
authenticated, transactional, or lifecycle capabilities conditionally. Never
offer a reduced-quality mode or substitute a page/event cap for closure.

## Acceptance Outcome

Declare the framework ready only when:

1. every mandatory gate is `pass` or `pass_with_exceptions`;
2. every exception is explicit, bounded, and linked to affected IDs;
3. every material included journey maps to at least one active objective;
4. every active objective has recorded outcome, driver, and guardrail decisions;
5. every material journey has recorded completion, step-conversion, and
   friction decisions;
6. every KPI formula component maps to a measurement requirement;
7. every segmentation decision names its source or explains why none is needed;
8. every current-tracking requirement is classified when current tracking was supplied;
9. no final GA4 or dataLayer implementation decision is presented as approved;
10. a stakeholder can understand the human output and a downstream agent can
    consume the canonical JSON without guessing.

