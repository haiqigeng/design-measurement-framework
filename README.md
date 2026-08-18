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

## Outputs

Every completed delivery contains exactly two core artifacts:

- `measurement-framework.json` — the canonical machine-readable source of
  truth;
- `measurement-framework.md` — the decision-oriented human review surface,
  rendered from the JSON.

JSON is authoritative. If Markdown and JSON disagree, update JSON and render
Markdown again. Authorized machine consumers can use the JSON directly; this
skill does not invoke or adapt itself to another skill or workflow.

## Workflow

1. Resolve scope, target state, evidence roles, and safe boundaries.
2. Build and close the material journey model, including relevant states and
   variants.
3. Identify and assess objective candidates.
4. Derive and validate the KPI system, including the North Star, recommended
   core, outcomes, drivers, guardrails, and useful diagnostics.
5. Decompose KPIs into semantic measurement requirements: facts, dimensions,
   sources, and derivations needed to calculate and interpret them.
6. Assess current measurement when relevant evidence exists.
7. Apply completeness, appropriateness, traceability, and exception gates.
8. Validate JSON, render Markdown, deliver both artifacts, and stop.

Evidence changes the depth and route of the work, not whether material
journey, objective, KPI, and requirement closure is assessed. There are no
lightweight or event-count-only quality modes.

## Acceptance rules

A delivery is ready only when:

- every mandatory quality gate is `pass` or `pass_with_exceptions`;
- every exception is explicit, evidence-linked where possible, and correctly
  linked to the affected gate or requirement;
- the in-scope candidate universe is closed for material journeys, objectives,
  states, and variants, or each boundary is documented;
- every proposed objective and KPI is decision-useful, appropriately scoped,
  precisely defined, and supported by evidence or a stated assumption;
- KPI-to-requirement and requirement-to-evidence traceability closes;
- current-measurement alignment, when supplied, covers every requirement with
  a semantic status; and
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

Validate and render a completed framework:

```powershell
python scripts/validate_framework.py measurement-framework.json --delivery
python scripts/render_framework.py measurement-framework.json --output measurement-framework.md
```

Run the repository tests with:

```powershell
python -m unittest discover -s tests
```

See [`SKILL.md`](SKILL.md) for routing and operating rules, the
[`references/`](references/) directory for focused guidance, and
[`schemas/measurement-framework.schema.json`](schemas/measurement-framework.schema.json)
for the canonical contract.

## Compatibility

Release `v1.1.0` introduces additive schema capabilities under schema version
`1.1.0`. The validator continues to accept `1.0.0` framework artifacts while
new drafts use the current schema.
