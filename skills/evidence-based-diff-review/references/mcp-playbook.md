# Evidence-Based Diff Review MCP Playbook

Use these recipes for a bounded change review. Inspect current tool descriptors
when a call is rejected; schemas can evolve.

## Contents

- [Snapshot and patch](#snapshot-and-patch)
- [SCC file ranking](#scc-file-ranking)
- [Tool-call recovery](#tool-call-recovery)
- [Head graph setup](#head-graph-setup)
- [Hunk-scoped symbols](#hunk-scoped-symbols)
- [Exposure, duplication, and coverage](#exposure-duplication-and-coverage)
- [Source validation](#source-validation)

## Snapshot and patch

For routine setup, prefer the deterministic helper:

```bash
python3 <skill-dir>/scripts/prepare_review.py \
  /repo <base-expression> <head-expression> \
  --output /tmp/review
```

It resolves both SHAs, creates the two worktrees and self-contained history
clone, captures both patches and Git summaries, and emits ranges plus hunk
classifications. It does not call MCP tools or classify repository ownership.
Use the manual commands below when setup needs to differ.

Resolve exact revisions before collecting metrics:

```bash
BASE=$(git -C /repo rev-parse <base-expression>)
HEAD_SHA=$(git -C /repo rev-parse <head-expression>)
```

Create two detached worktrees:

```bash
git -C /repo worktree add --detach /tmp/review/base "$BASE"
git -C /repo worktree add --detach /tmp/review/head "$HEAD_SHA"
```

Create a self-contained detached clone for SCC history queries:

```bash
git clone --no-local --no-checkout /repo /tmp/review/head-history
git -C /tmp/review/head-history checkout --detach "$HEAD_SHA"
```

Do not use a linked worktree or `git clone --shared` for SCC `hotspots` or
`coupling`. SCC's Git walker may not resolve linked-worktree metadata or object
alternates even when ordinary Git commands do.

Capture the authoritative patch and derived ranges:

```bash
git -C /tmp/review/head diff --find-renames \
  "$BASE".."$HEAD_SHA" > /tmp/review/change.patch
git -C /tmp/review/head diff --find-renames --unified=0 \
  "$BASE".."$HEAD_SHA" > /tmp/review/change.hunks.patch
python3 <skill-dir>/scripts/changed_ranges.py \
  /tmp/review/change.hunks.patch > /tmp/review/change.ranges.json
python3 <skill-dir>/scripts/classify_hunks.py \
  /tmp/review/change.hunks.patch \
  --base-root /tmp/review/base \
  --head-root /tmp/review/head \
  > /tmp/review/change.hunk-kinds.json
```

Record `git diff --shortstat` and `--name-status --find-renames`. The JSON range
map is derived evidence; the full patch remains authoritative. Its summary and
per-file `old_changed_lines`/`new_changed_lines` fields support deletion-aware
scope decisions.

Classify paths before applying the large-change guardrail. Calculate review
load from owned production files only:

- modified: old changed lines + new changed lines;
- added: new changed lines;
- renamed with edited hunks: old changed lines + new changed lines;
- deleted and rename-only: zero for the split threshold, while supported
  boundary removals still receive source review;
- tests, generated/vendor code, fixtures, docs, migrations, examples,
  benchmarks, verification tooling, and feature-gated research: separate
  buckets, not production review load.

Prefer splitting above 25 production files or 10,000 review-load lines. A
coherent aggregate may remain preferable when raw churn is mostly deletion or
relocation, or when one verified identifier/API rename accounts for the broad
file count and the surviving behavioral change is bounded. Verify a mechanical
rename by checking the replacement pattern across its changed files and
inspecting every `structural` hunk reported by `classify_hunks.py`.
`formatting_only`, `comment_only`, `import_only`, `identifier_only`,
`string_only`, and `lexical_only` are attention labels, not safety claims.
Record the numbers and rationale.

## SCC file ranking

Confirm SCC exposes `analyze`, `hotspots`, and `coupling`.

Analyze changed production files directly. Batch independent calls, but retain
one result per path:

```text
analyze({
  path: "/tmp/review/base/src/a.py",
  by_file: true,
  cognitive: true
})

analyze({
  path: "/tmp/review/head/src/a.py",
  by_file: true,
  cognitive: true
})
```

For a rename, use its old path in base and new path in head. Additions have no
base call; deletions have no head call. Missing sides remain unknown.

Whole-root analysis is an optional optimization only for a small repository
whose response is known to remain bounded. If a response is omitted because it
exceeds the MCP result limit, use its `fullResultPath` when available or switch
to direct file calls. Do not repeatedly request the same oversized result or
calculate deltas from independently truncated rankings.

Run bounded maintenance-history evidence from the detached history clone.
Choose `limit = max(100, min(1000, 5 × changed production files))`:

```text
hotspots({
  path: "/tmp/review/head-history",
  depth: 200,
  limit: <scaled-limit>
})
```

Filter all SCC results to paths in the captured diff. Preserve:

- cyclomatic and cognitive complexity before and after;
- lines and language;
- hotspot score, commits, lines changed, authors, and date window.

Record the requested limit and number of returned files. A changed path absent
from the response is `unknown—not returned`, not a zero-score hotspot. Do not
silently order unknown history below observed low scores. If the response is
omitted for size, read its `fullResultPath`; do not reduce the limit merely to
fit conversational output.

`hotspots.score` is normalized complexity × commit frequency, not defect
probability. A large file metric can mostly reflect size. Source must explain
the burden.

Use Git rename mappings when joining paths. For additions and deletions, leave
the absent side unknown. Do not infer a move from matching metrics or names.

Sort attention lexicographically rather than creating a score:

1. descending positive cognitive delta;
2. descending positive cyclomatic delta;
3. descending observed changed-file hotspot pressure;
4. descending head cognitive complexity;
5. descending removed complexity for strengths.

Keep paths absent from the hotspot response in an explicit unknown-history
bucket. They are not comparable to observed hotspot scores; inspect high
absolute-complexity unknowns when the observed set does not explain the change.

When a leading multi-file change suggests coordination or ownership spread,
make one focused history query:

```text
coupling({
  path: "/tmp/review/head-history",
  file: "relative/path.ext",
  depth: 200,
  limit: 20
})
```

Common source/test and manifest/lockfile coupling is expected. Treat coupling
as change-amplification context, not proof that files should be merged.

For deterministic joining, save the direct SCC JSON responses or their MCP
result files and run:

```bash
python3 <skill-dir>/scripts/rank_changed_files.py \
  /tmp/review/change.ranges.json \
  --base-root /tmp/review/base \
  --head-root /tmp/review/head \
  --base-analysis /tmp/review/scc/base/*.json \
  --head-analysis /tmp/review/scc/head/*.json \
  --hotspots /tmp/review/hotspots.json \
  --hunk-kinds /tmp/review/change.hunk-kinds.json \
  > /tmp/review/attention.json
```

The script performs path normalization, rename-aware joining, marks hotspot
history as observed or unknown, attaches hunk-kind counts, and applies the
specified lexicographic ranking. It intentionally does not decide which files
are production, research, generated, or tests.

`rank_changed_files.py` accepts direct SCC reports, common `ok/data/content`
MCP envelopes, and arrays or objects containing batched `base`, `head`,
`result`, or `results` payloads. Save the complete response verbatim when
possible. If the MCP gateway returns `fullResultPath`, pass that file directly;
do not hand-copy individual metric fields.

## Tool-call recovery

Inspect current descriptors before the first SCC and graph calls when schemas
are not already known.

- An argument or query-syntax rejection is not an availability failure. Correct
  the call from the descriptor and retry it once.
- For a transport, connection, or server-unavailable failure, reconnect once
  and retry once.
- Do not reconnect for a validation error.
- If a corrected required call still fails, stop and disclose which evidence
  could not be collected. If the availability retry fails, disclose the
  missing dependency instead of silently dropping that evidence source.

## Head graph setup

Call Codebase Memory `list_projects({include_details:true})` as the first graph
operation. Then create one moderate head index:

```text
index_repository({
  repo_path: "/tmp/review/head",
  name: "<repo>-diff-head-<sha7>",
  mode: "moderate",
  persistence: false
})
```

Reuse only an index rooted at this pinned head worktree whose
`index_status({verbose:true})` reports the exact `head_sha`, `status:"ready"`,
and a complete generation.

Run change impact:

```text
detect_changes({
  project: "<repo>-diff-head-<sha7>",
  scope: "impact",
  direction: "inbound",
  depth: 2,
  since: "<full-base-sha>",
  limit: 200,
  format: "json"
})
```

Verify `base` and `merge_base` equal the requested base. Record changed files,
seed symbols, impacted total/modules, and truncation. A mismatch invalidates
the review scope.

The raw seed count includes deleted and relocated symbols. If it exceeds 300,
do not split automatically. Count surviving hunk-intersecting `Function` and
`Method` nodes in the classified production paths. Reconsider grouping only
when that count also exceeds 300 or more than 25 production files survive.
Otherwise retain the aggregate and record the inflation source.

For this preliminary breadth check, generate a predicate for every surviving
production path and run count-only queries:

```cypher
MATCH (f:Function)
WHERE <generated predicate>
  AND (f.is_test = false OR f.is_test IS NULL)
RETURN count(f) AS hunk_functions
```

Repeat for `Method`. This all-production count is only a scope decision; the
detailed metric query below remains limited to the five leading files.

Call `get_graph_schema({project:"<repo>-diff-head-<sha7>"})` before relying on
labels, metrics, or edge types.

## Hunk-scoped symbols

Generate explicit predicates only for the leading SCC-ranked production files.
Use the helper rather than manually transcribing ranges:

```bash
python3 <skill-dir>/scripts/ranges_to_cypher.py \
  /tmp/review/change.ranges.json \
  --path src/a.py --path src/b.rs \
  > /tmp/review/hunk-predicate.cypher
```

Add `--deletion-anchors` only when the patch context confirms the old code was
inside a surviving symbol. The helper deliberately does not make that claim.
The current query engine does not reliably support `any(...)` list predicates;
the generated output has this form:

```cypher
(
  (f.file_path = 'src/a.py' AND f.start_line <= 42 AND f.end_line >= 35)
  OR
  (f.file_path = 'src/b.rs' AND f.start_line <= 91 AND f.end_line >= 91)
)
```

Query `Function`, `Method`, `Class`, and `Variable` separately when those labels
exist in `get_graph_schema`. Functions and methods describe behavior; classes
and variables capture renamed public types, module aliases, constants, and
other module-scope API changes.

For `Function` and `Method`:

```cypher
MATCH (f:Function)
WHERE (
    (f.file_path = 'src/a.py' AND f.start_line <= 42 AND f.end_line >= 35)
    OR
    (f.file_path = 'src/b.rs' AND f.start_line <= 91 AND f.end_line >= 91)
  )
  AND (f.is_test = false OR f.is_test IS NULL)
RETURN f.qualified_name AS symbol,
       f.name AS name,
       f.file_path AS file,
       f.start_line AS line,
       f.end_line AS end_line,
       f.lines AS lines,
       f.complexity AS cyclomatic,
       f.cognitive AS cognitive,
       f.param_count AS params,
       f.max_access_depth AS access_depth,
       f.loop_count AS loops,
       f.loop_depth AS loop_depth,
       f.transitive_loop_depth AS transitive_loop_depth,
       f.linear_scan_in_loop AS scan_in_loop,
       f.alloc_in_loop AS alloc_in_loop,
       f.recursion_in_loop AS recursion_in_loop,
       f.unguarded_recursion AS unguarded_recursion,
       f.is_exported AS exported,
       f.parent_class AS parent
ORDER BY file, line, symbol
LIMIT 200
```

Repeat for `Method`. For `Class`, request the shared span, export, line, and
complexity properties:

```cypher
MATCH (f:Class)
WHERE <generated predicate>
RETURN f.qualified_name AS symbol,
       f.name AS name,
       f.file_path AS file,
       f.start_line AS line,
       f.end_line AS end_line,
       f.lines AS lines,
       f.complexity AS cyclomatic,
       f.is_exported AS exported
ORDER BY file, line, symbol
LIMIT 200
```

For `Variable`, request the shared identity/span/export properties and inspect
the source assignment because graph metrics do not describe alias semantics.
Split batches that reach the limit. Request structured JSON when the runtime
accepts `format:"json"`; otherwise validate the fixed-column text table before
parsing it.

Prefer the smallest symbol containing a changed range. Avoid counting an outer
function and nested declarations as separate complexity when the extractor
aggregates them.

Join each symbol back to `change.hunk-kinds.json`. Rank `structural` hunks
before lexical/import/comment-only intersections. High symbol complexity does
not make a comment or identifier substitution complex. For module-scope hunks
that intersect no graph symbol, inspect the source directly and report the
module-level API or wiring change rather than dropping it.

Deletion anchors require special handling. Use the base old range and patch
context to verify that deleted code was inside the surviving symbol. An anchor
equal to an adjacent function's start or end line is not enough.

Default attention cues—not findings or gates—are:

- cognitive complexity at least 15;
- cyclomatic complexity at least 10;
- at least 80 lines;
- at least 6 parameters;
- maximum access depth at least 4;
- transitive loop depth at least 3;
- a linear scan or recursion inside a loop;
- unguarded recursion.

Missing metric values are unknown. Some Rust methods report `lines:0`; do not
present that as a zero-length method. Source visibility overrides
`is_exported`.

## Exposure, duplication, and coverage

Use separate direct-degree queries to avoid Cartesian multiplication and
ambiguous `UNION` column names:

```cypher
MATCH (caller)-[:CALLS]->(f:Function)
WHERE f.qualified_name IN ['exact.qn']
RETURN f.qualified_name AS symbol, count(DISTINCT caller) AS fan_in
```

```cypher
MATCH (f:Function)-[:CALLS]->(callee)
WHERE f.qualified_name IN ['exact.qn']
RETURN f.qualified_name AS symbol, count(DISTINCT callee) AS fan_out
```

Run these as separate calls; do not combine them with `UNION`. Repeat for
methods as needed. These counts include resolved static edges only.
Use `trace_path` at depth 2 for representative callers after a concern survives
source inspection. Keep `risk_labels:false` by default; reachability labels are
not defect severity.

Run duplication only for a concrete hypothesis:

```cypher
MATCH (a)-[r:SIMILAR_TO]->(b)
WHERE (a.file_path IN ['src/a.py'] OR b.file_path IN ['src/a.py'])
  AND (a.is_test = false OR a.is_test IS NULL)
  AND (b.is_test = false OR b.is_test IS NULL)
RETURN a.qualified_name AS symbol_a,
       a.file_path AS file_a,
       a.start_line AS line_a,
       a.end_line AS end_line_a,
       b.qualified_name AS symbol_b,
       b.file_path AS file_b,
       b.start_line AS line_b,
       b.end_line AS end_line_b,
       r.jaccard AS jaccard
ORDER BY jaccard DESC
LIMIT 20
```

Post-filter so a hunk intersects at least one endpoint. Inspect both endpoints.
Report only shared behavior or policy with credible divergence cost. No rows
means no indexed candidate, not no duplication.

After candidates are known, make one coverage call:

```text
check_index_coverage({
  project: "<repo>-diff-head-<sha7>",
  paths: ["src/a.py", "src/b.rs"]
})
```

Read exact flagged parse ranges directly. `no_recorded_issue` remains a
best-effort signal, not proof of completeness.

## Source validation

When a graph query returns an exact qualified name, call
`get_code_snippet` directly. Use `search_graph` only to resolve ambiguity.

Validate that the source contains the expected signature. If the snippet is
omitted, unavailable, truncated around the wrong function, or disagrees with
the pinned SHA, read the recorded line span from the pinned worktree.

Inspect representative callers before recommending an interface or ownership
change. The patch must show that the concern was introduced or extended;
otherwise retain it as attention context.

Read the base worktree directly when before-source context matters. For a
possible non-Git relocation, require the same signature and exact normalized
body before calling it relocated. Obtain old and new symbol spans and
signatures from graph/AST evidence, save a candidate manifest, then run:

```bash
python3 <skill-dir>/scripts/verify_relocations.py \
  /tmp/review/relocation-candidates.json \
  --base-root /tmp/review/base \
  --head-root /tmp/review/head \
  > /tmp/review/relocations.json
```

The manifest is a JSON array (or `{ "candidates": [...] }`) with
`old_path`, `new_path`, `old_start`, `old_end`, `new_start`, `new_end`,
`old_signature`, and `new_signature`. The helper is intentionally
conservative: only equal trimmed signatures and exact bodies after line-ending,
edge-blank-line, and trailing-whitespace normalization pass. Exclude verified
moved bodies from implementation-burden attribution, but inspect changed
wrappers, exports, module wiring, and ownership separately.

Useful interpretations:

- **SCC delta:** where file-level implementation burden changed.
- **Hotspot:** how often maintainers have historically paid that burden.
- **Head symbol metrics:** which changed implementation inside the file
  deserves inspection.
- **Fan-in/out:** exposure and coordination context, not defects.
- **Blast radius:** verification scope, not severity.
- **Duplication:** actionable only when policy can diverge.

Prefer a small change that deletes a branch, repeated policy, invalid state, or
caller obligation. Do not recommend extraction that merely moves complexity.

After evidence capture, remove the detached worktrees and history clone and
delete any transient graph project. When setup used `prepare_review.py`, remove
the filesystem artifacts with:

```bash
python3 <skill-dir>/scripts/cleanup_review.py /tmp/review
```

The cleanup helper only removes directories carrying its own manifest. Delete
the transient graph project separately before running it.
