# Red Kata Issues

Red issues are implementation work. Their output is a verified change at the delivery state requested by the user or required by the repository workflow.

## Issue Body

Use label `red`. Start the title with a verb naming the implemented change, such as the Red verbs listed in SKILL.md; do not add a `[Red]` prefix.

Examples: `Fix Safari callback duplication`, `Add ANN recall gates`, `Migrate legacy issue references`.

Required fields:

- `## Objective` - the known goal
- `## Context` - selected context needed to execute
- `## Scope In` / `## Scope Out` - boundaries for the work
- `## Acceptance Criteria` - observable completion criteria
- `## Pause Triggers` - conditions that should stop work and open Blue
- `## Deliverables` - every path that must be reviewed before close

Small Red issues may omit `Scope In/Out` only when acceptance criteria are
unambiguous.

Pause trigger examples: loss does not converge after repeated runs, data schema differs from Blue assumptions, or the implementation would require changing the settled product decision.

Red work still permits local implementation judgment. Do not open Blue merely to choose among equivalent local techniques that leave scope, acceptance criteria, settled decisions, and reusable policy unchanged.

## Workflow

Claim the issue and set `work.attention=ok` before starting. If you pause with work unfinished, set `needs-human` or `stuck` with a `work.attention_msg` and leave a durable comment.

1. Read the issue body and linked decision docs.
2. Check `Pause Triggers` before broadening scope.
3. Implement the smallest change that satisfies acceptance criteria.
4. Run focused checks while developing.
5. Run the issue's required verification before close.
6. Commit when the user's request or repository workflow requires it. Otherwise, a verified working-tree change may satisfy the requested delivery state; record that it remains uncommitted.
7. If uncertainty would change scope, acceptance criteria, a settled decision, or a reusable policy, stop and open or update a Blue issue.
8. Before close, consider whether execution produced reusable learning, exposed a faulty assumption, or suggests changing future decisions or process. If so, record it in a linked Blue issue; otherwise close without retrospective ceremony.

The learning review does not block Red closure unless it invalidates acceptance or verification. A follow-up Blue issue is sufficient when the Red change remains complete.

## Performance Work

For any Red issue that claims a performance improvement, optimization, fewer syncs, fewer allocations, faster runtime, lower memory, or benchmark evidence:

- Run or create the baseline benchmark against the starting behavior before changing code; identify the commit and any relevant working-tree changes.
- Record the baseline command, dataset or shape, seed, metric, and result.
- After implementation, run the same benchmark against the changed code.
- Do not call the change an improvement unless same-harness before/after results show it.
- If the benchmark is slower or inconclusive, record the result and choose the smallest reversible outcome that serves the authorized goal. In Human mode, ask only when the choice is consequential and not already settled by the user. In Agent mode, record the choice and continue. Revert only your own changes while preserving existing user work. Keep the issue open if its performance acceptance criteria remain unmet.

## Close-Out

Red closure must include:

- one-sentence `--message` naming what changed and how it was verified (at least 40 characters)
- the delivery state requested by the user or required by the repository workflow
- `--commit <sha>` when the completed work was committed; for uncommitted work, use verification and reviewed-path evidence and explicitly record the working-tree delivery state
- one `--evidence "test:<cmd>"` per verification command that passed; use `--test "<cmd>"` only when there is exactly one
- skipped or unavailable checks documented in reviewed docs/artifacts when they
  affect future work
- `--reviewed <path>` for every deliverable path
- residual risk or deferred follow-up documented in reviewed docs/artifacts

If the issue has no doc/artifact deliverable, record skipped checks, residual
risk, or deferred follow-up in a short kata comment before closing.

When a commit is required, supply the commit containing the completed work. A PR URL alone does not satisfy that requirement. Closing verified working-tree work asserts the requested implementation is complete; it does not assert that it was committed, merged, or deployed.

Example:

```bash
kata close abc4 --done \
  --message "Added ANN recall gates to the benchmark suite." \
  --commit <sha> \
  --evidence "test:cargo test" \
  --evidence "test:uv run pytest" \
  --reviewed tests/test_ann_recall.py \
  --reviewed examples/ann_benchmark.rs \
  --agent
```

Do not close if verification did not run and no accepted rationale is recorded.
