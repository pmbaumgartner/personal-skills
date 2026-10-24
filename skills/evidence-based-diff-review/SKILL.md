---
name: evidence-based-diff-review
description: Quickly assess a commit, pull request, branch, or pasted diff using SCC file deltas and maintenance history to rank changed code, then Codebase Memory structural evidence and focused source inspection to validate the leading concerns. Use for bounded evidence-based design or complexity reviews of changes. Do not use for repository-wide audits, SCC-only reviews, or broad defect and security hunts.
disable-model-invocation: true
---

# Evidence-Based Diff Review

Review the change, not the whole repository. SCC identifies where maintenance
pressure changed; Codebase Memory explains structural exposure; source confirms
the concern.

Read [references/mcp-playbook.md](references/mcp-playbook.md) before using SCC
or Codebase Memory.

## Evidence model

1. **Rank files with SCC:** compare the pinned base and head snapshots, then add
   bounded history evidence for changed files.
2. **Explain with Codebase Memory:** inspect hunk-intersecting symbols, callers,
   dependencies, duplication, and blast radius in the pinned head snapshot.
3. **Validate in source:** the captured patch and pinned worktrees determine
   what changed and whether it is a design concern.

SCC and graph metrics select attention; they are never findings by themselves.
Do not combine unlike signals into a composite score.

## Guardrails

- Pin exact base and head SHAs. Never review a dirty or moving checkout.
- The captured patch is authoritative for changed lines. `detect_changes`
  supplies changed paths and impact, not patch hunks.
- Compare SCC metrics only between the pinned worktrees. Graph symbol metrics
  describe the head; do not present them as before/after deltas.
- Use one pinned head graph index.
- Treat tests, generated or vendored code, fixtures, documentation, migrations,
  examples, benchmarks, and verification tooling separately from owned runtime
  code. Keep feature-gated research code in a separate bucket unless it affects
  a supported boundary.
- Prefer no finding over a weak metric-only finding. Report no more than three
  actionable concerns.
- Do not run tests, use external services, or spawn subagents unless the user
  expands the task.
- Shell/Git commands are for snapshot setup and evidence capture. The
  deterministic hunk classifier may inspect syntax before SCC only to route
  attention and choose scope. Use interactive source reads, AST tools, or exact
  text search only after SCC has produced the candidate files.
- If SCC or Codebase Memory remains unavailable after one reconnect attempt,
  stop and disclose the missing dependency.

## Workflow

### 1. Pin and capture the change

1. Resolve the requested base and head to full SHAs.
   Prefer [scripts/prepare_review.py](scripts/prepare_review.py) for steps 1–5;
   it creates the pinned filesystem artifacts and evidence manifest but does
   not call SCC or Codebase Memory.
2. Create detached base and head worktrees under a temporary path. Worktrees
   are cheap, give SCC two stable filesystem snapshots, and keep source spans
   aligned for the review.
3. Create a detached, non-local clone at the head SHA for SCC history queries.
   SCC's Git walker may not resolve linked-worktree metadata or shared-clone
   object alternates; `git clone --no-local` gives it a self-contained object
   database. Use this clone only for `hotspots` and `coupling`.
4. Capture:
   - `git diff --find-renames <base>..<head>`;
   - a zero-context copy;
   - machine-readable ranges using
     [scripts/changed_ranges.py](scripts/changed_ranges.py).
   - hunk kinds using
     [scripts/classify_hunks.py](scripts/classify_hunks.py). Treat these as
     routing hints, never proof that a change is safe.
5. Record changed paths, Git-confirmed renames, additions/deletions, diff size,
   range-summary counts, and whether extraction succeeded.
6. For a request spanning multiple commits, review the aggregate change by
   default. Classify changed files first. Prefer per-commit or coherent groups
   when there are more than 25 changed owned-production files or more than
   10,000 review-load lines in those files. Review load includes both sides of
   modified production hunks and the new side of added production files; it
   excludes deleted files, rename-only files, and non-production buckets.
   A coherent aggregate is still appropriate when raw size is dominated by
   deletion, relocation, or one verified cross-cutting rename and the surviving
   behavioral change is bounded. A lexical-only label does not verify semantic
   equivalence: confirm the replacement pattern and inspect every structural
   hunk. Record the calculation and scope choice; do not silently change scope.

If diff capture fails, observations are changed-file-level only. Disclose that
fallback and do not attribute a branch or metric change to a specific hunk.

### 2. Rank changed files with SCC

Run SCC `analyze` with cognitive metrics directly on each changed production
file in the pinned base and head worktrees. Batch independent calls when useful.
For renames, analyze the old path in base and the new path in head. Avoid
whole-repository `by_file` responses unless the changed set is small and the
response is known to remain bounded.

Run one bounded `hotspots` query against the detached history clone, using a
history depth of 200 unless the user requests another window. Scale its result
limit with the changed production set as described in the playbook. A changed
file absent from the response has unknown history; never rank it as zero.

