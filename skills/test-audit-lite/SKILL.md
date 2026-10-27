---
name: test-audit-lite
description: "Quickly audit existing tests for ones that cost more than they protect: tests that can't fail, pin implementation details, are overly precise, are disabled, keep legacy behavior alive, check repository artifacts instead of behavior, test language and third-party guarantees, replace the project's own code with test-side stand-ins, or script boundary fakes into impossible scenes, and propose fixtures or helpers for repetition among the tests worth keeping. Covers test bodies, doubles, and fixtures. Use for a fast low-value-test review of a diff, file, or directory. Not for finding missing coverage or tests that encode wrong behavior."
disable-model-invocation: true
---

# Test Audit Lite

Read the tests directly and find the ones that fail for the wrong reasons or protect nothing. Every test must answer one question: **what plausible bug in currently supported behavior would this catch?** A test with no concrete answer should be rewritten or deleted. Its existence, age, or passing status is not evidence that it's needed.

This is fast because it reads the tests first, and that is also its limit: the tests anchor the review. It does not find missing coverage, and it does not catch a test that confidently asserts the wrong behavior.

## Supported behavior

**Behavior** is an effect observable from outside the unit: return values, errors, output, side effects, and persisted or exchanged data. Internal steps, call order, and intermediate state are not behavior.

Behavior is **supported** when stated intent backs it: the user's requirements, documentation in scope (README, docs, doctests, examples), or the interface's own declarations (names, types, docstrings, help text, schemas). Neither the implementation nor the test itself establishes support. Git history, changelogs, and PR descriptions can establish that behavior was removed or deprecated.

Exact output is behavior when the format is the contract: CLI output that scripts parse, serialized schemas, wire formats, error codes. Fakes of coarse system boundaries (network, clock, filesystem, physics, external services) are fine when they compute results from arranged state the way the real boundary does. Stand-ins for the project's own code usually are not, and they don't always look like mocks: a same-named class compiled in place of the source has no `mock` or `patch` anywhere.

A boundary mock permits a test; it doesn't make the test valuable. Test the decision, not each forwarding layer. An assertion that an argument the test supplied reaches a dependency unchanged is Pins implementation, even when the dependency is external, unless that mapping is itself a stated contract. Keep boundary assertions that verify a choice or transformation the unit makes, or a required protocol detail. Passing `at_least_once=True` to a wrapper and asserting the pipeline client receives `True` tests forwarding; building a streaming intake and asserting its sink selects at-least-once delivery, while batch keeps exactly-once, tests policy.

## Labels

| Label | What the test does | Default action |
| --- | --- | --- |
| Vacuous | Can't fail when the behavior breaks: no meaningful assertion, asserts only type or non-None, asserts what a mock was configured to return, patches the unit under test, recomputes the expected value with the code's own logic, swallows failures (`raises(Exception)`, broad `except`), or arranges a setup element its outcome supposedly hinges on (an obstacle, a crowd, a flag) but still passes without it | Delete, or rewrite if it's the only test of supported behavior |
| Pins implementation | Asserts internal calls, call order, private helpers, mock call counts or arguments on internal collaborators, or intermediate state, restates source constants, defaults, or tables, or checks only that an argument the test supplied passes through to a dependency | Rewrite against the behavior, or delete |
| Faked own code | Replaces project code with a test-side stand-in: a same-named class compiled in place of the source, or a patch or module mock of a project module, where the real code could run with the existing boundary fakes | Use the real code; keep a stand-in only for code that pulls in a heavy dependency the tests can't build, with only the members the tests need |
| Scripted boundary | A boundary fake returns per-test canned results instead of computing them from arranged state (a query fake that returns "hit" whatever the geometry, a clock that jumps on request mid-call), so the test can assert outcomes no real input produces | Arrange real inputs to a shared fake that computes results the way the real boundary does; script only failures the real boundary can't be made to produce |
| Overly precise | Asserts more than is specified: exact human-readable messages, full snapshots or reprs, unspecified ordering, incidental formatting or whitespace, exact floats or timestamps | Loosen to the specified property |
| Legacy | Protects removed, deprecated, or compatibility behavior: aliases, re-exports, old input forms, shims, migrations. Also: asserts that removed behavior stays absent (the old flag now errors, the old route returns 404), when nothing outside the tests states that rejection is the contract. | Delete; if the behavior still exists, remove it along with its tests |
| Artifact check | Asserts that files, names, or layout exist or stay gone, or inspects source, docs, or generated text instead of running behavior | Delete |
| Not ours | Tests a language guarantee or behavior owned entirely by a third-party package | Delete |
| Redundant | A retained test or type-system guarantee catches the same bug, including parametrized cases in the same equivalence class | Delete, citing the retained coverage; trim parameter lists to one case per branch or boundary |
| Disabled | Permanently skipped, xfailed, commented out, or skipped under a condition that never holds in CI | Delete; fix only if it covers supported behavior nothing else does |
| Unspecified behavior | Asserts edge-case behavior, often rejection of input, that nothing outside the tests states or relies on, and that crosses no security or safety boundary | Delete |
| Duplicated setup | Surviving tests repeat the same data construction, boundary fakes, setup and teardown, or assertion sequence, or several test files define the same fake or stand-in, especially with differing behavior | Extract a fixture, builder, helper, or one shared double, reusing existing ones first |
| Unclear intent | The evidence conflicts on whether the behavior is supported | Ask, stating your best guess |

