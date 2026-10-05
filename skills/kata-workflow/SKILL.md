---
name: kata-workflow
description: Manage Kata issues using Blue decision and Red implementation workflows. Record model contributions, scope, decisions, dependencies, and verified completion in the shared issue ledger.
disable-model-invocation: false
---

# Kata Workflow

Use Kata as the durable record of work: what was attempted, which model contributed, what was decided, and how completion was verified.

## Start

- Use the Kata MCP tools (`kata.*`), not the `kata` CLI. Tools are grouped into sections that must be loaded before use: call `kata_load_issue_discovery`, `kata_load_issue_mutation`, and `kata_load_issue_lifecycle` at the start of the session, then load the listed tools' schemas if the harness defers them. Load other sections (projects, activity, recurrence) only when needed. Take parameter names and constraints from the tool schemas, not this skill.
- The server is fixed to its startup project scope and actor. Pass `project` when the scope covers several projects, and use qualified refs such as `project#abc4` across projects.
- Inspect with `kata.show` and search with `kata.search` before creating. Search and list cover open and closed issues when `status` is omitted. Link issues with the returned `web_url` values.
- Track real work in its correct project. Create practice or scratchpad issues only when requested.
- Call `kata.delete` or `kata.purge` only when the user explicitly requests that action and ref. Claim with `force` only on explicit user direction.

## Identity And Attribution

The author is the MCP server's startup actor: the accountable human managing the agents. Ownership and close history belong to the author; do not try to act as a per-agent author.

Identify each agent session (one harness conversation, start to finish) with a teammate handle `<harness>_<model>_<session-id>`, using the identifiers supplied by the runtime (`unknown` when unavailable; never guess). For `<session-id>`, use the last 8 characters of the session UUID, lowercased (`5ba8fe8e` for `…-ba6d-481c-8ee2-69d15ba8fe8e`); the leading characters of time-ordered UUIDs repeat across sessions. Read the UUID from the harness's environment:

| Harness | `<harness>` | Session UUID |
| --- | --- | --- |
| Claude Code | `claude-code` | `$CLAUDE_CODE_SESSION_ID` |
| Codex | `codex` | `$CODEX_THREAD_ID` |
| Pi | `pi` | `$PI_SESSION_ID` |

Kata accepts only letters, digits, `.`, `_`, and `-`, up to 64 characters. Pass the handle as `teammate` on every `kata.comment` and `kata.create` call, such as `"teammate": "claude-code_opus-5.5_5ba8fe8e"`; the MCP connection may be shared, so do not rely on its startup default.

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

Call `kata.next` with `unowned: true`; use `kata.ready` with `unowned: true` to compare candidates. Prefer upstream feeders when priority is close. Before starting, inspect the issue, parent, links, and previous comments, and check its assumptions against current code and docs; edit stale scope before implementing. Future schedules and `someday` parking can keep issues out of the ready queue.

Search before creating, reuse suitable issues, and give every create and comment a stable idempotency key:

```text
kata.search  {"query": "login race"}
kata.create  {"title": "Fix login race", "body": "<markdown>", "labels": ["red"],
              "idempotency_key": "login-race-2026-10-03", "teammate": "<handle>"}
kata.claim   {"ref": "abc4"}
kata.comment {"ref": "abc4", "body": "Claimed.", "idempotency_key": "abc4-claim-<handle>",
              "teammate": "<handle>"}
```

An issue owned by the author may belong to another session: resume it only after the latest teammate-attributed comment shows it is this session's to continue or was handed off.

Use relationships from the operating issue's perspective, on `kata.create` or as `add_*` / `remove_*` deltas on `kata.edit`:

- `parent`: this issue is a subtask of the target.
- `blocks`: this issue must finish before the target.
- `blocked_by`: the target must finish before this issue.
- `related`: context without ordering.

Block Red work on any required Blue decision. Use priority to rank ready work (`0` is highest), and dependency links to enforce sequencing. Parenting, labels, and titles do not establish blockers.

For plan conversion, read [references/plan-to-issues.md](references/plan-to-issues.md).

## Record Progress And Pause

