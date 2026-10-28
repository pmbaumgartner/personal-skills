---
name: evidence-based-code-review
description: Assess repository or change-set design complexity and recommend evidence-backed structural simplifications using independent SCC history/complexity evidence, codebase-memory structural evidence, and focused source inspection. Use for explicitly SCC-backed, graph-backed, hotspot, coupling, duplication, blast-radius, structural-improvement, or A Philosophy of Software Design reviews. Do not use for a full defect hunt or generic PR review.
disable-model-invocation: true
---

# Evidence-Based Design Complexity Review

Use SCC and codebase-memory to find design-complexity candidates, validate them in source, and recommend the smallest structural changes that remove complexity.

## Review philosophy

Complexity is anything that makes software harder to understand or modify.

- Its symptoms are **change amplification**, **cognitive load**, and **unknown unknowns**.
- Its common causes are dependencies and obscurity.
- Complexity matters in proportion to how often developers encounter or change it.
- Metrics find candidates; source inspection establishes design problems.
- SCC measures maintenance pressure: where complexity is costly and repeatedly encountered.
- Codebase-memory models structural shape: how knowledge, dependencies, and change propagate.
- Structural recommendations require both source evidence and inspection of affected callers.
- Tool agreement strengthens a signal but is not required.

Keep the review bounded. Do not use subagents, run broad test suites, or turn it into a general defect hunt unless the user expands the scope.

## Setup

Record repository identity, review scope, dirty state, production roots, exclusions, SCC history window, and graph freshness and coverage.

Confirm SCC exposes `analyze`, `hotspots`, and `coupling`. Call `list_projects` as the first graph operation and reuse a matching fresh index. Both SCC and codebase-memory are required; if either is unavailable, stop and disclose which dependency is missing.

Read [references/mcp-playbook.md](references/mcp-playbook.md) when executing MCP calls. It contains tool syntax, query safeguards, coverage checks, and ranking rules.

## Workflow

### 1. Run independent evidence lanes

Run in parallel when practical. If calls must be serial, do not let one lane narrow, suppress, or rerank the other before both finish.

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

Validate each lane's ordering, completeness, snapshot caveats, and coverage independently. Failed or partial queries are evidence gaps, not negative evidence.

### 2. Synthesize by design concern

After both lanes finish:

- preserve SCC-only, graph-only, overlapping, and contradictory candidates
- group evidence around design concerns or change paths, not files or metrics
- use files and symbols as supporting evidence without forcing unlike signals into one score
- treat overlap as corroboration and disagreement as a question to inspect
- check leading SCC coupling pairs for a static graph dependency; repeated co-change with none is a hidden-coupling candidate
- select up to 4–6 concerns from the union, proportional to scope, including material lane-unique concerns when they survive validation

Examples include distributed policy ownership, caller-managed state transitions, boundary leakage, shallow layer chains, and duplicated coordination. Do not force equal finding counts or manufacture weak lane parity.

### 3. Validate in source

Inspect each concern's formal interface, informal contract, implementation, representative callers, relevant history, and comments or names that define the abstraction.

For a leading graph hypothesis, establish its likely canonical owner, representative inbound and outbound paths, crossed boundaries, repeated caller knowledge including the arguments callers pass, blast radius, useful existing seams, and coverage limits. Read [references/mcp-playbook.md](references/mcp-playbook.md) for the structural dossier.

Ask five questions:

1. **Complexity burden:** How much must developers know, and how often do they pay that cost?
2. **Module depth:** Does a simple interface hide substantial knowledge and implementation complexity?
3. **Complexity direction:** Is complexity handled once below the interface or repeatedly pushed onto callers?
4. **Strategic direction:** Is the design becoming easier to change, or accumulating tactical exceptions?
5. **Simplification counterfactual:** Could a small change to ownership, the state model, or the default flow delete branches, modes, wrappers, or coordination rather than merely relocate them?

Before this stage, read [references/design-lenses.md](references/design-lenses.md) for the detailed *A Philosophy of Software Design* checks and interpretation cautions.

Run a focused reproduction only when an obvious high-impact failure is visible and cheap to check. Otherwise report design risk, not a verified defect.

### 4. Design the structural direction

For each concern that survives validation:

1. Identify the knowledge that should have one canonical owner.
2. Describe the simpler contract callers should see.
3. Look for an ownership, state-model, or default-flow change that deletes branches, modes, wrappers, or coordination.
4. Prefer deepening a sound existing seam over introducing a new abstraction.
5. Inspect affected callers and state the likely blast radius.
6. Propose the smallest safe first step and how to verify it.

For a non-trivial direction, briefly compare at most two plausible shapes. Recommend no redesign when the evidence does not justify one.

### 5. Report and stop

Stop after the leading signals and material discrepancies from both lanes have been explained or rejected. Do not manufacture findings.

## Structural moves

Report only source-validated observations. Lead each actionable concern with the recommended direction, then include:

- **Complexity symptom:** change amplification, cognitive load, or unknown unknowns
- **Structural change:** the ownership, interface, state-model, or default-flow change
- **Complexity removed:** the concepts, branches, wrappers, or coordination that disappear
- **Existing leverage:** the sound seam or abstraction to preserve or deepen
- **Scope:** representative affected callers and likely blast radius
- **First step:** the smallest safe implementation step and verification
- **Evidence:** provenance, tool signal, `path:line` observations, and confidence

## Report shape

Keep the response concise:

1. **Recommended direction:** overall structural opportunity in 2–4 bullets.
2. **Structural moves:** at most three, ordered by leverage.
3. **Strengths to preserve or deepen:** existing modules, contracts, or seams that already contain complexity well.
4. **Concerns without a justified remedy:** validated burdens where evidence does not support a responsible redesign.
5. **Rejected signals:** misleading or contradictory evidence worth noting.
6. **Evidence basis:** compact SCC and graph basis, repository identity, scope, dirty state, history window, coverage, and exclusions.

If no concern survives validation, say so and list the leading candidates from each lane to inspect next.
