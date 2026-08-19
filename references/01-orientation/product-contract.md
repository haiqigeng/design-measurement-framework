# Product Contract

## Product Identity

Apply the North Star and governing rule defined in `SKILL.md`. Produce a
standalone, platform-independent business measurement contract that answers:

1. Which outcomes matter?
2. Which journeys contribute to them?
3. Which KPIs express outcomes, drivers, guardrails, and useful diagnostics?
4. How is every KPI calculated and used for a decision?
5. Which observable facts, dimensions, systems, or derivations are required?
6. Which current measurements support or fail those needs?
7. Which evidence boundaries could change the answer?

The framework is complete in its own right. It may inform measurement
strategy, KPI governance, reporting, analysis, experimentation, implementation,
or other work, but no downstream workflow defines this skill's process,
schema, or acceptance.

Do not optimize for the number of journeys, objectives, KPIs, requirements, or
events. Optimize for closed decision coverage with no unsupported proposal.

## Primary Users

- Web analysts and measurement strategists who create, challenge, approve,
  revise, and maintain the framework.
- Digital analytics leads and consultants responsible for defining success and
  assessing whether current measurement supports business needs.
- Product, ecommerce, marketing, content, sales, finance, support, operations,
  service, and mission stakeholders who review intended outcomes and decisions.
- Analytics and data practitioners who must calculate the same KPI from the
  same definition.

Reporting, experimentation, implementation, and other analytics teams are
possible consumers of the canonical JSON. They are not primary product owners
and do not change the framework workflow.

## Standalone Use Cases

Use the framework for:

- measurement-strategy creation, review, and maintenance;
- journey and objective clarification;
- North Star, outcome, driver, guardrail, and diagnostic KPI design;
- stakeholder alignment around outcomes and decisions;
- KPI definition, rationalization, and governance;
- semantic assessment of current measurement against business needs;
- prioritization of missing data capabilities;
- calculation contracts for reporting and analysis requirements; and
- a platform-independent business contract that other workflows may consume.

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

## One Quality Standard

Use one adaptive workflow. Activate relevant business-model, alignment,
authenticated, transactional, lifecycle, or multi-scope considerations only
when applicable. Never offer a reduced-quality mode or substitute a page,
metric, event, or time cap for closure.

## Acceptance Outcome

Declare the framework ready only when:

1. the resolved delivery scope matches the non-secret intake baseline, and
   every transformation or unresolved target is evidenced or bounded;
2. every mandatory gate is `pass` or `pass_with_exceptions`;
3. every exception is explicit, bounded, linked to affected IDs, and cited by
   the correct quality gate;
4. every material included journey and variant is resolved and every material
   journey maps to at least one active objective;
5. every material journey explicitly resolves failure, empty, recovery,
   re-entry, and post-conversion states without pretending they were observed;
6. every observed or externally blocked claim has eligible, durable evidence;
7. every objective and journey has the required KPI-role considerations;
8. every active objective has an appropriate outcome KPI or a named exception;
9. every accepted KPI is precise, actionable, coherent, and traceable;
10. every KPI formula component and required dimension maps to a semantic
   measurement requirement;
11. every current-measurement requirement is classified when relevant evidence
   was supplied;
12. no platform-specific implementation decision is presented as approved;
13. a stakeholder can understand the Markdown and a machine consumer can use
    the canonical JSON without guessing; and
14. the Markdown is demonstrably rendered from and consistent with the JSON.
