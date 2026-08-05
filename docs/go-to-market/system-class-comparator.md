# Sharpe Nova OS — System-Class Comparator

## Purpose

Sharpe Nova OS does not claim to have invented pre-execution review.

Financial institutions already use policy engines, pre-trade controls,
compliance systems, approval workflows, audit logs, case-management systems,
wallet controls, and transaction-risk systems.

Nova’s differentiation is a hypothesis about a residual review-context gap.

The hypothesis must be tested against operator workflows and existing systems.

| System class | Primary function | Commonly preserved | Potential residual gap to test | Nova’s proposed role | Evidence status |
| --- | --- | --- | --- | --- | --- |
| Pre-trade or transaction control | Enforce limits or restrictions | Checks, thresholds, outcomes | Cross-system proposal history and review reconstruction may be fragmented | Preserve version-specific review context | hypothesis |
| Policy engine | Evaluate rules | Rule inputs and policy results | Evidence and authority context may remain distributed | Assemble governed review state around the proposal | hypothesis |
| Compliance gate | Screen actions or entities | Screening results, cases, alerts | Full proposal evolution and constraint context may not remain connected | Bind relevant results to the exact proposal version | hypothesis |
| Approval workflow | Route approval decisions | Approvers, timestamps, dispositions | Supporting evidence and assumptions may be stored elsewhere | Preserve what local authority actually reviewed | hypothesis |
| Audit or event log | Record system events | Actions, timestamps, mutations | The reason a proposal became reviewable may not be reconstructable | Preserve review-state lineage before execution | hypothesis |
| Wallet policy or signing control | Restrict signing and transaction authority | Permissions, signatures, policy checks | Institutional review context may precede and span multiple tools | Remain outside signing while structuring review context | hypothesis |
| Agent framework | Prepare plans and invoke tools | Agent messages, tool calls, execution traces | Institutional authority and source state may not be preserved as institution-owned review context | Separate agent preparation from local authority | hypothesis |
| Case-management system | Manage investigations or exceptions | Cases, assignments, notes | Pre-action proposal identity and replayable context may not be native | Package pre-action context for local review | hypothesis |

## Proposed Nova differentiation

Nova is testing whether institutions need a provider-neutral, institution-owned
record of:

- stable action identity across revisions;
- separately preserved proposal versions;
- review context bound to the exact version considered;
- source authority and observation time;
- constraint state;
- local-authority boundaries;
- correction and supersession lineage;
- reconstructable pre-execution chronology.

## Claim boundary

The comparator does not establish that existing systems lack these capabilities.

It identifies questions for operator discovery and bounded comparative testing.

No moat, buyer demand, workflow dependency, pricing power, or product-market fit
is established by this document.
