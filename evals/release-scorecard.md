# Release scorecard

Record the candidate release and baseline versions, benchmark ID, artifact
hashes, evaluator result, and reviewer.

Score each area as `better`, `equivalent`, `worse`, or `not comparable`, with
one evidence-based reason:

- material candidate and journey recall;
- journey granularity and merge/split appropriateness;
- objective coverage and business appropriateness;
- KPI outcome, driver, guardrail, and diagnostic coverage;
- formula unit, grain, population, window, and aggregation coherence;
- semantic requirement specificity and source feasibility;
- unsupported-claim control and evidence traceability;
- evidence-boundary honesty for gated and unexecuted paths;
- Markdown decision readability; and
- canonical JSON clarity for an independent machine consumer.

For every `worse` result, decide whether it is a justified truthfulness
correction, a benchmark limitation, or a release regression. A truthfulness
correction is acceptable only when the material candidate or decision need
remains visible as confirmed, planned, unresolved, excluded, or bounded rather
than silently disappearing.
