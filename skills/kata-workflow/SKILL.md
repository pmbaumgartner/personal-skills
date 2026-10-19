---
name: kata-workflow
description: Use whenever Kata is used for issue management, through the MCP tools or the CLI, including turning plans or review findings into issues. Applies Blue decision and Red implementation workflows, attribution, and verified close-out in the shared issue ledger.
disable-model-invocation: false
---

# Kata Workflow

Use Kata as the durable record of work: what was attempted, which model contributed, what was decided, and how completion was verified.

## Start

- Use whichever Kata interface the session has: the MCP tools (`kata.*`) or the `kata` CLI. This skill names operations by verb (search, show, create, claim, comment, edit, label, close, next, ready); see [Interfaces](#interfaces) for how each interface spells them. Take parameter and flag names from the interface's own schemas or `--help`, not this skill.
- Pass the project when the scope covers several projects, and use qualified refs such as `project#abc4` across projects.
- Show and search before creating. Search and list cover open and closed issues unless a status is given. Link issues with the web URLs the interface returns.
- Track real work in its correct project. Create practice or scratchpad issues only when requested.
- Delete or purge only when the user explicitly requests that action and ref. Force a claim only on explicit user direction.

## Identity And Attribution

The author is the interface's actor (see [Interfaces](#interfaces)): the accountable human managing the agents. Ownership and close history belong to the author; do not try to act as a per-agent author.

Identify each agent session (one harness conversation, start to finish) with a teammate handle `<harness>_<model>_<session-id>`, using the identifiers supplied by the runtime (`unknown` when unavailable; never guess). For `<session-id>`, use the last 8 characters of the session UUID, lowercased (`5ba8fe8e` for `…-ba6d-481c-8ee2-69d15ba8fe8e`); the leading characters of time-ordered UUIDs repeat across sessions. Read the UUID from the harness's environment:

| Harness | `<harness>` | Session UUID |
| --- | --- | --- |
| Claude Code | `claude-code` | `$CLAUDE_CODE_SESSION_ID` |
| Codex | `codex` | `$CODEX_THREAD_ID` |
| Pi | `pi` | `$PI_SESSION_ID` |

Kata accepts only letters, digits, `.`, `_`, and `-`, up to 64 characters. Pass the handle explicitly on every create, claim, comment, and close, such as `claude-code_opus-5.5_5ba8fe8e`; the MCP connection or the shell's `$KATA_TEAMMATE` may be shared with another session, so do not rely on a default.

Each session's attributed claim comment and its close or release comment are its minimum record, including for incomplete attempts. If the model changes mid-session, use the new identifier from then on.

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

Take the next unowned ready issue; list unowned ready issues to compare candidates. Prefer upstream feeders when priority is close. Before starting, inspect the issue, parent, links, and previous comments, and check its assumptions against current code and docs; edit stale scope before implementing. Future schedules and `someday` parking can keep issues out of the ready queue.

Search before creating, reuse suitable issues, and give every create a stable idempotency key such as `login-race-2026-10-03`. Give comments one too where the interface supports it (MCP); the CLI's `comment` has no key, so check before retrying a failed comment.

An issue owned by the author may belong to another session: resume it only after the latest teammate-attributed comment shows it is this session's to continue or was handed off.

Use relationships from the operating issue's perspective, when creating or as add/remove deltas when editing:

- `parent`: this issue is a subtask of the target.
- `blocks`: this issue must finish before the target.
- `blocked_by`: the target must finish before this issue.
- `related`: context without ordering.

Block Red work on any required Blue decision. Use priority to rank ready work (`0` is highest), and dependency links to enforce sequencing. Parenting, labels, and titles do not establish blockers.

For plan conversion, read [references/plan-to-issues.md](references/plan-to-issues.md).

## Record Progress And Pause

The issue body states current truth: what the next implementer or reader needs now, such as objective, constraints, scope, acceptance, deliverables, and for Blue the settled result. Comments hold the history a later reader needs and cannot recover from the body, commits, or close record: findings that changed the approach, failed attempts others should not repeat, blockers, decisions with their reasons, and handoff state.

Comment when one of those happens, not to report progress. Do not post status updates, step-by-step logs, plans you are about to execute, restatements of the body or diff, or summaries the close will repeat. Combine related findings into one comment. If nothing notable happens between claim and close, those two comments are the whole record.

When scope or a decision changes, rewrite the affected body sections in place and explain the change in a comment right after the edit (attach it to the edit where the interface allows). Do not add update sections, dated notes, or accounts of who changed what to the body. Add a `## Deliverables` block for artifact-producing work and review every listed path before close.

Pass bodies inline as markdown; draft long ones in `.kata/drafts/<slug>.md` first when review helps. Keep scratch notes and logs under gitignored `.kata/`. Create tracked artifacts only when requested or required by a deliverable; use accessible shared or tracked artifacts when collaborators need detail beyond the issue record. Edit durable documents in place.

Leave unfinished work open. Comment with evidence and the next action, and add the `needs-review` label when useful. When giving work back, clear the owner and comment with the reason, such as "Releasing; blocked on a missing fixture."

## Verify And Close

Closing asserts verified completion, and other agents and humans act on that claim without re-checking. Close each issue promptly after its completion claim and delivery requirements are satisfied so dependents become ready; leave incomplete work open.

Red issues should normally finish with a local commit, not implementation left only in the working tree. Review and verify the work, commit only the issue's changes, then close with `commit` evidence naming the commit containing the completed work. “Requested delivery state” adds requirements such as a PR, merge, publication, or deployment; it does not silently waive the commit requirement. A local commit does not authorize pushing or those additional actions. Tests, reviewed paths, or a PR URL supplement commit evidence; they do not replace it. If committing is not authorized or possible, record the verified but uncommitted state and leave the issue open. Adding a commit in a later comment does not repair the original close evidence; reopen a prematurely closed issue and close it again with the correct commit evidence.

Close with a substantive message naming the result and verification, and an attributed outcome comment limited to what the message and evidence do not already say. Supply at least one genuine typed evidence item for reason `done`, and review every deliverable:

- `commit`: the commit containing the completed work; never cite HEAD merely because it is convenient.
- `pr`: the relevant pull request.
- `test`: one per verification command that passed.
- `reviewed-paths`: every deliverable reviewed.
- Use reason `audit-no-change` (with `no-change-audit` evidence), `duplicate` (`duplicate-of`), `superseded` (`superseded-by`), or `wontfix` (no evidence) for those dispositions.

Record manual checks, benchmarks, skipped checks, residual risk, and rationale in the outcome comment or reviewed artifact. Use supported evidence types; do not invent prefixes or call ordinary research a test. Follow the Blue or Red reference for its specific completion requirements.

Preview complicated closes with a dry run.

Before ending, make ownership truthful, record remaining actions in Kata, reconcile discovered dependencies, and report the relevant refs and delivery state.

## Interfaces

**MCP.** Tools are grouped into sections that must be loaded first: call `kata_load_issue_discovery`, `kata_load_issue_mutation`, and `kata_load_issue_lifecycle` at the start of the session, then load the listed tools' schemas if the harness defers them. Load other sections (projects, activity, recurrence) only when needed. The server is fixed to its startup project scope and actor. Pass `teammate` and `idempotency_key` as arguments. `kata.close` takes no comment or teammate, so post the outcome comment just before closing.

```text
kata.create  {"title": "Fix login race", "body": "<markdown>", "labels": ["red"],
              "idempotency_key": "login-race-2026-10-03", "teammate": "<handle>"}
kata.comment {"ref": "abc4", "body": "Safari not tested manually.",
              "idempotency_key": "abc4-close-<handle>", "teammate": "<handle>"}
kata.close   {"ref": "abc4", "reason": "done",
              "message": "Committed the callback double-submit fix; callback tests pass.",
              "evidence": [{"type": "commit", "sha": "<verified-work-commit-sha>"},
                           {"type": "test", "command": "cargo test callback"},
                           {"type": "reviewed-paths", "paths": ["src/callback.rs"]}]}
```

**CLI.** Run `kata quickstart` once and `kata <verb> --help` for flags. The project comes from the workspace (`--project` overrides). The actor is `$KATA_AUTHOR`, then `$USER`, then the git user; do not override it with `--as`. Pass `--teammate <handle>` on every mutation and `--agent` for readable output. `close`, `claim`, and `edit` accept `--comment`, which posts the claim, change, or outcome comment with the mutation.

```text
kata create "Fix login race" --body-file .kata/drafts/login-race.md --label red \
  --idempotency-key login-race-2026-10-03 --teammate <handle> --agent
kata close abc4 --done --teammate <handle> \
  --message "Committed the callback double-submit fix; callback tests pass." \
  --comment "Safari not tested manually." \
  --commit <verified-work-commit-sha> --test "cargo test callback" --reviewed src/callback.rs
```

Whenever reporting on an issue or asking the user for input, explain its goal, relevant current state, why it matters, and what the proposed choice or next step would authorize; do not present only issue refs, options, or decisions without that context.
