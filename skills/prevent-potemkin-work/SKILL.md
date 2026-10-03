---
name: prevent-potemkin-work
description: Audit project completion claims against independent acceptance evidence. Assess task ledgers, tests, benchmarks, research records, handoffs, milestones, or releases for unsupported claims, omissions, weakened criteria, bypasses, and hidden failures.
disable-model-invocation: true
---

# Prevent Potemkin Work

Assess whether the evidence supports the visible signs of completion. Make no inference about intent: reject unsupported claims regardless of whether they arose from deception, weak verification, misunderstanding, or capability limits.

Audit read-only by default. Use the project's existing source of truth; do not create a competing task ledger.

## 1. Define the audit boundary

State the project, milestone, work items, claims, and acceptance surfaces under review. Obtain:

- the original requests and constraints;
- task states, dependencies, deliverables, and close evidence;
- changed artifacts and the path users actually exercise;
- tests, fixtures, datasets, thresholds, metrics, CI configuration, and relevant history;
- raw commands, logs, outputs, failures, and baselines.

Select a risk-weighted sample when full review is impractical. Include all high-impact claims, acceptance-oracle changes, reopened work, unusual exceptions, and work on which many downstream claims depend. Expand the sample when a material problem appears.

Record what the audit cannot access or did not inspect. Audit silence is not evidence.

## 2. Reconstruct completion independently

Before reading celebratory summaries, derive atomic obligations and non-negotiable constraints from the original sources. For each obligation, identify:

- the claimed state;
- the real-world or user-facing outcome;
- the evidence required;
- the actual evidence found;
- who could change the acceptance criteria.

Use only the highest state supported by evidence: `Pending`, `Produced`, `Exercised`, `Verified`, `Accepted`, `Failed`, or `Blocked`. An artifact that exists is `Produced`; a path that ran is `Exercised`; neither is automatically `Verified`.

For material claims, treat the worker's completion statement as a claim, not completion authority. Identify the protected mechanism or separately authorized actor that grants `Verified`. The worker may run checks and declare readiness, but must not exclusively control the criteria, evidence, and final verified state.

Audit the reporting incentive. If a confident completion claim receives more credit than an accurate incomplete or evidence-insufficient report when verification is weak, the process rewards overclaiming. Define explicit evidence thresholds for completion. Across repeated audits, compare claimed states with later outcomes and track false-positive completions separately from task success.

Classify unsupported success by failure mode, without inferring intent: state mismatch, procedurally invalid success, oracle or specification exploitation, or persuasive but unsupported reporting.

## 3. Map the cheat surface

List 3–6 task-specific ways the work could look successful without satisfying the outcome. Check the relevant routes:

- omit or defer the hardest requirement;
- narrow scope, relax a constraint, or move unfinished original scope into a follow-up;
- leave an old path authoritative while adding an unused replacement;
- substitute mocks, simulations, cached results, or synthetic evidence for the real path;
- hide command failures, warnings, timeouts, discarded examples, or manual repair;
- weaken tests, thresholds, metrics, datasets, expected outputs, or comparison cohorts;
- hardcode fixtures, leak evaluation information, or cherry-pick successful runs;
- choose the strongest-looking parallel result before checking its validity.

Pair each plausible shortcut with a direct detection or falsification check.

Audit reasonable-looking substitutions separately from overt shortcuts: a “control” with no relevant counterfactual, a metric computed on a favorable subset or denominator, a technically disclosed simulation presented as real-path evidence, a proxy measuring a nearby outcome, or compatibility language that leaves the old path authoritative. Ask what obligation each establishes, what cases it excludes, what counterfactual it tests, and what result would falsify its claimed value.

## 4. Audit completion claims

Trace every material claim to an exact command and result, artifact path, source location, log, or reproduction. Downgrade claims without a pointer.

For consequential mutations—such as changing tests, fixtures, evaluator configuration, dependencies, schemas, production paths, task status, or published state—check that the applicable constraints and expected state transition were identified before the action and that the system of record was reread afterward. A successful tool response is not proof of the intended state.

For task records and handoffs, check:

- original acceptance against actual artifacts and behavior;
- fresh and relevant evidence rather than convenient commits or stale runs;
- reviewed deliverables and accurate dependency state;
- failed attempts, deviations, mocks, and unresolved anomalies;
- follow-up work that actually belongs to the original incomplete contract;
- downstream work that relies on a weak or invalidated upstream claim.

Treat phrases such as “pre-existing,” “out of scope,” “backward compatible,” “future work,” and “time constraints” as claims requiring evidence or explicit authority.

