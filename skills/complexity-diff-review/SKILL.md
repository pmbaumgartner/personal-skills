---
name: complexity-diff-review
description: Quickly assess how a commit, pull request, or branch changed code complexity, using per-function lizard metrics before and after the change and focused source inspection. Use for fast complexity reviews of a diff. Do not use for repository-wide audits or for defect and security hunts.
disable-model-invocation: true
---

# Complexity Diff Review

Review where the change made code harder to read, not the whole repository.
Lizard measures every changed function before and after; the source decides
whether the growth is a burden. Metrics select attention. They are never
findings by themselves.

Do not run tests, edit code, or spawn subagents unless the user expands the
task.

## 1. Measure

```bash
uv run --script <skill-dir>/scripts/complexity_delta.py --repo <repo> <base> [<head>]
```

- Single commit: `<sha>^ <sha>`.
- Branch or pull request: `main <branch>`. The script diffs from the merge
  base, like `git diff main...branch`.
- `<head>` defaults to `HEAD`. Uncommitted changes are not included.
- Lists are capped at 25 lines; pass `--all` when a capped section matters.

The output reports, per changed function:

- **Grown:** functions over CCN 10 that gained 3 or more, or over cognitive 15
  that gained 5 or more, including new functions. Sorted by cognitive growth.
- **Tiny new helpers:** new named top-level functions of 3 NLOC or fewer,
  outside tests.
- **Reduced or removed:** strengths and context.
- **Moved across files:** functions matched by a name unique on both sides,
  ignoring case and underscores so ports between naming styles pair up.
- **Files:** function counts and total CCN before and after.

Reading the metrics:

- CCN counts decisions, with a switch counted once. Cognitive complexity adds
  weight for nesting and is closer to what a reader must track. High CCN with
  near-zero cognitive is usually flat code, such as Rust `?` chains or guard
  lists, and rarely a burden.
- Lizard sees functions only. Module-level code, class structure, type
  definitions, and configuration are not measured. A file whose function count
  jumps while its logic stays small may have gained layers; check the patch.
- A move between languages compares different counting rules. Treat its delta
  as context.
- Lizard names some functions `(anonymous)`, such as arrow-function
  components; use the line to find them.

## 2. Choose candidates

Pick at most five, production code before tests:

1. Grown functions, largest growth first.
2. Clusters of tiny new helpers in one file or one concern.
3. A file whose function count grew sharply with little logic.

Read the patch for each candidate with `git diff <base>...<head> -- <path>`,
then the surrounding source at the head.

## 3. Judge in source

Judge by what a reader must hold in mind: the branches they track plus the
definitions they must jump to. Splitting trades the first for the second, so a
split helps only when callers can be understood from the helper's name without
opening it.

For a grown function, ask:

1. Which changed lines added the branches, and which requirement do they serve?
2. Is the same condition checked in several places, or pushed onto callers as
   flags, mode parameters, or return codes?
3. What is the smallest fix? Prefer, in order:
   1. delete what the requirement does not need: checks for states that cannot
      occur, options nobody asked for, special cases a general path covers;
   2. flatten nesting with early returns or `continue`;
   3. merge duplicated conditions into one place or a lookup table;
   4. extract only a helper that hides a decision, has two or more callers, or
      names a step well enough that callers can skip its body.

For a tiny helper, count its call sites. Use codebase-memory if the repository
is already indexed, otherwise grep, and say which; grep is unreliable for
common names and dynamic dispatch. A helper with one caller and a body barely
longer than the call should be inlined. Keep a helper that hides a decision or
names a step callers can skip.

Reject candidates whose growth is generated, a relocation, or added test cases.
In tests, look only for duplicated setup or branching inside a test. Never
recommend an extraction that merely moves complexity.

## Report

1. **Scope:** base and head SHAs, files measured, excluded, and unmeasured, and
   the overall signal, including notable reductions.
2. **Findings:** zero to three, by priority. For each: `path:line`, the changed
   lines responsible, metrics before → after, what a reader now pays, the
   smallest fix, and confidence.
3. **Accepted growth:** one line per other inspected candidate:
   `kept: <the requirement the new branches serve>`. "Growth is warranted"
   without naming the requirement is not an answer.
4. **Limits:** what lizard could not see that matters here, capped sections
   not expanded, and how call sites were counted.

If no concern survives source inspection, say so.
