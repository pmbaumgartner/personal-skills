# Techniques

Read only the section for the current obstacle.

## Find and compare candidates

When no useful candidate is visible, try a way in:

- Solve a smaller instance that keeps the conditions that make it hard.
- Work backward from the required result to its preconditions.
- Adapt a related solution after naming the differences that matter.
- Change the representation or temporarily relax a constraint to expose structure.

Bring what the attempt revealed back to the original requirements; exploration does not authorize a changed commitment.

For an open, consequential design, sketch two materially different viable approaches, compare the decisive tradeoff, and recommend one. Do not manufacture an alternative when only one credible path exists.

Count each unfamiliar part's cost in learning, operation, and verification against the team's capacity. Do not assume AI assistance makes an unfamiliar part cheap; check it against current documentation and behavior you can verify. For a prototype, state what it should teach and whether to discard or develop it afterward.

## Diagnose a fault

During an active incident, contain the damage first and preserve evidence. Beyond the usual reproduce, reduce, compare, and bisect:

- Isolating a component changes state, ordering, timing, and load; a changed outcome does not show which factor caused it.
- For intermittent faults, capture timing, order, inputs, state, and environment. A short passing run does not show the fault is fixed.

Use a debugger, logs, or traces to expose the divergence. Conditional breakpoints, expression evaluation, and stack navigation can replace guesswork. For paths spanning services, correlated events can make the execution understandable. Where useful, support targeted diagnostics or adjustable log levels without a redeploy; respect privacy and security constraints and avoid exposing secrets or unnecessary personal data.

Fix the cause the evidence supports. Replace infrastructure only when the evidence points there.

For performance questions, profile representative workloads before optimizing. Include network latency and calls, not just CPU work, and check whether the measured bottleneck limits the intended outcome.

## Handle external or retried effects

Distinguish accepted, completed, failed, and unknown outcomes. Check what happens if the effect occurs before its result is recorded, and what a retry could repeat; a durable record alone does not guarantee exactly one effect. Keep state transitions valid under concurrent and late updates, and validate external inputs even when the internal model excludes invalid states. Make recovery actions understandable to whoever operates the system. Add only the protections the task requires.
