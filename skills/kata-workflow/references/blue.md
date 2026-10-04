# Blue Issues

Use Blue for a settled decision, finding, or recommendation. Apply the shared classification, attribution, evidence, and close rules in SKILL.md.

## Frame The Question

Include these issue fields:

- `## Question`: what must be resolved.
- `## Context`: the higher-level goal and relevant constraints.
- `## Decision Stakes`: for consequential decisions, `Consequential: Yes` with a brief reason; omission means nonconsequential.
- `## Approach`: options, evaluation criteria, and evidence to gather.
- `## Exit Criteria`: what makes the finding or decision settled.
- `## Decision Mode`: include Agent mode and its inherited authority when delegated; omission means Human mode.

Keep the frame in the body while investigating. Once settled, rewrite the body around the result: question, decision and owner, rationale, rejected alternatives that affect later work, conditions to revisit, and follow-up links. Drop investigation-only sections such as Approach and Exit Criteria, and leave the evidence trail in comments. Add `## Decision Artifact` and `## Deliverables` only when a separate reviewed artifact is needed. Keep the essential result in the issue even when detailed analysis lives elsewhere. For a required repo document, use the project's convention or `docs/<slug>.md`.

Draft the question, criteria, options, and evidence needed before settling a recommendation. Use this frame to check alignment with the higher-level goal; it is not a prewritten answer.

## Investigate And Decide

1. Read the issue, parent, links, and previous findings. Check that the question serves the authorized goal.
2. Gather evidence proportionate to the stakes. Compare plausible options, the strongest credible alternative, and what would change the recommendation.
3. Apply the decision mode from SKILL.md. For consequential Human-mode work, reuse an explicit user choice already made for this scope; otherwise present viable options, tradeoffs, a recommendation, and what would change it, then pause once for the decision owner named by the issue or project (default: the user).
4. Record the finding, decision, who decided, rationale, confidence, and evidence. Include material assumptions, rejected alternatives, or dead ends when they would affect later work. In Agent mode, add the signoff from [agent-mode.md](agent-mode.md).
5. Link necessary follow-up work. If further investigation is required to settle this issue, open a child Blue issue and block this issue on it. Record intentionally deferred questions as part of the decision.

## Close The Decision

Close after the mode-appropriate decision is recorded and any deliverables are reviewed. Agreement to investigate does not settle a consequential Human-mode choice.

Resolve open questions that affect the exit criteria before closing. Close with deferred questions only when the explicit decision is to defer them and the record explains the resulting limits. Blue closure asserts settled knowledge or a recorded decision; it does not assert that follow-up implementation has shipped.

Use genuine typed evidence: `--reviewed <path>` for each deliverable and for the code or docs the investigation actually examined, a relevant commit or PR, or a verification command that actually passed. The issue/comment containing the decision does not itself supply typed close evidence. Require a commit only when relevant to the requested delivery state. Do not create a file solely to satisfy close evidence.

Match the close to the outcome when no typed evidence fits `--done`:

- Keep current behavior or no change needed: `--audit-no-change --evidence "no-change-audit:<what was reviewed>"`.
- Decline the proposed work: `--wontfix` with the rationale.
- A durable choice worth keeping in the repository: record it in a tracked decision document and cite it with `--reviewed`.
