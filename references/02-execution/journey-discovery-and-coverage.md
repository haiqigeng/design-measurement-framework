# Journey Discovery And Coverage

## Contents

- [Define a journey](#define-a-journey)
- [Build the top-down candidate map](#build-the-top-down-candidate-map)
- [Build the bottom-up candidate universe](#build-the-bottom-up-candidate-universe)
- [Explore proportionately](#explore-proportionately)
- [Exercise material states](#exercise-material-states)
- [Separate evidence from resolution](#separate-evidence-from-resolution)
- [Closure conditions](#closure-conditions)

## Define A Journey

Model a journey as a goal-directed path toward a defined user or business
outcome. Merge alternate routes toward the same outcome as variants when their
measurement logic remains coherent. Split journeys when intent or outcome is
materially different.

Do not model aimless browsing, every page transition, or every click as a
journey. Keep navigation and interaction evidence in the candidate inventory
until analyst judgment establishes its role.

## Build The Top-Down Candidate Map

Detect the relevant business model and value streams. Use the applicable
prompts to consider:

- discovery and acquisition entry points;
- evaluation, comparison, configuration, or content-consumption paths;
- lead, booking, signup, purchase, subscription, donation, or service outcomes;
- authentication and account recovery;
- post-conversion account, fulfilment, return, cancellation, renewal, upgrade,
  support, advocacy, and re-entry paths;
- failure, validation, empty, zero-result, unavailable, and recovery states;
- backend-confirmed outcomes that have no visible UI representation.

Record every considered expected candidate. Use `excluded` or a named exception
when evidence shows it is irrelevant or unavailable. Never silently delete an
expected family because the first crawl did not find it.

## Build The Bottom-Up Candidate Universe

Use every available source. For rendered websites, inspect:

- robots and reachable sitemap branches;
- primary, secondary, account, footer, and contextual navigation;
- breadcrumbs and rendered internal links;
- route and page-template families;
- every distinct CTA family and material placement;
- every distinct form purpose and material implementation variant;
- internal search, listing, filter, sort, pagination, recommendation, and
  merchandising surfaces;
- campaign, SEO, deep-link, notification, and saved-state entry points;
- confirmation, thank-you, receipt, error, and post-conversion endpoints;
- authenticated, anonymous, responsive, experiment, and market variants when
  they materially change intent, path, outcome, or measurement needs.

Preserve a distinct candidate when the same visual control has a different
purpose, context, funnel shape, or outcome. Merge repeated instances only after
proving that their role is equivalent. Map every scanned navigation item, CTA,
form, template, entry point, and endpoint to a journey, a merged family, an
explicit exclusion, or a named unresolved exception.

## Explore Proportionately

Build the candidate universe before sampling. Explore by materially distinct
journey, route family, page template, component, state, and funnel variant—not
by link order or repeated product/content pages.

Render at least one representative of every material family. Exhaust small,
stable, finite variant sets when the variant can change the outcome or needed
measurement. For large or combinatorial sets, use semantic partitions,
boundaries, and risk combinations; record the strategy and residual limitation.

Treat a page cap as a round budget, never as proof of closure. Run targeted
rounds for unvisited material families and material `unknown` candidates.

## Exercise Material States

When safe, inspect:

- entry and qualification;
- meaningful progression;
- success and confirmed outcome;
- validation and business-process failure;
- recovery after failure;
- empty and zero-result states;
- abandonment boundary and re-entry;
- post-conversion self-service or lifecycle state.

Do not require a state that is genuinely not applicable. Record the
not-applicable decision and reason. Never use one successful variant to close a
different funnel shape or implementation.

Every material goal-directed journey needs a declared entry point, an explicit
entry-state step, and an explicit success-state step. A success step may be
confirmed by backend, lifecycle, business-system, research, or planned evidence;
it does not require a visible confirmation page. When evidence cannot establish
the entry or outcome, retain the gap through a journey exception rather than
inventing a step or calling the journey closed.

## Separate Evidence From Resolution

Use factual journey states:

- `observed`: directly rendered or executed;
- `confirmed`: established by a credible non-live source;
- `planned`: present only in future-state evidence;
- `partial`: only part of the journey or variant is evidenced;
- `not_tested`: not attempted or outside the completed investigation;
- `externally_blocked`: an evidenced access, CAPTCHA, credential, technical, or
  consequential boundary prevented observation.

Use candidate resolutions separately:

- `mapped`;
- `merged`;
- `excluded`; or
- `unresolved`.

Do not relabel `not_tested` as externally blocked. Do not relabel `partial` as
observed merely to pass a gate. A user description is `confirmed` evidence
from a user source, not a special behavior state.

## Closure Conditions

Close journey coverage only when:

1. every material discovery candidate has an explicit resolution;
2. every expected material journey is included, excluded, or tied to an exception;
3. every material page/template and interaction family maps to a journey or exclusion;
4. every material journey has a declared entry point plus explicit entry and
   success steps, and every confirmed conversion endpoint maps back to an entry
   and progression path;
5. every material journey records applicable success, failure, empty, re-entry,
   and post-conversion decisions;
6. every material variant has its own evidence state;
7. every included journey states its outcome and evidence;
8. every residual gap names the affected journey and downstream impact.

Closure may be `pass_with_exceptions`; it may never rely on silent omission.
