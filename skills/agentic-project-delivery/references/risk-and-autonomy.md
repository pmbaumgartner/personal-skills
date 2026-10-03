# Risk and Autonomy

Load this reference when work touches production, sensitive data, security boundaries, money movement, regulated behavior, destructive operations, or irreversible state.

## Classify the current boundary

Classify the action being authorized now, not the future system it might influence.

A private, sandboxed, reversible experiment can be operationally low risk even when its subject is consequential. Moving the same result into authoritative state, production credentials, public distribution, or user exposure is a new boundary and must be classified again.

Scientific validity and operational delivery risk are different:

- scientific validity asks whether the evidence supports the claim;
- operational risk asks what harm the authorized action can cause.

Require a strong oracle for a consequential claim without inventing production ceremony for an isolated research experiment.

Evaluate consequence, escape likelihood, reversibility, recovery time, affected users and data, available credentials, legal duties, observability, containment, oracle maturity, and available expertise. A small diff can be high risk; a large mechanical change can be lower risk when it is isolated, specified, and reversible.

## Low-risk boundary

Examples include documentation, fixtures, isolated tests, deterministic codemods, private benchmarks, internal refactors behind strong contracts, and reversible dependency maintenance.

Agents may execute within a bounded packet when protected checks pass, sensitive authority is absent, and rollback or discard is immediate.

## Medium-risk boundary

Examples include user-visible behavior, public interfaces, performance-sensitive paths, cross-service changes, or reversible data transformations.

Use a named acceptance owner, evidence beyond the implementer, compatibility and rollback checks, progressive exposure when relevant, and recorded material exceptions. A human authorizes the consequential boundary crossing.

## High-risk boundary

Treat authentication, authorization, cryptography, secrets, sensitive personal data, financial accounting or money movement, destructive data operations, irreversible schema changes, production infrastructure, safety-critical behavior, and regulated decisions as high risk unless strong evidence supports a narrower boundary.

Require as applicable:

- explicit human approval before execution or exposure;
- dual control for irreversible or financially material operations;
- separate implementation and acceptance authority;
- threat modeling and specialist review;
- least-privilege, time-bounded credentials;
- dry runs, backups, recovery rehearsals, and rollback validation;
- bounded canaries or automatic containment;
- immutable audit evidence and incident ownership.

Do not give a general implementation agent raw production shells, unrestricted cloud tools, broad network access, or standing credentials when a narrow schema-defined operation is sufficient.

## Separate authority only where it adds control

Distinguish authority to propose, implement, change protected acceptance, merge, distribute, expose, mutate authoritative state, waive a control, and declare the outcome achieved.

One person may hold several accountabilities for lower-risk work. High consequence or policy may require different people. A separate issue is needed only when the decision blocks several packets, crosses a materially different authority, authorizes a consequential boundary, or policy requires it.

## Reversibility test

Before delegating a consequential action, answer:

1. Can the prior state be reconstructed?
2. Has recovery been exercised?
3. Can partial completion be detected?
4. Can rollback itself cause harm?
5. How long will detection and recovery take?
6. Who can contain the action?

Reduce autonomy when an answer is unclear.

## Progressive exposure

Use only stages that reduce material risk:

1. historical replay or sandbox;
2. shadow or differential execution;
3. internal or low-consequence use;
4. bounded canary;
5. gradual exposure;
6. full exposure with containment retained;
7. retirement of the old path after sufficient evidence.

For stateful systems, separately verify read compatibility, write compatibility, mixed-version operation, backfill, rollback, and partial-migration recovery.

Configure automatic containment where feasible for correctness breaches, permission expansion, unexplained divergence, resource regressions, integrity violations, monitoring loss, or failed recovery. Automatic rollback is not always safe for stateful changes; traffic containment or write suspension may be safer.
