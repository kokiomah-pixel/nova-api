from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from scripts.content.check_content_rule_promotion import check_content_rule_promotion
from scripts.content.validate_content_assignment import validate_content_assignment
from scripts.content.validate_content_operational_items import validate_content_operational_items
from scripts.content.validate_experiment_register import validate_experiment_register
from scripts.content.validate_monthly_review import validate_monthly_review
from scripts.content.validate_post_record import validate_post_record
from scripts.content.validation_common import ContentValidationError, ROOT


def test_repository_content_control_artifacts_validate() -> None:
    experiments = validate_experiment_register(ROOT / "docs/content/content-experiment-register.yaml")
    operations = validate_content_operational_items(ROOT / "docs/content/content-operational-items.yaml")
    monthly = validate_monthly_review(ROOT / "docs/content/monthly/2026-08-content-performance-review.md")
    current_state = yaml.safe_load(
        (ROOT / "docs/content/content-current-state.yaml").read_text(encoding="utf-8")
    )["content_current_state"]

    assert experiments["active_experiment_count"] == 0
    assert experiments["approved_experiment_count"] == 3
    assert operations["completed_item_count"] == 0
    assert monthly["canonical_rule_change_count"] == 0
    assert current_state["content_system_state"] == {
        "repository_status": "proposed_until_merge",
        "operating_status": "initialized_after_merge",
        "publication_status": "inactive",
        "evidence_status": "no_historical_evidence_loaded",
        "first_learning_cycle": "not_started",
    }
    assert current_state["active_experiments"] == []


def test_valid_assignment_and_published_record(tmp_path: Path) -> None:
    assignment = tmp_path / "assignment.yaml"
    assignment.write_text(
        yaml.safe_dump(
            {
                "content_assignment": {
                    "assignment_id": "ASSIGN-001",
                    "publication_target_date": "2026-08-10",
                    "intended_audience": "institutional_treasury_operators",
                    "audience_stage": "problem_aware",
                    "narrative_pillar": "institutional_review_problems",
                    "governed_distinction": "action_identity_vs_proposal_version",
                    "institutional_scenario": "revised treasury proposal",
                    "content_objective": "make revision lineage legible",
                    "desired_reader_understanding": "Nova structures review context",
                    "prohibited_misunderstanding": "Nova approves the transfer",
                    "content_pattern": "scenario_to_consequence",
                    "hook_direction": "revised action event",
                    "CTA_direction": "bounded operator question",
                    "media_format": "text",
                    "experiment_id": "CONTENT-EXP-001",
                    "variable_being_tested": "opening_frame",
                    "control_requirements": "hold topic, audience, format, and CTA constant",
                }
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    post_record = tmp_path / "post.yaml"
    post_record.write_text(
        yaml.safe_dump(
            {
                "post_record": {
                    "post": {
                        "post_id": "POST-001",
                        "status": "published",
                        "publication_date": "2026-08-10",
                        "post_url": "https://example.invalid/post/1",
                        "intended_audience": "institutional_treasury_operators",
                        "narrative_pillar": "institutional_review_problems",
                        "governed_distinction": "action_identity_vs_proposal_version",
                        "experiment_id": "CONTENT-EXP-001",
                    },
                    "final_published_copy": "A revised proposal is not a new institutional action.",
                    "measurement_schedule": {
                        "post_id": "POST-001",
                        "due": [
                            {"window": "24_hours", "date": "2026-08-11"},
                            {"window": "7_days", "date": "2026-08-17"},
                            {"window": "30_days", "date": "2026-09-09"},
                        ],
                    },
                }
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    assert validate_content_assignment(assignment)["assignment_id"] == "ASSIGN-001"
    assert validate_post_record(post_record)["publication_status"] == "published"


def test_completed_experiment_without_measurement_evidence_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "experiments.yaml"
    payload = yaml.safe_load((ROOT / "docs/content/content-experiment-register.yaml").read_text(encoding="utf-8"))
    payload["experiments"][0]["status"] = "complete"
    payload["experiments"][0]["result"] = "higher engagement"
    payload["experiments"][0]["interpretation"] = "scenario opening may help"
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    with pytest.raises(ContentValidationError, match="measurement_evidence"):
        validate_experiment_register(path)


def test_monthly_accepted_rule_without_approval_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "review.md"
    path.write_text(
        """# Review

```yaml
monthly_review_validation:
  month: 2026-08
  demand_claim_basis: none
  measurement_window_comparisons: []
  canonical_rule_changes: []
  findings:
    - finding_id: F-1
      observed: Three posts reached target roles.
      inferred: Scenario hooks may help.
      recommended_test: Repeat across another pillar.
      accepted_rule: Always use scenario hooks.
      evidence_strength: moderate
      supporting_posts: [P-1, P-2, P-3]
      supporting_measurement_windows: [7_days]
      approval:
        status: not_requested
        approved_by: null
```
""",
        encoding="utf-8",
    )

    with pytest.raises(ContentValidationError, match="explicit Architect or CCO approval"):
        validate_monthly_review(path)


def test_false_operational_completion_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "operations.yaml"
    path.write_text(
        yaml.safe_dump(
            {
                "operational_items": [
                    {
                        "item_id": "OPS-1",
                        "title": "Backfill",
                        "affected_layer": "performance",
                        "owner": "Daily_Coherence_Agent",
                        "urgency": "due",
                        "status": "verified_complete",
                        "created_at": "2026-08-04",
                        "target_date": "2026-08-07",
                        "completion_condition": "Evidence is archived.",
                        "completion_evidence": {
                            "artifact_path": "docs/content/posts",
                            "measurement_records": [],
                            "review_record": None,
                            "verified_at": "2026-08-07",
                            "verified_by": "Daily_Coherence_Agent",
                        },
                    }
                ]
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    with pytest.raises(ContentValidationError, match="measurement or review evidence"):
        validate_content_operational_items(path)


def test_candidate_and_canonical_promotion_thresholds(tmp_path: Path) -> None:
    path = tmp_path / "proposal.md"
    path.write_text(
        """# Proposal

```yaml
content_OS_change_proposal:
  requested_promotion_status: canonical_rule
  supporting_posts: [P-1, P-2, P-3]
  supporting_measurement_windows: [7_days]
  supporting_pillars: [category_definition, institutional_review_problems]
  supporting_months: [2026-08]
  approval_status: not_requested
  approved_by: null
```
""",
        encoding="utf-8",
    )

    with pytest.raises(ContentValidationError, match="explicit Architect or CCO approval"):
        check_content_rule_promotion(path)


def test_valid_provisional_pattern_proposal(tmp_path: Path) -> None:
    path = tmp_path / "provisional-proposal.md"
    path.write_text(
        """# Proposal

```yaml
content_OS_change_proposal:
  requested_promotion_status: provisional_pattern
  supporting_posts: [P-1, P-2, P-3]
  supporting_measurement_windows: [7_days]
  supporting_pillars: [institutional_review_problems]
  supporting_months: [2026-08]
  approval_status: not_requested
  approved_by: null
```
""",
        encoding="utf-8",
    )

    result = check_content_rule_promotion(path)

    assert result["requested_promotion_status"] == "provisional_pattern"
    assert result["supporting_post_count"] == 3
