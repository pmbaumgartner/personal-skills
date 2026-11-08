---
name: context-file-audit
description: Review CLAUDE.md, AGENTS.md, GEMINI.md, Cursor or Copilot rules, and similar agent context files, then propose a leaner, more effective version. Based on controlled studies of coding agents and current vendor guidance.
disable-model-invocation: true
---

# Context File Audit

Review a repository's agent context files against the repo, then propose how they should
change.

## What the evidence says

- Context files barely change whether agents solve tasks. They change what agents *do*:
  agents follow the instructions closely, and every followed instruction adds work and cost.
- Useful content is what the agent can't discover and would otherwise get wrong or do
  expensively: non-default commands, environment traps, hard constraints, and conventions the
  code doesn't show (including code that misleads, like a legacy pattern new code shouldn't
  copy).
- Overviews, directory trees, and anything repeated from the README or config don't help.
  Generic advice ("follow the existing style", "handle edge cases") is neutral to harmful.
  Short scope-limiting "don't" rules ("don't refactor unrelated code") helped in one study.
- Stale instructions do real damage: agents follow the file over the code in front of them.
- Length, section order, and splitting into several files don't measurably change adherence.
  Wording does: direct imperatives are followed more than conditionals or "never X without Y".
- Adherence fades over a long session, and prose guarantees nothing. Rules that must always
  hold need a hook, permission rule, pre-commit check, or CI.

Sources are in `references/findings.md`. Most studies are Python and model-specific, so don't
promise success-rate gains.

## Review

1. **Find what the agent actually reads.** Look at every context file in the repo (root and
   nested) and personal ones (`CLAUDE.local.md`, `~/.claude/CLAUDE.md`, auto memory). Also
   look at the README, docs, and config they might duplicate. Confirm each agent loads what
   you think it does:
   - Claude Code ignores `AGENTS.md` when a `CLAUDE.md` exists, unless that file imports it
     with `@AGENTS.md`. `/context all` shows what loaded.
   - Codex drops content past 32 KiB.
2. **Check each instruction against the repo:**
   - Is it still true? Check commands, paths, and conventions against current code and
     config, and run commands where possible. Wrong instructions are worse than none.
   - Could the agent find it itself? Cut it, unless the file is the repo's only documentation.
   - Is it generic advice, or a workaround for older models (IMPORTANT/caps, "think hard",
     "don't be lazy")? Cut it.
   - Does it add work to every task ("always run the full suite", "read all related files
     first")? Scope it down or cut it.
   - Must it never be broken? Propose enforcement and leave a one-line pointer in the file.
   - Does it apply only to part of the codebase, or only sometimes? Move it to a path-scoped
     rule, a per-directory file, or a focused skill. Moving content into a skill doesn't make
     it useful; the same test applies. Personal preferences go in a local or user-level file.
   - Is it a direct, checkable imperative? Rewrite vague or conditional phrasing.
3. **Skip** reordering, splitting or merging files for adherence, and format changes. Treat
   length as a sign of discoverable or generic content, not as a problem in itself.

## Propose

Give the user:
- The main problems, most harmful first: wrong or stale content, costly rituals, unenforced
  must-hold rules, then noise.
- The proposed file, ready to replace the current one. Also list any content moved elsewhere
  and any enforcement to add (hook, deny rule, pre-commit, CI).
- An honest expectation: less wasted work and fewer wrong turns, not a jump in success rate.
  For a well-documented repo with standard tooling, a minimal file or none is a fine answer.

If a repo has both `AGENTS.md` and `CLAUDE.md`, propose one source of truth: `AGENTS.md`, plus
a `CLAUDE.md` that imports it with `@AGENTS.md` only if Claude-specific lines are needed.

Apply the changes only if the user asks.

## Generating a new file

Don't produce the usual generated file (overview, tech stack, directory tree, generic
guidelines); that pattern doesn't help. Extract only the non-discoverable items above, and if
there are none, say so. Suggest growing the file from repeated mistakes: add a line when the
agent gets the same thing wrong twice.
