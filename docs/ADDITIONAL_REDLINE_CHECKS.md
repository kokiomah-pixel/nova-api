# Additional Redline Checks (Critical Additions)

## 1. Decision vs State Language Enforcement
Ensure all mentions of:
- state
- regime
- risk

are explicitly tied to:
-> decision context or constraint system

Flag any language that sounds like passive observation rather than decision conditioning.

---

## 2. Verifiability Positioning Check
Ensure repository includes at least one clear reference to:
- decision attestation
- verifiable outputs
- integrity of decision process

Flag absence as HIGH severity.

---

## 3. API Structure Invariance
Ensure documentation explicitly states that Nova output format is fixed and structured.

Flag:
- variable output shapes
- unclear response structure
- missing IC-format explanation

---

## 4. Snapshot vs Live Data Clarity
All static examples must:
- be labeled as captured snapshots
- not imply live system state

Flag any ambiguity.

---

## 5. Billing / Payments Explicit Boundary
Ensure repo clearly states:
- payments are NOT implemented
- billing is NOT handled by this repo
- Base (if referenced) is not handling entitlements

Flag any ambiguity as HIGH severity.
