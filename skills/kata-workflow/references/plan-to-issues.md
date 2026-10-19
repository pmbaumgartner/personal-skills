# Convert Plans To Issues

Use this workflow to convert a plan or several plan documents into Kata issues. Apply SKILL.md for attribution, Blue/Red classification, decisions, relationships, and close evidence.

## Scale The Review

Default to a lightweight conversion: keep the coverage map and review findings in the gate issue, and inspect issue bodies, relationships, and readiness directly with Kata. Separate draft files are useful for multiline bodies; additional manifests, snapshots, or audit scripts are optional.

Use more structured reconciliation when overlapping plans, concurrent creators, ambiguous scope, or complex dependencies make direct review unreliable. Automate specific checks where automation adds confidence—not merely to produce closure evidence.

Either path must preserve substantive source requirements, genuine dependencies, deliverables, acceptance criteria, and unresolved decisions. Before closing the gate, confirm that rejected or deferred choices cannot release unapproved implementation and that the resulting ready queue matches the intended next work.

## Draft And Review

Read every source plan. Map its substantive requirements to proposed issues, including outcomes, dependencies, deliverables, acceptance evidence, and unresolved decisions. Search existing issues and reuse suitable work.

Before creating, consider how the proposed set could fail: missing scope, oversized tasks, hidden dependencies, weak acceptance evidence, over-specified acceptance (test matrices or implementation details), or stale code assumptions. Resolve material risks through issue edits, splits, dependencies, or Blue decisions. Prefer small vertical increments that can be independently verified. Keep source-plan requirements distinguishable from useful additions grounded in the repository.

## Create Behind A Review Gate

First create a Blue gate issue, `Review conversion of <plan>`, whose exit criteria are the linking and fidelity checks below. Create every new issue with `blocked_by: [<gate>]` so it stays out of `ready` and `next` until review finishes. Apply the same blocker to new work discovered during linking or review.

Create sequentially unless authorized parallel work has independent scopes and justifies the coordination. When using multiple creators, assign nonoverlapping issues and have one coordinator add the remaining relationships after creation.

For each issue:

- Use an idempotency key such as `<plan-slug>-<issue-slug>-<YYYY-MM-DD>`.
- Include `## Source Plan` naming the source file(s) and sections, plus the appropriate Blue/Red fields and artifact deliverables.
- Record the ref, title, label, source coverage, proposed relationships, additions, and unresolved questions.

Do not gate reused issues; coordinate with their owner before editing them, and preserve existing scheduling and ownership.

## Link And Reconcile

Inspect each issue and add the relationships centrally. Use blockers for real ordering and related links for context. Explain non-obvious sequencing in mutation comments. Block affected Red work on unresolved Blue decisions.

Compare assumptions with current code, docs, checks, and previous issue comments. Edit stale or underspecified issues before implementation. Record durable constraints in acceptance criteria, deliverables, or Blue decisions. Route unresolved consequential choices through the selected decision mode.

## Check Fidelity

Reconcile the source coverage map with the final issue set:

- Represent every substantive requirement, fold it into another issue, or record why it was omitted.
- Preserve dependencies, deliverables, acceptance checks, and evidence expectations.
- Verify one workflow label and an opening verb matching each completion claim.
- Resolve material review findings and evaluate repository-grounded additions within the authorized scope.

Repair gaps before releasing work. If review cannot finish, leave the gate open and record the remaining action on it.

## Release And Report

Close the gate with the coverage result to release the reviewed issues. List unowned ready issues for actionable work; remaining dependencies may correctly exclude some issues.

Report created/reused refs, major dependencies, source coverage, additions, and the gate's state. Include unresolved user choices in Human mode, or decisions, material assumptions, confidence, and reversal paths in Agent mode.
