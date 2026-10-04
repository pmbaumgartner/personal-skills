# Red Issues

Use Red for verified, committed implementation at the delivery state requested by the user or repository. A commit is the minimum closure requirement, not a claim that the work is merged, published, or deployed. Apply the shared classification, attribution, evidence, and close rules in SKILL.md.

## Define The Work

Include these issue fields:

- `## Objective`: the known goal.
- `## Context`: relevant decisions and execution constraints.
- `## Scope In` / `## Scope Out`: boundaries; omit for small work with unambiguous acceptance criteria.
- `## Acceptance Criteria`: observable completion criteria.
- `## Pause Triggers`: discoveries that would change scope, acceptance, a settled decision, or reusable policy.
- `## Deliverables`: every path to review before close.

## Implement And Verify

1. Read the issue and linked decisions, then claim it.
2. Implement the smallest change satisfying acceptance criteria. If a pause trigger changes scope, acceptance, a settled decision, or reusable policy, pause affected implementation and open or update Blue. Block affected Red work on that decision before continuing. Keep equivalent local implementation choices inside Red.
3. Run focused checks and the required acceptance verification.
4. Review the final changes and commit the completed, verified work before closing. Preserve unrelated user changes. If committing is not authorized or possible, report the verification and remaining commit step, and leave the issue open; do not treat passing tests as permission to close uncommitted work.
5. Record reusable learning or faulty assumptions in linked Blue work when warranted. Such follow-up blocks Red closure only if it invalidates acceptance or verification.

For a performance claim, benchmark the starting behavior before editing and the changed behavior with the same harness. Record the starting commit and relevant working-tree changes, command, dataset/shape, seed, metric, and both results. Claim an improvement only when the comparison shows one. If results are slower or inconclusive, apply the decision mode and preserve existing user work; leave the issue open while its performance criteria remain unmet.

## Close The Implementation

Record what changed, checks performed, skipped checks, residual risk, and deferred work in the close's outcome comment or a reviewed artifact.

For a completed implementation, close with `--done --commit <sha>` citing the commit containing the reviewed and verified work. If completion spans several commits, include the relevant commit evidence. Tests, reviewed paths, and a PR URL are supplemental evidence, not substitutes for the commit. Never cite an unrelated HEAD or close first with a promise to commit later.

Leave the issue open while its implementation is uncommitted, required verification is incomplete without an accepted rationale, or an additional requested delivery step remains unfinished. Do not create an empty commit for work that made no changes; use the appropriate no-change or other disposition from SKILL.md.
