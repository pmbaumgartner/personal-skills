# Red Issues

Use Red for verified implementation at the delivery state requested by the user or repository. Apply the shared classification, attribution, evidence, and close rules in SKILL.md.

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
4. Commit when requested or required by the repository. Otherwise, verified working-tree changes may satisfy delivery; explicitly record that they remain uncommitted.
5. Record reusable learning or faulty assumptions in linked Blue work when warranted. Such follow-up blocks Red closure only if it invalidates acceptance or verification.

For a performance claim, benchmark the starting behavior before editing and the changed behavior with the same harness. Record the starting commit and relevant working-tree changes, command, dataset/shape, seed, metric, and both results. Claim an improvement only when the comparison shows one. If results are slower or inconclusive, apply the decision mode and preserve existing user work; leave the issue open while its performance criteria remain unmet.

## Close The Implementation

Record what changed, checks performed, skipped checks, residual risk, and deferred work in the close's outcome comment or a reviewed artifact.

When a commit is required, cite the commit containing the completed work; a PR URL alone is insufficient. Closing working-tree work asserts the requested implementation is complete, not that it was committed, merged, or deployed. Leave the issue open when required verification is incomplete and no accepted rationale settles that gap.
