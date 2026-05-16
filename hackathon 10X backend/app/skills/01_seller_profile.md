# SKILL 01 — Seller Profile Analyzer
**Version:** 2.0 (Final)
**Used by:** Skill 04 — Sentiment Analysis
**Output feeds into:** `seller_profile_score` (0–25) + `profile_flags`

---

## Purpose

Reads raw seller identity and business profile fields and produces:
1. A **Profile Strength Score** (0–25 points)
2. Flags for downstream skills

Does NOT make upsell decisions. Only assesses how strong and trustworthy a seller's business profile is.

---

## Input Fields

| Field | Description |
|---|---|
| `glusr_usr_id` | Seller's unique identifier |
| `company` | Company name |
| `city` | Seller's city |
| `STATE` | Seller's state |
| `company_type` | Proprietor / Partnership / Ltd. Company |
| `gst` | 1 = GST registered, 0 = not registered |
| `tan` | 1 = TAN available |
| `Turnover` | Revenue bracket in INR |
| `preferred_location` | Local / India / Global |
| `client_vintage_days` | Days since seller joined IndiaMart |
| `vintage` | Human-readable vintage e.g. "3Y" |
| `avg_ratings` | Seller's average rating |
| `ratings_count` | Number of ratings received |
| `prime_segment` | Platform signal: 2=Highest, 1=Medium, 0=Low, -1=Churn |
| `industry` | Industry vertical |
| `highest_service` | Current / highest domestic service tier |

---

## Scoring Rules — Profile Strength Score (Max 25)

### 1. Compliance & Trust (Max 7 pts)

| Condition | Points | Notes |
|---|---|---|
| `gst = 1` | +5 | Mandatory trust signal. 100% of historical upsell conversions had GST. |
| `tan = 1` | +2 | Additional compliance signal |
| `gst = 0` | 0 | No points; set FLAG_NO_GST |

### 2. Business Scale — Turnover (Max 8 pts)

Use highest matching bracket only. Do not stack.

| Turnover | Points |
|---|---|
| `100 - 500 Cr` or higher | +8 |
| `25 - 100 Cr` | +7 |
| `5 - 25 Cr` | +6 |
| `1.5 - 5 Cr` | +5 |
| `40 L - 1.5 Cr` | +3 |
| `0 - 40 L` | +1 |
| Missing / Unknown | 0 |

### 3. Platform Vintage (Max 7 pts)

| `client_vintage_days` | Points |
|---|---|
| ≥ 2000 days | +7 |
| ≥ 1000 days | +6 |
| ≥ 730 days | +5 |
| ≥ 365 days | +4 |
| ≥ 180 days | +2 |
| < 180 days | +1 |

### 4. Reputation — Ratings (Max 5 pts)

**Only apply if `ratings_count ≥ 10`.** Fewer ratings are statistically unreliable — skip this dimension entirely if below threshold.

| `avg_ratings` | Points |
|---|---|
| ≥ 4.5 | +5 |
| ≥ 4.0 | +4 |
| ≥ 3.5 | +2 |
| < 3.5 | 0 — set FLAG_LOW_RATING |

### 5. Company Type Bonus

| `company_type` | Bonus |
|---|---|
| `Ltd. Company` | +3 |
| `Partnership` | +1 |
| `Proprietor` | 0 |

> **Cap:** Total cannot exceed **25**.

---

## Flags Generated

| Flag | Condition | Meaning |
|---|---|---|
| `FLAG_NO_GST` | gst = 0 | Near-zero upsell conversion historically; note prominently |
| `FLAG_CHURN_RISK` | prime_segment = -1 | Do not upsell; escalate to retention team immediately |
| `FLAG_NEW_SELLER` | client_vintage_days < 180 | Too new for confident upsell assessment |
| `FLAG_LOW_RATING` | avg_ratings < 3.5 AND ratings_count ≥ 10 | Reputational risk |
| `FLAG_HIGH_SCALE` | Turnover ≥ 5 Cr | Strong business scale — reinforces upsell case |

---

## Hard Rules

- `prime_segment = -1` → Set `FLAG_CHURN_RISK`. Immediately pass to Skills 04 and 05. No upsell under any circumstance.
- `gst = 0` → Set `FLAG_NO_GST`. Historical data shows 0% upsell conversion without GST.
- Do not infer missing fields. Null or empty = treat as 0; skip that scoring dimension.

---

## Domestic Service Hierarchy (Reference)

Pass `highest_service` to Skill 05 to determine next recommended tier.

```
Free → Catalog → TrustSEAL → Maximiser → Star → Leader → Featured Leader → Industry Leader
```

---

## Output Block

```
SKILL 01 — SELLER PROFILE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Seller ID     : <glusr_usr_id>
Company       : <company>
Location      : <city>, <STATE>
Industry      : <industry>
Company Type  : <company_type>
Current Plan  : <highest_service>
Vintage       : <vintage> (<client_vintage_days> days)
Turnover      : <Turnover>
Preferred Mkt : <preferred_location>

Compliance    : GST=<✓/✗>  TAN=<✓/✗>
Ratings       : <avg_ratings> avg (<ratings_count> ratings)
Prime Segment : <prime_segment>  [Highest Potential / Medium / Low / Churn Risk]

PROFILE STRENGTH SCORE : XX / 25

Score Breakdown:
  Compliance & Trust  : +X
  Business Scale      : +X
  Platform Vintage    : +X
  Reputation          : +X
  Company Type Bonus  : +X

Flags Set: [FLAG_CHURN_RISK] [FLAG_HIGH_SCALE] [FLAG_LOW_RATING] ...
           (NONE if no flags triggered)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
