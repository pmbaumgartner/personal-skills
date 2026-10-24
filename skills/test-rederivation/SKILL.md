---
name: test-rederivation
description: "Re-derive what a codebase's tests should be from what the code observably does and what justifies it, without seeing the existing tests, then classify the existing tests against that spec. Use when asked to re-derive tests, run an independent test-suite audit or test-blind review, or check whether tests are being treated as ground truth."
disable-model-invocation: true
---

# Test Re-derivation

Agents tend to treat tests they wrote as ground truth, even when those tests encode a narrow or wrong implementation, duplicate other coverage, or have gone stale. Hide the tests and start from what the system actually does, not from the design its code or tests suggest: the purpose of a system is what it does. Keep the behavior that stated intent justifies as the test spec, note what depends on it, and only then compare that spec with the existing suite.

## Deriving the spec

**Behavior** is an effect observable from outside the unit: return values, errors, output, side effects, and persisted or exchanged data. Internal steps, call order, and intermediate state are not behavior.

A behavior is **justified** when it has stated intent: it is stated in the user's requirements, documentation in scope (README, docs, doctests, runnable examples), or the interface's own declarations (names, types, docstrings, help text, schemas).

**Callers and data** that rely on a behavior, including data already persisted or exchanged across the system boundary, are evidence of change impact, not necessarily correctness. Record those dependencies. When a depended-on behavior lacks clear intent, make it an open question: show what depends on it and ask whether to preserve it. A caller and callee can share the same mistake; existing data does not by itself establish a supported contract.

The implementation alone never justifies a behavior. Issues, PR descriptions, and Git history are not blind-phase sources: they are outside the copy and often describe tests.

Prefer observing to reading. Run a small probe when a behavior is uncertain or a defect depends on it, and record each behavior as observed or read.

Reconcile what the system does with what is justified:

| The system | Justified? | Result |
| --- | --- | --- |
| Does it | Yes | Spec item |
| Doesn't do it | Yes | Defect, plus a spec item for its regression test |
| Does it | No | Open question; harmful behavior such as data loss or security exposure is a defect instead |

When stated intent contradicts what callers and data rely on, record an open question rather than picking a side. Open questions produce neither tests nor defects until the user answers them.

## Workflow

1. **Scope and exposure.** Record the scope and the source checkout status. Note whether this session has already read, written, or run tests in scope.
2. **Prepare the copy.** Create a temporary copy outside the source checkout, excluding `.git`, dependencies, and build output. Identify tests by path and file name only. Remove test files, test directories, fixtures, snapshots, and standalone test configuration without reading them. Keep doctests and examples. Remove separable inline tests; if that isn't safe, leave the file out and disclose the gap. Leave test settings embedded in non-test files (for example `[tool.pytest]` in `pyproject.toml` or Makefile test targets) in place, and disclose them in the removal summary. Record a non-test file inventory and a short removal summary.
3. **Blind phase.** Derive the spec, defects, and open questions.
   - **Who runs it:** if step 1 found test exposure, a fresh-context subagent runs this phase. It gets only the scope, the path to the copy, and the user's stated requirements quoted verbatim, never paraphrased by an exposed agent. Without exposure, run it directly.
   - **What it reads:** only the copy. No source checkout, Git history, test output, coverage, or code indexes (the codebase-memory graph indexes test files).
   - **Defects:** each has a severity, `path:line`, impact, and the smallest reasonable fix. Merge defects with the same root cause, and drop any that callers, guards, or dependency guarantees invalidate. A comprehensive code audit is outside this workflow's scope.
   - **Test spec:** one entry per justified behavior worth testing, with:
     - a short, stable ID;
     - the behavior;
     - its justification and exact reference, plus any callers and data that rely on it;
     - its status: met, or unmet with its defect; observed or read;
     - the concrete bug the test would catch;
     - a suggested test level (unit, integration, end-to-end).

     Leave out a behavior if you can't name a concrete bug its test would catch.
   - **Probes:** small, independently written programs run against non-test code in the temporary copy. Keep a probe that demonstrates a spec item as that item's draft test. Test infrastructure was removed from the copy, so draft tests may be self-contained sketches rather than suite-ready code. Never present an unexecuted probe as observed behavior.
