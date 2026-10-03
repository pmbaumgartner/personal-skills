---
name: test-blind-code-review
description: "Review code without seeing its tests. Use when asked for a test-blind, test-free, acceptance-independent, or independent code review: make a temporary copy, remove test files from it, assess the remaining code on its own merits, and report concrete defects and design problems."
---

# Test-Blind Code Review

Review the code without using tests as requirements or hints.

## Workflow

1. **Record scope and baseline.** Record the requested scope and source checkout status. Disclose any tests or test-derived evidence already seen in the conversation; a temporary copy cannot erase prior exposure.
2. **Prepare once.** Create a temporary copy outside the source checkout, excluding `.git`, dependencies, and build output. Identify tests from path and file names only. Remove test files, test directories, fixtures, snapshots, and test configuration without reading them. Remove separable inline tests; if unsafe, omit the file and disclose the gap. Produce a production-file inventory and a brief removal summary.
3. **Review production code.** Review only the test-free copy. Do not inspect the original checkout, Git history, existing test output, coverage, or external code indexes. Assess correctness, failure handling, security, API behavior, data flow, and maintainability. Track reviewed files and omissions as work proceeds.
4. **Consolidate and challenge findings.** Merge candidates with the same root cause before verification. Check whether callers, guards, documented restrictions, or dependency guarantees invalidate each claim. Drop unsupported claims. Use an independent reviewer or isolated reproduction where uncertainty or impact justifies the cost, not automatically for every finding.
5. **Report once.** Report actionable, source-supported findings with severity, `path:line`, impact, and the smallest reasonable fix. State what was reviewed, omitted, and executed, including sampling or incomplete coverage. If there are no material findings, say so.
6. **Clean up.** Delete the temporary copy after all reviewers finish. On failure or cancellation, stop reviewers before deleting their workspace. Freeze the production findings before any separately requested test inspection; do not automatically rewrite or compare tests.

## Isolation and delegation

- Review small scopes directly. For large scopes, optional reviewers should own non-overlapping subsystems rather than independently rereviewing the entire repository.
- Give reviewers fresh context where possible, containing only task framing and production evidence. Do not transfer test names, test-derived findings, or original-checkout search results.
- Point reviewers and their tools explicitly at the temporary copy. Do not assume that a copied repository changes their working directory or inherited context.
- Allow targeted production caller reads across subsystem boundaries. Request concise findings, supporting paths, reviewed files, gaps, and unresolved questions—not exploration transcripts.
- Give verifiers known paths and relevant source evidence. Ask them to resolve a specific uncertainty rather than rediscover the repository.

## Execution and efficiency

- Small, independently constructed reproductions against production code are permitted in the temporary environment. Do not run or inspect existing tests. Disclose what was executed and do not present an unexecuted reproduction as observed behavior.
- Do not install dependencies or build automatically. Do so only when a concrete reproduction needs them, within the user's execution permissions.
- Search to locate; use bounded reads to understand complete relevant implementations and trace important success and failure paths. Avoid giant search dumps.
- Prioritize risky paths first, but complete the requested scope before claiming full coverage. Reuse the prepared copy for follow-up verification during the review.
- Use brief progress updates when useful, then one consolidated report. Do not impose finding-count targets or mandatory multi-agent orchestration.

## Guidance

- Infer behavior from production code, public documentation, callers, and user requirements.
- Treat unclear behavior as ambiguity, not an invented requirement.
- Do not report missing tests.
- Do not compare findings with the removed tests unless separately asked.
- Do not modify the source checkout.
