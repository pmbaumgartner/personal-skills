---
name: test-audit-lite
description: "Quickly audit existing tests for ones that cost more than they protect: tests that pin implementation details, are overly precise, keep legacy behavior alive, guard against removed code returning, or test language and third-party guarantees. Use for a fast low-value-test review of a diff, file, or directory. Not for finding missing coverage or tests that encode wrong behavior."
disable-model-invocation: true
---

# Test Audit Lite

Read the tests directly and find the ones that fail for the wrong reasons or protect nothing. Every test must answer one question: **what plausible bug in currently supported behavior would this catch?** A test with no concrete answer is a candidate for rewriting or deletion.

This is fast because it reads the tests first, and that is also its limit: the tests anchor the review. It does not find missing coverage, and it does not catch a test that confidently asserts the wrong behavior.

## Supported behavior

**Behavior** is an effect observable from outside the unit: return values, errors, output, side effects, and persisted or exchanged data. Internal steps, call order, and intermediate state are not behavior.

Behavior is **supported** when stated intent backs it: the user's requirements, documentation in scope (README, docs, doctests, examples), or the interface's own declarations (names, types, docstrings, help text, schemas). Neither the implementation nor the test itself establishes support. Git history, changelogs, and PR descriptions can establish that behavior was removed or deprecated.

Exact output is behavior when the format is the contract: CLI output that scripts parse, serialized schemas, wire formats, error codes. Mocks of coarse system boundaries (network, clock, filesystem, external services) are fine; mocks of the unit's own collaborators usually are not.

## Labels

| Label | What the test does | Default action |
| --- | --- | --- |
| Pins implementation | Asserts internal calls, call order, private helpers, mock call counts or arguments on internal collaborators, or intermediate state | Rewrite against the behavior, or delete |
| Overly precise | Asserts more than is specified: exact human-readable messages, full snapshots or reprs, unspecified ordering, incidental formatting or whitespace, exact floats or timestamps | Loosen to the specified property |
| Legacy | Protects removed, deprecated, or compatibility behavior: aliases, re-exports, old input forms, shims, migrations | Delete; if the behavior still exists, remove it along with its tests |
| Absence guard | Asserts a deleted file, name, feature, or layout stays gone, or inspects source text | Delete |
| Not ours | Tests a language guarantee or behavior owned entirely by a third-party package | Delete |
| Redundant | A retained test or type-system guarantee catches the same bug | Delete, citing the retained coverage |
| Unspecified rejection | Rejects input the spec doesn't mention and that crosses no security or safety boundary | Delete |
| Unclear intent | The evidence can't settle whether the behavior is supported | Ask, stating your best guess |

Overlapping tests are not redundant when they catch different bugs. A test is not low-value just because it is a unit test, is short, or uses boundary mocks. For mixed tests, label the assertions, not the whole test: "Keep the return-value assertions; drop the `_normalize` call check."

## Workflow

1. **Scope.** Use the tests the user names. If none, use tests added or changed on the current branch against its base; if there are none, ask. Large scopes may be sampled; say how.
2. **Read.** For each test, read its setup and assertions, the code it exercises, and the stated intent for that code. When a test looks like Legacy or an Absence guard, check whether the behavior still exists and whether docs or history mark it removed or deprecated.
3. **Recommend.** In chat, list only tests with a problem as numbered recommendations, most valuable first. Each one is short enough to accept or reject at a glance:

   ```
   1. tests/test_parser.py:42 test_parse_calls_tokenizer (Pins implementation)
      Delete. Asserts `_tokenize` is called once; test_parse_nested already covers the parsed result.
   2. tests/test_cli.py:88 test_old_flag_alias (Legacy)
      Delete with the `--out` alias in cli.py:31. Docs list only `--output`.
   ```

   Give `path:line`, the test, the label, the concrete change, and why: the bug it fails to catch, or what it would break on instead. Mention a coverage gap only when a recommendation would leave supported behavior untested. End with one line naming what was reviewed or sampled and how many tests were fine, then ask which to apply. The user can accept, reject, or change each one by number.
4. **Apply.** Apply only what the user accepts, as they changed it. Before deleting a test as Redundant, point to the retained assertion that catches the same bug; if that's doubtful, break the behavior in a scratch copy and confirm the retained test fails. When removing legacy behavior, delete its implementation, types, exports, and docs along with the tests. Run the affected tests and appropriate checks after editing.

## Rules

- Don't modify tests or code before step 4.
- Don't write a report file.
- Don't spawn subagents or run the full suite unless the user expands the scope.
- Don't hunt for missing coverage or general defects; report a defect only if you happen to confirm one.
