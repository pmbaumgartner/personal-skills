---
name: evidence-based-design-review
description: Assess design complexity in a repository or change set and recommend evidence-backed structural simplifications, using independent SCC history/complexity evidence and codebase-memory structural evidence validated in source. Use for SCC-backed, graph-backed, hotspot, coupling, duplication, blast-radius, structural-improvement, or A Philosophy of Software Design reviews. Do not use for a full defect hunt or generic PR review.
disable-model-invocation: true
---

# Evidence-Based Design Review

Use SCC and codebase-memory to find design-complexity candidates, validate them in source, and recommend the smallest structural changes that remove complexity.

## Principles

- Metrics and graph signals find candidates; only source inspection establishes a design problem. Weight a problem by how often developers encounter or change it.
- SCC measures maintenance pressure: where complexity is costly and repeatedly touched. Codebase-memory models structural shape: how knowledge, dependencies, and change propagate.
- Keep the two evidence lanes independent until both finish. Neither lane narrows, suppresses, or reranks the other. Agreement corroborates a signal but is not required; a lane-unique signal can stand on its own.
- Keep the review bounded. Do not use subagents, run broad test suites, or turn it into a general defect hunt unless the user expands the scope.

## Setup

Run the collector first, before any separate checks. It verifies the tools and index itself, and its header records repository identity, dirty state, SCC history window, and graph freshness and coverage. Choose the production roots and exclusions from one look at the repository layout.

The collector gathers both lanes' standard evidence in one step:

```bash
uv run --script <skill-dir>/scripts/collect.py REPO --root PREFIX [--root PREFIX ...] [--exclude REGEX] [--base REV] [--json FILE]
```

Pass the production roots (for example `--root src/`), and `--base` for a diff. The collector needs the `scc` and `codebase-memory-mcp` commands and an existing index; it finds the project, falls back to a clone when SCC cannot open the checkout, and prints ranked SCC files, hotspots, co-change pairs with whether a graph edge links them, commit breadth, a component edge matrix for judging edge quality, and the graph's complexity, interface, shared-state, and similarity rankings. `--json` keeps the raw data for follow-up. If a required tool or index is missing, stop and say which.

Read [references/playbook.md](references/playbook.md) only when you need a call the collector does not make (tracing, architecture layers, dependency cones, policy scatter, `detect_changes`), when only MCP servers are available, or when the collector fails.

### Reviewing a diff

For a commit, branch, or pull request, the findings are scoped to the change, but the evidence keeps repository context:

- History stays repository-wide; history limited to the changed files loses their co-change partners. Ask whether the change lands in, deepens, or relieves an existing hotspot. With `--base`, the collector lists each complex changed file's usual co-change partners missing from the diff: a strong one is a candidate for missed change amplification or hidden coupling.
- Use `detect_changes` against the base to map changed files to changed symbols and their inbound impact. Focus the graph lane on changed symbols, their callers, and the concepts they own or touch.
- Ask whether the change adds or removes a mode, flag, special case, caller obligation, or cross-module dependency.
- Report pre-existing problems only where the change makes them worse or where the diff is the natural place for a first step.
- History cannot rank uncommitted work. For a dirty tree, say which files history does not cover.

## Workflow

### 1. Run independent evidence lanes

The collector's output holds both lanes. Read each lane's sections on their own terms before combining them.

**SCC lane**

Use file analysis, history hotspots, and change coupling to find:

- concentrated implementation complexity
- complexity weighted by change frequency
- repeated co-change and possible change amplification
- tactical accretion or knowledge scattered across files

**Codebase-memory lane**

Use architecture layers, symbol metrics, interface size, fan-in/out, cycles, similarity, and change traces to find:

- central interfaces and dependency concentration
- complexity concentration in a small share of production functions
- shallow modules whose exported surface rivals their hidden complexity
- oversized transitive dependency cones where a lightweight caller pulls in a heavy runtime subgraph
- hidden call paths, boundary crossings, and blast radius
- state written from several modules, or policy/constant symbols read across sibling modules to assemble parallel lookup tables
- pass-through layers or adjacent layers with similar abstractions
- duplicated policy, algorithmic risk, and structural unknown unknowns

Turn leading graph signals into structural hypotheses about ownership, caller knowledge, boundaries, or change propagation rather than merely ranking symbols.

Validate each lane's ordering, completeness, snapshot caveats, and coverage on its own terms. Failed or partial queries are evidence gaps, not negative evidence.

### 2. Synthesize by design concern

After both lanes finish:

- group evidence around design concerns or change paths, not files or metrics; files and symbols support a concern but need not be its boundary
- record each concern's provenance: SCC-only, graph-only, both, or contradictory
- keep unlike signals separate rather than combining them into one score; treat disagreement as a question to inspect
- check leading SCC coupling pairs for a static graph dependency; repeated co-change with none is a hidden-coupling candidate
- rank the concerns by leverage and take the top 2–3 into source validation, including a material lane-unique concern if one ranks there; the rest get one line each in the report, stated from the collector output and source already read, without further reading

Examples include distributed policy ownership, caller-managed state transitions, boundary leakage, shallow layer chains, and duplicated coordination. Do not force equal finding counts or manufacture weak lane parity.

A working table per concern (provenance, SCC pressure, graph hypothesis, representative symbols, source verification, coverage, direction) helps keep this straight. Leave it out of the final report unless the user asks for the audit trail.

### 3. Validate in source

Read [references/design-lenses.md](references/design-lenses.md) first; it holds the detailed *A Philosophy of Software Design* checks and interpretation cautions.

Spend source reading on the selected concerns only. Before reading, list every file and line range a concern needs (interface, implementation, representative callers, relevant history) and read them in one step; follow up only on what that read raises. Stop once the five questions below can be answered. Inspect each concern's formal interface, informal contract, implementation, representative callers, relevant history, and the comments or names that define the abstraction.

For a leading graph hypothesis, assemble a structural dossier: the likely canonical owner, representative inbound callers and the arguments they pass, important outbound dependencies and boundary crossings, policy or state knowledge repeated across symbols, blast radius, an existing seam that could contain the knowledge, and coverage limits or unresolved dynamic behavior. Build it from several traces and source reads, not one. The playbook's tracing section has the calls.

Ask five questions:

1. **Complexity burden:** How much must developers know, and how often do they pay that cost?
2. **Module depth:** Does a simple interface hide substantial knowledge and implementation complexity?
3. **Complexity direction:** Is complexity handled once below the interface or repeatedly pushed onto callers?
4. **Strategic direction:** Is the design becoming easier to change, or accumulating tactical exceptions?
5. **Simplification counterfactual:** Could a small change to ownership, the state model, or the default flow delete branches, modes, wrappers, or coordination rather than merely relocate them?

Run a focused reproduction only when an obvious high-impact failure is visible and cheap to check. Otherwise report design risk, not a verified defect.

### 4. Design the structural direction

For each concern that survives validation, work out the fields listed under [Structural moves](#structural-moves). Prefer deepening a sound existing seam over introducing a new abstraction, and prefer a change that deletes branches, modes, wrappers, or coordination over one that relocates them. Do not propose a new owner before inspecting its contract and representative callers.

For a non-trivial direction, compare two plausible shapes by module depth, information hiding, special-case reduction, consistency, and total cognitive load. Recommend no redesign when the evidence does not justify one.

### 5. Report and stop

Stop after the leading signals and material discrepancies from both lanes have been explained or rejected. Do not manufacture findings.

Before sending, recheck each count and `path:line` in the report against this session's command output, and confirm every structural move has each field below (say when evidence for one is missing). When two numbers describe related things, say what each counts.

## Structural moves

Report only source-validated observations. Lead each actionable concern with the recommended direction, then include:

- **Complexity symptom:** change amplification, cognitive load, or unknown unknowns
- **Structural change:** the ownership, interface, state-model, or default-flow change, and the knowledge it gives one canonical owner
- **Target contract:** what ordinary callers need to know afterward
- **Complexity removed:** what the proposed shape actually deletes: concepts, branches, wrappers, or coordination. A difference that history, comments, or tests mark as deliberate is behavior to keep, not complexity; say how the new shape keeps it
- **Existing leverage:** the sound seam or abstraction to preserve or deepen
- **Scope:** representative affected callers and likely blast radius
- **First step:** the smallest independently useful step and how to verify it
- **Evidence:** provenance, tool signal, `path:line` observations, and confidence

## Report shape

Keep the whole report under about 700 words. Give each structural move one short line per field, gathering `path:line` citations in Evidence, and give each item in the other sections one line.

1. **Recommended direction:** overall structural opportunity in 2–4 bullets.
2. **Structural moves:** at most three, ordered by leverage.
3. **Strengths to preserve or deepen:** existing modules, contracts, or seams that already contain complexity well.
4. **Concerns without a justified remedy:** burdens the evidence shows where it does not support a responsible redesign.
5. **Rejected signals:** misleading or contradictory evidence worth noting.
6. **Evidence basis:** SCC and graph invocation forms, repository identity, scope (and base revision for a diff), dirty state, history window, coverage, and exclusions.

If no concern survives validation, say so and list the leading candidates from each lane to inspect next.
