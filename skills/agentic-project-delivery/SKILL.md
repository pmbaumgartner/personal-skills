---
name: agentic-project-delivery
description: Plan, coordinate, assess, or release staged agent-led software delivery when integration, acceptance, or release risk requires bounded work packets and progressive delivery. Not for ordinary bugs, routine reviews, or reversible changes handled by normal repository workflow.
disable-model-invocation: true
---

# Agentic Project Delivery

## Mission

Turn a staged engineering outcome into verified, modular, progressively delivered work without hiding uncertainty or transferring unacceptable risk to users or operations.

> Think slowly. Let agents act quickly. Integrate continuously. Release progressively.

Optimize for accepted, production-worthy outcomes—not generated code, agent count, commits, issue count, or apparent activity.

## First decide whether APD is needed

Use APD only when delivery coordination is a material part of the problem.

Exit to the repository's normal workflow when all are true:

- one repository or component and one accountable maintainer;
- no more than three initially independent work packets;
- one ordinary acceptance command can verify the outcome;
- changes are readily reversible;
- no coordinated release, production exposure, or cross-owner authority boundary exists.

Do not invoke APD merely because work uses agents, tests, benchmarks, research, or several implementation sessions. When uncertain, choose the normal workflow. A pull-request count does not determine applicability.

For advisory requests, assess or plan without mutating the repository or ledger. For implementation, initialize only the durable coordination that the work actually needs.

## Use one bounded workflow

Apply this workflow once at the highest governing outcome. Do not instantiate the complete workflow again inside every child feature, experiment, or research priority. A child becomes a new APD effort only when it has its own beneficiaries, authority boundary, multi-packet coordination problem, or release path; technical complexity alone is insufficient.

### Ceremony budget

Default to:

- one outcome issue;
- zero to three initially open implementation packets;
- zero standalone gate issues;
- zero standalone audit issues;
- zero standalone pilot or enablement issues;
- one durable acceptance record and one durable result record;
- one human authorization for the bounded implementation or pilot, plus a later release or exposure decision when applicable.

The acceptance and result records normally live in the outcome body, one linked contract, an outcome comment, or close evidence; they do not require separate files or issues.

Record ordinary enablement, pilot findings, and intermediate decisions as comments on the outcome issue. Add packets just in time. Exceed a default only when the extra issue or artifact creates a named control that a comment, executable check, or existing packet cannot provide; record that reason when creating it.

### One durable record per fact

- If a durable contract exists, keep the issue body to a short scope and link.
- If the contract fits in the issue, do not create duplicate Markdown.
- Create JSON only when executable tooling consumes it.
- Prefer generated human summaries over independently maintained machine and prose records.
- Record frozen identities and hashes once in a manifest; link it elsewhere.
- Do not repeat status, ownership, dependencies, acceptance, or disposition across issue bodies, comments, reports, and decision documents.
- Treat rendered sites, screenshots, caches, build directories, and reproducible intermediates as disposable unless the contract or repository requires retention.

## Use Kata only for durable coordination

When the repository is already bound to Kata and the work spans sessions or workers, use it as the primary work ledger. Do not initialize Kata solely for an advisory request or a one-session task that should use the normal workflow.

Before durable work:

1. Run `kata version --json`.
2. Run `kata quickstart` and `kata list --agent` in a bound workspace.
3. If durable setup was requested and the workspace is unbound, run `kata init --with-agents`; inspect `kata init --help` when project selection or hooks matter.
4. Give each concurrently active worker lane a stable actor identity. Reuse it across packets; create a distinct auditor identity only when a separate audit is warranted.
5. Confirm that workers share the intended project and database before concurrency.
6. Because Kata is pre-1.0, inspect `kata <command> --help` before automating flags.

Kata is canonical for issue identity, status, ownership, priority, relationships, comments, events, and close evidence. The repository owns code, tests, architecture records, and long-lived specifications; CI and runtime systems own observed verification. Do not create or maintain a parallel Markdown, chat, spreadsheet, or GitHub-issue ledger for the same work.

If Kata is unavailable, continue in advisory mode or surface the required installation and initialization step. Do not silently invent a replacement ledger.

Load [references/kata-ledger.md](references/kata-ledger.md) before initializing, executing, coordinating, auditing, or closing durable Kata work.

## Begin with evidence

Inspect the current repository, executable checks, design records, issue history, integration behavior, release path, and current Kata ledger before making material claims.

Prefer:

1. protected executable acceptance and explicit contracts;
2. reproducible production or benchmark observations;
3. authoritative architecture and product decisions;
4. current implementation and integration behavior;
5. documentation and ledger comments;
6. agent inference.

Expose conflicts rather than choosing the interpretation that makes execution easiest.

## 1. Frame the outcome

Define the beneficiary-visible improvement independently of the proposed implementation. Record:

