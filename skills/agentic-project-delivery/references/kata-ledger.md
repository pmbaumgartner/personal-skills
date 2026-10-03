# Kata Ledger Contract

Load this reference before initializing, executing, coordinating, auditing, or closing durable Kata work.

Kata is the primary work ledger for issue identity, status, ownership, priority, relationships, comments, events, and completion claims. The repository owns code, tests, architecture decisions, and long-lived specifications. CI, launchers, and runtime systems own observed verification and process state. Do not create or maintain a parallel Markdown, chat, spreadsheet, or GitHub-issue ledger for the same work.

This integration was checked against `kenn-io/kata` documentation on `main` at commit `0abb14f783ed25161714f552006120c16d3f73a4` on 2026-07-19. Kata is pre-1.0; run `kata <command> --help` before automating flags.

## Verify before mutating

Start with:

```sh
kata version --json
kata quickstart
kata list --agent
```

If durable setup was requested and the workspace is unbound, run `kata init --with-agents`. Inspect `kata init --help` when selecting a project or hooks.

If Kata is unavailable, remain advisory or surface the installation and initialization dependency. Do not invent a shadow ledger.

## Establish attributable identity

Use one stable actor identity per concurrently active worker lane:

```sh
export KATA_AUTHOR=agent-parser-a
kata whoami --agent
```

Reuse the lane identity across successive packets. Create another identity for a separate auditor only when a distinct audit is warranted. A fresh session does not create independent human authority.

All concurrent workspaces must share the intended Kata project and database. Use the smallest sharing model that works: one local project for one workstation, a secured remote daemon for trusted hosts needing immediate shared state, or federation only when its lease, stale-read, quarantine, and recovery behavior is understood.

## Keep the issue graph small

Default to one root outcome issue and zero to three initially open implementation packets. Add later packets just in time.

Create no standalone pilot, gate, audit, release, or enablement issue unless it needs a separate owner, blocks multiple packets, crosses a consequential authority boundary, or satisfies a policy requirement. Ordinary findings and decisions belong in attributable comments on the outcome.

Recommended labels are:

- `apd:outcome` for the root;
- `apd:packet` for independently completable work;
- `risk:low`, `risk:medium`, or `risk:high` only when useful.

Do not encode the workflow as a label sequence. Respect an equivalent repository convention.

Search before creating:

```sh
kata search "<specific objective or symptom>" --agent
```

Create deterministically only when no issue already fits:

```sh
kata create "<outcome, not implementation>" \
  --body-file /path/to/project-charter.md \
  --label apd:outcome \
  --idempotency-key "apd:<project>:outcome" \
  --agent

kata create "<bounded packet>" \
  --body-file /path/to/work-packet.md \
  --parent <outcome-ref> \
  --label apd:packet \
  --idempotency-key "apd:<project>:<stable-slug>" \
  --agent
```

## Model dependencies structurally

```sh
kata edit <child> --parent <parent> --agent
kata edit <dependent> --blocked-by <prerequisite> --agent
kata edit <issue> --related <context-only-ref> --agent
```

Use `parent` for composition, `blocked-by` for real ordering, and `related` for context. Do not leave a structural dependency only in prose.

## Claim and execute one packet at a time

```sh
kata next --unowned --label apd:packet --agent
kata claim <ref> --agent
```

A failed claim is a coordination signal; select another issue. Do not force ordinary claims. One active working-agent side owns an issue.

Use `work.attention` only for live attention, never as lifecycle state or a replacement for dependency links:

```sh
kata meta set <ref> work.attention ok --agent
kata meta set <ref> work.attention needs-human --agent
kata meta set <ref> work.attention stuck --agent
kata meta set <ref> work.attention_msg "<one-line reason>" --agent
```

The launcher owns worktrees, branches, process supervision, and the work-in-progress cap.

## Keep one durable record per fact

- Keep scope and acceptance in the issue body or in one linked repository artifact, not both.
- Record decisions, failed approaches, handoffs, and remaining work as comments.
- Link CI, benchmark, runtime, commit, and PR evidence instead of copying it into another state system.
- Store frozen identities and hashes once in the acceptance record or manifest.
- Create machine-readable evidence only when a check, CI job, or audit tool consumes it.
- Do not store secrets, credentials, or sensitive payloads in Kata.

Rendered reports, screenshots, caches, and reproducible intermediate artifacts are disposable unless the contract, consumer, or policy requires retention. Retain the outcome decision, acceptance identity, material exceptions, completion claim, and evidence links for the repository's normal record period.

## Close only with fresh evidence

Close promptly when the stated acceptance is complete and freshly verified:

```sh
SHA=$(git rev-parse HEAD)
kata close <ref> --done \
  --message "<what changed and what was verified>" \
  --commit "$SHA" \
  --test "<fresh verification command>" \
  --agent
```

Use `--pr <url>`, `--reviewed <path>`, or documented no-change evidence when applicable. A `--done` close needs a substantive message and supported typed evidence.

If acceptance is incomplete, keep the issue open, comment with evidence and remaining work, and add a structural dependency or attention signal when appropriate. Do not close an attempt merely to clean the board.

## Record decisions proportionally

A comment on the outcome issue is normally sufficient. Use a separate decision issue only when the decision blocks at least two independent packets, belongs to a materially different authority, permits production or public exposure, permits irreversible mutation, or policy requires a separate record.

Keep merge, distribution, exposure, and decommissioning conceptually distinct. Represent only the boundaries that need durable control.

## Monitor and audit when warranted

Useful read operations include:

```sh
kata events --tail --agent
kata digest --since 24h
kata audit closes
```

Use a separate completion audit only for high-risk work, material oracle changes, consequential milestone claims, hard-to-observe outcomes, or suspicious evidence. Sample the assembled outcome rather than creating an audit issue for every packet.

## Back up before high-impact concurrency

Name backup and restore ownership. Export from the storage-owning host:

```sh
kata daemon stop
kata export --output <backup-path>.jsonl
kata daemon start
```

Use the documented online snapshot option when downtime is not acceptable. Do not copy a live SQLite file or mistake `.kata.toml` for issue history.

Never run `kata delete` or `kata purge` unless the user explicitly requests the exact destructive operation and target.

## End a durable session cleanly

1. Leave truthful ownership and attention on attempted packets.
2. Comment on incomplete work with evidence and the next action.
3. Close verified work with typed evidence using `kata close`.
4. Confirm real ordering is represented with `--blocked-by`.
5. Report relevant Kata refs; leave no durable next step only in chat.
