# Source Reconciliation Runbook

## Status

Governance runbook  
Operational source-coherence procedure  
Non-authority documentation layer

## Purpose

This runbook defines how Sharpe Nova OS handles source conflicts across local repo state, origin/main, GitHub connectors, agent reports, Architect-provided output, and CCO-reconciled state.

The goal is to distinguish source freshness issues from doctrine failures.

A stale connector is not automatically a boundary failure.

A local-ahead repo is not automatically drift.

A source-incomplete run is not automatically wrong.

Source conflicts should be classified, confirmed, reconciled, and preserved.

---

## Canonical Boundary

Agent prepares action.  
Nova structures review context.  
Local authority decides.  
Nova does not execute.

Source reconciliation must preserve this boundary.

No source conflict should be resolved by expanding Nova into approval, denial, authorization, blocking, routing, settlement, payment execution, treasury management, compliance review, audit reporting, trading, portfolio optimization, or agent-control language.

---

## Source Types

Use the following source categories.

```yaml
source_types:
  local_repo:
    meaning: canonical local working tree available to the Architect
  origin_main:
    meaning: pushed GitHub remote branch state
  connector_visible_state:
    meaning: state visible to GitHub or other connectors during an agent run
  agent_memory:
    meaning: prior agent reports or stored summaries
  architect_provided_output:
    meaning: terminal output or file state provided directly by the Architect
  cco_reconciled_state:
    meaning: state accepted or corrected by Jarvis-Nova CCO after reviewing conflicts
```

---

## Conflict Types

Classify source conflicts before recommending action.

```yaml
conflict_types:
  stale_connector_artifact:
    meaning: connector-visible state appears behind current local, origin, or CCO-reconciled state

  local_ahead_of_origin:
    meaning: local commits exist but have not yet been pushed to origin/main

  origin_ahead_of_local:
    meaning: origin/main contains commits not present locally

  source_incomplete_run:
    meaning: an agent did not have access to one or more necessary sources

  architect_provided_unverified:
    meaning: the Architect supplied output that connectors could not independently verify during the run

  true_boundary_drift:
    meaning: current confirmed local or origin head contains unqualified authority-adjacent language or capability claims

  doctrine_failure:
    meaning: confirmed current repo state contradicts the canonical boundary or materially expands Nova's role
```

Do not classify a conflict as doctrine failure unless current confirmed source state supports it.

---

## Standard Source Conflict Closure Packet

When source conflict appears, the Architect should run this from the canonical repo:

```bash
cd /Users/komeokiomah/nova-api/sharpe-nova-os

git status -sb
git branch --show-current
git rev-parse --short HEAD
git log --oneline --decorate -n 10

grep -RInE "admissibility|allow|allows|approve|denies|authorize|block|permit|routes|settles|executes" START_HERE.md docs/start-here.md README.md docs/governance
```

If `rg` is available, `rg -n` may be used instead of `grep -RInE`.

---

## Interpretation Rules

Use the following rules.

```yaml
if_local_head_equals_origin_main:
  sync_state: synced

if_local_head_ahead_of_origin:
  sync_state: local_ahead_of_origin
  action: verify_boundary_scan_then_push_or_mark_intentionally_unpushed

if_origin_ahead_of_local:
  sync_state: origin_ahead_of_local
  action: pull_or_inspect_origin_changes_before_editing

if_connector_visible_head_behind_origin_or_local:
  sync_state: connector_stale
  action: classify_as_stale_connector_artifact

if_boundary_scan_hits_only_negative_cautionary_or_legacy_contexts:
  boundary_status: acceptable

if_boundary_scan_finds_unqualified_authority_language_in_current_public_surface:
  boundary_status: active_surface_risk
  action: correct_before_push_or_public_use

if_agent_report_conflicts_with_architect_provided_local_output:
  action: prefer_current_local_output_for local_state while preserving agent_report_as_source_incomplete
```

---

## Push Discipline

After every committed documentation, governance, content-engine, proof, or public-surface update, check whether local and origin are aligned.

Run:

```bash
git status -sb
git log --oneline --decorate -n 5
```

If local is ahead of origin, either push or explicitly record why the commit remains local.

```yaml
push_status:
  state: pushed | intentionally_unpushed | pending_push
  reason:
  expected_follow_up:
```

Unpushed local commits should not be treated as public remote evidence.

---

## Agent Escalation Rules

Agents should escalate source conflicts to CCO when:

* connector-visible public surfaces contain authority-adjacent language that conflicts with current CCO-known state
* local and origin head cannot be confirmed
* a current confirmed public surface contains unqualified approval, denial, authorization, blocking, routing, settlement, execution, payment, compliance, audit, trading, or portfolio-optimization language
* a source conflict affects NSF, grant, public repo, proof-chain, or content-publication claims
* source-incomplete runs repeat without reconciliation

Agents should not repeatedly escalate the same stale connector artifact after CCO reconciliation unless:

* the stale state persists after a confirmed push and refresh interval
* current origin/main still contains the risky language
* a new file introduces unqualified authority language
* the stale state affects a publication or grant submission decision

---

## Chronology Requirement

Every resolved source conflict should create or update a chronology entry.

Minimum entry:

```yaml
event_type: source_reconciliation
date:
layer_affected:
  - repo
  - governance
  - chronology
summary:
source_classification:
boundary_state:
decision_impact:
repo_action:
chronology_action:
```

Source reconciliation entries should preserve both:

* what the agent or connector saw during the run
* what the Architect or CCO later confirmed

This prevents false conflict and false cleanliness.

---

## What Source Reconciliation Does Not Mean

Source reconciliation does not prove:

* production readiness
* market validation
* buyer validation
* adoption
* institutional deployment
* execution authority
* payment capability
* compliance approval
* audit completion

It only resolves what state was visible, confirmed, stale, missing, pushed, or reconciled.

---

## Correct Compression

```text
Detect the conflict.
Classify the sources.
Confirm local and remote state.
Separate sync issues from doctrine issues.
Correct only if current surfaces require correction.
Push when clean.
Preserve the reconciliation.
```

---

## Final Principle

Source reconciliation protects coherence.

It should make Nova easier to verify without making Nova sound broader, more operational, or more authoritative than it is.

The goal is source clarity before interpretation.
