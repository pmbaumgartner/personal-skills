# Research and Practice Basis

This skill synthesizes general delivery patterns rather than prescribing one case study, model, or orchestration product.

## Large-project delivery

Bent Flyvbjerg and Dan Gardner’s *How Big Things Get Done* supplies the project logic:

- think slowly and act quickly;
- work backward from the desired outcome;
- preserve optionality before commitment;
- take the outside view and use reference classes;
- find repeatable modules—the project’s “Lego”;
- use relevant experience and explicit downside controls;
- execute rapidly after planning removes avoidable uncertainty;
- measure realized benefits rather than ceremonial completion.

## Evolutionary architecture

Martin Fowler’s work contributes evolutionary replacement, explicit seams, continuously releasable systems, modular boundaries, and deterministic feedback around probabilistic agents:

- Strangler Fig Application: https://martinfowler.com/bliki/StranglerFigApplication.html
- Branch by Abstraction: https://martinfowler.com/bliki/BranchByAbstraction.html
- Harness Engineering: https://martinfowler.com/articles/harness-engineering.html
- Pushing AI Autonomy: https://martinfowler.com/articles/pushing-ai-autonomy.html
- The Role of Developer Skills in Agentic Work: https://martinfowler.com/articles/exploring-gen-ai/13-role-of-developer-skills.html

## Contemporary agentic engineering

Thoughtworks’ *Future of Software Engineering in Europe 2026* and related guidance emphasize verification as a central constraint, layered harnesses, behavior preservation before redesign, caution with large swarms, risk-tiered autonomy, and small human control teams focused on intent, architecture, acceptance, and risk.

- Report: https://www.thoughtworks.com/content/dam/thoughtworks/documents/report/tw_future_of_software_engineering_europe_2026.pdf
- Spec-driven development: https://www.thoughtworks.com/en-us/insights/blog/agile-engineering-practices/spec-driven-development-unpacking-2025-new-engineering-practices
- Team of coding agents: https://www.thoughtworks.com/radar/techniques/team-of-coding-agents

## Durable agent coordination

Kata provides the ledger model used by this skill: stable issues, parent and blocking relationships, atomic claims, agent-readable output, durable comments and events, live attention metadata, and evidence-backed closes. It intentionally leaves worktrees, process supervision, branches, and CI to external launchers and harnesses.

- Repository: https://github.com/kenn-io/kata
- Agent workflows: https://github.com/kenn-io/kata/blob/main/docs/workflows/agents.md
- Agent orchestration: https://github.com/kenn-io/kata/blob/main/docs/operations/agent-orchestration.md

## Reference example, not a template

Bun’s Rust rewrite demonstrates unusually favorable agentability: a working reference implementation, behavior-preserving scope, a large independent test suite, mechanical compiler and test queues, an experienced technical owner, separated implementation and review passes, a pilot, and staged merge and release decisions.

Reference: https://bun.com/blog/bun-in-rust

The transferable lesson is not “perform wholesale rewrites.” Large-scale agent execution becomes more viable as work becomes decomposable and wrong answers receive fast, cheap, unambiguous feedback.

## Adaptation rule

Use the principles, not the surface form of an example. Weak tests, hidden integrations, unresolved product intent, irreversible data changes, slow feedback, or an unshared ledger require enablement and incremental seams before substantial concurrency is responsible.

Use one bounded workflow with conditional controls. Preserve outcome-first planning, executable acceptance, representative work, modular packets, outside-view forecasting, continuous integration, progressive release, and benefit realization. Add structure only for a concrete coordination or authority boundary; contextual risk determines authority and safeguards.
