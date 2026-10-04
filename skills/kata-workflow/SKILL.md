---
name: kata-workflow
description: Manage Kata issues using Blue decision and Red implementation workflows. Record model contributions, scope, decisions, dependencies, and verified completion in the shared issue ledger.
disable-model-invocation: false
---

# Kata Workflow

Use Kata as the durable record of work: what was attempted, which model contributed, what was decided, and how completion was verified.

## Start

- Run `kata quickstart` in an unfamiliar workspace or after an upgrade. Use `kata <command> --help` for syntax. Keep version-specific CLI quirks and input/output normalization in Kata's CLI help/docs, not this workflow skill. These examples were checked against v0.18.0.
- Work in the bound project; use `--workspace` or `--project` when needed. Run `kata init` only when binding a workspace is intended. Use qualified refs such as `project#abc4` across projects.
- Use `--agent` for normal reads and mutations; use `--json` for scripts. Inspect with `kata show <ref> --agent` and search before creating. Use `list --status all` for history; search includes open and closed issues by default.
- Track real work in its correct project. Create practice or scratchpad issues only when requested.
- Run `delete` or `purge` only when the user explicitly requests that action and ref. Transfer ownership with `--force` only on explicit user direction.

## Identity And Attribution

The author (`KATA_AUTHOR` / `--as`) is the accountable human managing the agents. Keep it stable; do not set a per-agent author. Ownership and close history belong to the author.

Identify each agent run with a teammate handle `<harness>_<model>_<run-id>`, using the identifiers supplied by the runtime (`unknown` when unavailable; never guess). Kata accepts only letters, digits, `.`, `_`, and `-`, up to 64 characters, so keep the run ID short. Set it in the run's own environment, or pass `--teammate` per command; on shared MCP connections pass `teammate` per call on `kata.comment` and `kata.create`.

```bash
export KATA_TEAMMATE='codex_gpt-6.1-sol_s42'
```

Comment when starting substantive work and record the outcome when finishing or handing off, including incomplete attempts. If the model changes mid-run, use the new identifier from then on.

## Classify And Decide

Give every issue exactly one workflow label and start its title with a verb naming its completion claim. Use titles such as `Investigate callback duplication` or `Fix callback duplication`; omit `[Blue]` / `[Red]` prefixes.

| Label | Completion claim | Read when doing this work |
| --- | --- | --- |
| `blue` | Settled decision, finding, or recommendation | [references/blue.md](references/blue.md) |
| `red` | Verified, committed implementation, plus any additional requested delivery steps | [references/red.md](references/red.md) |

Split decision and implementation only when they have independently durable outputs. Keep ordinary local implementation choices inside Red work. Open or update Blue when uncertainty changes scope, acceptance, settled decisions, or reusable policy. Create retrospective Blue work only for reusable learning or a faulty assumption.

Use exactly one decision mode per goal or root issue.

Use **Human mode** by default. State intent and decide nonconsequential choices within the authorized goal. For unresolved consequential choices, present viable options, tradeoffs, and a recommendation, then pause once for the user. A choice is consequential when a wrong decision could cause material harm, establish a durable dependency or precedent, commit significant downstream work, or require more than a local correction to reverse. Uncertainty calls for more evidence; it does not alone require a checkpoint.

Reuse the user's existing decisions and authorization. Authorization to execute permits selecting and claiming ready work within scope without another checkpoint.

Use **Agent mode** only after explicit delegation for reversible, non-production work. Record its authority in the root issue or reviewed policy; children inherit it. Follow [references/agent-mode.md](references/agent-mode.md) for signoff and reporting. An active Goal supplies persistence, not decision authority or additional action permissions.

## Select, Create, And Claim

Run `kata next --unowned --agent`; use `kata ready --unowned --agent` to compare candidates. Prefer upstream feeders when priority is close. Before starting, inspect the issue, parent, links, and previous comments, and check its assumptions against current code and docs; edit stale scope before implementing. Future schedules and `someday` parking can keep issues out of the ready queue.

Search before creating, reuse suitable issues, and give every create an idempotency key:

```bash
kata search "login race" --agent
kata create "Fix login race" --body-file .kata/drafts/login-race.md \
  --label red --idempotency-key login-race-2026-10-03 --agent
kata claim abc4 --if-unowned --comment "Starting the agreed implementation." --agent
```

