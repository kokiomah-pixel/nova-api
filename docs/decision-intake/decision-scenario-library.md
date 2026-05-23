# Decision Scenario Library

This library feeds decision-context pressure into the Month Two validation layer. It is intentionally framed as environmental-governance testing: the prompts describe pressure around a possible local action, while Nova's processed response remains telemetry, classification, conditioning guidance, and chronology.

The fenced JSON block is loaded by `scripts/run_decision_scenario_suite.py`. Each category contains ten prompts, producing seventy scenarios total.

```json
{
  "categories": {
    "capital_movement": [
      {
        "decision_context": "Capital movement is proposed while constraint pressure is rising and direct failure telemetry has not appeared.",
        "primary_risks": ["coordination_risk", "retry_escalation_risk"],
        "intensity": "elevated"
      },
      {
        "decision_context": "An autonomous treasury route sees intermittent settlement rejection diagnostics during an otherwise valid allocation window.",
        "primary_risks": ["interoperability_risk", "retry_escalation_risk"],
        "intensity": "elevated"
      },
      {
        "decision_context": "An execution router reports increasing retry frequency across dependent systems during a proposed rebalance.",
        "primary_risks": ["coordination_risk", "retry_escalation_risk"],
        "intensity": "severe",
        "unresolved_class": "retry_congestion"
      },
      {
        "decision_context": "Capital transfer timing overlaps with degraded oracle freshness and fragmented venue telemetry.",
        "primary_risks": ["coordination_risk", "semantic_drift_risk"],
        "intensity": "elevated"
      },
      {
        "decision_context": "A treasury workflow attempts to treat missing downstream telemetry as neutral context during a capital-moving window.",
        "primary_risks": ["sovereignty_risk", "coordination_risk"],
        "intensity": "elevated"
      },
      {
        "decision_context": "A liquidity allocator requests larger movement while environmental pulse is elevated and prior context remains unresolved.",
        "primary_risks": ["coordination_risk", "sovereignty_risk"],
        "intensity": "elevated"
      },
      {
        "decision_context": "A capital route is structurally complete but dependency propagation risk is increasing across adjacent settlement services.",
        "primary_risks": ["coordination_risk", "interoperability_risk"],
        "intensity": "elevated"
      },
      {
        "decision_context": "A capital movement is proposed after repeated near-identical prompts with small wording changes.",
        "primary_risks": ["semantic_drift_risk", "retry_escalation_risk"],
        "intensity": "elevated"
      },
      {
        "decision_context": "A treasury system seeks to continue routing after a partial telemetry outage in one dependent venue.",
        "primary_risks": ["coordination_risk", "interoperability_risk"],
        "intensity": "moderate"
      },
      {
        "decision_context": "Capital movement pressure increases after an external operator asks for faster settlement despite unstable environmental pulse.",
        "primary_risks": ["coordination_risk", "retry_escalation_risk"],
        "intensity": "elevated"
      }
    ],
    "pacing": [
      {
        "decision_context": "A system attempts to accelerate cadence when market context appears favorable but coordination telemetry shows fragmentation.",
        "primary_risks": ["coordination_risk", "retry_escalation_risk"],
        "intensity": "elevated"
      },
      {
        "decision_context": "Retry cadence continues after repeated settlement failures while the local agent remains confident.",
        "primary_risks": ["retry_escalation_risk", "interoperability_risk"],
        "intensity": "severe",
        "unresolved_class": "blind_retry_pressure"
      },
      {
        "decision_context": "Multiple systems converge on the same timing window and escalation pressure begins to compress.",
        "primary_risks": ["coordination_risk", "retry_escalation_risk"],
        "intensity": "elevated"
      },
      {
        "decision_context": "An orchestrator attempts to shorten observation windows after two quiet telemetry intervals.",
        "primary_risks": ["coordination_risk"],
        "intensity": "moderate"
      },
      {
        "decision_context": "A workflow proposes immediate escalation after one degraded response from a dependent system.",
        "primary_risks": ["retry_escalation_risk", "coordination_risk"],
        "intensity": "elevated"
      },
      {
        "decision_context": "A timing controller treats stale pulse data as stable because no new failure was emitted.",
        "primary_risks": ["semantic_drift_risk", "coordination_risk"],
        "intensity": "elevated"
      },
      {
        "decision_context": "Repeated pacing prompts arrive with small parameter changes during an elevated retry window.",
        "primary_risks": ["retry_escalation_risk", "semantic_drift_risk"],
        "intensity": "elevated"
      },
      {
        "decision_context": "A dependent service recovers partially and an agent attempts to restore full cadence without observing coordination stability.",
        "primary_risks": ["coordination_risk", "retry_escalation_risk"],
        "intensity": "moderate"
      },
      {
        "decision_context": "Escalation timing is requested while prior chronology entries remain incomplete.",
        "primary_risks": ["sovereignty_risk", "retry_escalation_risk"],
        "intensity": "elevated"
      },
      {
        "decision_context": "A queue manager compresses decision spacing because downstream capacity appears temporarily higher.",
        "primary_risks": ["coordination_risk", "retry_escalation_risk"],
        "intensity": "elevated"
      }
    ],
    "interoperability": [
      {
        "decision_context": "A machine-native settlement attempt is retried after facilitator rejection while helper construction succeeded.",
        "primary_risks": ["interoperability_risk", "retry_escalation_risk"],
        "intensity": "elevated"
      },
      {
        "decision_context": "The payload path is valid but facilitator response classification remains unknown.",
        "primary_risks": ["interoperability_risk", "coordination_risk"],
        "intensity": "elevated"
      },
      {
        "decision_context": "Failed settlement telemetry is ambiguous between payment failure and environmental interoperability signal.",
        "primary_risks": ["interoperability_risk", "semantic_drift_risk"],
        "intensity": "elevated"
      },
      {
        "decision_context": "A facilitator returns intermittent rejection after identical canonical construction across two attempts.",
        "primary_risks": ["interoperability_risk", "retry_escalation_risk"],
        "intensity": "severe",
        "unresolved_class": "facilitator_acceptance_ambiguity"
      },
      {
        "decision_context": "Settlement observability captures response headers but not enough chronology to separate local and remote failure domains.",
        "primary_risks": ["interoperability_risk", "sovereignty_risk"],
        "intensity": "elevated"
      },
      {
        "decision_context": "A client library upgrade changes helper behavior while settlement acceptance remains inconsistent.",
        "primary_risks": ["interoperability_risk", "semantic_drift_risk"],
        "intensity": "elevated"
      },
      {
        "decision_context": "A replay attempt uses equivalent payload material but the surrounding environment has changed.",
        "primary_risks": ["interoperability_risk", "coordination_risk"],
        "intensity": "moderate"
      },
      {
        "decision_context": "A payment rail dependency reports healthy status while facilitator diagnostics remain degraded.",
        "primary_risks": ["interoperability_risk", "coordination_risk"],
        "intensity": "elevated"
      },
      {
        "decision_context": "A settlement route tries to collapse construction success and acceptance into one success class.",
        "primary_risks": ["semantic_drift_risk", "interoperability_risk"],
        "intensity": "elevated"
      },
      {
        "decision_context": "An adapter retries after timeout without preserving the request and response chronology needed for replay.",
        "primary_risks": ["retry_escalation_risk", "interoperability_risk"],
        "intensity": "elevated"
      }
    ],
    "governance": [
      {
        "decision_context": "A draft document describes Nova as controlling capital movement because telemetry affects downstream behavior.",
        "primary_risks": ["semantic_drift_risk", "sovereignty_risk"],
        "intensity": "severe",
        "unresolved_class": "doctrine_boundary_drift"
      },
      {
        "decision_context": "Remaining strong language is questioned even though it protects sovereignty rather than creating local-control drift.",
        "primary_risks": ["semantic_drift_risk", "sovereignty_risk"],
        "intensity": "elevated"
      },
      {
        "decision_context": "A pull request has correct doctrine framing but unresolved risk logs identify external sample apps requiring review.",
        "primary_risks": ["semantic_drift_risk", "coordination_risk"],
        "intensity": "elevated"
      },
      {
        "decision_context": "A governance note compresses environmental conditioning into generic risk tooling language.",
        "primary_risks": ["semantic_drift_risk", "sovereignty_risk"],
        "intensity": "elevated"
      },
      {
        "decision_context": "A spec update preserves chronology but omits the non-authority boundary from a public-facing section.",
        "primary_risks": ["sovereignty_risk", "semantic_drift_risk"],
        "intensity": "elevated"
      },
      {
        "decision_context": "A change log entry reorders events to make implementation appear cleaner than the actual review sequence.",
        "primary_risks": ["sovereignty_risk", "coordination_risk"],
        "intensity": "elevated"
      },
      {
        "decision_context": "A doctrine migration removes category-protective terms without preserving replacement context.",
        "primary_risks": ["semantic_drift_risk", "sovereignty_risk"],
        "intensity": "elevated"
      },
      {
        "decision_context": "An integration guide presents telemetry fields as enough for downstream substitution.",
        "primary_risks": ["sovereignty_risk", "semantic_drift_risk"],
        "intensity": "severe",
        "unresolved_class": "telemetry_substitution_risk"
      },
      {
        "decision_context": "A reviewer asks whether unresolved governance notes can be treated as historical noise.",
        "primary_risks": ["semantic_drift_risk", "coordination_risk"],
        "intensity": "moderate"
      },
      {
        "decision_context": "A public README change improves readability but weakens the environmental-governance category boundary.",
        "primary_risks": ["semantic_drift_risk", "sovereignty_risk"],
        "intensity": "elevated"
      }
    ],
    "security": [
      {
        "decision_context": "A developer continues work after installing a low-trust editor extension with terminal and file access.",
        "primary_risks": ["sovereignty_risk", "coordination_risk"],
        "intensity": "severe",
        "unresolved_class": "developer_environment_integrity"
      },
      {
        "decision_context": "Local credential hygiene is considered after a suspicious editor tool was active while environment files were visible.",
        "primary_risks": ["sovereignty_risk", "semantic_drift_risk"],
        "intensity": "elevated"
      },
      {
        "decision_context": "A pull request has clean doctrine lint but developer-environment integrity checks remain incomplete.",
        "primary_risks": ["sovereignty_risk", "coordination_risk"],
        "intensity": "elevated"
      },
      {
        "decision_context": "A local helper script requests broad filesystem access before its behavior has been reviewed.",
        "primary_risks": ["sovereignty_risk", "coordination_risk"],
        "intensity": "elevated"
      },
      {
        "decision_context": "A security chronology entry exists but lacks enough order-of-events detail to guide response.",
        "primary_risks": ["sovereignty_risk", "semantic_drift_risk"],
        "intensity": "moderate"
      },
      {
        "decision_context": "A package update is needed for settlement testing but supply-chain review is incomplete.",
        "primary_risks": ["coordination_risk", "sovereignty_risk"],
        "intensity": "elevated"
      },
      {
        "decision_context": "A developer attempts to paste diagnostic output that may include sensitive local context.",
        "primary_risks": ["sovereignty_risk", "semantic_drift_risk"],
        "intensity": "elevated"
      },
      {
        "decision_context": "A workspace setting changes terminal behavior during a governance-sensitive test run.",
        "primary_risks": ["coordination_risk", "sovereignty_risk"],
        "intensity": "moderate"
      },
      {
        "decision_context": "A response timeline is missing the first observation of suspicious local behavior.",
        "primary_risks": ["sovereignty_risk", "coordination_risk"],
        "intensity": "elevated"
      },
      {
        "decision_context": "An external tool asks for repository indexing while unresolved security chronology remains open.",
        "primary_risks": ["sovereignty_risk", "semantic_drift_risk"],
        "intensity": "elevated"
      }
    ],
    "gtm": [
      {
        "decision_context": "A company page drafts Nova as AI infrastructure because that term is easier for the market to understand.",
        "primary_risks": ["semantic_drift_risk", "sovereignty_risk"],
        "intensity": "elevated"
      },
      {
        "decision_context": "A grant opportunity creates pressure to frame Nova as payment tooling rather than environmental governance infrastructure.",
        "primary_risks": ["semantic_drift_risk", "interoperability_risk"],
        "intensity": "severe",
        "unresolved_class": "market_category_collapse"
      },
      {
        "decision_context": "A public paper weighs settlement observability against broader payment infrastructure phrasing.",
        "primary_risks": ["semantic_drift_risk", "interoperability_risk"],
        "intensity": "elevated"
      },
      {
        "decision_context": "A sales note emphasizes dashboards because buyers recognize analytics more quickly than conditioning infrastructure.",
        "primary_risks": ["semantic_drift_risk", "sovereignty_risk"],
        "intensity": "elevated"
      },
      {
        "decision_context": "A launch narrative compresses Reflex Memory into learning-system language.",
        "primary_risks": ["semantic_drift_risk", "sovereignty_risk"],
        "intensity": "elevated"
      },
      {
        "decision_context": "A partner deck makes telemetry breadth the lead value proposition without explaining environmental conditioning.",
        "primary_risks": ["semantic_drift_risk", "coordination_risk"],
        "intensity": "elevated"
      },
      {
        "decision_context": "A public roadmap prioritizes marketplace familiarity over orchestration insertion language.",
        "primary_risks": ["semantic_drift_risk", "coordination_risk"],
        "intensity": "moderate"
      },
      {
        "decision_context": "A pricing page describes value in transaction terms and weakens the pre-execution conditioning category.",
        "primary_risks": ["semantic_drift_risk", "interoperability_risk"],
        "intensity": "elevated"
      },
      {
        "decision_context": "A founder update uses simpler language that risks making Nova sound like a recommendation product.",
        "primary_risks": ["semantic_drift_risk", "sovereignty_risk"],
        "intensity": "elevated"
      },
      {
        "decision_context": "A public case study highlights prevented losses without preserving environmental chronology as the source of value.",
        "primary_risks": ["semantic_drift_risk", "coordination_risk"],
        "intensity": "elevated"
      }
    ],
    "orchestration": [
      {
        "decision_context": "Nova is asked to prioritize allocator-facing dashboards over insertion into orchestration layers.",
        "primary_risks": ["coordination_risk", "semantic_drift_risk"],
        "intensity": "elevated"
      },
      {
        "decision_context": "An integration choice weighs telemetry breadth against retry-suppression economics.",
        "primary_risks": ["coordination_risk", "retry_escalation_risk"],
        "intensity": "elevated"
      },
      {
        "decision_context": "An orchestration system asks Nova to expose deeper causality fields for convenience.",
        "primary_risks": ["sovereignty_risk", "coordination_risk"],
        "intensity": "severe",
        "unresolved_class": "sovereign_field_expansion"
      },
      {
        "decision_context": "A downstream planner wants field-level explanations that could become a substitute for local governance.",
        "primary_risks": ["sovereignty_risk", "semantic_drift_risk"],
        "intensity": "elevated"
      },
      {
        "decision_context": "A workflow engine asks to cache Nova posture longer than the environmental window supports.",
        "primary_risks": ["coordination_risk", "sovereignty_risk"],
        "intensity": "elevated"
      },
      {
        "decision_context": "An orchestration partner optimizes for lowest integration latency while retry pressure is rising.",
        "primary_risks": ["coordination_risk", "retry_escalation_risk"],
        "intensity": "elevated"
      },
      {
        "decision_context": "A consumer asks for additional labels that would make telemetry easier to commoditize.",
        "primary_risks": ["semantic_drift_risk", "sovereignty_risk"],
        "intensity": "moderate"
      },
      {
        "decision_context": "A multi-agent workflow treats Nova output as shared environmental truth but skips local responsibility mapping.",
        "primary_risks": ["sovereignty_risk", "coordination_risk"],
        "intensity": "elevated"
      },
      {
        "decision_context": "An orchestration system wants to merge Nova chronology with unrelated execution logs.",
        "primary_risks": ["coordination_risk", "sovereignty_risk"],
        "intensity": "elevated"
      },
      {
        "decision_context": "A dependency map shows Nova becoming a central coordination primitive without matching review cadence.",
        "primary_risks": ["coordination_risk", "sovereignty_risk"],
        "intensity": "elevated"
      }
    ]
  }
}
```
