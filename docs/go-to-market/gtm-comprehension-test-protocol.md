# GTM Comprehension Test Protocol

## Status

Go-to-market operating artifact  
Reviewer-facing comprehension test  
Non-authority documentation layer

## Purpose

This protocol helps test whether institutional readers understand Sharpe Nova OS's integration path.

The integration path is:

```text
Nova is called after an action is prepared and before local authority decides.
```

The purpose of this protocol is not to prove buyer validation, market validation, production readiness, deployment, willingness to pay, or external dependency.

The purpose is to test comprehension.

---

## Canonical Boundary

Agent prepares action.  
Nova structures review context.  
Local authority decides.  
Nova does not execute.

Every comprehension test must preserve this boundary.

---

## What This Protocol Tests

This protocol tests whether a serious reader can answer five questions:

```text
1. Where does Nova sit?
2. What does Nova return?
3. Who reads the output?
4. What decision does Nova support?
5. What does Nova not do?
```

If a reader cannot answer these questions clearly, the GTM language is not yet clear enough.

---

## Desired Reader Understanding

A reader should understand:

```text
Nova sits after action preparation and before local authority decision.
```

A reader should understand:

```text
Nova returns governed review context.
```

A reader should understand:

```text
The review-context packet is read by local authority or authorized institutional reviewers.
```

A reader should understand:

```text
Nova supports review before local decision.
```

A reader should understand:

```text
Nova does not approve, deny, authorize, block, route, settle, sign, execute, manage wallets, perform treasury management, perform compliance review, perform audit reporting, optimize portfolios, trade, or replace local authority.
```

---

## Reader Prompt

Use the following prompt when testing comprehension:

```text
After reading the Nova integration-path explanation, please answer five questions in your own words:

1. Where does Nova sit in the workflow?
2. What does Nova return?
3. Who reads Nova's output?
4. What decision does Nova support?
5. What does Nova not do?
```

Do not coach the reader before they answer.

The point is to test whether the material is clear without additional explanation.

---

## Source Material for Test

Use one or more of the following GTM documents as the source material:

* Where Nova Sits
* First Use Case: Agent-Prepared Treasury Action
* Institution-Owned Governance Chronology
* Governance-Context Rot
* Chronology Preservation Standard

Preferred first test source:

```text
docs/go-to-market/where-nova-sits.md
```

Preferred second test source:

```text
docs/go-to-market/first-use-case-agent-prepared-treasury-action.md
```

---

## Scoring Rubric

Use this rubric after the reader answers.

```yaml
comprehension_score:
  5_clear:
    description: Reader understands placement, output, reviewer, supported decision, and non-role without major correction.

  4_mostly_clear:
    description: Reader understands the core placement and non-execution boundary but needs minor correction.

  3_partial:
    description: Reader understands Nova is pre-action context but confuses one important boundary, such as approval, compliance, or integration with execution systems.

  2_confused:
    description: Reader treats Nova as an approval system, compliance workflow, audit product, wallet layer, payment-permission layer, agent supervisor, or execution checkpoint.

  1_failed:
    description: Reader cannot explain where Nova sits or what Nova returns.
```

Target score before using language externally:

```text
4 or higher
```

If repeated readers score below 4, revise GTM language before increasing public distribution.

---

## Required Answer Elements

A strong reader answer should include these elements.

### Placement

```text
After action preparation and before local authority decision.
```

### Output

```text
Governed review context or review-context packet.
```

### Reader

```text
Local authority or authorized institutional reviewers.
```

### Supported Decision

```text
Whether and how local authority proceeds through systems outside Nova.
```

### Non-Role

```text
Nova does not approve, deny, authorize, block, route, settle, sign, execute, manage wallets, perform compliance review, perform audit reporting, or replace local authority.
```

---

## Failure Modes to Track

Track these misunderstandings.

```yaml
failure_modes:
  approval_confusion:
    description: Reader thinks Nova approves or denies actions.

  execution_confusion:
    description: Reader thinks Nova blocks, routes, settles, signs, executes, or moves capital.

  wallet_or_rail_confusion:
    description: Reader thinks Nova plugs directly into wallets, rails, custodians, or settlement systems as a control layer.

  compliance_or_audit_confusion:
    description: Reader thinks Nova is a compliance system or audit product.

  treasury_software_confusion:
    description: Reader thinks Nova is a treasury management system.

  agent_supervisor_confusion:
    description: Reader thinks Nova controls, supervises, or governs agents directly.

  abstraction_failure:
    description: Reader understands Nova is not execution but cannot explain what Nova returns.

  buyer_value_failure:
    description: Reader understands the boundary but cannot explain why review context matters.
```