- baseline, target, and decision horizon;
- constraints, non-goals, and frozen scope;
- plausible alternatives and the do-nothing counterfactual;
- central assumptions to test;
- downside limits, stop conditions, and rollback expectations;
- technical, acceptance, and release-risk accountability.

Use [assets/project-charter.md](assets/project-charter.md) for a durable outcome issue when its fields add control. Label the root `apd:outcome` plus the repository's normal workflow label. Keep it open until the promised outcome or a justified stop disposition is verified—not merely until code exists.

## 2. Assess agentability and build the executable definition of done

Assess target clarity, oracle strength, feedback speed, environment reproducibility, reversibility, seams, coupling, blast radius, sensitive authority, and relevant human expertise.

Choose one:

- **Ready:** a representative slice is reversible and has a credible oracle.
- **Enable first:** a required test, seam, fixture, observability signal, or environment control is missing.
- **Not suitable now:** intent is unresolved, materially wrong behavior cannot be observed, recovery is not credible, or no authorized owner can define acceptance.

Keep small enablement inside the outcome issue. Create a child only when the work is independently executable, needs its own owner, or blocks multiple packets.

Freeze the smallest acceptance contract that can reject materially wrong behavior:

- candidate decision and failure modes;
- sensors and known coverage gaps;
- frozen inputs, baselines, and provenance;
- hard gates, comparative gates, and diagnostics;
- one reproducible command with nonzero rejection semantics;
- representative known-good and deliberately broken controls;
- protected files, thresholds, and change authority;
- repeatability, runtime, and resource bounds.

Use [assets/acceptance-contract.md](assets/acceptance-contract.md) once, either embedded or linked. Load [references/oracle-construction.md](references/oracle-construction.md) when the oracle is missing, weak, new, or materially changing. Implementation agents cannot weaken protected checks, inputs, or thresholds or approve their own exceptions.

Scientific uncertainty and operational delivery risk are different. A private reversible experiment may need a rigorous protected oracle while remaining operationally low risk.

## 3. Choose the three topologies and bounded packets

Decide, without automatically creating separate issues:

- **Transformation:** incremental change, mechanical translation, dependency upgrade, strangler replacement, branch by abstraction, dual implementation, or another approach.
- **Integration:** how accepted changes remain continuously buildable.
- **Release:** how distribution or exposure grows and how rollback, containment, yanking, or replacement works.

Separate behavior preservation, architecture change, and new behavior when combining them would weaken acceptance or rollback.

Create one issue only for one independently completable work packet. Use [assets/work-packet.md](assets/work-packet.md) when a short body is insufficient. A packet needs an observable objective, allowed and frozen scope, exact acceptance, material risk, escalation boundary, deliverables, and rollback or discard path.

Search before creating, use structural `blocked-by` relationships for real ordering, and claim work atomically. Do not encode the workflow as an `apd:gate`, `apd:pilot`, `apd:audit`, and `apd:enablement` label sequence.

Prefer deterministic scripts, codemods, compilers, or schema tools when they are sufficient. Use agents where contextual judgment is genuinely needed.

## 4. Build the harness and run a representative pilot

Put fast deterministic sensors inside the correction loop. Add probabilistic review as another sensor, not as a replacement for executable checks. Constrain credentials, dependencies, resources, and production authority according to risk.

Use one representative implementation packet as the pilot. It must include ordinary work and the characteristic difficulty—not only the easiest slice. Record its result as a compact outcome comment rather than a separate pilot issue.

Call work an APD delivery pilot only when it records:

- elapsed time from ready to integrated;
- accepted, rejected, retried, and discarded work;
- first-pass versus repaired outcome;
- human attention and decision-waiting time;
- defects caught by each verification layer;
- the scale, reshape, enable, or stop decision.

Otherwise call it an implementation packet or product experiment. Do not scale merely from code-generation speed. Load [references/evaluation-and-forecasting.md](references/evaluation-and-forecasting.md) when designing the pilot, forecasting, or deciding whether to increase concurrency.

## 5. Execute and integrate

For each packet:

1. Select ready, unowned work and claim it with `kata claim`.
2. Set truthful `work.attention`; use the stable lane identity.
3. Read only the governing outcome, acceptance, source, and relevant dependencies.
4. Reproduce the baseline, implement the smallest coherent change, and run fast checks.
5. Run broader integration checks and risk-appropriate review.
6. Close promptly with substantive typed evidence using `kata close`, or keep it open with what remains.

One active working-agent side owns an issue. Use structural `--blocked-by` links for sequencing and attention metadata only for live state.

When verification or integration is the bottleneck, cap or reduce implementation launches and first reassign existing capacity to the constraint. Do not increase total agent count during the initial diagnosis and enablement pilot, and do not add agents merely because generated-work demand exists. Test any specialized capacity increase as a separate bounded pilot.

