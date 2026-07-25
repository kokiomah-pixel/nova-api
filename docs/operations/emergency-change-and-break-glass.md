# Emergency Change and Break-Glass

## Purpose

This runbook permits the Architect to contain an active production exposure when
normal pull-request timing would create material risk. It does not authorize
product expansion, settlement activation, commercial changes, or unrelated
remediation.

Jarvis-Nova may identify the emergency, recommend containment, preserve bounded
evidence, and conduct coherence review. Jarvis-Nova does not own credentials or
exercise independent production authority.

## Canonical Boundary

```text
Agent prepares action.
Nova structures review context.
Local authority decides.
External systems execute.
Nova does not execute.
```

## Emergency Triggers

```yaml
emergency_triggers:
  - OpenAPI_or_docs_return_200
  - services_manifest_returns_200
  - x402_feed_returns_402
  - payment_or_wallet_metadata_reappears
  - unauthenticated_v1_returns_domain_response
  - deployed_commit_is_unrecognized
  - successful_unexpected_settlement_occurs
  - production_secret_is_exposed
  - public_route_bypasses_expected_authentication
```

An uncertain signal may justify immediate read-only verification. Break-glass
execution begins only when an active exposure exists or delay would create
material risk.

## Immediate Action

1. Suspend or contain the affected public surface.
2. Preserve bounded evidence.
3. Do not broaden the remediation.
4. Identify the deployed commit.
5. Identify effective environment flags.
6. Verify authentication behavior.
7. Rotate credentials only when compromise or uncertain custody warrants it.
8. Run external route verification.
9. Create a private incident receipt.
10. Return for CCO classification.

Service suspension is the safe fallback when the deployed source, containment
configuration, or credential custody cannot be established. Do not restore an
older exposed deployment merely to recover availability.

## Break-Glass Rules

```yaml
break_glass:
  Architect_may_bypass_normal_PR_flow: true

  only_when:
    - active_exposure_exists
    - immediate_containment_is_required
    - normal_PR_timing_creates_material_risk

  required_after_action:
    - exact_change_recorded
    - reason_recorded
    - pre_and_post_behavior_recorded
    - credentials_not_disclosed
    - retrospective_PR_or_documentation_created
    - CCO_review_completed
```

Administrator bypass is not a standing production workflow. It is limited to
the smallest reversible containment action that addresses the observed risk.

## Evidence Boundary

The private incident receipt may contain:

- UTC timestamps;
- service and deployment identifiers;
- commit SHAs;
- environment-variable names and effective non-secret states;
- bounded response status, header names, and redacted body classification;
- credential rotation occurrence without values;
- provider event counts;
- rollback or suspension status.

It must not contain:

- secret or API-key values;
- key prefixes;
- payment signatures;
- private keys;
- wallet addresses;
- request or action payloads;
- IP addresses;
- personal identifiers;
- unredacted provider account data.

## Decision Sequence

```yaml
emergency_sequence:
  detect:
    evidence_source:
    observed_at_UTC:
    trigger:

  classify:
    active_exposure:
    material_risk:
    affected_surface:
    change_class:

  authorize:
    Architect_authorization:
    normal_PR_delay_is_material:

  contain:
    action:
    executed_by:
    executed_at_UTC:

  verify:
    deployed_commit:
    effective_flags:
    authentication_behavior:
    external_routes:
    settlement_activity:

  reconcile:
    private_receipt:
    retrospective_PR:
    CCO_review:
    remaining_unknowns: []
```

## Credential Rotation Standard

Rotate credentials when compromise is confirmed, exposure is plausible, custody
is unknown, or the Architect cannot establish who controls the credential.
Rotation is not a substitute for containment: public discovery, payment
challenge, or unauthenticated domain behavior must still be disabled.

Record only:

- credential class;
- provider;
- rotation or revocation status;
- responsible owner;
- UTC completion time;
- dependent service revalidation status.

## Restoration Gate

Restore or retain service availability only when:

```yaml
restore_gate:
  deployed_commit_identified: true
  containment_flags_verified: true
  public_discovery_disabled: true
  public_x402_disabled: true
  settlement_disabled: true
  authentication_boundary_verified: true
  external_route_check_passed: true
```

If any required fact remains unknown, keep the affected surface contained or the
service suspended.

## Post-Event Requirements

Within the retrospective record:

1. identify the trigger and evidence;
2. record the exact bounded action;
3. distinguish verified facts from unknown history;
4. document pre- and post-action behavior;
5. state whether credentials were rotated without exposing them;
6. identify any runtime or configuration divergence from `main`;
7. create the smallest retrospective PR or documentation update;
8. obtain CCO classification;
9. update readiness and incident status;
10. reopen the incident if containment later regresses.
