# Sharpe Nova OS Pull Request Checklist

## Purpose

This checklist preserves Sharpe Nova OS public repo visibility discipline.

The public repo is a controlled proof surface.

It is not the full operating archive of the Sharpe Nova OS Living OS.

Canonical rule:

> Public repo shows the proof surface.
> Private OS preserves the operating memory.

---

## 1. Change Type

Select all that apply:

- [ ] Documentation
- [ ] Governance standard
- [ ] Architecture / API review-context documentation
- [ ] GTM / public framing
- [ ] Grant-facing material
- [ ] Proof-chain material
- [ ] Example / fixture
- [ ] Script / tooling
- [ ] Other:

---

## 2. File Visibility Classification

Every new or materially revised file must be classified before merge.

Select one:

- [ ] Public
- [ ] Controlled public
- [ ] Private or not public by default
- [ ] Not applicable

If public or controlled public, explain why it belongs in the public repo:

```text
Reason:
```

If private or not public by default, explain why it is included or confirm it is not being committed:

```text
Reason:
```

Reference:

- `docs/governance/public-repo-visibility-standard.md`
- `docs/governance/public-file-review-checklist.md`

---

## 3. Canonical Boundary Check

This PR preserves the canonical Nova boundary:

- [ ] Agent prepares action.
- [ ] Nova structures review context.
- [ ] Local authority decides.
- [ ] Nova does not execute.

If any item is not checked, explain why:

```text
Explanation:
```

---

## 4. Role Safety Check

This PR does not frame Sharpe Nova OS as:

- [ ] an approval engine
- [ ] an authorization layer
- [ ] an execution layer
- [ ] a payment rail
- [ ] a wallet
- [ ] a signing tool
- [ ] a settlement layer
- [ ] a trading system
- [ ] a portfolio optimizer
- [ ] a compliance product
- [ ] an audit system
- [ ] a treasury management system
- [ ] an agent supervisor
- [ ] an autonomous financial brain

If any risk exists, explain containment:

```text
Containment:
```

---

## 5. Unsupported Claim Check

This PR does not claim or imply:

- [ ] production readiness
- [ ] institutional adoption
- [ ] customer usage
- [ ] buyer validation
- [ ] market validation
- [ ] live capital control
- [ ] live deployment
- [ ] automatic Reflex Memory mutation
- [ ] autonomous financial decision-making

If any risk exists, explain containment:

```text
Containment:
```

---

## 6. Memory Language Check

If this PR discusses memory, it preserves this distinction:

- [ ] Logs are operational residue.
- [ ] Working memory is current operating context.
- [ ] Chronology is accepted decision-state lineage.
- [ ] Reflex Memory is accepted governance memory that may condition future review posture.
- [ ] API output remains review context, not authority.
- [ ] Not applicable; this PR does not discuss memory.

Safe compression:

> Memory conditions review.
> Authority remains local.
> Execution happens elsewhere.

---

## 7. API / Proof Language Check

If this PR discusses API or proof behavior, it preserves the non-authority frame:

- [ ] API output is governed review context.
- [ ] Proof artifacts support reviewability / replay / inspection.
- [ ] Proof does not authorize action.
- [ ] Proof does not imply production readiness.
- [ ] API does not approve, deny, authorize, block, route, settle, sign, or execute.
- [ ] Not applicable; this PR does not discuss API or proof behavior.

---

## 8. Public Repo Visibility Check

This PR strengthens the public proof surface without exposing private operating memory.

Confirm:

- [ ] No raw Living OS working memory is committed.
- [ ] No Reflex Memory candidates are committed.
- [ ] No unaccepted chronology is committed.
- [ ] No private CCO notes are committed.
- [ ] No internal GTM strategy is committed.
- [ ] No Content Production Engine drafts are committed before CCO review.
- [ ] No buyer objection logs are committed.
- [ ] No pricing or monetization strategy is committed.
- [ ] No allocator-specific or partner-specific materials are committed.
- [ ] No security-sensitive API behavior is committed.

If any risk exists, explain containment:

```text
Containment:
```

---

## 9. Security / Integrity Checklist

- [ ] No secrets, keys, tokens, or credentials committed.
- [ ] No `.env` files committed.
- [ ] `.env.example` contains placeholders only.
- [ ] No hidden Unicode / bidi control characters introduced.
- [ ] No unsafe VS Code extension recommendations added.
- [ ] Doctrine/security lint passes.
- [ ] No runtime settlement secrets logged.
- [ ] No private x402, CDP, wallet, or facilitator credentials exposed.

---

## 10. CCO Review Requirement

Select one:

- [ ] CCO review not required.
- [ ] CCO review required before merge.
- [ ] CCO review completed.

CCO review is required if the PR involves:

- living OS memory discipline
- Reflex Memory
- API review-context behavior
- chronology or memory mutation
- public GTM framing
- grant-facing claims
- pricing or monetization logic
- compliance / audit / regulatory language
- payment, wallet, rail, settlement, custody, or execution-adjacent language
- institution-owned governance memory
- production, adoption, buyer, or market-validation language

Notes:

```text
CCO notes:
```

---

## 11. Validation

Before merge, run:

```bash
git diff --check
python3 scripts/doctrine_lint.py
```

Optional high-risk-language scan:

```bash
grep -RInE "approves|denies|authorizes|blocks|routes|settles|executes|signs|manages wallets|compliance product|audit system|agent supervisor|capital-governance brain|powers live API decisions|learns from capital actions|production-ready|buyer-validated|market-validated" README.md START_HERE.md docs .github || true
```

Confirm:

- [ ] `git diff --check` passed.
- [ ] `python3 scripts/doctrine_lint.py` passed.
- [ ] High-risk-language hits were reviewed, if scan was run.

---

## Final Confirmation

This PR keeps Sharpe Nova OS aligned with the repo visibility rule:

> Keep GitHub public enough to prove Nova.
> Curate it enough to protect Nova.
> Do not let the repo become the OS.
