# Design Measurement Framework

Design, review, and maintain an evidence-backed, platform-independent web
measurement framework. The skill closes material journey, objective, KPI, and
semantic measurement-requirement coverage before implementation decisions are
made.

## North star

Turn incomplete business, website, and technical evidence into a
coverage-closed, decision-ready measurement framework: account for every
material journey and plausible digital objective in scope, derive the complete
set of justified and precisely defined KPIs, and trace every KPI to the
observable facts and dimensions needed to calculate and interpret it.

Everything material is accounted for; everything proposed is justified.
Completeness and appropriateness are co-equal quality standards. A missing
item must be an explicit exclusion or evidence boundary, not an accidental
omission.

## Who it is for

The primary users are web analysts, measurement strategists, analytics leads,
and business stakeholders reviewing objectives and KPIs. Reporting,
experimentation, analytics, and implementation teams may consume the result,
but no downstream workflow defines this skill's process or acceptance.

## Inputs

At minimum, provide one of the following:

- an in-scope URL; or
- a sufficiently concrete description of the website, product, service,
  journeys, or intended future experience.

Useful optional evidence includes business and product briefs, designs,
technical or business-system documentation, existing frameworks, tracking
plans, GTM or dataLayer evidence, and analytics exports. Each source is used
only for what it can prove. Missing evidence becomes an explicit assumption,
evidence request, or bounded gap; credentials, payment details, and personal
information are not needed in the artifacts.

Direct exploration is not the only discovery route. When authentication or
safe interaction limits observation, available technical, lifecycle,
business-system, design, historical, and credible user evidence can preserve
material journey candidates for explicit resolution and support mapped
journeys as confirmed or planned. Only eligible direct evidence can make
execution `observed` or an attempted boundary `externally_blocked`.

Schema 1.3 preserves a structured intake baseline before investigation: each
requested non-secret target is included, canonicalized, explicitly excluded,
or left unresolved. Production scope remains the delivery scope even when one
safe UAT or staging source represents several production sites or locales.
Categorical testing authorization may be recorded, but secrets never are.

## Outputs

Every completed delivery contains exactly two core artifacts:

- `measurement-framework.json` — the canonical machine-readable source of
  truth;
- `measurement-framework.md` — the decision-oriented human review surface,
  rendered from the JSON.

JSON is authoritative. If Markdown and JSON disagree, update JSON and render
Markdown again. Authorized machine consumers can use the JSON directly; this
skill does not invoke or adapt itself to another skill or workflow.

The Markdown exposes scope provenance, evidence roles and maturity, explicit
material-state decisions, discovery/evidence coverage, computed gate facts,
KPI coherence advisories, and bounded exceptions. The same facts are available
in the validator's machine-readable diagnostic output; this does not create a
third delivery artifact.

## Workflow

1. Capture the non-secret intake baseline, then resolve scope, target state,
   evidence roles, and safe boundaries.
2. Build and close the material journey model, including relevant states and
   variants. If direct exploration is limited, continue with available
   alternative evidence until every material expected or source-derived
   candidate is resolved.
3. Identify and assess objective candidates.
4. Derive and validate the KPI system, including the North Star, recommended
   core, outcomes, drivers, guardrails, useful diagnostics, rate population
   coherence, and cross-journey aggregation logic.
5. Decompose KPIs into semantic measurement requirements: facts, dimensions,
   sources, and derivations needed to calculate and interpret them.
6. Assess current measurement when relevant evidence exists.
7. Apply completeness, appropriateness, traceability, and exception gates.
8. Validate JSON, render Markdown, deliver both artifacts, and stop.

Evidence changes the depth and route of the work, not whether material
journey, objective, KPI, and requirement closure is assessed. There are no
lightweight or event-count-only quality modes.

For current-state claims, `observed` means timestamped direct live/test
behavior with a stable locator. `externally_blocked` means a direct attempt
encountered a recorded boundary. Technical or business-system evidence may
still confirm a capability or backend outcome; it is never relabeled as
observed execution.

Production scope is never replaced by UAT. Bind each representative test
source to the production targets it supports and record an assumption or
bounded exception when environment or locale equivalence is not established.

## Acceptance rules

