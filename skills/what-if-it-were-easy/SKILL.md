---
name: what-if-it-were-easy
description: Find the simplest sound path to a developer's intended outcome, counting the effort to use, operate, and change the result. Use when a problem is poorly framed, overcomplicated, or stuck.
disable-model-invocation: true
---

# What if it were easy?

Find the simplest sound way to achieve the user's intended outcome, counting the effort of using, operating, repairing, and changing the result.

Use the four questions below to direct attention where an answer could change the decision. Question 4 sets how deep to go on the others. For a settled task, check the facts that matter and proceed; do not reopen the choice or produce a four-part report.

Preserve the user's purpose, authorized scope, and required properties such as correctness, access, accessibility, durability, and recovery. Treat a reframe as a hypothesis: make any change of outcome or scope explicit for the user to choose. Simplicity does not justify dropping a requirement.

Advice alone does not authorize edits. Make confusion safe to admit: question a design you cannot understand rather than pretending; uncertainty is not evidence of incompetence.

## 1. Whose outcome needs to improve, and what prevents it?

**Don Norman: establish whose activity improves before accepting the proposed problem.**

Use a concrete instance to identify who needs to do what, where the activity breaks down, and what observable result would count as success. For technical work, establish inputs, outputs, and required properties.

Separate the need from a proposed mechanism, inherited convention, or untested explanation. Check whether improving the chosen measure could leave the actual outcome unchanged or worse. Find the limiting factor: would changing this part improve the whole result, or move work elsewhere?

## 2. Which uncertain belief could change the answer, and how can we check it?

**Peter Norvig: make the central assumption concrete and expose it to a check that could overturn it.**

Separate observations, estimates, and explanations. Check the assumption that creates the most work or could invalidate the recommendation. Use the cheapest adequate evidence: existing artifacts, a rough calculation, a representative case, runtime observation, a focused experiment, or observation of an intended user.

When feasible, try a direct baseline and let observed failures guide added complexity. Required protections still apply to the experiment.

Challenge the candidate with the case most likely to break it. Say what is known, what remains assumed, and which checks actually ran. For unexplained behavior, use [Diagnose a fault](references/techniques.md#diagnose-a-fault).

## 3. What can we remove, simplify, or contain without losing required behavior?

**Rich Hickey: reject apparent simplicity that forces independent concerns to change together.**

Look for work that can disappear through a clearer representation, a change in the activity, or a negotiable constraint. Consider building nothing new, existing capabilities, a bounded manual approach, and a direct implementation. Add machinery only where a demonstrated need or required property earns its cost.

Imagine the result already works: which decision, handoff, conversion, state, duplicate source of truth, or need for a feature disappeared?

Distinguish familiarity and ease of adoption from simplicity. Name concerns that must be understood or changed together. Prefer models that eliminate invalid combinations and boundaries that contain likely changes, counting the interfaces they add.

Grug's countercheck: can someone locate, follow, and debug the behavior? Keep related behavior nearby and data flow visible. Simple duplication can cost less than an abstraction that couples unrelated changes; share knowledge when it genuinely must change together. Understand an existing complication's purpose before removing it.

Count human effort, handoffs, support, and operation, not just code. Trace an ordinary task and its recovery: can someone discover the next action, recognize the result, and correct a mistake? Treat repeated human errors as evidence to investigate the design and environment; prefer prevention and usable recovery over another warning.

When unclear ownership or handoffs produce technical complexity, a clearer owner, agreement, or communication path may remove machinery. Propose organizational changes only within the user's authority and scope.

When stuck or facing an open, consequential choice, use [Find and compare candidates](references/techniques.md#find-and-compare-candidates). For effects outside the current operation, use [Handle external or retried effects](references/techniques.md#handle-external-or-retried-effects).

For code, API, architecture, or testing decisions, read the relevant section of [Engineering details](references/engineering.md).

## 4. What is the smallest sound next action, given the stakes and cost of reversal?

**Ryan Singer: make the design fit what the outcome warrants; challenge work that exceeds that appetite.**

Where scope is flexible, set an appetite (how much effort the outcome warrants, which is not an estimate) and shape the solution to fit it. If the smallest sound option exceeds it, expose the mismatch. Include deliberate learning when it is part of the user's goal.

When consequences are bounded and reversal is cheap and credible, act and check the result. Judge reversal by actual effects, not merely the ability to revert code. When reversal is costly, strengthen the evidence and limit the commitment. Stop investigating once the decision is adequately supported.

## Make the result usable

The lenses genuinely conflict. Untangling concerns can scatter a maintainer's task or add steps for the user (Hickey against Grug and Norman), and more evidence or cleaner boundaries can exceed the appetite (Norvig and Hickey against Singer). For an open, consequential choice, take the strongest objection from the lenses and either improve the recommendation or accept the tradeoff on evidence or a requirement. Do not stage a panel discussion.

Lead with the recommended path and any material reframe. For consequential choices, briefly give the decisive evidence, tradeoff, key assumption, and the condition that would warrant reconsideration. Give a concrete next action and how to verify its result; derive thresholds from the task rather than inventing them. When implementation was requested, carry it out and verify it rather than stopping at advice.

For deeper source context or attribution, see [Sources](references/sources.md). Read only what the current question needs; ordinary use does not require consulting the sources.
