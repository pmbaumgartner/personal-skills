# Evaluation and Forecasting

Load this reference when designing an APD delivery pilot, estimating staged work, deciding whether to increase concurrency, or auditing agent-heavy delivery.

## Distinguish the experiment

A product or research experiment tests whether an idea or behavior works. It can remain in the repository's normal workflow.

An APD delivery pilot tests whether the delivery system can repeatedly turn representative packets into accepted, integrated work at tolerable cost and risk. Do not call work a delivery pilot unless the decision depends on delivery measurements.

## Measure accepted work

Do not use lines of code, tokens, commits, pull requests, issue count, agent count, or compiler errors removed as primary progress measures.

A delivery pilot must record:

- elapsed time from ready to integrated;
- accepted, rejected, retried, and discarded work;
- first-pass versus repaired acceptance;
- human attention and decision-waiting time;
- defects caught by each verification layer;
- the scale, reshape, enable, or stop decision.

Cost, queue time, conflicts, compatibility, performance, and escaped defects are useful when material. Validate Kata closes before treating them as accepted throughput.

## Choose representative work

Use an ordinary packet that also contains the characteristic difficulty: coupling, weak documentation, performance sensitivity, state, platform variation, or another dominant risk. Do not pilot only the cleanest slice.

Exercise the relevant delivery loop: archaeology, packet framing, claim, implementation, fast checks, broader verification, integration, evidence-backed close, and rollback or discard. Include human or release decisions only when the current boundary requires them.

## Track production and waiting separately

- **Production time:** agents and tools producing and checking work.
- **Decision waiting time:** delay from unresolved intent, architecture, acceptance, risk, or release authority.

When waiting dominates, adding agents raises work in progress. Improve decision rights, specifications, or human availability first.

## Build a local reference class

Use accepted representative packets and include fast successes, retries, discards, human intervention, integration failures, and downstream defects. Group by meaningful difficulty or risk.

Forecast favorable, expected, and adverse ranges. Include enablement, verification, integration, waiting, stabilization, and decommissioning when they are part of the outcome. Do not extrapolate raw generation speed.

## Scale only into spare capacity

Watch for growing unverified work, longer CI or integration queues, decision backlogs, falling first-pass acceptance, broader conflicting changes, weak close evidence, and more post-integration defects.

When verification or integration is the constraint, cap or reduce launches and first move existing capacity to the bottleneck. Test a specialized capacity increase as its own bounded pilot.

## Improve the harness

Attribute defects to the sensor that caught them. Turn recurring reviewer findings into deterministic controls where practical. Remove redundant instructions and checks when a stronger sensor replaces them.

Human attention should concentrate on outcome, architecture, protected acceptance, exceptions, and release authority—not routine rescue or ritual review.

## Decide and record

Choose:

- **Scale:** evidence supports one bounded increase.
- **Extend:** another representative packet can resolve uncertainty.
- **Enable:** improve the oracle, tooling, seams, environment, or decision flow.
- **Reshape:** change scope or topology.
- **Stop:** benefit, economics, or controllability do not justify continuation.

Record the decision as an attributable outcome comment unless it triggers a separate decision issue under the main workflow.
