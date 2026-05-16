# SKILL 03 — Negative Signals Analyzer
**Version:** 2.0 (Final)
**Used by:** Skill 04 — Sentiment Analysis
**Output feeds into:** `friction_penalty` (0 to −20) + `risk_flags`

---

## Purpose

Reads all NI/QRF feedback and complaint data and produces:
1. A **Friction Penalty Score** (0 to −20 points)
2. Risk flags that downstream skills must respect as hard blocks or warnings

Answers: *"Is this seller frustrated, receiving bad leads, or at risk of churning if pushed to a higher plan?"*

---

## Critical Gate Rule — NI/QRF Threshold

> **If `total_ni_qrf ≤ 10` → DO NOT score or comment on any NI/QRF fields.**
> Values at or below 10 are noise, not signal. Treat as zero. Skip all NI scoring.
> Only `complaints_count` is evaluated independently of this gate.

This rule is non-negotiable.

---

## Input Fields

| Field | Description |
|---|---|
| `total_ni_qrf` | Total NI (Not Interested) / QRF (Query Rejection Feedback) count |
| `wrong_category_ni_qrf` | NI count for wrong category leads |
| `location_ni_qrf` | NI count for wrong location leads |
| `retail_ni_qrf` | NI count for low-value / retail leads (seller wants B2B bulk) |
| `complaints_count` | Formal complaints filed by seller (NaN = treat as 0) |

---

## Scoring Rules — Friction Penalty (Max deduction: −20)

All values are negative deductions. Cap total at −20 regardless of how many conditions apply.

### 1. Total NI/QRF Volume (Gate: total_ni_qrf > 10)

| `total_ni_qrf` | Deduction | Label |
|---|---|---|
| > 100 | −12 | Severe — seller is deeply frustrated |
| > 50 | −10 | High rejection load — major relevance issue |
| > 25 | −7 | Moderate friction |
| 11–25 | −4 | Mild friction |
| ≤ 10 | 0 | Gate not met — skip all NI scoring |

### 2. Wrong Category NI (only if total_ni_qrf > 10)

| `wrong_category_ni_qrf` | Deduction | Meaning |
|---|---|---|
| > 30 | −5 | Platform severely miscategorizing this seller |
| > 15 | −3 | Noticeable category mismatch |
| > 5 | −1 | Minor category issue |
| ≤ 5 | 0 | Not significant |

### 3. Location NI (only if total_ni_qrf > 10)

| `location_ni_qrf` | Deduction | Meaning |
|---|---|---|
| > 30 | −5 | Leads arriving from completely wrong geographies |
| > 15 | −3 | Geographic mismatch is recurring |
| > 5 | −1 | Minor location issue |
| ≤ 5 | 0 | Not significant |

### 4. Retail NI (only if total_ni_qrf > 10)

| `retail_ni_qrf` | Deduction | Meaning |
|---|---|---|
| > 30 | −3 | B2B seller receiving retail queries — poor fit |
| > 15 | −2 | Retail mismatch noticeable |
| > 5 | −1 | Minor retail friction |
| ≤ 5 | 0 | Not significant |

### 5. Complaints (Always applied — independent of NI gate)

| `complaints_count` | Deduction | Action |
|---|---|---|
| ≥ 1 | −10 | Hard block — must resolve before any upsell |
| 0 or NaN | 0 | No penalty |

> **Cap total friction penalty at −20.**

---

## NI Issue Classification (when gate is met)

Compute contribution % of each NI type and identify the dominant issue:

```
Category %  = wrong_category_ni_qrf / total_ni_qrf × 100
Location %  = location_ni_qrf / total_ni_qrf × 100
Retail %    = retail_ni_qrf / total_ni_qrf × 100

Primary Issue:
  IF Category % is highest  → "Wrong Category Leads"
  IF Location % is highest  → "Geographic Mismatch"
  IF Retail % is highest    → "Order Size Mismatch (Retail vs B2B)"
  IF all % are low / mixed  → "Unattributed / Broad Mismatch"
```

Always include this classification in output when gate is met.

---

## Risk Flags Generated

| Flag | Condition | Action |
|---|---|---|
| `RISK_COMPLAINT_OPEN` | complaints_count ≥ 1 | **HARD BLOCK** — no upsell; escalate to account manager |
| `RISK_HIGH_NI` | total_ni_qrf > 50 | Strong negative — seller likely frustrated; upsell may accelerate churn |
| `RISK_CATEGORY_MISMATCH` | wrong_category_ni_qrf > 15 | Wrong category leads; upsell pitch must address this |
| `RISK_LOCATION_MISMATCH` | location_ni_qrf > 15 | Geographic lead mismatch; recommend preference audit |
| `RISK_RETAIL_MISMATCH` | retail_ni_qrf > 15 | Seller needs B2B; getting retail — upsell may not resolve |
| `RISK_SEVERE_FRICTION` | total_ni_qrf > 100 | Seller in very bad platform experience — do not upsell |

---

## Output Block

```
SKILL 03 — NEGATIVE SIGNALS / PLATFORM FRICTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

NI/QRF Gate   : total_ni_qrf = <value>  →  <MET / NOT MET>

[If NOT MET:]
  NI/QRF data at or below threshold — no friction scoring applied.

[If MET:]
NI/QRF Breakdown:
  Total NI/QRF          : <total_ni_qrf>              → [Label]      [−X pts]
  Wrong Category NI     : <value>  (<X%>)                            [−X pts]
  Location NI           : <value>  (<X%>)                            [−X pts]
  Retail NI             : <value>  (<X%>)                            [−X pts]
  Primary Issue Type    : <Wrong Category / Geographic Mismatch / Order Size / Unattributed>

Complaints:
  Complaints Filed      : <value or "None">                          [−X pts]

FRICTION PENALTY : −XX  (capped at −20)

Risk Flags: [RISK_COMPLAINT_OPEN] [RISK_HIGH_NI] [RISK_CATEGORY_MISMATCH] ...
            (NONE — no significant platform friction detected)

⚠️ Risk Insights:
  • <specific finding with actual numbers>
  • <recommended action before upsell — if applicable>
  • <"No significant friction detected" if penalty = 0>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Messaging Rules

**Hard block — complaint open:**
> "⛔ HARD BLOCK: Active complaint on record. Upsell suspended. Assign to account manager before any commercial conversation."

**Severe friction:**
> "97 total NI rejections — seller is receiving a high volume of irrelevant leads. Root cause is unattributed (no specific category/location/retail breakdown). Do not upsell until lead quality is addressed."

**Gate not met:**
> "total_ni_qrf = 4 — below threshold. No friction penalty applied. Platform friction is negligible for this seller."

---

## Historical Context

From 223 successfully upselled sellers:
- Only **18 of 223 (8%)** had `total_ni_qrf > 10`
- Sellers with `total_ni_qrf > 50` have very low upsell conversion
- Sellers with complaints had 0% upsell conversion in the dataset
