# SKILL 02 — Positive Signals Analyzer
**Version:** 2.0 (Final)
**Used by:** Skill 04 — Sentiment Analysis
**Output feeds into:** `engagement_score` (0–45) + `engagement_flags`

---

## Purpose

Reads all seller platform activity and engagement signals and produces:
1. An **Engagement Score** (0–45 points)
2. Engagement flags that indicate upsell readiness

Answers: *"How actively and effectively is this seller using IndiaMart today?"*

---

## Input Fields

| Field | Description |
|---|---|
| `bl_active_days_30` | Days active on IndiaMart in last 30 days |
| `bl_usage_percent` | % of Buy Lead quota consumed (string e.g. "75%") |
| `total_consumed` | Absolute BL count consumed |
| `success_call` | Count of successful calls |
| `call_success_percent` | % of calls that were successful (string e.g. "60%") |
| `bl_notif_open` | Count of notifications opened |
| `bl_notif_open_percent` | % of notifications opened (string e.g. "40%") |
| `rank_a_mcat` | Count of A-rank macro categories |
| `rank_d_mcat` | Count of D-rank macro categories |
| `high_sold_a_rank` | A-rank count from high-sold categories (subset of rank_a_mcat) |
| `high_sold_d_rank` | D-rank count from high-sold categories |
| `major_cities` | Count of major cities seller is active in |

---

## Pre-Processing Rules — Apply Before Scoring

These fields are valid only if minimum thresholds are met. If not met, set to NULL and do NOT score.

| Field | Minimum Threshold to Score | If Not Met |
|---|---|---|
| `call_success_percent` | `success_call >= 10` | Mark as "Insufficient call data" — score 0 |
| `bl_notif_open_percent` | `bl_notif_open >= 10` | Mark as "Insufficient notification data" — score 0 |

> **Parse percentage strings:** Strip "%" and convert to float before all comparisons.
> e.g. "75%" → 75.0, "39%" → 39.0

---

## Scoring Rules — Engagement Score (Max 45)

### 1. Platform Activity — Active Days (Max 10 pts)

| `bl_active_days_30` | Points | Label |
|---|---|---|
| ≥ 25 days | +10 | Highly Active |
| ≥ 20 days | +8 | Active |
| ≥ 15 days | +5 | Moderately Active |
| ≥ 10 days | +3 | Occasionally Active |
| < 10 days | 0 | Low Activity |

### 2. Buy Lead Consumption (Max 10 pts)

| `bl_usage_percent` (parsed) | Points | Label |
|---|---|---|
| ≥ 90% | +10 | Quota exhausted — needs more capacity |
| ≥ 70% | +8 | High utilization |
| ≥ 50% | +5 | Moderate utilization |
| ≥ 30% | +3 | Below average |
| < 30% | 0 | Not utilizing plan |

> If bl_usage_percent ≥ 85%, add note in output: *"Seller is near quota capacity — strong functional need for upgrade."*

### 3. Call Performance (Max 8 pts)

> Only score if `success_call >= 10`. Otherwise score = 0, note "Insufficient call data."

| `call_success_percent` (parsed) | Points | Label |
|---|---|---|
| ≥ 75% | +8 | Excellent conversion |
| ≥ 60% | +6 | Strong conversion |
| ≥ 45% | +4 | Average |
| ≥ 30% | +2 | Below average |
| < 30% | 0 | Poor call quality |

### 4. Notification Engagement (Max 5 pts)

> Only score if `bl_notif_open >= 10`. Otherwise score = 0, note "Insufficient notification data."

| `bl_notif_open_percent` (parsed) | Points | Label |
|---|---|---|
| ≥ 60% | +5 | Highly responsive |
| ≥ 40% | +4 | Engaged |
| ≥ 25% | +3 | Moderately engaged |
| ≥ 10% | +1 | Low engagement |
| < 10% | 0 | Not responsive |

### 5. Category Opportunity — A & D Rank (Max 12 pts)

**A-Rank Score (Max 7 pts):**

| `rank_a_mcat` | Points |
|---|---|
| ≥ 50 | +7 |
| ≥ 30 | +6 |
| ≥ 15 | +5 |
| ≥ 8 | +3 |
| ≥ 3 | +1 |
| < 3 | 0 |

