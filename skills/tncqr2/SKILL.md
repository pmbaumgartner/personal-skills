---
name: tncqr2
description: Thermo-nuclear code-quality review with evidence checks, whole-codebase and plan scope, and findings you pick by ID.
disable-model-invocation: true
---

# Thermo-Nuclear Code Quality Review 2.0

Read [references/thermo-nuclear-code-quality-review.md](references/thermo-nuclear-code-quality-review.md) and apply it. Layer on the following additions:

## Scope
- **No diff given.** For "all code" or when there is no diff, review the whole codebase; don't look for a branch diff first.
- **Plans.** A plan or design document can be reviewed too. Check its steps against the current code and against what the user said they want.

## Claims
- **Ran or read.** Say for each finding whether you ran something or only read the code. Call a finding verified only if a command, test or run in this session showed it. Run a cheap check before calling a finding a blocker.
- **Outside behavior.** A claim about how a framework, library or runtime behaves needs a trace into that code or a run. It can't be inferred from the calling code.
- **Sub-agents.** When the review is split across sub-agents, don't put conclusions in their prompts, so their findings are independent checks, not confirmations.

## Remedies
- **Check before recommending.** Before recommending removal or restructuring, check what uses the code and what its tests protect.
- **Metrics.** Size and complexity metrics suggest candidates; they are never the goal. Landing just under a limit doesn't satisfy it.

## Output
A short list in the conversation that the user can accept, reject or modify by ID:
1. One line with the scope, the revision and the verdict: `revise`, or `approve` when nothing above the bar remains (say `converged` on a re-review).
2. Decisions and behavior changes the user should see before anything is changed (`D1`, `D2`, …): removals, changed observable behavior, platform assumptions. One line each, with a recommendation.
3. The findings (`R1`, `R2`, …), most valuable first. Each gives its location, the recommendation, whether it was run or read, and its severity: `blocker` (one of the original's presumptive blockers), `major` or `minor`.
4. A question asking which IDs to act on. Don't change code until the user answers.
