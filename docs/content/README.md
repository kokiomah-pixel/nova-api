# Sharpe Nova OS content system

This directory contains the governed content-production and qualified-distribution
control loop for Sharpe Nova OS. It separates durable production rules from
operating state and performance evidence.

```yaml
content_system_state:
  repository_status: proposed_until_merge
  operating_status: initialized_after_merge
  publication_status: inactive
  evidence_status: no_historical_evidence_loaded
  first_learning_cycle: not_started
```

The repository proposal becomes the initialized operating system only after
merge. File creation does not activate experiments, publication, or learning.

## Authority map

| Layer | Proposed artifact | Owner |
| --- | --- | --- |
| Durable production rules | `content-production-os.md` | Architect or Jarvis-Nova CCO |
| Daily operating control | `daily-coherence-content-operating-contract.md` | Daily Coherence Agent |
| Draft production | Content Production Engine | Content Production Engine |
| Performance evidence | `performance/` | Daily Coherence Agent |
| Experiments | `content-experiment-register.yaml` | Daily Coherence Agent, within approved scope |
| Publication | External LinkedIn account | Architect or explicitly authorized operator |

Nothing in this directory grants publication, execution, accepted-state,
chronology, or Reflex Memory authority.

## Operating sequence

```text
Daily Coherence assignment
-> Content Production Engine draft
-> coherence review
-> Architect publication or hold
-> 24-hour, 7-day, and 30-day evidence collection
-> weekly review
-> monthly interpretation
-> Architect or CCO rule decision
```

## Artifact guide

- `content-production-os.md`: proposed durable instructions; authoritative after merge.
- `audience-and-distribution-thesis.md`: target-audience hypotheses and stages.
- `narrative-pillars.md`: governed topic taxonomy.
- `content-pattern-library.md`: reusable patterns and drift controls.
- `content-governance-standard.md`: evidence, privacy, authority, and change control.
- `content-current-state.yaml`: current operating state only.
- `content-experiment-register.yaml`: controlled hypotheses and results.
- `content-operational-items.yaml`: persistent work items and verification evidence.
- `templates/`: briefs, records, reviews, plans, and change proposals.
- `performance/`: append-only performance and audience-quality ledgers.
- `monthly/`: month-specific plans and reviews.
- `posts/YYYY/MM/`: immutable published-copy records when posts exist.
- `archive/superseded-content-instructions/`: retired instructions, preserved rather than erased.

## Data discipline

Unknown and unavailable metrics are not zero. Exact published copy must be
preserved. Performance observations remain outside the post-merge Content
Production OS until the promotion threshold is met and the Architect or CCO
explicitly approves the change.
