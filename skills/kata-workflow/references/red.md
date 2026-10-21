# Red Issues

Use Red for work an agent executes and verifies: implementation, or a spike that gathers evidence for a decision gate. Implementation is verified, committed work, plus any additional delivery steps requested by the user or repository. Normally finish with a local commit rather than leaving completed work only in the working tree. A commit is the minimum closure requirement, not a claim or authorization that the work is pushed, merged, published, or deployed. Apply the shared classification, attribution, evidence, and close rules in SKILL.md.

## Define The Work

Include these issue fields:

- `## Objective`: the known goal.
- `## Context`: relevant decisions and execution constraints.
- `## Scope In` / `## Scope Out`: boundaries; omit for small work with unambiguous acceptance criteria.
- `## Acceptance Criteria`: observable completion criteria, stated as outcomes. Name specific tests only for reproduced bugs or safety invariants; leave other test selection to the implementer under the repository's testing guidance.
- `## Pause Triggers`: discoveries that would contradict a settled decision, change scope or acceptance, or cross a limit of the epic's authority.
- `## Deliverables`: every path to review before close.

## Implement And Verify

1. Read the issue and linked decisions, then claim it.
2. Implement the smallest change satisfying acceptance criteria. Handle discoveries as SKILL.md describes: decide and record choices within scope, and on a pause trigger stop affected work and escalate through the decision gate.
3. Run focused checks and the required acceptance verification.
4. Review the final changes and commit the completed, verified work before closing. Stage only the issue's changes and preserve unrelated user changes; a clean entire working tree is not required. Do not infer permission to omit the commit from an issue's silence about delivery. If committing is not authorized or possible, report the verification and remaining commit step, and leave the issue open; do not treat passing tests as permission to close uncommitted work.
5. Record reusable learning or faulty assumptions in a comment so the review summary carries them, and open linked follow-up work for anything deferred. Such follow-up blocks Red closure only if it invalidates acceptance or verification.

For a performance claim, benchmark the starting behavior before editing and the changed behavior with the same harness. Record the starting commit and relevant working-tree changes, command, dataset/shape, seed, metric, and both results. Claim an improvement only when the comparison shows one. If results are slower or inconclusive, preserve existing user work, handle it as a pause trigger, and leave the issue open while its performance criteria remain unmet.

## Spikes

Use a spike, titled `Spike <question>`, to run an experiment such as a prototype, benchmark, or reproduction whose result a decision gate needs. Its body states the question as its objective and the evidence that would answer it as acceptance criteria. Keep spike code out of the main line, on a spike branch or under gitignored `.kata/`, unless the decision makes it a deliverable.

Close a spike once its findings are written to the decision gate's `## Findings`, with `reason: "done"` and genuine evidence: `commit` on a spike branch, `test` for commands that produced results, or `reviewed-paths` for code examined. Spike closure asserts recorded findings, not shipped implementation, so the commit requirement does not apply.

## Close The Implementation

Record what changed, checks performed, skipped checks, residual risk, and deferred work in the close's outcome comment or a reviewed artifact.

For a completed implementation, close with `reason: "done"` and `commit` evidence citing the commit containing the reviewed and verified work. If completion spans several commits, include the relevant commit evidence. Tests, reviewed paths, and a PR URL are supplemental evidence, not substitutes for the commit. Never cite an unrelated HEAD or close first with a promise to commit later.

Leave the issue open while its implementation is uncommitted, required verification is incomplete without an accepted rationale, or an additional requested delivery step remains unfinished. Do not create an empty commit for work that made no changes; use the appropriate no-change or other disposition from SKILL.md.
