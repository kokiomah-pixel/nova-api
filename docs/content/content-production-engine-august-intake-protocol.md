# Content Production Engine — August 2026 intake protocol

## Purpose

This protocol authorizes the Content Production Engine to receive and structure
recent August 2026 LinkedIn posts and associated performance evidence supplied
by the Architect.

It does not authorize automatic repository writes.

```yaml
Architect_authorization:
  Content_Production_Engine_may_receive_August_posts: true
  Content_Production_Engine_may_extract_post_metadata: true
  Content_Production_Engine_may_structure_performance_evidence: true
  Content_Production_Engine_may_prepare_repository_handoffs: true
  Content_Production_Engine_may_write_repository_automatically: false
  Content_Production_Engine_may_claim_persistence_without_commit: false
  autonomous_publication_authorized: false
  experiment_activation_by_intake: false
  interpretation_by_intake: false
```

## Architect submission experience

The Architect may paste any combination of:

```yaml
minimum_post_input:
  exact_published_copy:
  post_url:
  publication_date_or_timestamp:

optional_performance_input:
  analytics_screenshot:
  copied_metrics:
  measurement_date_or_timestamp:
  comments_or_audience_observations:
```

The Architect must not be required to manually format YAML, CSV, or Markdown.

## Supported intake cases

### Published post only

Use when the Architect supplies the post before performance evidence is
available. Create a handoff for:

```text
docs/content/posts/2026/08/<post-id>.md
```

### Published post and performance

Use when the post and one or more analytics snapshots are supplied together.
Create:

- the post-record handoff;
- one performance-ledger row per supported snapshot;
- audience rows only where material audience evidence exists;
- updated measurement scheduling information.

### Performance update

Use when the post record already exists and the Architect supplies a later
measurement. Resolve the post using:

1. exact post ID;
2. exact LinkedIn URL;
3. unique publication date and exact published copy;
4. otherwise mark the post unresolved.

Never guess between multiple posts. Ask one concise question only when the post
cannot be uniquely identified.

### Audience observation

Preserve an audience observation only when it materially supports audience
quality or content-understanding review. Record the minimum identity context
needed and a specific relevance basis.

## Exact-copy rule

The exact published LinkedIn copy must be preserved unchanged. Do not rewrite,
polish, or normalize it inside the post record. Draft improvement belongs in a
separate content-production task.

## Performance windows

```yaml
measurement_windows:
  controlled:
    - 24_hours
    - 7_days
    - 30_days
  observational:
    - ad_hoc
    - historical_unknown_age
```

For already-published August posts:

- use a controlled window only when the measurement time supports it;
- use `ad_hoc` when the age is known but does not match a controlled window;
- use `historical_unknown_age` when measurement age cannot be established;
- never reconstruct a missed measurement;
- never relabel a current screenshot as a 24-hour result without timestamp
  evidence.

Observational windows may be preserved but cannot independently establish a
controlled experiment result.

## Experiment rule

A supplied August post receives an `experiment_id` only when the experiment was
assigned before publication. Do not retroactively convert an ordinary published
post into controlled experiment evidence.

Unassigned posts use:

```yaml
experiment_assignment:
  experiment_id: null
  evidence_role: baseline_observation
```

## Evidence discipline

The Content Production Engine must distinguish `observed`, `unavailable`,
`uncertain`, and `inferred`.

- Missing is not zero.
- Cropped screenshot fields are unavailable.
- Unclear screenshot values are uncertain.
- Zero is permitted only when visibly observed.
- Person or company relevance must include a recorded basis.
- Impressions do not prove demand.
- Comments do not prove institutional dependency.
- Follower changes do not prove product-market fit.

## Required repository handoff

For each submission, return:

```yaml
august_content_intake_handoff:
  handoff_version: 1.0.0
  prepared_at:
  supplied_by: Architect

  intake_type:
    - published_post_only
    - post_and_performance
    - performance_update
    - audience_observation

  post:
    post_id:
    title_or_working_name:
    exact_published_copy:
    post_url:
    publication_date:
    publication_timestamp:
    intended_audience:
    audience_stage:
    narrative_pillar:
    governed_distinction:
    hook_type:
    content_pattern:
    media_format:
    cta_type:
    experiment_id:
    evidence_role:

  measurements:
    - measurement_window:
      measurement_date:
      measurement_timestamp:
      calculated_age_hours:
      observed_metrics:
        impressions:
        reactions:
        comments:
        reposts:
        saves:
        profile_views:
        new_followers:
        link_clicks:
        inbound_messages:
      unavailable_metrics: []
      uncertain_fields: []
      evidence_status:
      notes:

  audience_observations:
    - date:
      engagement_type:
      person_or_company:
      role:
      company:
      inferred_segment:
      target_market_relevance:
      relevance_basis:
      content_understanding:
      misunderstanding:
      follow_up_occurred:
      qualified_conversation:
      evidence_status:
      notes:

  repository_plan:
    post_record:
    performance_rows:
    audience_rows:
    current_state_update:

  unresolved_fields: []

  effects:
    publication_created: false
    performance_interpretation_created: false
    experiment_result_created: false
    canonical_rule_changed: false
    accepted_state_changed: false
    chronology_event_created: false
    Reflex_Memory_object_created: false

  status: ready_for_repository_handoff
```

## Persistence honesty

The Content Production Engine may return:

```yaml
status: ready_for_repository_handoff
```

after it has structured the supplied evidence. It may return:

```yaml
status: persisted
```

only when a real repository commit or merged pull request is supplied as
completion evidence. Conversation state is not repository persistence.

## Repository persistence workflow

The structured handoff is suitable for direct submission to VS Code. The
authorized repository operator must:

```text
Receive handoff
-> verify post identity
-> create or update post record
-> append supported performance rows
-> append material audience rows
-> update current state and measurement schedule
-> run validators
-> commit on a bounded evidence branch
-> open or update a pull request
-> return persistence evidence
```

Suggested monthly branch:

```text
ops/content-evidence-2026-08-manual
```

Suggested rolling PR title:

```text
ops: record August 2026 LinkedIn content evidence
```

Each persistence commit identifies the post and window:

```text
ops(content): record <post-id> published post
ops(content): record <post-id> 24-hour evidence
ops(content): record <post-id> ad-hoc evidence
```

Do not use unrestricted `git add -A`.

## Synthetic schema acceptance

This fixture proves representation only. It is not a post record or evidence.

```yaml
august_content_intake_acceptance_fixture:
  intake_type: published_post_only
  publication_month: 2026-08
  exact_published_copy: fixture_only
  post_url: https://www.linkedin.com/posts/example
  publication_date: "2026-08-01"
  experiment_id: null
  evidence_role: baseline_observation
  repository_write_performed: false
```