4. **Freeze.** Save the blind-phase output (spec, defects, and open questions) and any draft tests outside the temporary copy and the source checkout before anyone opens the existing tests. Don't edit the frozen output afterward; anything learned during comparison, including supported corrections or additions to the spec, goes in the report.
5. **Compare.** Read the existing tests in the source checkout and recommend an action for each test, using these labels where useful:

   | Label | Meaning | Default action |
   | --- | --- | --- |
   | Keep | Its assertions would catch the concrete bug identified by a spec item | Retain; note any remaining coverage gap |
   | Redundant | Identified retained coverage or a type-system guarantee catches the same concrete bug | Delete, with a reference to that coverage or guarantee |
   | Pins implementation | Asserts something that isn't behavior, such as internal calls, call order, or intermediate state | Rewrite against its spec item, or delete |
   | Contradicts spec | Test and spec item disagree | User decides which side is wrong |
   | Stale | Evidence establishes that the behavior is no longer intended | Delete |
   | Needs investigation | Asserts behavior missing from the blind spec or recorded as an open question, or intent remains unclear | Preserve while investigating; record supported spec corrections in the report |

   The label classifies the test; the action defaults from it and may be qualified. Assess the setup and assertions, not just whether a test exercises the named behavior. Overlapping tests are not redundant when they catch different bugs. Record partial coverage and weak assertions explicitly: matching a spec item does not by itself close its coverage gap. A test may map to multiple spec items. For mixed assertions, give a primary action and qualify which assertions to keep, change, or remove rather than forcing the whole test into one label. For example: "Keep the behavioral assertions; remove the assertion on the private helper call."

   Spec items with no effective coverage become **tests to add**, using any draft test from the blind phase. For partial coverage, propose a focused improvement to an existing test where practical.

   For large scopes, split comparison by subsystem, the same way as the blind phase.
6. **Report.** Write one Markdown report next to the frozen output, give the user its path, and keep the chat reply to a short summary. In order:
   1. **Decisions:** every item that needs the user: open questions, `Contradicts spec` tests, `Needs investigation` tests the evidence can't settle, defects whose fix or regression test needs a choice, and approval of the remaining recommended test changes. Settle what evidence can settle first; uncertainty alone is not a decision. Give each entry an ID and make it stand on its own: what the code does (observed or read, `path:line`), stated intent and the callers and data that rely on it, the tests and spec items involved, the options and what each changes, and a pre-filled `**Decision:**` with your recommendation, or `undecided`. Other sections refer to decisions by ID instead of restating them.
   2. defects;
   3. the comparison table (test, label, recommended action, spec item IDs, reason), plus supported spec corrections. List every test needing changes or investigation individually, including mixed-assertion tests; summarize tests kept unchanged per file with their counts and spec item IDs;
   4. tests to add or improve;
   5. coverage: what was reviewed, left out, and executed, including any sampling;
   6. the frozen blind-phase output, copied verbatim from its file, and the path to any draft tests.
7. **Apply authorized changes.** Unless the user already gave explicit authorization, wait for their reply. Treat it as confirming each decision as the report then reads; `undecided` changes nothing. Before deleting a test as redundant, inject its spec item's concrete bug into a scratch copy of the source checkout and confirm the retained coverage fails; if it doesn't, relabel instead of deleting. Adapt draft tests to the existing suite's conventions, fixtures, and layout rather than pasting them in. Run focused tests and appropriate checks after the edits.
8. **Clean up.** Delete the temporary copy after any subagents finish. On failure or cancellation, stop subagents before deleting their workspace.

## Isolation and delegation

- If there was test exposure, the blind phase runs in a fresh subagent. Otherwise subagents are optional.
- For large scopes, subagents own non-overlapping subsystems; they may read non-test callers across subsystem boundaries.
- Point subagents and their tools explicitly at the temporary copy. Don't assume a copied repository changes their working directory.
- Pass subagents only the task framing and evidence from non-test code: no test names, nothing derived from the tests, no search results from the source checkout.
- Ask subagents for spec items, defects, open questions, reviewed files, and gaps, not exploration transcripts.

## Rules

- Don't run or inspect existing tests before the freeze.
- Install dependencies or build only when a specific probe needs it, within the user's execution permissions.
- Don't modify the source checkout before step 7.
