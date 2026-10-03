# Scaling Controls

Load this reference only when the bounded workflow cannot safely govern the delivery boundary.

There is no larger default workflow. Keep one outcome and add the smallest control that addresses a named coordination or authority failure.

## Test whether the workflow is actually insufficient

Do not escalate for code volume, technical difficulty, agent count, pull-request count, or a long backlog alone.

Escalation is warranted when one or more of these boundaries cannot be represented safely by the normal outcome and packet structure:

- several independent human authorities must approve different consequences;
- repositories, organizations, or release trains have coupled schedules or incompatible ledgers;
- production mutation is irreversible or recovery requires coordinated operators;
- policy or regulation requires durable separation, evidence, or approval;
- one acceptance oracle cannot govern materially different systems or beneficiaries;
- integration capacity, environment access, or release ownership is shared across competing outcomes.

## Tailor one control at a time

| Observed problem | Smallest likely addition |
|---|---|
| One decision blocks several packets | One decision issue owned by its authority |
| Several outcomes compete for one integration queue | One shared queue owner and explicit work-in-progress limit |
| Repositories must release together | One cross-repository integration contract and release checkpoint |
| Authorities must remain independent | Separate named actors and protected approval boundaries |
| Recovery needs several operators | One rehearsed runbook with explicit command authority |
| Acceptance differs by system | Separate protected oracle contracts linked to the same outcome |
| Policy requires traceable approval | The minimum mandated durable approval record |

Prefer an existing organizational control when it already solves the problem. Do not reproduce portfolio, incident, security, or compliance systems inside Kata.

## Preserve the ceremony budget

- Keep implementation packets just in time.
- Keep ordinary decisions as outcome comments.
- Keep one durable record per fact.
- Create no generic sequence of enablement, pilot, gate, audit, and release issues.
- Do not instantiate this skill recursively for each workstream.
- Keep derived dashboards and reports disposable unless a consumer or policy requires retention.

## Escalation output

Before adding structure, state:

1. the exact boundary the bounded workflow cannot govern;
2. the consequence if it remains uncontrolled;
3. the existing control and why it is insufficient;
4. the smallest additional owner, record, check, or relationship needed;
5. the trigger for removing that addition.

If these cannot be stated concretely, retain the bounded workflow.
