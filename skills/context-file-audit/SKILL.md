---
name: context-file-audit
description: Audit, trim, improve, or generate CLAUDE.md, AGENTS.md, GEMINI.md, and similar agent context files using empirical research. Assess instruction content, context cost, and what belongs in skills rather than always-loaded guidance.
disable-model-invocation: true
---

# Context File Audit (CLAUDE.md / AGENTS.md)

Audit and fix repository context files based on the empirical literature (2025-2026).

## The evidence, synthesized

**Content is what matters; structure barely does.** A 1,650-session factorial study found that
file size (25-500 lines), instruction position, architecture (single file vs CLAUDE.md+AGENTS.md
vs nested per-directory files), and locally contradictory instructions produced **no detectable
effect on adherence**. Serialization format (Markdown vs YAML vs JSON) also matters far less
than what information is present and how it's organized across files. So: don't burn effort
reordering sections or debating formats — audit the content.

**Every line has a behavioral cost.** Agents follow context-file instructions (mentioned tools
used 30-250x more often). Generic guidelines, blanket rituals, and overviews drive more testing,
grepping, and reasoning tokens (+10-22%) without improving success. LLM-generated files *reduced*
success on average; developer-written ones helped only ~+4%.

**But a good minimal file can pay for itself.** A paired controlled study (124 PRs, GPT-5.2-Codex)
found AGENTS.md presence associated with **-28.6% median runtime and -16.6% output tokens** at
comparable task completion — savings concentrated in runs where the agent would otherwise thrash
exploring. The literature's apparent contradiction (+20% cost vs -29% runtime) resolves on
content: files stuffed with overviews and requirements add work; files that short-circuit
expensive discovery (exact commands, traps) remove it. The audit's job is to move a file from the
first category to the second.

**Adherence decays within a session, and no amount of prose fixes it.** Compliance drops as the
agent generates more code in one session. Emphasis ("IMPORTANT", "ALWAYS"), position, and
repetition showed no adherence effect — so critical constraints should be **mechanically
enforced** (hooks, CI, linters) rather than shouted in Markdown.

**Redundancy is the main failure mode.** When all other documentation was deleted, generated
context files went from harmful to helpful (+2.7%). Content the agent can discover in
README/config/code is pure cost.

Conclusion: a context file should contain **only minimal, non-discoverable, repository-specific
requirements** — and anything the agent must *never* violate belongs in enforcement tooling,
with the context file as a pointer.

## Workflow

### 1. Locate and inventory

