# Nova API Observability Boundary

## Purpose

CCO assessments must distinguish three API evidence surfaces. None may be
silently substituted for another.

## Surface A — Repository implementation

```yaml
API_repository_surface:
  evidence_source: repository
  example_path: app.py
  establishes:
    - code_present_in_current_remote_main
  does_not_establish:
    - code_currently_deployed
    - route_currently_active
    - production_configuration
```

## Surface B — Externally observed runtime

```yaml
API_external_runtime_observation:
  establishes:
    - bounded_observed_behavior_at_a_point_in_time
  requires:
    - observed_at
    - endpoint_or_surface
    - observation_method
    - evidence_references
  does_not_establish:
    - control_plane_custody
    - deployed_commit_without_attestation
```

An external response proves only the behavior observed through the stated
method and window.

## Surface C — Control-plane attestation

```yaml
API_control_plane_attestation:
  establishes:
    - point_in_time_control_plane_state
  requires:
    - attestation_contract_reference
    - attestation_evidence_reference
    - environment_identifier
    - observed_at
    - observer_or_system
    - evidence_method
    - control_plane_owner_or_custody
    - deployed_commit
    - evidence_references
```

An available external-runtime observation is invalid without its observation
time, endpoint or bounded surface, and method. An available control-plane
attestation is invalid without its environment identifier, observation time,
observer or system, method, control-plane owner or custody, deployed commit,
and an independent evidence reference. The canonical contract reference
`docs/operations/production-control-plane-attestation.md` is a template, not
attestation evidence. The evidence reference must resolve outside the CCO
assessment; a CCO assessment cannot self-attest. For `unavailable`,
`not_checked`, or `stale`, missing evidence fields remain absent or null and an
explicit limitation is required. Do not fabricate missing values or create an
attestation merely to satisfy an assessment.

## Required separations

```text
repository code != deployed runtime
health response != deployed commit attestation
attestation contract template != attestation evidence
CCO assessment != independent production evidence
externally observed behavior != control-plane custody
Legacy v1 implementation != target v2 implementation
target v2 contract approval != target v2 runtime
```

## Jarvis-Nova / Nova API relationship

Jarvis-Nova observes Nova API evidence. Jarvis-Nova is not governed by Nova API
output. Nova API does not decide Jarvis-Nova priorities. Jarvis-Nova does not
use Legacy-v1 `decision_status` as authority over CCO decisions. CCO state does
not live in Nova runtime.

This boundary adds no endpoint, API call, monitor, scheduler, deployment
connection, or external integration. A future read-only target-v2 integration
requires a separately governed change.
