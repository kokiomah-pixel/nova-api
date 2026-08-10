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
    - environment_identifier
    - observed_at
    - evidence_method
    - custody_or_owner_evidence
```

Do not fabricate missing environment, owner, custody, configuration, or
deployed-commit fields.

## Required separations

```text
repository code != deployed runtime
health response != deployed commit attestation
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