Join results by repository-relative path, using Git rename mappings. Rank
changed production files with these separate signals:

1. positive cognitive-complexity delta;
2. positive cyclomatic-complexity delta;
3. observed hotspot pressure among changed files, with unreturned paths kept in
   an explicit unknown-history bucket;
4. high absolute head complexity;
5. substantial complexity removal.

Do not independently truncate base and head before joining. Missing values are
unknown, not zero. Keep removals as strengths or change context unless they
scatter surviving policy.

Use [scripts/rank_changed_files.py](scripts/rank_changed_files.py) when SCC
results need deterministic path normalization, rename-aware joining, or
ranking. It accepts direct SCC JSON, common MCP envelopes, and batched results;
save a complete tool response or its `fullResultPath` rather than manually
rewriting metrics. Keep runtime, research, tests, generated code, and other
categories separate after the script produces the neutral joined data.

Run file-specific SCC `coupling` against the history clone only for a leading
file when the diff suggests policy or ownership spread across files.

Treat `detect_changes.seed_symbols` as a coarse warning because deletions and
relocations can inflate it. Reconsider grouping only when the raw count exceeds
300 *and* the surviving production scope remains broad (more than 25 files or
300 hunk-intersecting `Function`/`Method` nodes). Otherwise retain the coherent
aggregate and record why. If splitting is impractical, inspect at most five
leading files and disclose reduced sensitivity.

### 3. Add bounded head-graph context

Call `list_projects` as the first graph operation, then ensure one moderate
Codebase Memory index rooted at the pinned head worktree.

1. Call `get_graph_schema` with the pinned project name.
2. Run `detect_changes` inbound at depth 2 over the dependency edge types the
   schema lists, paging all changed files. Verify `base` and `merge_base`.
3. In no more than the five leading SCC files, query `Function`, `Method`,
   `Class`, and `Variable` nodes whose spans intersect new hunk ranges or
   confirmed deletion anchors. Use the labels present in the graph schema.
   Module-level classes and aliases often carry the actual API change.
   Generate the range predicate with
   [scripts/ranges_to_cypher.py](scripts/ranges_to_cypher.py); do not transcribe
   long range lists by hand.
4. Rank those symbols using head complexity, algorithmic-risk flags, source-
   validated visibility, and direct exposure.
5. Call `check_index_coverage` once with every production path used as evidence.
6. Trace representative callers only for concerns that survive initial source
   inspection.

Before ranking an intersecting symbol, record whether its hunk is structural,
an import, an identifier/literal substitution, or comment-only. Prefer
structural hunks. A complex symbol intersected only by a lexical or comment
change is context, not a design concern.

Run the `SIMILAR_TO` and `SEMANTICALLY_RELATED` queries only when SCC, the
patch, or source suggests duplicated policy. Inspect no more than three pairs. Shared scaffolding and parallel boundary
adapters are not findings.

### 4. Validate the leading candidates

Inspect at most five candidates across the SCC ranking and graph context.

For each candidate ask:

1. Which changed lines create or extend the burden?
2. What knowledge or state must maintainers coordinate?
3. Is policy repeated or pushed onto callers?
4. Does the interface contain complexity or expose it?
5. What smallest change deletes branching, modes, duplication, or coordination?

Reject candidates that are pre-existing, cohesive, generated, test-only,
relocated, metric artifacts, or unrelated to changed lines.

A non-Git move may be classified as `relocated` only when the base and head
sources have the same signature and exact normalized body. Use graph or AST
spans to create candidates, then verify them with
[scripts/verify_relocations.py](scripts/verify_relocations.py). Similar names
or file-level metric offsets are insufficient. Remove verified relocated
symbol bodies from implementation-burden interpretation while retaining any
changed wrappers, visibility, module wiring, or ownership boundaries.

A deletion anchor alone does not prove the adjacent surviving symbol changed.
Confirm from patch context that the deleted old range was inside that symbol;
otherwise reject the anchor-only candidate.

## Report

Keep the report concise:

1. **Assessment** — scope, evidence health, overall signal, and useful rejected
   signals or strengths.
2. **Findings** — zero to three, ordered by review priority. Include
   `path:line`, changed-line evidence, SCC pressure, relevant graph context,
   why it matters, the smallest useful fix, and confidence.
3. **Changed-file attention table** — up to five files with SCC
   cyclomatic/cognitive before → after, hotspot context, leading changed symbol,
   hunk kind, exposure, and line- versus file-level attribution. Mark missing
   hotspot history as unknown. Include validated coupling, duplication, or
   blast radius only when useful.
4. **Evidence limits** — SHAs, history window, head index identity, coverage,
   truncation, scope choices, relocation handling, and unresolved dynamic
   behavior.

Report head symbol metrics without inventing symbol-level deltas. If no concern
survives source validation, say so and retain only the most useful attention
candidates.

Remove temporary worktrees, the history clone, and transient graph projects
after report evidence has been captured.
