# Custom lint rules

These are ast-grep rules for problems that code reviews keep finding and that standard linters (ruff, clippy, Biome/ESLint, go vet) don't cover. So far they fall into three families:

- **API design:** public signatures and names that mislead callers, such as positional booleans, durations without units, and errors returned as strings.
- **Untyped data:** kinds stored as strings and records passed as untyped JSON maps.
- **Test value:** Python tests that can't fail, pin implementation details, or protect behavior that is no longer supported.

The families aren't a closed list. New recurring findings may not fit any of them and start a family of their own.

Each rule is one file in `rules/<language>/` (Python test rules are in `rules/python-tests/`). The file is the documentation: `message` says what was found, `note` says how to fix it, the failure it prevents, and when a hit is fine, and `files`/`ignores` say which paths it scans. A hit is a lead, not a verdict, especially for `info` rules.

## Running

Requires [ast-grep](https://ast-grep.github.io/) (`brew install ast-grep`).

From any repository:

```sh
ast-grep scan -c <path-to>/lints/sgconfig.yml src/ tests/
```

- Scan source and test paths, not the repository root, so vendored and generated code stays out.
- ast-grep honors `.gitignore` and `.ignore`. Add vendored directories that are checked in to an `.ignore` file.
- Most source rules skip test, script, benchmark, example, e2e and vendor paths. `py-test-*` rules run only on test files (`tests/`, `test_*.py`, `*_test.py`, `conftest.py`).
- To run only the test-value rules: `--filter '^py-test-' tests/`.

Useful options:

| Option                 | Effect                                                  |
| ---------------------- | ------------------------------------------------------- |
| `--report-style short` | one line per finding                                    |
| `--json=compact`       | machine-readable output                                 |
| `--filter '^py-'`      | run only rules whose id matches                         |
| `--off=RULE_ID`        | turn a rule off for this run                            |
| `--error=RULE_ID`      | make a rule fail the run                                |
| `--update-all`         | apply fixes (only `py-main-discards-exit-code` has one) |

Severities are `error` (definite bugs), `warning` (design findings) and `info` (context-dependent). A scan exits non-zero only on errors.

## Repository-local rules

A repository can combine these rules with its own. Put this `sgconfig.yml` in the repository, with absolute paths to this directory:

```yaml
ruleDirs:
  - <path-to>/lints/rules
  - .ast-grep/rules
utilDirs:
  - <path-to>/lints/utils
languageGlobs:
  tsx: ["*.ts", "*.mts", "*.cts"]
```

Then `ast-grep scan src/` runs both sets. Rules that need project knowledge belong there. A glossary that bans synonyms for a canonical term is a few lines:

```yaml
id: glossary-document-not-page
language: python
severity: warning
message: "Say `document`, not `page` ($NAME)."
rule:
  kind: identifier
  pattern: $NAME
  regex: "(^|_)page(s)?(_|$)"
```

A test that patches the project's own code instead of running it needs the package name. For a package named `mypkg`:

```yaml
id: test-patches-own-module
language: python
severity: info
files: ["**/tests/**/*.py", "**/test_*.py"]
message: "Test replaces project code `$T`."
note: "Run the real code and fake only system boundaries, unless it pulls in a dependency tests can't build."
rule:
  any:
    - pattern: patch($T $$$)
    - pattern: mock.patch($T $$$)
    - pattern: mocker.patch($T $$$)
    - pattern: monkeypatch.setattr($T, $$$)
  has:
    field: arguments
    has: { nthChild: 1, kind: string, regex: '^["'']mypkg\.' }
```

## Standard linter settings

Recurring findings that a standard linter already catches once a setting is turned on. Add them to a repository's own config rather than writing an ast-grep rule.

| Linter | Setting                                                                                                                          | Flags                                                             | Typical failure                                                                                                       |
| ------ | -------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| clippy | `fn_params_excessive_bools = "warn"` under `[lints.clippy]` in `Cargo.toml`, plus `max-fn-params-bools = 1` in `clippy.toml`     | functions with two or more `bool` parameters                      | `git_apply(root, patch, true, false)`, where the call site doesn't say which flag is which                            |
| Ruff   | `extend-select = ["BLE001"]` under `[tool.ruff.lint]` in `pyproject.toml`                                                     | `except Exception` handlers that neither re-raise nor log the traceback | a handler that prints or logs a one-line warning and returns normally, so a failed job, check or write reports success |
| Ruff   | `extend-select = ["PLR0913"]` under `[tool.ruff.lint]`, plus `max-args = 10` under `[tool.ruff.lint.pylint]` in `pyproject.toml` | oversized function definitions, including keyword-only parameters | the same long options list copied across entry points, builders and validators, letting defaults and validation drift |

Treat `PLR0913` as a design-review lead, not a demand to wrap every signature in an options object. Ten is a starting threshold; exempt deliberate framework/estimator signatures and test-data builders narrowly. `PLR0917` counts only positional arguments, so it does not cover long keyword-only signatures.

## What a syntax tree can't catch

Many review findings need context these rules don't have: whether behavior is supported, whether another test already catches the same bug, whether a fake computes results or replays a script, and repetition across files (jscpd on `tests/` gets part of that). Structural findings such as duplicated helpers or code in the wrong layer belong to other tools (jscpd, import-linter, dependency-cruiser) or stay with human judgment.

## Notes

TypeScript rules use the tsx grammar for both `.ts` and `.tsx` files (see `sgconfig.yml`), because ast-grep rules are single-language. `utils/ts-exported-function.yml` defines "exported" once, for all TypeScript rules. `utils/py-test-function.yml` and `utils/py-assertion.yml` define a test function and an assertion for the test-value rules; a helper that asserts is only recognized when named `assert_*`, `check_*`, `expect_*` or `verify_*`.

## Adding a rule

1. Write `rules/<language>/<id>.yml`. Prefix the id with `py-`, `rs-`, `ts-` or `go-`, or `py-test-` in `rules/python-tests/`. Its `message` says what was found. Its `note` says how to fix the problem, describes the failure it prevents (`Typical failure: …`), and says when a hit is fine. Someone reading only the rule file should understand it.
2. Write `rule-tests/<language>/<id>-test.yml` with `valid` cases (including the exemptions you chose) and an `invalid` case for each pattern branch.
3. If the rule belongs to a new family, add it to the family list above.
4. Run the tests:

   ```sh
   ast-grep test -c lints/sgconfig.yml --skip-snapshot-tests
   ```

5. Scan a few real repositories and read the hits before committing. Tune exemptions until most hits are real.

Never name the repositories or projects a rule came from, or their identifiers, in notes, tests, or this README. Describe the failure generically (`kind: String` plus Options that depend on it), not where it was seen.

To see how ast-grep parses a construct, use `ast-grep run -l python -p '<code>' --debug-query=cst`.
