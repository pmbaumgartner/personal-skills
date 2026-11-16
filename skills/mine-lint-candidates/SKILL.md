---
name: mine-lint-candidates
description: Mine past code reviews in agent sessions from every harness (Claude Code, Codex, Pi) through the agentsview CLI for findings that keep recurring across projects, then turn the mechanical ones into linter config changes or tested ast-grep rules. Use when asked to find lint or ast-grep candidates from agent history, past reviews, or recurring review findings. Not for reviewing code directly.
disable-model-invocation: true
---

# Mine Lint Candidates

Reviews keep finding the same problems in different projects, whether a review skill, a review bot, or an ad-hoc "review this" produced them. Find the ones a syntax tree can catch, prove each rule against the repositories the findings came from, and land the survivors as cheaply as possible.

A rule earns its place only if the finding **recurs in several projects** and the rule's hits in real code are **mostly true**. Most review findings fail the first test because they are structural judgment. Report those as out of scope; don't force rules for them. Workflow preferences that users keep repeating to agents ("don't add tests for scripts") aren't lint material either; they belong in an agent context file.

## Inputs

- **Review markers (optional):** text that marks a review in a transcript. The script defaults to review vocabulary (`Findings`, `Severity`, `code review`), which catches reviews from any source. Add the name of a review command, skill, or bot when the user wants a particular kind of review, or when the defaults miss one.
- **Excluded projects:** wherever review prompts and instructions are written, such as a repository of agent skills. Those sessions quote review instructions and drown out real findings.
- **Rule pack:** this repository's `lints/` (resolve the skill's real path; the pack is `../../lints` from the skill directory). Read `lints/README.md` first: it describes the rule families found so far, the rule file format, ignores, test layout, and how to add a rule. The families are not exhaustive; mining may turn up a new kind of recurring finding that deserves rules of its own.
- **Scratch directory:** keep extracts, draft rules, and scan output there, not in the pack.

## Workflow

### 1. Know what exists

- List the pack's rules and read their `note`s, so you don't propose duplicates.
- For every candidate, check whether a standard linter already has the rule (ruff, clippy, Biome/ESLint, basedpyright, go vet). Search the installed linter's catalog first, then read the relevant explanations. For Python, save `uvx ruff rule --all --output-format json` once in scratch. Compare the exact behavior: `PLR0913` counts keyword-only arguments too, while `PLR0917` counts positional arguments. If a standard rule covers the finding, the outcome is "enable that rule", not a custom rule.

### 2. Extract the findings

```sh
uv run --script <skill-dir>/scripts/extract_findings.py [marker ...] \
  --exclude-project skills --out <scratch>/items.jsonl
```

It searches every harness, includes subagent sessions (where parallel reviewers write their findings), and keeps long assistant messages that look like review output after each session's first mention of a marker. It prints each project's item count and checkout directory.

The output is one deduplicated JSON record per line: `project`, `text`, `session_id`, `ordinal`, and `truncated`. Provenance identifies the retained occurrence. The extractor keeps at most 12 qualifying messages per session and shortens each excerpt to 700 characters; `truncated` marks shortened excerpts, not skipped messages. This is a discovery aid, not exhaustive review coverage.

Read a finding's original message when the excerpt is truncated or its meaning is uncertain:

```sh
agentsview session messages <session_id> --around <ordinal> --before 0 --after 0 --json
```

The default markers also pick up plans, audit tables, and summaries that use the same vocabulary. Triage drops them; they aren't findings.

### 3. Triage by recurrence

1. Sort findings into **structural** (duplicated helpers, god files, wrong layer, lifecycle and ownership, missing abstractions) and **code-shaped** (a type, signature, call, or expression you could point to). Only code-shaped findings are rule candidates, whether or not they fit one of the pack's existing families. Structural ones belong to other tools (jscpd, import-linter, dependency-cruiser) or stay judgment.
2. Group code-shaped findings by the shape of the code, not the wording: `kind: String` in Rust, `status: str` in Python, and `status: string` in TypeScript are one finding in three languages.
3. Count **projects**, not mentions. One project reviewed five times is one project; renamed checkouts aren't independent projects. Aim for three or more. For language-focused work, report target-language recurrence separately from analogous findings in other languages.

Before scanning source, build a small scratch evidence table: candidate shape, actual project and language, finding excerpt, source location, and transcript `session_id`/`ordinal`. A session's project label can differ from the repository discussed; check the finding itself. Keep historical review recurrence separate from current scan hits: finding a pattern in three checkouts does not prove that three reviews reported it.

Keyword regexes over `items.jsonl` are only for orientation: they miscount (case-insensitive `Any` matches every "any") and miss findings described in prose. Read the items for every theme you consider.

For a large corpus, use bounded thematic passes (for example, Python IO/error handling versus signatures/types/tests), with non-overlapping scopes if delegating. Each pass should return evidence-backed candidates before anyone scans repositories. After a bounded pass, stop expanding a theme when it is already covered, below the recurrence threshold, or requires semantic judgment. A negative result is useful; don't turn a weak lead into open-ended mining.

### 4. Prove each candidate on real code

Use the checkout directories the script printed. This applies to existing linter rules too: run the linter with only that rule enabled.

1. Draft a custom rule in the scratch directory with an `sgconfig.yml` that points `utilDirs` at the pack's `utils/`. Inspect the syntax tree with `ast-grep run -l <lang> -p '<concrete code>' --debug-query=cst`. Before trusting a real-code scan, run positive snippets for each intended variant and negative snippets for exemptions. For example, a matcher for `bool(config.get(...))` needs positive cases both with and without a default argument. A zero-hit scan means nothing until these controls pass and the scan's scope and diagnostics are checked.
2. Scan the source and test paths of every project the finding came from, plus a few that never had it.
3. Read the hits. Check a sample of each repository's hits in context, not just the matched line.
4. Tune until most hits are real: narrow name lists, restrict to fields or signatures, exempt serializers and generated files, constrain metavariables (`constraints: { K: { kind: string_literal } }`).
5. Decide:
   - **Keep** a rule whose hits are mostly true.
   - **Drop** a rule with no hits anywhere: the code has moved on, and a rule nothing triggers isn't worth maintaining.
   - **Drop** a rule whose hits are mostly deliberate idioms (parse-or-null `catch` blocks, for example).

### 5. Land the survivors

- **Existing linter rule:** add it to the "Standard linter settings" table in `lints/README.md`, and recommend the config change for each project where it held up (for example, `extend-select = ["UP045"]` in `pyproject.toml`). Don't edit those repositories unless the user asks.
- **Custom rule:** follow `lints/README.md`'s "Adding a rule", which covers the rule file, its note, its tests, and the test command. The rule file is the only documentation of the rule, so its `message` and `note` must make sense to someone who never saw the review it came from. If it starts a new family, add that family to the README's list.

## Report

- **What was searched:** the markers, time window, session and project counts, exclusions, reused prior work, and coverage limits (including truncated extracts and missing checkouts).
- **Linter rules to enable:** each with the recurring finding, the projects, and its hit quality. Label opportunities found only in current code separately from recurring review findings.
- **Custom rules added:** each with its family (or the new family it starts), the recurring finding behind it, historical project counts (target language versus other languages), and current scan results and hit quality.
- **Candidates rejected:** each with the reason (structural, no hits left, mostly idioms, one project).
- **Verification:** the `ast-grep test` result. State that nothing is committed unless the user asked for a commit.

Project names belong in this report to the user, not in the rule pack.
