# Blue Issues

Blue issues are the user's gates in an epic: an optional decision gate before implementation and a review gate after it. Agents prepare them; the user decides or accepts. A standalone question for the user with no planned implementation is a decision gate without a chain. Apply the shared epic, attribution, evidence, and close rules in SKILL.md.

## Decision Gate

Collect every consequential choice the epic needs into one gate so the user decides in a single pass. Before asking, settle what evidence can settle; run experiments as Red spikes that block the gate. Reuse choices the user has already made for this scope.

While the gate is open, its body holds:

- `## Context`: the epic goal and relevant constraints.
- `## Questions`: each open choice with viable options, tradeoffs, a recommendation, and what would change it.
- `## Findings`: spike results and other evidence bearing on the questions.

Present all questions to the user together and pause once. When the user answers, rewrite the body around the result: each decision with its rationale, rejected alternatives that affect later work, conditions to revisit, and links to the chain. Leave the evidence trail in comments. Add `## Decision Artifact` and `## Deliverables` only when a separate reviewed artifact is needed; for a required repo document, use the project's convention or `docs/<slug>.md`. Keep the essential result in the issue even when detailed analysis lives elsewhere.

When a mid-chain discovery escalates, reopen the gate, add the new question to `## Questions`, ask the user, then fold the answer into the decisions and close it again.

## Review Gate

Create the review gate with the epic. While the chain runs, its body holds:

- `## Goal`: what the epic delivers.
- `## Scope`: what is in and out.
- `## Authority`: what the user authorized, including granted delivery steps and hard limits.
- `## Acceptance`: observable outcomes for the whole epic.

When the last blocking Red issue closes, claim the gate and add the review summary so the user can review the epic in one sitting:

- `## Summary`: what changed and how it meets acceptance, with commits and any branch or pull request.
- `## Agent Decisions`: choices made during the chain, each with its Red ref, rationale, confidence, and reversal; material assumptions accepted without resolution.
- `## Deviations`: departures from the plan or the decision gate, or none.
- `## Verification`: checks run, checks skipped, and residual risk.
- `## Deferred`: follow-up work with refs, or none.

Link detailed records rather than repeating them. Add the `needs-review` label, release the gate with a comment, and ask the user to review.

When the user requests changes, create Red issues for them as one batch, each blocking the gate, and remove `needs-review`. Complete them, update the summary, and request review again on the same gate. When the user accepts, record the acceptance in a comment, perform any granted delivery steps, and close.

## Close The Gate

Close only after the user's decision or acceptance is recorded on the issue, and any deliverables are reviewed. Agreement to investigate does not settle a choice. Close a decision gate with deferred questions only when the user decided to defer them and the record explains the resulting limits. Decision gate closure asserts settled decisions, not shipped implementation.

Use genuine typed evidence. For a decision gate: `reviewed-paths` for each deliverable and for the code or docs the investigation examined, or a relevant commit, pull request, or passing verification command. For a review gate: `commit` evidence for the epic's commits, plus `pr` and `reviewed-paths` where relevant. The issue or comment containing the decision does not itself supply typed close evidence. Do not create a file solely to satisfy close evidence.

Match the close to the outcome when no typed evidence fits `reason: "done"`:

- Keep current behavior or no change needed: `reason: "audit-no-change"` with `{"type": "no-change-audit", "rationale": "<what was reviewed>"}`.
- The user declines the proposed work: `reason: "wontfix"` with the rationale in `message`.
- A durable choice worth keeping in the repository: record it in a tracked decision document and cite it with `reviewed-paths`.
