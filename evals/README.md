# Analytical release evaluations

These evaluations test the skill's analytical output, not only its schema and
renderer. They are release safeguards against a framework becoming more
formally valid while losing material journey candidates, useful objectives,
coherent KPIs, evidence traceability, or reviewer usability.

## Release procedure

1. In a clean, isolated workspace, give an independent agent the candidate
   skill and one benchmark `input.md`. Do not provide the expected answer or a
   previous output.
2. Ask it to produce only `measurement-framework.json` and
   `measurement-framework.md`.
3. Validate the JSON with `scripts/validate_framework.py --delivery`.
4. Run the benchmark evaluator. When a prior release output exists for the
   same fixed input, include it as the baseline:

   ```powershell
   python scripts/evaluate_release.py measurement-framework.json `
     --benchmark evals/benchmarks/gated-multilingual-service/expectations.json `
     --baseline prior-release-measurement-framework.json
   ```

5. Complete `release-scorecard.md` against both JSON and Markdown. Automated
   concept matching is an omission detector; it cannot judge whether a
   candidate was merged appropriately, whether an objective is truly useful,
   or whether a formula expresses the right business decision.

A release is blocked by schema or traceability failure, a missing required
benchmark concept, an unexplained concept loss relative to the same benchmark,
or a material human-review downgrade. A lower count is not automatically a
regression: a previous unsupported claim may be removed when the new artifact
keeps the underlying candidate visible and records the evidence boundary.

Benchmark expectations are case-specific ground truth for a fixed package.
They are not universal quotas for journeys, objectives, KPIs, dimensions, or
requirements in ordinary skill runs.