Prefer the cheapest action that keeps supported behavior covered: delete over rewrite when retained tests cover the behavior, loosen over rewrite, and fold a rewritten assertion into an existing test instead of adding one. Use Unclear intent only when the evidence conflicts. Missing intent is not unclear intent: if nothing outside the tests states or relies on a behavior, it is unsupported.

Propose consolidation only for tests that survive pruning, and only when it removes real repetition: three or more uses, or a setup long enough to hide what the test checks. Keep the inputs and expected values that explain a test visible in the test. Don't share mutable state between tests, and don't build helpers around mocks of internal collaborators; those are Pins implementation or Faked own code. Report repetition in other files only when a search confirms it.

Overlapping tests are not redundant when they catch different bugs. A test is not low-value just because it is a unit test, is short, or uses boundary mocks, and not valuable just because its mock stands in for something external. For mixed tests, label the assertions, not the whole test: "Keep the return-value assertions; drop the `_normalize` call check."

## Workflow

1. **Scope.** Use the tests the user names. If none, use tests added or changed on the current branch against its base; if there are none, ask.
2. **Read.** For each test, read its setup and assertions, the doubles and fixtures it uses, the code it exercises, and the stated intent for that code. Then check whichever of these apply:

   - **Doubles.** Search the test directories for definitions that shadow source: classes, functions, or modules with the same name as project code, patches or module mocks targeting project modules (`mock.patch("pkg.`, `jest.mock('./`), and the same fake defined in more than one file. For each stand-in, read the real code's dependencies to judge whether it could run instead. For each boundary fake, check whether it computes results from arranged state or returns what each test asks for.
   - **Call-argument assertions.** Ask whether the unit chooses or transforms the value, or the test supplies the answer and watches it pass through. That a dropped argument would fail the test doesn't justify a forwarding test.
   - **Scenario tests.** When the outcome hinges on one setup element, remove that element in a scratch copy and confirm the test fails.
   - **Possible Legacy or Artifact checks.** Check whether the behavior still exists and whether docs or history mark it removed or deprecated.
   - **Repetition.** Note repeated setup, data construction, fakes, and assertion sequences as you go, and check for existing fixtures and helpers that already cover them.

   If the scope is too large to read in full, run the doubles search, then search all of it for high-signal patterns (mock call assertions and call counts, snapshots, skip and xfail markers, source inspection and file-existence checks, legacy, compat, alias, or deprecated names, long exact message strings), read every hit, then sample the rest and say how.
3. **Recommend.** In chat, list only tests with a problem as numbered recommendations, most valuable first. Each one is short enough to accept or reject at a glance:

   ```
   1. tests/test_parser.py:42 test_parse_calls_tokenizer (Pins implementation)
      Delete. Asserts `_tokenize` is called once; test_parse_nested already covers the parsed result.
   2. tests/test_cli.py:88 test_old_flag_alias (Legacy)
      Delete with the `--out` alias in cli.py:31. Docs list only `--output`.
   ```

   Give `path:line`, the test, the label, the concrete change, and why: the bug it fails to catch, or what it would break on instead. Name anything the change would leave unused: fixtures, helpers, test data, snapshot files, and production seams that exist only for those tests, such as exported private functions or test-only parameters and hooks. Mention a coverage gap only when a recommendation would leave supported behavior untested. End with one line naming what was reviewed or sampled and how many tests were fine, then ask which to apply. The user can accept, reject, or change each one by number.
4. **Apply.** Apply only what the user accepts, as they changed it. Before deleting a test as Redundant, point to the retained assertion that catches the same bug; if that's doubtful, break the behavior in a scratch copy and confirm the retained test fails. When removing legacy behavior, delete its implementation, types, exports, and docs along with the tests. Delete the fixtures, helpers, test data, snapshots, and test-only seams named in accepted recommendations. Run the affected tests and appropriate checks after editing.

## Rules

- Don't modify tests or code before step 4.
- Don't write a report file.
- Don't spawn subagents or run the full suite unless the user expands the scope.
- Don't hunt for missing coverage or general defects; report a defect only if you happen to confirm one.
