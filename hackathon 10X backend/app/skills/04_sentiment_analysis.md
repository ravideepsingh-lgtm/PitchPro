# SKILL 04 — Seller Sentiment Analysis
**Version:** 2.0 (Final)
**Depends on:** Skills 01, 02, 03
**Output feeds into:** Skill 05 — Upsell Decision

---

## Purpose

Synthesizes outputs from all three upstream skills into a single **Seller Sentiment Score (SSS)** and classified **sentiment verdict**. Does NOT make the final recommendation — prepares the complete evidence picture for Skill 05.

Answers: *"What is this seller's overall disposition toward the platform and toward receiving a higher-value domestic service?"*

---

## Execution Order — Mandatory

Run skills strictly in this sequence before running Skill 04:

```
Step 1 → SKILL 01 (Seller Profile)      → seller_profile_score, profile_flags
Step 2 → SKILL 02 (Positive Signals)    → engagement_score, engagement_flags
Step 3 → SKILL 03 (Negative Signals)    → friction_penalty, risk_flags
Step 4 → SKILL 04 (this skill)          → SSS + sentiment verdict
Step 5 → SKILL 05 (Decision)            → final recommendation
```

Do not skip or reorder.

---

## Inputs Required

| Input | Source | Type |
|---|---|---|
| `seller_profile_score` | Skill 01 | Integer 0–25 |
| `profile_flags` | Skill 01 | Set of flags |
| `engagement_score` | Skill 02 | Integer 0–45 |
| `engagement_flags` | Skill 02 | Set of flags |
| `friction_penalty` | Skill 03 | Integer −20 to 0 |
| `risk_flags` | Skill 03 | Set of flags |
| `prime_segment` | Raw data | Integer −1 to 2 |

---

## Step 1 — Prime Segment Boost

| `prime_segment` | Boost | Label |
|---|---|---|
| 2 | +10 | Highest platform-assessed upsell potential |
| 1 | +6 | Medium potential |
| 0 | +2 | Low potential |
| −1 | 0 | Churn risk — boost not applicable |

---

## Step 2 — Compute Seller Sentiment Score (SSS)

```
SSS = seller_profile_score + engagement_score + friction_penalty + prime_segment_boost
```

| Component | Max Points | Source |
|---|---|---|
| Profile Strength | +25 | Skill 01 |
| Engagement Score | +45 | Skill 02 |
| Friction Penalty | −20 | Skill 03 |
| Prime Segment Boost | +10 | Raw data |
| **Total SSS** | **80** | — |

> **Floor:** SSS cannot go below 0. Apply max(0, computed_SSS).

---

## Step 3 — Hard Block Check (Before Classification)

Check before assigning any sentiment class. If any hard block is active, it overrides SSS entirely.

| Hard Block Flag | Override |
|---|---|
| `FLAG_CHURN_RISK` (prime_segment = −1) | ⛔ DO NOT UPSELL — CHURN RISK |
| `RISK_COMPLAINT_OPEN` (complaints ≥ 1) | ⛔ DO NOT UPSELL — COMPLAINT OPEN |

---

## Step 4 — Sentiment Classification

If no hard blocks, classify using SSS:

| SSS Range | Class | Icon | Meaning |
|---|---|---|---|
| 65–80 | **Strong Positive** | 🟢 | High confidence — pitch next domestic tier now |
| 50–64 | **Positive with Caveats** | 🟡 | Upsell viable — address specific gaps in pitch |
| 35–49 | **Neutral / Borderline** | 🟠 | Not ready — monitor and re-evaluate in 30 days |
| 0–34 | **Negative** | 🔴 | Do not upsell — risk of churn if pushed |

---

## Step 5 — Seller Intent Classification

Classify the seller's current platform intent based on overall signal picture:

| Intent Type | Criteria | Upsell Implication |
|---|---|---|
| **Growth-Oriented** | High BL usage + active days + A-rank opportunity | Actively trying to grow; more capacity directly serves them |
| **Passive User** | Low BL usage despite long vintage and active days | Present but not investing; pitch must lead with missed value |
| **Frustrated User** | NI > 25 + low call success | Quality issues; upsell risks accelerating churn |
| **Expansion-Ready** | High major_cities + high A-rank + strong engagement | Scaling — needs higher-tier visibility to match reach |
| **At Risk** | prime_segment = −1 OR complaint > 0 | Retention is the priority — no commercial pitch |

---

## Step 6 — Sentiment Drivers

Identify the **top 3 positive drivers** and **top 2 risk signals** by score contribution.

**Positive drivers:** Highest-contributing signals from Skills 01 and 02.
**Risk signals:** What dragged the score down or left points on the table.

---

## Output Block

```
SKILL 04 — SELLER SENTIMENT ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Score Assembly:
  Profile Strength Score  : +XX / 25   (Skill 01)
  Engagement Score        : +XX / 45   (Skill 02)
  Friction Penalty        :  −XX       (Skill 03)
  Prime Segment Boost     : +XX / 10   (prime_segment = <value>)
  ──────────────────────────────────────
  SELLER SENTIMENT SCORE  :  XX / 80

Hard Block Check          : NONE  /  ⛔ CHURN RISK  /  ⛔ COMPLAINT OPEN

SENTIMENT CLASS           : 🟢 Strong Positive  /  🟡 Positive with Caveats  /
                            🟠 Neutral  /  🔴 Negative  /  ⛔ Hard Block

Seller Intent Type        : <Growth-Oriented / Passive User / Frustrated User /
                             Expansion-Ready / At Risk>

──────────────────────────────────────
📈 TOP POSITIVE DRIVERS:
  1. <signal>  →  +X pts  —  <one-line insight with actual data>
  2. <signal>  →  +X pts  —  <one-line insight with actual data>
  3. <signal>  →  +X pts  —  <one-line insight with actual data>

📉 TOP RISK SIGNALS:
  1. <signal>  →  −X pts or missed opportunity  —  <one-line explanation>
  2. <signal>  →  −X pts or missed opportunity  —  <one-line explanation>

──────────────────────────────────────
SENTIMENT SUMMARY (2–3 sentences):
  <Plain-language briefing for the sales team — who this seller is, what their
   platform relationship looks like, and what the sentiment means for a domestic
   upsell pitch>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Sentiment Summary Writing Rules

Write as if briefing a sales rep before a call. Be direct and data-specific.

**🟢 Strong Positive:**
> "Toshvin Analytical is a 13-year Ltd. Company veteran with 100-500 Cr turnover and near-daily platform activity. Despite low BL usage (39%), their 23 A-rank categories and exceptional profile make them a confident TrustSEAL pitch. Clarify the BL usage on the call — if it's selectivity rather than quality issues, close without hesitation."

**🟡 Positive with Caveats:**
> "Integrated Energy Engineering has solid engagement — 75% BL usage, 24 active days — but is only 1 year old with 5 ratings (below scoring threshold). Platform segments them as high potential (prime_segment = 2). Maximiser is the right next tier; validate value realization on the call before closing."

**🔴 Negative — Frustrated User:**
> "Mig Fitt Engineering Works has top-tier engagement metrics but carries 97 NI rejections with no identified root cause. Upselling to Featured Leader risks deepening dissatisfaction if lead quality isn't resolved first. Recommend an account review call focused on the NI issue before any commercial pitch."

**⛔ Hard Block:**
> "⛔ Active complaint on file. Sentiment analysis complete but no upsell action should be taken. Pass to account manager immediately."