Find all context files: `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `.cursorrules`,
`.github/copilot-instructions.md`, plus nested variants in subdirectories. Also inventory the
repo's other documentation (`README*`, `docs/`, `CONTRIBUTING*`), since redundancy with these is
a core audit criterion. Note repo size and whether docs are sparse — the sparse-docs case changes
recommendations (see rule R6).

### 2. Audit — classify every section/line

Go section by section (a section = content under one Markdown header) and tag each item with one
of the rules below. Produce an audit table: `section | verdict | rule | rationale`.

**KEEP — high-value, non-discoverable content** (this is what made human-written files win):
- **K1 Non-standard tooling**: exact build/test/lint commands when they deviate from ecosystem
  defaults (`uv run pytest`, custom `make` targets, repo-specific CLIs). Agents used these
  almost exclusively when mentioned. If the repo just uses plain `pytest`, it's discoverable —
  cut it.
- **K2 Environment traps**: setup steps that fail silently or non-obviously (required env vars,
  services that must run, "don't run the full suite, it takes 40 min — use `-k`").
- **K3 Hard constraints**: things the agent must never do (don't edit generated files in `gen/`,
  never bump versions, migrations only via tool X).
- **K4 Non-discoverable conventions**: policies not inferable from the code itself (commit/PR
  conventions the team enforces, which of two coexisting patterns is canonical).

**FIX or CUT — content the paper shows is costly or useless:**
- **R1 Codebase overviews / directory listings** (CUT): measured to not reduce time-to-relevant-file
  at all; agents discover structure themselves. Cut "Project structure" trees, per-directory
  descriptions, architecture prose. Exception: a single line for genuinely surprising layout.
- **R2 Redundant documentation** (CUT): anything already in README/docs/CONTRIBUTING or obvious
  from config files (`pyproject.toml` names the test runner; `package.json` lists scripts).
  Point to the doc instead of duplicating it, or say nothing.
- **R3 Generic best-practice exhortations** (CUT): "write clean code", "add tests for changes",
  "follow PEP 8", "handle errors gracefully". Agents already do this; extra instructions
  measurably inflate testing/exploration/reasoning without improving outcomes.
- **R4 Blanket expensive rituals** (FIX → scope or CUT): "always run the full test suite",
  "always lint the whole repo", "read all related files before editing". These are followed
  literally and drive the +20% cost. Rescope to targeted forms ("run only tests for touched
  modules: `pytest tests/<module>`") or delete.
- **R5 Discoverable trivia** (CUT): language, framework, dependency lists, file counts, "we use
  Python 3.11" when `pyproject.toml` says so.
- **R6 Sparse-docs exception**: if the repo has little/no README or docs, a context file *is*
  the documentation and modest setup/run content earns its keep (this is the one setting where
  generated files improved success by +2.7%). Prefer fixing the README, but don't strip a
  context file to nothing if it's the only doc.
- **R7 Stale or contradictory content** (FIX): verify commands actually work (run them if an
  execution environment is available); remove instructions contradicting current code/config.
- **R8 Length budget**: developer files in the Gloaguen study averaged ~640 words and still cost
  ~19% extra. Target well under that — a good file is often 10-30 lines. If the draft exceeds
  ~60 lines, re-audit; something discoverable or generic almost certainly crept in. (Note: the
  factorial study found length alone doesn't change *adherence* — the cost of length is wasted
  tokens and behavioral overhead, not disobedience.)
- **R9 Emphasis theater** (CUT/FIX): "IMPORTANT:", "ALWAYS", "NEVER FORGET", bold-caps repetition,
  and placing rules at top vs bottom showed no measurable adherence effect. Strip the emphasis;
  if a rule is genuinely critical, convert it to enforcement (R10) instead of volume.
- **R10 Enforce, don't exhort** (FIX): adherence decays within long sessions regardless of file
  content. For must-never-break rules (protected files, forbidden commands, formatting), recommend
  mechanical enforcement — Claude Code hooks, pre-commit, CI checks, lint rules, `settings.json`
  permission denials — and reduce the context-file line to a one-line pointer ("formatting is
  enforced by pre-commit; don't fight it"). A rule that matters is a rule with a failing check.
- **R11 Structure micro-optimization** (SKIP): don't recommend reordering sections, moving rules
  to the top, splitting/merging CLAUDE.md and AGENTS.md, or format changes *as adherence fixes* —
  all null results. Splitting is fine for human maintainability; just keep one source of truth
  and avoid divergent duplicates.
- **R12 Skills are not a dumping ground** (FLAG): if the user wants to offload trimmed content
  into Claude Code Skills, warn that skill injection showed near-zero benefit for most skills
  (39/49 with zero pass-rate improvement, avg +1.2%, token overhead up to +451%). Skills earn
  their place for genuinely procedural, rarely-needed knowledge — not as a landfill for cut
  overview prose.

### 3. Verify before cutting

Don't cut on pattern-matching alone. For each R2/R5 verdict, confirm the information actually
exists elsewhere (grep the README/docs/config). For each K1, confirm the command is real
(check `pyproject.toml`, `Makefile`, CI config; execute if possible). Wrong information is worse
than none.

### 4. Rewrite

Produce the fixed file:
- Order by importance: hard constraints → build/test commands → environment traps → conventions.
- Imperative, specific, one instruction per line. No filler prose, no headers for two-line
  sections.
- Every retained line must answer "yes" to: *Is this non-discoverable, repo-specific, and does
  the benefit of the agent following it every single task outweigh a ~1-2% cost bump?*
- Keep the file at the repo root under the name the user's agent reads (CLAUDE.md for Claude
  Code; AGENTS.md as the cross-agent standard). If both exist, make one the source of truth and
  the other a one-line pointer or symlink — divergent duplicates are a maintenance trap (though
  note: local contradictions didn't measurably hurt adherence; the risk is human confusion and
  staleness, not agent failure).
- Treat the file as configuration-as-code: recommend it be reviewed in PRs and updated alongside
  the tooling it describes, like a Dockerfile or CI workflow. A stale command violates the
  "wrong information is worse than none" rule on every future session.
- Where a cut rule was load-bearing, emit the enforcement artifact too (hook config, pre-commit
  entry, CI step) rather than leaving the constraint unprotected.

### 5. Report

Give the user: the audit table, a summary of cuts with word/line count before → after, the
rewritten file, any enforcement artifacts, and impact framing: overview-heavy files measured
~20% cost overhead with flat-to-negative success rates, while lean discovery-shortcut files
measured up to ~29% *lower* runtime — the audit aims to move the file from the first regime to
the second. Offer the honest caveats: even good context files buy small success-rate gains; if
the repo is popular, well-documented Python, "no context file" is defensible; the file matters
most for niche stacks, sparse docs, and non-standard tooling; and the literature recommends
measuring in your own repo rather than trusting either headline number.

## Anti-patterns to flag in generation requests

If asked to *generate* a context file from scratch (e.g., an `/init`-style request), do not
produce the typical LLM-generated file (overview + tech stack + directory tree + generic
guidelines) — that pattern measurably hurts. Instead, interview the repo: find non-default
commands, traps, and constraints (steps 1-3 above), and emit only those. If nothing
non-discoverable exists, say so and recommend a minimal file or none at all.
