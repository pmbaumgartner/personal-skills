# Engineering details

Read only the section relevant to the decision. These are ways to judge total difficulty, not mandatory architecture or process.

## Locality and abstraction

Judge a boundary by what it hides and what the caller must understand, not by file counts or ceremonial separation. A narrow interface can contain necessary complexity; layers that merely forward calls can scatter one task without containing anything.

Let prototypes reveal stable patterns before generalizing, while allowing a concrete uncertain decision to justify a boundary early. Similar-looking code need not represent shared knowledge. Consolidate when the behavior must change together and the abstraction makes that relationship clearer, rather than introducing callbacks, flags, or an object model to eliminate obvious duplication.

## Representations and caller ergonomics

Use data structures, language idioms, built-ins, and the standard library when they make the model clear. Prefer simple data over unnecessary class hierarchies. Types should help discoverability, comprehension, and correctness; elaborate generics must earn the difficulty they add.

Use the problem's vocabulary in names. Keep boundary names descriptive and unpack dense expressions into named intermediate steps. Shorter code is not necessarily simpler code.

Design APIs around the caller's task. Give common operations a direct path with sensible defaults, and expose advanced capabilities when needed. Do not conceal consequential choices merely to shorten a call.

## Incremental change and verification

Investigate what existing structure protects; tests can explain its purpose without obliging you to preserve it forever. Prefer small, completed refactors that leave the system working over broad rewrites unsupported by evidence.

During exploration, avoid freezing an uncertain domain behind premature test scaffolding. Once behavior firms up, verify current observable contracts and safety properties. Reproduce observed bugs through supported behavior before fixing them when practical.

Choose tests for confidence and diagnosability. Stable logic can merit unit tests; real interactions often merit integration tests. Avoid assertions tied to incidental implementation details and unnecessary mocks; when mocking is needed, prefer coarse system boundaries. Keep end-to-end coverage focused on critical journeys and reliably passing.

## Operational boundaries

Introduce concurrency when the task needs it, accounting for shared mutable state, ordering, and coordination. Independent jobs or stateless handlers can simplify some workloads, but a queue does not automatically remove those costs. For retried effects, use [Handle external or retried effects](techniques.md#handle-external-or-retried-effects).

A service boundary must justify network calls, partial failure, deployment, and observability. Judge distributed designs and fashionable stacks by actual needs and maintenance costs, not novelty or doctrine. Leave a working system alone when the proposed change does not earn those costs.

Process cannot substitute for prototypes, effective tools, and capable people. Add coordination practices where they resolve a concrete difficulty rather than treating ceremony as a cure-all.