---

## Comprehension Test Log Format

Use the following format after each test.

```yaml
gtm_comprehension_test:
  date:
  reader_type:
  source_material:
  score:
  understood:
    placement:
    output:
    reader:
    supported_decision:
    non_role:
  confusion_detected:
    -
  direct_reader_language:
    -
  cco_interpretation:
  recommended_language_adjustment:
  follow_up_required:
```

Do not include confidential reader-identifying information unless the institution has explicitly approved it for internal preservation.

---

## Reader Types

Use broad reader types only.

Examples:

```text
allocator
treasury_operator
digital_asset_operator
fund_operations
risk_governance
institutional_reader
technical_operator
nontechnical_institutional_reader
```

Do not overfit the test to one reader profile too early.

---

## Minimum Test Set

Before treating the integration-path language as externally legible, test at least:

```yaml
minimum_test_set:
  readers: 3
  preferred_mix:
    - one institutional finance reader
    - one technical/operator reader
    - one nontechnical strategic reader
  target_score: 4_or_higher
```

If all three readers understand where Nova sits and what Nova does not do, the language is usable for broader content testing.

If two or more readers confuse Nova with approval, execution, compliance, audit, payment authorization, wallet control, or treasury management, revise the GTM documents.

---

## Acceptable Feedback

Useful feedback includes:

* "I understand where Nova sits."
* "I understand this is not execution."
* "I understand the review-context packet."
* "I understand why chronology matters."
* "I understand why this is before local authority acts."
* "I can see how this fits before a treasury action."
* "I still do not know who calls Nova."
* "I still do not know what the packet looks like."
* "This sounds like compliance."
* "This sounds like approval."
* "This sounds like a wallet control layer."

All confusion should be treated as signal.

---

## What Not to Claim From Testing

Comprehension testing does not prove:

* buyer validation
* market validation
* product-market fit
* willingness to pay
* institutional adoption
* production readiness
* deployment readiness
* external dependency
* procurement readiness

It only tests whether the explanation is understood.

---

## Language Revision Rule

If readers repeatedly confuse Nova with execution or approval, strengthen this line:

```text
Execution happens outside Nova.
```

If readers repeatedly confuse Nova with compliance or audit, strengthen this line:

```text
Nova structures review context; it does not perform compliance review or audit reporting.
```

If readers repeatedly fail to understand what Nova returns, strengthen this line:

```text
Nova returns a governed review-context packet.
```

If readers repeatedly fail to understand where Nova sits, strengthen this line:

```text
Nova is called after an action is prepared and before local authority decides.
```

---

## Escalation Triggers

Escalate to CCO if:

* repeated readers classify Nova as approval infrastructure
* repeated readers classify Nova as execution infrastructure
* repeated readers classify Nova as compliance or audit software
* repeated readers classify Nova as treasury management software
* repeated readers cannot explain what Nova returns
* repeated readers understand the role but cannot explain why it matters
* content language creates confusion across multiple reader types

---

## Optional Advanced Question - Review-Context Capacity Gap

This question should be used only after the reader understands the basic Nova boundary.

### Question

In agentic financial workflows, what happens when actions can be prepared faster than institutions can assemble governed review context?

### Strong Answer

The institution needs pre-execution review-context infrastructure before local authority decides.

The prepared action may exist, and the rail may be capable of movement, but local authority still needs governed context around source state, classification, proof evidence, chronology, and authority boundaries.

### Weak or Confused Answers

- The agent should execute automatically.
- Nova should approve or block the action.
- The payment rail should handle governance.
- The custodian should own the decision record.
- The API should decide based on Reflex Memory.
- The review step can be skipped if the action is formatted correctly.

### What This Tests

This question tests whether the reader sees the distinction between:

- action preparation
- movement capacity
- governed review context
- local authority
- execution

It also tests whether the reader understands that Nova's value is not execution, approval, or payment control.

Nova structures review context before local authority acts.

Execution happens elsewhere.

---

## Final Compression

```text
The integration path is documented.

The next task is comprehension.

A serious reader should be able to say:

Nova is called after an action is prepared and before local authority decides.

Nova returns governed review context.

Local authority decides.

Execution happens outside Nova.
```