## 5. Audit the acceptance oracle

Inspect changes to tests, data, thresholds, metrics, skips, timeouts, mocks, and configuration before trusting reported results.

Map the verifier boundary:

- what the implementer could read or modify;
- which evaluator inputs, expected outputs, hidden data, baselines, parsers, and status transitions were protected;
- which artifacts and measurements were independently recomputed;
- which tampering, leakage, omission, or malformed-output events disqualify the result.

Missing, malformed, or unverifiable evidence cannot earn `Verified`; fail closed at the verification-status boundary.

Determine whether the oracle is:

- **Falsifiable:** a materially wrong result can fail;
- **Real-path:** required integration and user-facing paths are exercised;
- **Representative:** important failure modes and boundaries have sensors;
- **Reproducible:** another authorized actor can rerun and interpret it;
- **Protected:** the implementer cannot silently weaken it.

Run the strongest practical checks yourself. Prefer a real entry-point test, a counterfactual that disables or removes the claimed implementation and makes acceptance fail, a deliberately broken candidate, mutation or negative control, clean-state reproduction, or comparison with a recorded baseline. Exclude worker-local caches, uncommitted files, inherited services, and manual artifacts from clean replay. Lower-level tests do not compensate for an unexercised required path.

For a new, reused, or high-stakes oracle, inspect whether representative counterfeit solutions have been tried. When authorized, run a hacker–fixer–solver cycle: attempt empty or schema-minimal artifacts, hardcoded visible cases, mocked integrations, old-path fallbacks, skipped steps, fabricated metrics, or excluded failures; strengthen the oracle; rerun a legitimate solution; and retain useful counterfeits as regression fixtures.

If reluctant to run one check, run that one first.

## 6. Form the verdict before reading the narrative

Complete a provisional assessment from the original request, raw artifacts, and direct checks. Only then read worker summaries and record omissions, contradictions, or status inflation.

Do not rely on confessions, incriminating language, or visible code smells. Inspect effects, denominators, counterfactuals, and real-path behavior. For recurring audits, vary some samples and probes so the review process does not become a fixed target.

Disqualify results with oracle tampering, hidden-data leakage, omitted required steps, hard-constraint violations, or irreproducible evidence before comparing quality or performance. Do not average a disqualifying gate into a scalar score. For parallel candidates, independently reproduce the winner.

Use critics only to generate suspicions. Ground every adopted finding in direct evidence or targeted reproduction; a critic does not grant completion.

Use these overall risk levels:

- **Low:** direct evidence covers the sampled claims, the oracle rejects representative defects, and residual gaps are bounded.
- **Medium:** evidence is narrow, stale, or weakly traceable, but no material completion claim is contradicted.
- **High:** a material obligation lacks real-path evidence or a plausible shortcut is not detectable.
- **Critical:** a completion claim is contradicted, the acceptance oracle was compromised, or downstream decisions rely on invalid evidence.

The rating applies only to the stated audit scope.

## 7. Act on findings

- Retract, invalidate, or reopen an original work item when its stated acceptance was never met. Do not launder it into a new follow-up.
- Create separate work only for genuinely new scope.
- Repair or strengthen a weak oracle before relying on more output that it cannot judge.
- Treat changes to protected acceptance criteria as separately authorized decisions.
- Recheck dependent claims when upstream evidence fails.

Do not mutate project state unless the audit request authorizes it. Otherwise report the required dispositions precisely.

## Report

Lead with unsupported or invalidated claims:

```text
Audit scope: <items and evidence inspected>
Overall Potemkin risk: Low | Medium | High | Critical
Verification authority: <protected mechanism or separately authorized actor>

Unsupported or invalidated claims:
- <failure mode> — <claim> — <evidence or missing evidence> — <consequence>

Acceptance-oracle weaknesses:
- <failure mode> — <missing or weak sensor>

Verifier boundary:
- <implementer access, protected elements, recomputed evidence, and disqualifying events>

Supported claims:
- <claim> — <evidence pointer>

Coverage limits:
- <not inspected or inaccessible>

Named uncertainty:
- <specific likely failure and its observable consequence>
- <confidence or range, only when defensible>
- <check that would materially change the assessment>

Required actions:
- <smallest evidence-producing or corrective actions>
```

Reject generic caveats, but do not force a number without evidence or a reference class; false precision is another unsupported claim.

For independent use without an established workflow, retain three lightweight rules between audits: record deviations when they happen, prevent silent changes to acceptance criteria, and never claim more than the strongest check supports.
