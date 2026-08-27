# Public Projection Sanitization Execution v0.1

**Status:** inventory complete; removals blocked by production continuity gate  
**Baseline repository:** `nova-infrastructure-systems/sharpe-nova-os`  
**Baseline branch:** `main`  
**Baseline SHA:** `eeba729534088bdec705e84219188bb5aaaa14eb`  
**Tracked paths inventoried:** 638

## Governing boundary

```text
Public = contract, doctrine, interoperability, and approved proof.
Private = production machinery, proprietary derivation, corporate state, and operating evidence.
Provider-only = secret values and live environment credentials.
```

This inventory protects future compounding implementation. It does not claim
that material already published in Git history has become confidential.

## Production continuity gate

```yaml
deployment_reconciliation:
  repository_dependency_found: true
  dependent_provider: Render
  observed_service: nova-api
  observed_source_repository: nova-infrastructure-systems/sharpe-nova-os
  observed_source_branch: main
  auto_deploy_observed_enabled: true
  evidence_state: Architect_attested_authenticated_provider_observation_2026_08_24
  provider_state_verified_during_this_execution: false
  provider_access_available_during_this_execution: false
  private_repoint_required_before_runtime_removal: true
  private_repoint_completed: false
  production_continuity_preserved: true
  removal_gate: BLOCKED_PENDING_PROVIDER_REPOINT_AND_VERIFICATION
```

No runtime, deployment, payment, control, telemetry, or provider-topology file
may be removed from the public branch while the recorded production service may
still depend on it.

## Exact classification rules

The rules below classify every tracked path at the baseline SHA. They are
evaluated from top to bottom; the first match wins. A rule is an inventory
classification, not deletion authority.

```yaml
path_classification:
  PROVIDER_ONLY:
    tracked_paths: []
    note: >-
      No provider-only value is intentionally tracked. The tracked .env.example
      contains names, blank fields, and placeholders only.

  PRIVATE:
    exact_paths:
      - .dockerignore
      - Dockerfile
      - app.py
      - runtime.txt
      - add_key_aliases.py
      - apply_key_aliases.py
      - export_nova_state.py
      - fix_key_aliases.py
      - fix_key_aliases_clean.py
      - key_manager.py
      - nova_state_log.md

    path_prefixes:
      - agent_files/
      - archive/
      - chronology/
      - config/
      - core/
      - deployment/
      - nova/
      - nova_api/
      - reports/
      - retail_context/

    scripts_private_by_default:
      prefix: scripts/
      public_exceptions:
        - scripts/doctrine_lint.py
        - scripts/run_decision_scenario_suite.py
        - scripts/validate_arc_market_signal_watch.py
        - scripts/validate_gate3_field_derivation.py
        - scripts/validate_gate5_entry_design_review.py
        - scripts/validate_market_signal_scan_coverage.py
        - scripts/validate_public_surface_coherence.py
        - scripts/validate_target_v2_contract_revision.py

    tests_private_by_default:
      prefix: tests/
      public_exceptions:
        - tests/conftest.py
        - tests/fixtures/
        - tests/test_agent_prepared_action_example.py
        - tests/test_arc_market_signal_watch.py
        - tests/test_classification_determinism.py
        - tests/test_decision_intake_scenarios.py
        - tests/test_deep_scenario_authority_boundary.py
        - tests/test_doctrine_lint.py
        - tests/test_gate3_field_derivation_design.py
        - tests/test_gate5_entry_design_review.py
        - tests/test_market_signal_scan_coverage.py
        - tests/test_model_provider_independence.py
        - tests/test_proof_reproducibility.py
        - tests/test_public_api_documentation_boundary.py
        - tests/test_public_discovery_boundary.py
        - tests/test_public_surface_coherence.py
        - tests/test_public_x402_containment.py
        - tests/test_review_context_contract_v2_spec.py
        - tests/test_target_v2_contract_revision.py
        - tests/test_workspace_continuity_docs.py

  PUBLIC:
    exact_paths:
      - .env.example
      - .gitignore
      - .python-version
      - CATEGORY.md
      - CHANGELOG.md
      - CONTRIBUTING.md
      - CURRENT_STATE.md
      - LICENSE
      - Makefile
      - README.md
      - SECURITY.md
      - START_HERE.md
      - constraints.txt
      - pytest.ini
      - requirements-dev.txt
      - requirements.txt

    path_prefixes:
      - .github/

    note: >-
      The scripts and tests explicitly excepted from PRIVATE above are PUBLIC
      contract and doctrine validation surfaces.

  PUBLIC_SANITIZED:
    path_prefixes:
      - demos/
      - docs/
      - examples/
      - fixtures/
      - schemas/
      - specs/

    remaining_tracked_paths: true
    treatment: >-
      File-level exposure review is required before retention. Preserve external
      contracts, schemas, integration examples, synthetic vectors, public
      security posture, and approved proof; remove or reduce production
      topology, proprietary derivation, operating evidence, accepted-state
      mechanics, and private Reflex Memory mechanics only after continuity is
      verified.
```

## Current execution result

```yaml
public_projection_sanitization:
  inventory_complete: true
  baseline_paths_classified: 638
  private_destination_exists: true
  private_history_parity_verified: true
  private_bootstrap_merged: true
  private_target_files_removed_from_current_projection: 0
  public_contracts_removed: 0
  public_CI_weakened: false
  production_behavior_changed: false
  sanitization_complete: false
  blocker: provider_repoint_and_continuity_verification_required
```

## Required unblocking evidence

Before a deletion-bearing sanitization commit:

1. connect the production provider to `nova-infrastructure-systems/nova-core`;
2. verify the exact private deployed commit and provider branch;
3. verify health and the existing external containment contract;
4. verify rollback and credential continuity;
5. record provider evidence separately from repository configuration;
6. re-run the full public contract and private implementation validation suites.

Repository migration alone does not authorize production activation, payment or
settlement change, retail behavior change, institutional Gate 5, chronology, or
institutional Reflex Memory mutation.
