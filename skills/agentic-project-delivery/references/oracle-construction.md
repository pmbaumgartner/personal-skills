# Oracle Construction

Load this reference when an acceptance oracle is missing, weak, newly created, or materially changed. The output should normally be one completed [acceptance contract](../assets/acceptance-contract.md), not a second overlapping artifact.

## Procedure

1. **State the candidate decision.** Define exactly what candidate, version, artifact, migration result, or behavior is being accepted or rejected and at which boundary.
2. **Enumerate material failure modes.** Include functional errors, compatibility breaks, state corruption, security or privacy failures, performance regressions, recovery failures, packaging errors, and operational defects that matter for this project.
3. **Map every failure mode to an observable sensor.** Name the deterministic check, comparison, invariant, replay, benchmark, scan, telemetry signal, or explicitly acknowledged coverage gap that can reveal it. Do not substitute a list of test types for this mapping.
4. **Select and freeze inputs, datasets, baselines, and provenance.** Record origin, collection method, version, content hash, relevant licenses or privacy constraints, and authorized refresh procedure. Separate training or implementation examples from evaluation data when leakage could invalidate the result.
5. **Define hard gates, comparative gates, and diagnostic metrics.** Hard gates reject independently; comparative gates reject unacceptable deltas against a baseline; diagnostics explain results but do not silently become acceptance criteria.
6. **Provide one reproducible command with nonzero rejection semantics.** The command must run from a stated environment, emit a concise decision, return zero only for acceptance, and return nonzero for a rejected or invalid evaluation. Pin or record material dependencies.
7. **Define protected files, thresholds, and change authority.** Identify what implementation agents cannot modify, who may authorize a change, the evidence required, and where the separate decision is recorded.
8. **Validate the oracle with known-good and deliberately broken candidates.** Include representative negative controls for the failure modes with the highest consequence or escape likelihood. A check that has never rejected a plausible defect is not yet credible.
9. **Measure repeatability, runtime, and flakiness.** Run enough repetitions to characterize nondeterminism, document variance treatment and retry rules, and assign the oracle to a fast PR tier or slower release tier based on cost and feedback needs.
10. **Produce attributable evidence.** Record candidate identity, oracle version, frozen input hashes, command, environment, per-gate results, diagnostics, timestamp, and actor or CI identity. Create JSON or another machine-readable record only when executable tooling consumes it; otherwise retain one stable minimal record linked from Kata.

## Oracle-adequacy checklist

The oracle is adequate for its intended decision only when it is:

- **Falsifiable:** a materially wrong candidate can fail.
- **Model/implementation-neutral:** it evaluates observable outcomes without requiring the candidate to use the expected implementation.
- **Reproducible:** another authorized actor can run the command against the same frozen inputs and interpret the result.
- **Sensitive to representative defects:** known negative controls fail for the intended reason.
- **Protected from self-certification:** implementers cannot weaken protected checks, inputs, or thresholds without explicit authority.
- **Fast enough for its intended feedback tier:** PR-tier checks support correction loops; slower release checks are scheduled before distribution or exposure.
- **Explicit about uncertainty and uncovered failures:** gaps, variance, and unobservable failure modes are recorded with enablement or residual-risk decisions.

If a material failure mode has no credible sensor, classify the project as needing enablement or reduce its delegated scope. Do not compensate by requiring humans to read every generated line.
