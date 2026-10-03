# Agent Decision Mode

Use this reference after the user explicitly delegates decisions for reversible, non-production work. Apply the shared attribution and issue lifecycle rules in SKILL.md.

## Record Authority

Add the mode and authority source to the root issue or reviewed policy:

```md
## Decision Mode
Agent

## Decision Authority
<The user's delegation, authorized scope, and constraints.>
```

Children inherit the mode and cite the root or policy. An active Goal alone does not delegate decisions. Agent mode changes who decides; it does not authorize deployment, destructive operations, external communication, spending, or scope expansion.

The primary agent owns the delegated decision and signoff. Close Blue only after signoff and required review; this records the agent's authorized decision, not later human endorsement.

## Decide And Continue

Frame Blue decisions using [blue.md](blue.md). Gather proportionate evidence, compare plausible alternatives, and identify the strongest objection and evidence that would reverse the choice. Choose the smallest, simplest, easiest-to-reverse option when evidence is close. Resolve researchable questions; record remaining assumptions rather than adding human checkpoints.

Record signoff in the decision record:

```md
## Decision Signoff
**Mode:** Agent
**Authority:** <root-ref or policy>
**Decision:** <choice>
**Confidence:** High | Medium | Low
**Material assumptions:** <facts accepted without resolution, or none>
**Reversal:** <how to undo or supersede the choice>
```

Keep evidence, rationale, and rejected alternatives in the decision record without repeating them in signoff. Low confidence calls for explicit uncertainty and a reversible choice. Reopen or supersede the decision if later evidence invalidates it.

For an authorized continuous goal, select and claim ready work, complete it, verify and close, reconcile necessary follow-ups, and continue until the goal is achieved or a genuine blocker prevents progress. Defer nonessential uncertainty to linked follow-up work; create no backlog merely to keep the loop active. Record unavailable authority or environmental dependencies when they prevent completion.

## Report

Report decisions retrospectively: relevant refs, choices and reasons, confidence, material assumptions, reversal paths, deferred work, verification, and the resulting delivery state. Link detailed records. If the user later disagrees, reopen or supersede affected decisions and track the needed reversal.
