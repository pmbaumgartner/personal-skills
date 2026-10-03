# Blue Kata Issues

Blue issues are decision and discovery work. Their output is "we know enough to
act," not shipped code.

## Contents

- Issue Body
- Decision Frame
- Workflow
- Final Record
- Close-Out

## Issue Body

Use label `blue`. Start the title with a verb naming the decision or finding, such as the Blue verbs listed in SKILL.md; do not add a `[Blue]` prefix.

Examples: `Decide whether to retain ANN dispatch`, `Investigate Safari callback duplication`, `Compare vector-index options`.

Required fields:

- `## Decision Mode` - `Human`, or `Agent` with the inherited authority source; omitted means Human
- `## Question` - the decision or unknown to resolve
- `## Context` - selected context, not a full history
- `## Decision Stakes` - `Consequential: Yes | No - <brief rationale>`, using the definition in SKILL.md
- `## Approach` - how to investigate
- `## Exit Criteria` - what makes the decision settled

Use one of two recording scales:

- Inline Blue - when the shared issue can hold the decision and its supporting evidence. Record the frame, finding, decision, rationale, evidence, and who decided in the issue body or a short comment. A separate artifact and `## Deliverables` block are needed only if closure requires a reviewed record as described below.
- Artifact Blue - when the issue record is insufficient for the detailed analysis or evidence collaborators need. Add `## Decision Artifact` and `## Deliverables` fields and link an accessible shared or tracked document. Keep the essential finding, decision, rationale, evidence, and decision owner in the shared issue as well. Use `.kata/` for drafts and supplementary local material. For a required repo document, prefer `docs/<slug>.md` unless the project has another convention.

In Human mode, the primary agent decides nonconsequential Blue work by intent; the decision owner named by the issue or project, defaulting to the current user, decides consequential Blue work. In Agent mode, the primary agent is the decision owner.

## Decision Frame

The first draft is an outline with selected context, not the answer. Use it to check whether the original issue still points at the right higher-level goal. For Inline Blue, the required issue fields may serve as this frame; do not create a document merely to reproduce them.

Artifact Blue doc shape:

```md
---
kata: <ref>
created: YYYY-MM-DD
---

# <Title>

**Decision to make:**
**Why now / higher-level goal:**
**Goal check:**
**Consequential:** Yes | No - <brief rationale>
**Evaluation criteria:**
**Hypotheses / options:**
**Evidence needed:**
**Known constraints:**
**Open questions:**
```

Do not rush to a final recommendation in the first draft.

## Workflow

1. Read the issue body, parent, links, and existing docs.
2. Draft the decision frame in the issue for Inline Blue or at the artifact path for Artifact Blue.
3. Classify the decision as consequential or nonconsequential. Pause early only when scope or authority is unclear.
4. Investigate and compare plausible alternatives in proportion to the stakes. Resolve researchable questions with evidence; in Agent mode, document any remaining assumptions.
5. Identify the strongest credible alternative and what evidence would change the recommendation.
6. Decide:
   - In Human mode, state intent and decide nonconsequential work without a checkpoint.
   - In Human mode, reuse an explicit user decision already recorded for this choice; otherwise present consequential work in the format below and pause once for the human decision owner.
   - In Agent mode, choose without a human checkpoint and use the signoff in agent-mode.md.
7. Record the decision and who decided, then create necessary follow-up issues.
8. Finalize the shared issue record and any required artifact. Review every deliverable and supply typed evidence before closing.

For a consequential Human-mode decision, present:

```md
## Decision Needed

- **Option A:** <tradeoff>
- **Option B:** <tradeoff>
- **Recommendation:** <choice and reason>
- **What would change the recommendation:** <evidence, or none>
```

Use 2-3 viable options when they exist; do not invent alternatives. High uncertainty scales investigation but does not by itself require a human checkpoint. For nonconsequential Inline Blue work, one proportionate evidence pass and recorded intent may be enough.

## Final Record

After evidence and mode-appropriate calibration, convert the frame into the final issue record or artifact:

```md
**Finding:** 1-3 sentences.
**Decision:** The chosen option and who decided.
**Recommendation:** What next? Link follow-up Red/Blue issues.
**Confidence:** High / Medium / Low - what would raise it?
**Evidence:** Commands, benchmarks, docs, upstream behavior, links.
**Rejected alternatives:** What was considered and why it lost.
**Dead ends:** What did not work, so nobody repeats it.
```

For Inline Blue, keep only the fields needed to make the decision legible; record rejected alternatives and dead ends only when material.

Remove `## Open questions` before close, unless the final decision is explicitly to defer and the remaining questions are part of that outcome.

If a question needs new investigation, open a child Blue issue and mark the current issue `--blocked-by` it rather than stalling.

## Close-Out

Blue closure must include:

- substantive `--message` naming the settled decision and verification (at least 40 characters)
- mode-appropriate decision and owner recorded in the shared issue body or comment: agent intent for nonconsequential Human-mode work, explicit human choice for consequential Human-mode work, or primary-agent signoff in Agent mode
- at least one valid typed evidence item for `--done`; use `--reviewed <path>` for every artifact deliverable
- `--commit <sha>` when there is a relevant commit, but do not require one just to close Blue work
- follow-up issues listed in the decision record, if opened
- material rejected or deferred options recorded in the decision record

For Inline Blue, use genuine existing evidence such as a relevant `--commit`, `--pr`, a verification command that actually passed via `--evidence "test:<cmd>"`, or a reviewed supporting path. A decision recorded in an issue or comment does not itself supply a supported typed evidence item. Do not invent an issue/comment prefix or describe ordinary research as a test.

If no existing typed evidence fits, write a concise decision and review record to `.kata/blue/<ref>-review.md`, add that path to `## Deliverables`, inspect it, and close with `--reviewed <path>`. Include the finding, decision, owner, rationale, and checks performed. Copy the essential record into the shared issue before closing so the local file is supplementary. Use an accessible shared or tracked artifact instead if collaborators need detail beyond the issue record. A commit is not required solely for this fallback.

Example:

```bash
kata close abc4 --done \
  --message "Kept match-based ANN dispatch after reviewing the decision record." \
  --reviewed docs/ann_abstraction_decision.md \
  --agent
```

For consequential Human-mode work, agreement to investigate is not the final decision; an explicit user choice already made for the same scope does not need reconfirmation.