Convert recurring failure classes into stronger guides, sensors, tools, or packet boundaries rather than repeatedly patching symptoms.

## 6. Release progressively and realize benefits

Keep transformation, integration, and release decisions distinct even when one issue records them.

- **Merge:** commit to maintaining the integrated change.
- **Deploy or distribute:** make an artifact available in a production-capable or user-installable form.
- **Expose or adopt:** let real users or authoritative workloads depend on it.

Use only the release stages that materially reduce risk. Preserve rollback, containment, yanking, or compatible replacement until evidence is sufficient.

After adoption, compare realized outcomes with the baseline, simplify transitional boundaries, remove temporary systems, and feed escaped defects into the harness. Create separate decommissioning or benefit issues only when they are independently executable or materially block closure.

## Add controls only when triggered

### Separate gate issue

Create one only when the decision:

- blocks at least two independently executable packets;
- belongs to a materially different person or authority;
- authorizes production, public exposure, irreversible mutation, or another consequential boundary; or
- must be a distinct record under policy.

Otherwise record the decision as an attributable comment on the governing outcome issue.

### Separate completion audit

Use ordinary evidence-backed close for routine reversible work. Create a separate audit only for high-risk work, a material oracle change, a milestone or release claim, a hard-to-observe outcome that authorizes consequential work, or suspicious and conflicting evidence. Audit the assembled outcome and risk-sample supporting packets.

A fresh agent session provides reviewer separation and provenance, not independent organizational authority.

### Contextual risk

Classify the action at its current boundary, not by what a successful result might later influence. Load [references/risk-and-autonomy.md](references/risk-and-autonomy.md) for production, sensitive data, security, money movement, regulated behavior, destructive operations, irreversible state, or other high-impact authority.

### When this workflow is insufficient

Stop and design a task-specific delivery system when several independent human authorities, coordinated repositories or organizations, irreversible production mutation, regulated approval, or coupled release trains create a genuine program-control problem.

Do not automatically expand the ledger into a generic larger workflow. Present the coordination problem, existing controls, missing controls, and smallest tailored addition required. Load [references/scaling-controls.md](references/scaling-controls.md) for that assessment.

## Human control plane

Keep three accountabilities conceptually explicit; one person may fill all three unless risk or policy requires separation:

- technical design, topology, and exceptions;
- acceptance and protected-oracle authority;
- release, exposure, and residual-risk authority.

Apply deliberately:

- **Accountability separation:** distinguish the decisions even when one person owns them.
- **Personnel separation:** require different people only when consequence or policy warrants it.
- **Temporal separation:** a solo maintainer defines and freezes the oracle before implementation and treats later changes as a separate decision.
- **Tool separation:** implementation agents cannot modify protected acceptance material without explicit authorization.

One human authorization may cover the contract, harness, visible checks, and one bounded protected run when all are frozen together. Ask again only when scope, acceptance, budget, irreversible authority, supported behavior, or release exposure changes.

## Stop or escalate

Stop or reduce scope when:

- the oracle is missing, compromised, or weakened without authority;
- behavior preservation, architecture change, and new features become entangled;
- generation outpaces verification or integration;
- a change is irreversible and recovery has not been exercised;
- human attention, retries, cost, or defect escape invalidate the pilot economics;
- evidence and summaries disagree;
- workers do not share an attributable ledger;
- no authorized person owns the next consequential boundary.

## Default advisory output

Cover only applicable items:

1. whether APD is warranted;
2. the outcome, boundaries, counterfactual, and owner;
3. agentability and the executable acceptance command;
4. the smallest just-in-time issue graph;
5. triggered risk, audit, release, or recovery controls;
6. the next reversible action.

Distinguish observed facts, inferences, assumptions, and decisions. Do not create artifacts for an advisory answer unless the user requests them.

## Supporting resources

- [references/kata-ledger.md](references/kata-ledger.md): durable Kata operations, evidence, identity, retention, and audit.
- [references/oracle-construction.md](references/oracle-construction.md): build or repair an acceptance oracle.
- [references/evaluation-and-forecasting.md](references/evaluation-and-forecasting.md): pilot economics, bottlenecks, and forecasting.
- [references/risk-and-autonomy.md](references/risk-and-autonomy.md): high-impact authority, recovery, and exposure.
- [references/scaling-controls.md](references/scaling-controls.md): tailor controls when the bounded workflow is insufficient.
- [references/research-basis.md](references/research-basis.md): explain or adapt the conceptual basis.
- [assets/project-charter.md](assets/project-charter.md): compact durable outcome record.
- [assets/acceptance-contract.md](assets/acceptance-contract.md): compact executable oracle record.
- [assets/work-packet.md](assets/work-packet.md): compact packet body.

After modifying this package, run `python3 scripts/validate_skill.py` from the skill directory and:

```sh
uv run --with pyyaml python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py .
```