Always claim with `--if-unowned`. Concurrent runs share the author, so it is the only claim check that stops two runs taking the same issue; it fails whenever the issue has any owner. On failure, choose other ready work. An issue owned by the author may belong to another run: resume it only after the latest teammate-attributed comment shows it is this run's to continue or was handed off.

Use relationships from the operating issue's perspective:

- `--parent <ref>`: this issue is a subtask of the target.
- `--blocks <ref>`: this issue must finish before the target.
- `--blocked-by <ref>`: the target must finish before this issue.
- `--related <ref>`: context without ordering.

Block Red work on any required Blue decision. Use priority to rank ready work (`0` is highest), and dependency links to enforce sequencing. Parenting, labels, and titles do not establish blockers.

For plan conversion, read [references/plan-to-issues.md](references/plan-to-issues.md).

## Record Progress And Pause

The issue body states current truth: what the next implementer or reader needs now, such as objective, constraints, scope, acceptance, deliverables, and for Blue the settled result. Comments hold the history: attempts, findings, blockers, decisions as they happened, and next actions. When scope or a decision changes, rewrite the affected body sections in place and explain the change in the edit's `--comment`. Do not add update sections, dated notes, or accounts of who changed what to the body. Add a `## Deliverables` block for artifact-producing work and review every listed path before close.

Use `.kata/drafts/<slug>.md` with `--body-file` for multiline drafts. Keep scratch notes and logs under gitignored `.kata/`. Create tracked artifacts only when requested or required by a deliverable; use accessible shared or tracked artifacts when collaborators need detail beyond the issue record. Edit durable documents in place.

Leave unfinished work open. Comment with evidence and the next action, and add `kata label add <ref> needs-review` when useful (`kata edit` has no `--label` flag, despite hints in `close` help and errors). Release ownership when giving work back:

```bash
kata unassign abc4 --comment "Releasing; blocked on a missing fixture." --agent
```

## Verify And Close

Closing asserts verified completion, and other agents and humans act on that claim without re-checking. Close each issue promptly after its completion claim and delivery requirements are satisfied so dependents become ready; leave incomplete work open.

Red issues should normally finish with a local commit, not implementation left only in the working tree. Review and verify the work, commit only the issue's changes, then close with `--commit <sha>` naming the commit containing the completed work. “Requested delivery state” adds requirements such as a PR, merge, publication, or deployment; it does not silently waive the commit requirement. A local commit does not authorize pushing or those additional actions. Tests, reviewed paths, or a PR URL supplement commit evidence; they do not replace it. If committing is not authorized or possible, record the verified but uncommitted state and leave the issue open. Adding a commit in a later comment does not repair the original close evidence; reopen a prematurely closed issue and close it again with the correct commit evidence.

Close with a substantive sentence naming the result and verification, and record the attributed outcome with `--comment`. Supply at least one genuine typed evidence item for `--done`, and review every deliverable:

- `--commit <sha>` for the commit containing the completed work; never cite HEAD merely because it is convenient.
- `--pr <url>` for the relevant pull request.
- Repeat `--evidence "test:<cmd>"` for each verification command that passed.
- Repeat `--reviewed <path>` for every deliverable reviewed.
- Use `--audit-no-change`, `--duplicate-of <ref>`, `--superseded-by <ref>`, or `--wontfix` for those dispositions.

Record manual checks, benchmarks, skipped checks, residual risk, and rationale in the outcome comment or reviewed artifact. Use supported evidence types; do not invent prefixes or call ordinary research a test. Follow the Blue or Red reference for its specific completion requirements.

```bash
kata close abc4 --done \
  --message "Committed the callback double-submit fix; callback tests pass." \
  --commit <verified-work-commit-sha> \
  --evidence "test:cargo test callback" --reviewed src/callback.rs \
  --comment "Deduplicated submit handler and committed the verified changes. Safari not tested manually." \
  --agent
```

Preview complicated closes with `--dry-run`.

Before ending, make ownership truthful, record remaining actions in Kata, reconcile discovered dependencies, and report the relevant refs and delivery state.

Whenever reporting on an issue or asking the user for input, explain its goal, relevant current state, why it matters, and what the proposed choice or next step would authorize; do not present only issue refs, options, or decisions without that context.