A delivery is ready only when:

- every mandatory quality gate is `pass` or `pass_with_exceptions`;
- resolved delivery scope matches the intake dispositions, with every
  transformation confirmed or explicitly bounded;
- every exception is explicit, evidence-linked where possible, and correctly
  linked to the affected gate or requirement;
- the in-scope candidate universe is closed for material journeys, objectives,
  states, and variants, or each boundary is documented;
- every proposed objective and KPI is decision-useful, appropriately scoped,
  precisely defined, and supported by evidence or a stated assumption;
- KPI-to-requirement and requirement-to-evidence traceability closes;
- current-measurement alignment, when supplied, covers every requirement with
  a semantic status;
- observed and externally blocked claims meet their evidence-eligibility and
  provenance rules;
- a direct access boundary did not erase candidates supported by credible
  alternative evidence;
- rate numerator and denominator units, grains, eligible populations, and
  subset logic are coherent;
- cross-journey KPIs and any broad North Star have defensible aggregation and
  mix-shift logic; and
- the JSON validates and the Markdown is freshly rendered from that JSON.

`pass_with_exceptions` is usable but not fully verified. A structurally valid
draft with failed gates remains a draft.

## Boundary with tracking-plan creation

This skill answers what matters, why it matters, how success is defined, and
which semantic facts and dimensions are needed. It does not create a tracking
plan or select final platform events and parameters. In particular, it does
not define exact triggers, value domains, dataLayer contracts, developer
tickets, GTM configuration, runtime QA, dashboards, targets, or legal
decisions.

A separate tracking-plan skill may consume this framework's JSON as upstream
semantic input. That consumer is optional and independent: this repository
neither calls it nor duplicates its implementation design.

## Install as a Codex skill

The repository root is the skill directory. Install it with Codex's GitHub
skill installer by selecting the repository root (`--path .`) and naming the
destination `design-measurement-framework`.

## Quick start

Install the validation dependency and initialize a non-overwriting draft:

```powershell
python -m pip install -r requirements.txt
python scripts/init_framework.py --title "Website measurement framework" --scope "Whole public website" --site https://www.example.com/ --output measurement-framework.json
```

The initializer creates an intentionally incomplete draft with failed gates.
Replace its example values through evidence-backed analysis; do not change a
gate merely to satisfy validation.

Inspect candidate, state-decision, and representative-source coverage without
mutating the artifact:

```powershell
python scripts/candidate_census.py measurement-framework.json
```

Validate and render a completed framework:

```powershell
python scripts/validate_framework.py measurement-framework.json --delivery
python scripts/render_framework.py measurement-framework.json --output measurement-framework.md
```

Add `--json` to validation for a reproducible diagnostic block containing the
artifact SHA-256, schema and validator versions, evidence maturity, candidate
census, discovery/evidence coverage, KPI coherence checks, computed gate facts,
errors, and advisories.

For release-level analytical regression testing, run a fixed benchmark and
optionally compare the same task against a prior release artifact:

```powershell
python scripts/evaluate_release.py measurement-framework.json --benchmark evals/benchmarks/gated-multilingual-service/expectations.json --baseline prior-release-measurement-framework.json
```

The benchmark catches material concept loss even when both files are schema
valid. Complete the human scorecard in [`evals/`](evals/) for objective and KPI
appropriateness, Markdown readability, and independent-agent JSON usability.

Run the repository tests with:

```powershell
python -m unittest discover -s tests
```

See [`SKILL.md`](SKILL.md) for routing and operating rules, the
[`references/`](references/) directory for focused guidance, and
[`schemas/measurement-framework.schema.json`](schemas/measurement-framework.schema.json)
for the canonical contract.

## Compatibility

Release `v1.4.0` remains on canonical schema `1.3.0`; no new authoring ledger is
required. It adds evidence-limited discovery fallback, linked journey-variant
inheritance, conservative KPI coherence diagnostics, computed
discovery/evidence coverage, conditional UAT-to-production and locale review,
and fixed analytical release benchmarks. The validator continues to accept
`1.0.0`, `1.1.0`, and `1.2.0` artifacts under their prior blocking behavior;
newly detectable semantic risks remain non-blocking legacy advisories.
