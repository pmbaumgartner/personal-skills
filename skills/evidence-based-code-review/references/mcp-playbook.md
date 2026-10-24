# MCP Playbook

Use this reference when executing an evidence-based review. Tool schemas can evolve; inspect current descriptors if a call is rejected.

## Contents

- [Independent lane discipline](#independent-lane-discipline)
- [Runtime tool syntax](#runtime-tool-syntax)
- [SCC calls](#scc-calls)
- [Index setup and coverage](#index-setup-and-coverage)
- [Architecture and changed-code scope](#architecture-and-changed-code-scope)
- [Query results](#query-results)
- [Symbol complexity and hot-path queries](#symbol-complexity-and-hot-path-queries)
  - [Complexity concentration](#complexity-concentration)
  - [Interface size](#interface-size)
- [Fan-in and fan-out](#fan-in-and-fan-out)
- [Shared-state writers](#shared-state-writers)
- [Duplicate candidates](#duplicate-candidates)
- [Tracing and source evidence](#tracing-and-source-evidence)
  - [Structural dossier](#structural-dossier)
- [Dead-code candidates](#dead-code-candidates)
- [Hidden change coupling](#hidden-change-coupling)
- [Design-concern evidence matrix](#design-concern-evidence-matrix)

## Independent lane discipline

Treat SCC and codebase-memory as complementary discovery lanes, not a serial filter:

1. Establish shared scope, production roots, exclusions, and snapshot caveats.
2. Complete and validate the SCC ranking independently.
3. Complete and validate the graph candidate set and structural hypotheses independently.
4. Only then synthesize the union by design concern or change path, preserving SCC-only, graph-only, overlapping, and contradictory signals.
5. Source-validate a bounded selection that includes material lane-unique candidates; overlap is corroboration, not an admission requirement.

Run the lanes concurrently when practical. If calls must be serial, do not use early results from one lane to narrow, suppress, or rerank the other. Do not combine unlike metrics into a pseudo-precise score.

Use SCC primarily to establish maintenance pressure and exposure. Use graph evidence to establish structural shape, ownership, dependency direction, caller coordination, and blast radius. Neither role vetoes a lane-unique signal.

Use SCC for history evidence: frequency, churn, and co-change. The graph's `FILE_CHANGES_WITH` edges and `File.change_count` come from the same git log, filtered and without rename tracking, so they neither corroborate SCC nor rank candidates. Use the graph to explain history instead: map a diff to symbols with `detect_changes`, and test whether SCC's co-change pairs and hotspots have structural dependencies.

## Runtime tool syntax

Discover the tools, then confirm the exact invocation form with a harmless call such as `list_projects` or a tool descriptor. Record the successful form in the review basis. Do not assume namespacing from the displayed server name. For example, one gateway may accept a flat tool name with a separate server selector:

```text
tool="list_projects", server="codebase-memory-mcp"
tool="analyze", server="scc"
```

Another runtime may expose prefixed names. Use only the form returned and accepted by that runtime; if `server/tool` fails, rediscover rather than guessing.

## SCC calls

Use one explicit history depth. Keep history calls at the repository root, but choose file-analysis paths from the Git/filesystem inventory and graph-coverage reconciliation.

For a small, homogeneous repository with bounded output:

```text
analyze({
  path: "/absolute/repo",
  by_file: true,
  cognitive: true,
  no_min_gen: true,
  sort: "complexity",
  limit: 100
})
```

For a large, polyglot, monorepo, or artifact-heavy repository, an optional compact root summary can establish scale and languages:

```text
analyze({path: "/absolute/repo", by_file: false, cognitive: true, no_min_gen: true})
```

Then analyze the discovered owned categories or components separately; these paths are examples, not conventions:

```text
analyze({path: "/absolute/repo/component-a", by_file: true, cognitive: true, no_min_gen: true, sort: "complexity", limit: 100})
analyze({path: "/absolute/repo/packages/service-b", by_file: true, cognitive: true, no_min_gen: true, sort: "complexity", limit: 100})
```

Always keep history analysis at the repository root:

```text
hotspots({path: "/absolute/repo", depth: 1000, limit: 50})
coupling({path: "/absolute/repo", depth: 1000, limit: 50})
coupling({path: "/absolute/repo", file: "relative/path.ext", depth: 1000, limit: 30})
```

If repo-wide coupling is dominated by data, generated, or lock files, the SCC CLI can weight pairs by file complexity: `scc --coupling-weighted --format json --depth 1000 /absolute/repo`.

Interpretation:

- `analyze` reads the filesystem snapshot, including eligible modified or untracked files; it is not necessarily a HEAD snapshot. History calls cannot rank uncommitted files. Record dirty state and reconcile the inputs.
- With `by_file`, `limit` applies per language and rows are sorted within each language. Always merge owned production rows client-side into one global numeric ranking. Keep separate rankings for tests, benchmarks, migrations, and owned scripts/tooling. Keep fixtures, generated code, and vendored code separate or excluded.
- `hotspots` and `coupling` take no exclusion filters; drop generated, vendored, and fixture rows client-side.
- Capture SCC candidates before consulting graph architecture. After both lanes complete, architecture may help explain component boundaries, but it is never proof that the file inventory is complete.
- File complexity is partly a size signal. Source inspection and post-synthesis symbol evidence can refine it, but lack of graph corroboration does not discard an SCC candidate.
- `hotspots.score` is normalized complexity × commits, not defect probability. Preserve `commits`, `linesChanged`, `codeChurn`, `commentChurn`, `authors`, and the returned date window as context. Code churn distinguishes behavioral accretion from comment-only edits.
- Repo-wide coupling uses symmetric Jaccard-like degree. File-specific coupling reports directional `couple` and `reverse`; a large gap suggests a hub relationship rather than peer coupling.
- Common source↔test and manifest↔lockfile pairs are expected. Unexpected cross-module policy coupling deserves inspection.

SCC's `no_duplicates` option concerns duplicate-file accounting in line counts; it is not a source-clone detector.

## Index setup and coverage

```text
list_projects({include_details: true})
index_repository({
  repo_path: "/absolute/repo",
  name: "stable-project-name",
  mode: "moderate",
  persistence: false
})
index_status({project: "stable-project-name", diagnostics: "summary"})
get_graph_schema({project: "stable-project-name", diagnostics: "full"})
```

`project` accepts the stable name or an absolute directory, which resolves to its owning project. Reuse an index only when its root matches the repository. `index_status.watch` reports whether the index auto-refreshes; only the project an MCP session is rooted in is watched, so an unwatched index is a snapshot as of `indexed_at`. Use `index_repository` when absent, or when the index is unwatched and the repository changed materially since `indexed_at`; for a large repository, pass `async: true` and poll with `status: true`. Before citing files:

```text
check_index_coverage({
  project: "stable-project-name",
  paths: ["src/a.py", "src/b.py"]
})
```

Before saying a bounded area has no cycles, duplicates, callers, dead code, or other matches:

```text
check_index_coverage({project: "stable-project-name", scopes: ["src/domain/"]})
```

To list every flagged gap file under a scope at once, query the coverage-gap graph, which holds only `Project`, `Folder`, and `File` nodes:

```text
query_graph({
  project: "stable-project-name",
  graph: "missed",
  format: "json",
  query: "MATCH (f:File) WHERE f.file_path STARTS WITH 'src/' RETURN f.file_path AS file ORDER BY file ASC"
})
```

Inspect skipped and parse-partial paths directly. `indexed_no_recorded_gap` is still not proof of completeness.

## Architecture and changed-code scope

```text
get_architecture({
  project: "stable-project-name",
  path: "src/",
  aspects: ["overview", "hotspots", "layers", "boundaries", "cycles", "clusters"]
})

detect_changes({
  project: "stable-project-name",
  scope: "impact",
  direction: "inbound",
  depth: 3,
  edge_types: ["CALLS", "USAGE", "CALL_REFERENCE", "READS", "WRITES", "INHERITS", "IMPLEMENTS", "OVERRIDE"],
  seeds: "list",
  seed_filter: "product",
  via: true,
  limit: 200
})
```

`detect_changes` defaults to the repository's default branch; pass `since` when the user gives an exact revision or `base_branch` for another base. Record merge base, changed files, changed product symbols, impacted total, truncation, and direction/depth. `changed_files` is paged separately (20 by default); follow `changed_next_cursor` with `changed_cursor` while `changed_has_more` is true. `via_qn` and `via_edge` show how each impacted symbol is reached; use them to describe blast radius rather than citing only the total.

The walk follows only `CALLS` unless `edge_types` is given, which misses change that spreads through type usage, references, shared state, and inheritance. `edge_types`, `via`, and `fixpoint` require `direction: "inbound"`, and the call rejects edge types the index lacks, so pass only types listed by `get_graph_schema`.

Architecture hotspots rank by fan-in and can include builtins and test utilities. Scope architecture calls to production roots, reconcile returned paths with `index_status`, and filter to owned production symbols before prioritizing. `layers` classifies modules as entry, core, internal, or leaf from fan-in/out; an internal layer whose callers and callees offer the same abstraction is a pass-through candidate. Clusters reveal de-facto seams, not necessarily desired architecture.

## Query results

Request `format: "json"` for every query that will be ranked or merged; it returns `columns`, row arrays, `total`, `truncated`, and `next_cursor`.

- Use Cypher `ORDER BY` with a deterministic tie-break and `LIMIT N`. `max_rows` only bounds visible rows after ordering.
- While `has_more` is true, continue with `next_cursor` and otherwise identical arguments.
- Metric cells are strings. Parse them as numbers and verify the final ranking is monotonically descending.
- Treat a warning, timeout, unexpected shape, unexplained empty result, or results skewed to one label as failure.
- If a gateway summarizes or saves the output, parse the complete saved result; never rank from a preview.
- The Cypher subset rejects arithmetic, `CASE`, and most functions outside aggregation. Return raw columns and compute derived values client-side.

## Symbol complexity and hot-path queries

Check `get_graph_schema` for available properties first. Restrict to production with the repository's roots and `is_test = false`:

```cypher
MATCH (f:Function|Method)
WHERE f.file_path STARTS WITH 'src/'
  AND f.is_test = false
RETURN f.qualified_name AS symbol,
       f.file_path AS file,
       f.start_line AS line,
       f.complexity AS cyclomatic,
       f.cognitive AS cognitive
ORDER BY cognitive DESC, cyclomatic DESC, symbol ASC
LIMIT 20
```

For broader metric collection, return a fixed column order such as `lines`, `loop_count`, `loop_depth`, `transitive_loop_depth`, `linear_scan_in_loop`, `alloc_in_loop`, `recursion_in_loop`, `unguarded_recursion`, `param_count`, and `max_access_depth`, and page with the cursor rather than accepting truncation.

Use this focused query for algorithmic-risk candidates:

```cypher
MATCH (f:Function|Method)
WHERE f.transitive_loop_depth >= 3
   OR f.linear_scan_in_loop >= 1
   OR f.recursion_in_loop >= 1
   OR f.unguarded_recursion = true
RETURN f.qualified_name, f.file_path, f.start_line,
       f.complexity, f.cognitive, f.loop_depth,
       f.transitive_loop_depth, f.linear_scan_in_loop,
       f.alloc_in_loop, f.recursion_in_loop,
       f.unguarded_recursion
```

Validate complexity against source. A high transitive loop depth can be intended numerical work; `alloc_in_loop` often needs workload and allocation-lifetime evidence before it is actionable.

### Complexity concentration

Estimate how much cyclomatic complexity lies in production functions above complexity 10. Run the query once as written and once with `AND f.complexity > 10` added:

```cypher
MATCH (f:Function|Method)
WHERE f.file_path STARTS WITH 'src/'
  AND f.is_test = false
RETURN sum(f.complexity) AS cyclomatic,
       sum(f.lines) AS lines,
       count(f) AS function_count
```

Report `high.cyclomatic / all.cyclomatic`, with the matching line share and function counts, as a repository-level candidate signal, not a quality verdict or composite score. `lines` is source span, including comments and blank lines. Validate the graph coverage of the measured production scope before interpreting the result.

### Interface size

Compare each file's exported symbols with the complexity they hide. Run both queries and join by file client-side:

```cypher
MATCH (f:Function|Method)
WHERE f.file_path STARTS WITH 'src/' AND f.is_test = false
RETURN f.file_path AS file, count(f) AS symbols,
       sum(f.complexity) AS cyclomatic, sum(f.lines) AS lines
ORDER BY cyclomatic DESC, file ASC
LIMIT 50
```

```cypher
MATCH (f:Function|Method)
WHERE f.file_path STARTS WITH 'src/' AND f.is_test = false
  AND f.is_exported = true
RETURN f.file_path AS file, count(f) AS exported
ORDER BY exported DESC, file ASC
LIMIT 50
```

Many exported symbols over little complexity suggests a shallow module; few exports over substantial complexity suggests a deep one. `is_exported` follows each language's convention and can mark every top-level function of a plain script, so confirm the real interface in source. For a leading candidate, `get_file_outline({project: "stable-project-name", file_path: "src/a.py"})` lists every declaration, including variables and classes, in source order with exact paging; page while `has_more` is true.

## Fan-in and fan-out

Run separate queries to avoid accidental Cartesian multiplication:

```cypher
MATCH (caller)-[:CALLS]->(f:Function|Method)
WHERE f.file_path STARTS WITH 'src/'
  AND f.is_test = false AND caller.is_test = false
RETURN f.qualified_name AS symbol, f.file_path AS file,
       f.start_line AS line, count(DISTINCT caller) AS fan_in
ORDER BY fan_in DESC, symbol ASC
LIMIT 50
```

```cypher
MATCH (f:Function|Method)-[:CALLS]->(callee)
WHERE f.file_path STARTS WITH 'src/' AND f.is_test = false
RETURN f.qualified_name AS symbol, f.file_path AS file,
       f.start_line AS line, count(DISTINCT callee) AS fan_out
ORDER BY fan_out DESC, symbol ASC
LIMIT 50
```

These count resolved graph edges, not all runtime calls. Builtins, dynamic dispatch, callbacks, macros, reflection, and FFI can distort the result. Program launches are `SPAWNS` edges to `Process` nodes, not `CALLS`, so fan-out omits them; count them separately when external programs are a boundary crossing.

`Function`, `Method`, and `Class` nodes also carry `importance`, an index-time weighted degree. Use `ORDER BY f.importance DESC` as a quick cross-check of the fan-in ranking. It is precomputed over the whole graph and cannot be scoped to production callers or chosen edge types, so rank from the explicit queries.

## Shared-state writers

Find fields and variables written from several files:

```cypher
MATCH (w:Function|Method)-[:WRITES]->(v)
WHERE w.file_path STARTS WITH 'src/' AND w.is_test = false
RETURN v.qualified_name AS state, v.file_path AS file,
       count(DISTINCT w) AS writers,
       count(DISTINCT w.file_path) AS writer_files
ORDER BY writer_files DESC, writers DESC, state ASC
LIMIT 20
```

State mutated from several files suggests distributed state ownership or caller-managed transitions. Inspect the writers: constructors, builders, and a single owning type writing its own fields are expected; scattered writers that must preserve one invariant are the finding.

## Duplicate candidates

Query graph-generated token-similarity edges:

```cypher
MATCH (a)-[r:SIMILAR_TO]->(b)
WHERE a.file_path STARTS WITH 'src/'
  AND b.file_path STARTS WITH 'src/'
  AND a.is_test = false AND b.is_test = false
RETURN a.qualified_name AS symbol_a, a.file_path AS file_a,
       a.start_line AS line_a, b.qualified_name AS symbol_b,
       b.file_path AS file_b, b.start_line AS line_b,
       r.jaccard AS jaccard, r.same_file AS same_file
ORDER BY jaccard DESC
LIMIT 100
```

`SIMILAR_TO` compares tokens, so it misses the same policy written with different code. Query vocabulary-based `SEMANTICALLY_RELATED` edges as a complementary lane:

```cypher
MATCH (a:Function|Method)-[r:SEMANTICALLY_RELATED]->(b:Function|Method)
WHERE a.file_path STARTS WITH 'src/'
  AND b.file_path STARTS WITH 'src/'
  AND a.is_test = false AND b.is_test = false
RETURN a.qualified_name AS symbol_a, a.file_path AS file_a,
       a.start_line AS line_a, b.qualified_name AS symbol_b,
       b.file_path AS file_b, b.start_line AS line_b,
       r.p AS p, r.score AS score, r.same_file AS same_file
ORDER BY p DESC, score DESC, symbol_a ASC
LIMIT 100
```

`p` is the calibrated probability that a reader would judge the pair related, not that they duplicate behavior. Prefer cross-file pairs, and treat a pair that also has a `SIMILAR_TO` edge as corroborated.

No rows means no indexed similarity edges, not no duplication. Inspect both snippets. Strong evidence of harmful duplication requires shared behavior or policy plus a plausible divergence cost; similar tests or boundary adapters often should remain explicit.

Repeated symbol names can identify parallel implementations worth comparison, but are weaker evidence than `SIMILAR_TO`:

```cypher
MATCH (f:Function|Method)
WHERE f.is_test = false
WITH f.name AS name, count(f) AS definitions
WHERE definitions > 1
RETURN name, definitions
ORDER BY definitions DESC, name ASC
```

Then locate each repeated name with `search_graph`.

## Tracing and source evidence

Discover the exact qualified name before tracing:

```text
search_graph({
  project: "stable-project-name",
  name_pattern: ".*CandidateName.*",
  label: "Function",
  fields: ["complexity", "cognitive", "signature"],
  limit: 50
})

trace_path({
  project: "stable-project-name",
  function_name: "exact.qualified.name",
  direction: "both",
  depth: 3,
  risk_labels: true,
  include_evidence: true,
  include_tests: false,
  limit: 200
})
```

To see what callers must know, trace argument flow into a candidate interface:

```text
trace_path({
  project: "stable-project-name",
  function_name: "exact.qualified.name",
  mode: "data_flow",
  direction: "inbound",
  depth: 1,
  limit: 100
})
```

Each caller row carries the argument expressions passed at the call site. Repeated flags, mode values, setup objects, or derived state across callers is evidence of complexity pushed onto callers.

For blast radius, trace `direction: "inbound"` with the same `edge_types` as `detect_changes`; the default follows calls only.

Follow `has_more` and `next` cursors. Use `get_code_snippet` for exact symbols, then direct file reads when more context is needed or coverage is partial. Treat trace `risk_labels` only as prioritization hints: they are not finding severity, and transitive risk propagation can label harmless accessors, builtins, or wrappers as `CRITICAL` or recursive.

### Structural dossier

For each leading graph hypothesis, capture enough evidence to explain the design concern rather than merely cite a rank:

- the concept and its likely canonical owner
- representative inbound callers and what they must pass, coordinate, or know
- important outbound dependencies and boundary crossings
- policy or state knowledge repeated across symbols
- likely change blast radius
- an existing seam that could contain the knowledge
- index coverage, unresolved dynamic behavior, and other limits

Use the dossier to test a specific hypothesis such as distributed ownership, boundary leakage, shallow layering, or duplicated coordination. Do not infer all fields from one trace, and do not prescribe a new owner before inspecting its contract and representative callers.

## Dead-code candidates

```text
search_graph({
  project: "stable-project-name",
  label: "Function",
  max_degree: 0,
  exclude_entry_points: true,
  limit: 100
})
```

Paginate. Never report dead code from graph isolation alone. Verify exports, framework registration, reflection, plugin hooks, callbacks, FFI, macros, scripts, and direct textual references. `search_code({project: "stable-project-name", pattern: "candidate_name", mode: "files"})` finds textual references in indexed files only; grep the excluded and unindexed paths reported by `index_status` before calling a symbol unreferenced.

## Hidden change coupling

After both lanes complete, check each leading SCC coupling pair for a static dependency in either direction:

```cypher
MATCH (a)-[r]-(b)
WHERE a.file_path = 'src/a.py' AND b.file_path = 'src/b.py'
RETURN type(r) AS edge, count(r) AS n
ORDER BY n DESC, edge ASC
```

`type()` is not allowed in `WHERE`, so filter client-side: count dependency edges such as `CALLS`, `USAGE`, `IMPORTS`, `READS`, `WRITES`, `CALL_REFERENCE`, `INHERITS`, `IMPLEMENTS`, and `OVERRIDE`; ignore containment (`DEFINES*`, `CONTAINS_*`), similarity, documentation links (`MENTIONS`, `REFERENCES_FILE`), and `FILE_CHANGES_WITH`. Confirm both paths with `check_index_coverage` first.

Environment variables, launched programs, and HTTP routes are shared nodes rather than edges between the two files, so check them separately:

```cypher
MATCH (a)-[:CONFIGURES|SPAWNS|HTTP_CALLS]->(x)<-[:CONFIGURES|SPAWNS|HTTP_CALLS]-(b)
WHERE a.file_path = 'src/a.py' AND b.file_path = 'src/b.py'
RETURN labels(x) AS shared_label, x.name AS shared, count(*) AS n
ORDER BY n DESC, shared ASC
```

A shared environment variable or route names the coupling; a shared common program such as `git`, or a `<dynamic>` process, does not.

Repeated co-change with no dependency edge is a hidden-coupling candidate: shared knowledge such as a format, protocol, or invariant that neither file states. Inspect a few co-change commits to name it. A link through a third module, dynamic dispatch, configuration, or a coverage gap explains the pair rather than proving the coupling hidden.

## Design-concern evidence matrix

After both independent lanes complete, maintain a small working table before source validation:

| Design concern / change path | Provenance | SCC pressure | Graph structural hypothesis | Representative symbols | Source verification | Coverage | Structural direction |
|---|---|---|---|---|---|---|---|

`Provenance` is SCC-only, graph-only, both, or discrepancy. Preserve leading lane-unique concerns instead of requiring populated cells from both tools. Treat disagreement as a question to inspect, not a reason to average ranks or discard the concern. Files and symbols support the concern; they are not necessarily its boundary.

The table is an analysis aid. Keep it out of the final report unless the user asks for the full audit trail.