**High-Sold A-Rank Bonus (Max 5 pts — additive):**

| `high_sold_a_rank` | Points |
|---|---|
| ≥ 30 | +5 |
| ≥ 15 | +4 |
| ≥ 10 | +3 |
| ≥ 5 | +2 |
| < 5 | 0 |

> `high_sold_a_rank` is a subset of `rank_a_mcat` — weighted more heavily because it confirms actual market demand alignment, not just category listing.

**D-Rank — Supplementary Note (no direct points):**
- If `rank_d_mcat > 20` → add to output commentary: *"High D-rank count signals additional uncaptured opportunity on platform."*

### 6. Geographic Reach — Major Cities (Max 5 pts)

| `major_cities` | Points | Label |
|---|---|---|
| ≥ 30 | +5 | Pan-India reach |
| ≥ 15 | +4 | Multi-region |
| ≥ 10 | +3 | Multi-city |
| ≥ 5 | +2 | Regional |
| < 5 | 0 | Hyper-local |

> **Cap total Engagement Score at 45.**

---

## Engagement Flags Generated

| Flag | Condition | Meaning |
|---|---|---|
| `ENG_QUOTA_SATURATED` | bl_usage_percent ≥ 85% | Near full capacity — functional need for more leads |
| `ENG_HIGHLY_ACTIVE` | bl_active_days_30 ≥ 20 | Daily platform habit established |
| `ENG_STRONG_CALLS` | success_call ≥ 10 AND call_success_percent ≥ 60% | Call quality is proven |
| `ENG_NOTIF_RESPONSIVE` | bl_notif_open ≥ 10 AND bl_notif_open_percent ≥ 40% | Seller acts on platform alerts |
| `ENG_HIGH_OPPORTUNITY` | rank_a_mcat ≥ 15 OR high_sold_a_rank ≥ 10 | Large category opportunity visible |
| `ENG_WIDE_REACH` | major_cities ≥ 10 | Geographic breadth — scaling seller |

---

## Output Block

```
SKILL 02 — POSITIVE ENGAGEMENT SIGNALS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Platform Activity:
  Active Days (last 30)  : <bl_active_days_30> days  → [Label]      [+X pts]
  BL Usage               : <bl_usage_percent>         → [Label]      [+X pts]
  BL Consumed (count)    : <total_consumed>

Call Performance:
  Success Calls          : <success_call>
  Call Success Rate      : <call_success_percent>     → [Label / Insufficient data]  [+X pts]

Notification Behavior:
  Notifs Opened          : <bl_notif_open>
  Notif Open Rate        : <bl_notif_open_percent>    → [Label / Insufficient data]  [+X pts]

Category Opportunity:
  A-Rank Categories      : <rank_a_mcat>              → [Label]      [+X pts]
  High-Sold A-Rank       : <high_sold_a_rank>                        [+X pts]
  D-Rank Categories      : <rank_d_mcat>              → [Note if >20]
  High-Sold D-Rank       : <high_sold_d_rank>

Geographic Reach:
  Major Cities Active    : <major_cities>             → [Label]      [+X pts]

ENGAGEMENT SCORE : XX / 45

Engagement Flags: [ENG_QUOTA_SATURATED] [ENG_HIGHLY_ACTIVE] [ENG_HIGH_OPPORTUNITY] ...
                  (NONE if no flags triggered)

Top Engagement Insights:
  • <most impactful positive signal with actual numbers>
  • <second signal with actual numbers>
  • <third signal or note on a gap>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Insight Writing Rules

Always data-specific, never generic.

**Good:** "BL usage at 87% — seller is near quota exhaustion and needs more lead capacity."
**Good:** "27 of 30 active days — near-daily login habit; platform is central to this seller's workflow."
**Good:** "96 A-rank + 81 high-sold A-rank — massive opportunity that more visibility will directly convert."
**Bad:** "Seller has good engagement." (no data)

---

## Historical Benchmarks (from 223 converted sellers)

| Metric | Avg in Converted Sellers | Strong Threshold |
|---|---|---|
| `bl_active_days_30` | 21 days | ≥ 20 days |
| `bl_usage_percent` | 57% | ≥ 50% |
| `rank_a_mcat` | 18 | ≥ 15 |
| `major_cities` | varies | ≥ 10 = strong |