The issue body states current truth: what the next implementer or reader needs now, such as objective, constraints, scope, acceptance, deliverables, and for Blue the settled result. Comments hold the history a later reader needs and cannot recover from the body, commits, or close record: findings that changed the approach, failed attempts others should not repeat, blockers, decisions with their reasons, and handoff state.

Comment when one of those happens, not to report progress. Do not post status updates, step-by-step logs, plans you are about to execute, restatements of the body or diff, or summaries the close will repeat. Combine related findings into one comment. If nothing notable happens between claim and close, those two comments are the whole record.

When scope or a decision changes, rewrite the affected body sections in place and explain the change in a `kata.comment` right after the `kata.edit` (edits carry no comment of their own). Do not add update sections, dated notes, or accounts of who changed what to the body. Add a `## Deliverables` block for artifact-producing work and review every listed path before close.

Pass bodies inline as markdown; draft long ones in `.kata/drafts/<slug>.md` first when review helps. Keep scratch notes and logs under gitignored `.kata/`. Create tracked artifacts only when requested or required by a deliverable; use accessible shared or tracked artifacts when collaborators need detail beyond the issue record. Edit durable documents in place.

Leave unfinished work open. Comment with evidence and the next action, and add the `needs-review` label with `kata.set_label` (`present: true`) when useful. Release ownership when giving work back:

```text
kata.edit    {"ref": "abc4", "clear_owner": true}
kata.comment {"ref": "abc4", "body": "Releasing; blocked on a missing fixture.",
              "idempotency_key": "abc4-release-<handle>", "teammate": "<handle>"}
```

## Verify And Close

Closing asserts verified completion, and other agents and humans act on that claim without re-checking. Close each issue promptly after its completion claim and delivery requirements are satisfied so dependents become ready; leave incomplete work open.

Red issues should normally finish with a local commit, not implementation left only in the working tree. Review and verify the work, commit only the issue's changes, then close with `commit` evidence naming the commit containing the completed work. “Requested delivery state” adds requirements such as a PR, merge, publication, or deployment; it does not silently waive the commit requirement. A local commit does not authorize pushing or those additional actions. Tests, reviewed paths, or a PR URL supplement commit evidence; they do not replace it. If committing is not authorized or possible, record the verified but uncommitted state and leave the issue open. Adding a commit in a later comment does not repair the original close evidence; reopen a prematurely closed issue and close it again with the correct commit evidence.

Close with `kata.close` and a substantive `message` naming the result and verification. Record the attributed outcome in a `kata.comment` posted just before the close, limited to what the message and evidence do not already say; `kata.close` takes no teammate or comment. Supply at least one genuine typed evidence item for `reason: "done"`, and review every deliverable:

- `{"type": "commit", "sha": ...}` for the commit containing the completed work; never cite HEAD merely because it is convenient.
- `{"type": "pr", "url": ...}` for the relevant pull request.
- One `{"type": "test", "command": ...}` for each verification command that passed.
- `{"type": "reviewed-paths", "paths": [...]}` for every deliverable reviewed.
- Use `reason` `audit-no-change` (with `no-change-audit` evidence), `duplicate` (`duplicate-of`), `superseded` (`superseded-by`), or `wontfix` (no evidence) for those dispositions.

Record manual checks, benchmarks, skipped checks, residual risk, and rationale in the outcome comment or reviewed artifact. Use supported evidence types; do not invent prefixes or call ordinary research a test. Follow the Blue or Red reference for its specific completion requirements.

```text
kata.comment {"ref": "abc4", "body": "Safari not tested manually.",
              "idempotency_key": "abc4-close-<handle>", "teammate": "<handle>"}
kata.close   {"ref": "abc4", "reason": "done",
              "message": "Committed the callback double-submit fix; callback tests pass.",
              "evidence": [{"type": "commit", "sha": "<verified-work-commit-sha>"},
                           {"type": "test", "command": "cargo test callback"},
                           {"type": "reviewed-paths", "paths": ["src/callback.rs"]}]}
```

Preview complicated closes with `dry_run: true`.

Before ending, make ownership truthful, record remaining actions in Kata, reconcile discovered dependencies, and report the relevant refs and delivery state.

Whenever reporting on an issue or asking the user for input, explain its goal, relevant current state, why it matters, and what the proposed choice or next step would authorize; do not present only issue refs, options, or decisions without that context.
