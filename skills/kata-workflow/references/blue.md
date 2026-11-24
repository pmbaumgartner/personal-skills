# Blue Issues

Blue issues are the user's gates in an epic: an optional decision gate before implementation and a review gate after it. Agents prepare them; the user decides or accepts. A standalone question for the user with no planned implementation is a decision gate without a chain. Apply the shared epic, attribution, evidence, and close rules in SKILL.md.

## Decision Gate

Collect every consequential choice the epic needs into one gate so the user decides in a single pass. Before asking, settle what evidence can settle; run experiments as Red spikes that block the gate. Reuse choices the user has already made for this scope.

While the gate is open, its body holds:

- `## Context`: the epic goal and relevant constraints.
- `## Questions`: each open choice with viable options, tradeoffs, a recommendation, and what would change it.
- `## Findings`: spike results and other evidence bearing on the questions.

Hand the gate to the user once, with all its questions, as SKILL.md describes. When the user answers, rewrite the body around the result: each decision with its rationale, rejected alternatives that affect later work, conditions to revisit, and links to the chain. Leave the evidence trail in comments. Add `## Decision Artifact` and `## Deliverables` only when a separate reviewed artifact is needed; for a required repo document, use the project's convention or `docs/<slug>.md`. Keep the essential result in the issue even when detailed analysis lives elsewhere.

When a mid-chain discovery escalates, reopen the gate, add the new question to `## Questions`, hand the gate to the user again, then fold the answer into the decisions and close it again.

## Review Gate

Create the review gate with the epic. Until the chain's final issues exist and block it, the gate has no open blocker and looks ready, so keep it claimed while the chain is created and release it once they do. While the chain runs, its body holds:

- `## Goal`: what the epic delivers.
- `## Scope`: what is in and out.
- `## Authority`: what the user authorized, in their words, including granted delivery steps and hard limits.
- `## Acceptance`: observable outcomes for the whole epic.

When the last blocking Red issue closes, claim the gate and verify the epic as a whole. Each Red issue was verified alone, and a later issue can break an earlier one, so check every `## Acceptance` outcome against the final integrated commit. Where the harness can start one, prefer a fresh agent that did not implement the chain, given only the gate body and the commit: it tests the result, not its memory of the work, and reports to this session, which records the outcome. A failed outcome becomes a Red issue blocking the gate.

Then add the review summary so the user can review the epic in one sitting:

- `## Summary`: what changed and how it meets acceptance, with commits and any branch or pull request.
- `## Agent Decisions`: choices made during the chain, each with its Red ref, rationale, confidence, and reversal; material assumptions accepted without resolution.
- `## Deviations`: departures from the plan or the decision gate, or none.
- `## Verification`: each acceptance outcome as checked on the final commit and who checked it, checks skipped, and residual risk.
- `## Deferred`: follow-up work with refs, or none.

Link detailed records rather than repeating them, then hand the gate to the user as SKILL.md describes.

When the user requests changes, create Red issues for them as one batch, each blocking the gate. Complete them, verify the epic again, update the summary, and hand the same gate back. When the user accepts, record the acceptance in a comment, perform the granted delivery steps, and close. A step that needs the user's confirmation in the current session (SKILL.md) waits for it: leave the gate open and hand it to the user again with that request.

## Close The Gate

Close only after the user's decision or acceptance is recorded on the issue, and any deliverables are reviewed. Agreement to investigate does not settle a choice. Close a decision gate with deferred questions only when the user decided to defer them and the record explains the resulting limits. Decision gate closure asserts settled decisions, not shipped implementation.

Closing a gate for any reason releases the issues it blocks. Before closing a gate whose proposal the user declined or changed, close the issues that are no longer wanted and re-block any that still await a decision. When the user declines the whole epic, close its issues and then both gates as `wontfix`.

Use genuine typed evidence for `reason: "done"`. The user's decision or acceptance is `external` evidence: an account of what they decided, when, and which comment records it, such as `{"type": "external", "account": "The user chose the SQLite store on 2026-11-17; recorded in comment <uid>."}`. Add `reviewed-paths` for each deliverable; for a review gate add `commit` evidence for the epic's commits and `pr` where relevant.

Match the close reason to the outcome:

- The user decided or accepted: `reason: "done"`.
- Keep current behavior or no change needed: `reason: "audit-no-change"` with `{"type": "no-change-audit", "rationale": "<what was reviewed>"}`.
- The user declines the proposed work: `reason: "wontfix"` with the rationale in `message`.
