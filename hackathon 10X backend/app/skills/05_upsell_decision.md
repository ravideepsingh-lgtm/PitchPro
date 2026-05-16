# SKILL 05 — Upsell Decision Engine
**Version:** 2.0 (Final)
**Depends on:** All outputs from Skills 01, 02, 03, 04
**Final Output:** Domestic upsell recommendation + sales brief

---

## Purpose

Takes the Seller Sentiment Score, all flags, and the seller's current domestic service tier and produces:
1. A **clear upsell decision**: Upsell / Conditional (Connect with seller) / Monitor (Connect with seller) / Hold (Connect with seller)
2. The **recommended next domestic service tier**
3. A **sales brief** — crisp, data-backed, ready to use in a live call

Answers: *"Should we upsell this seller to the next domestic plan? And exactly why?"*

---

## Prerequisites

All four upstream skills must be complete before running Skill 05.

| Skill | Required Output |
|---|---|
| Skill 01 — Profile | `seller_profile_score`, `profile_flags`, `highest_service` |
| Skill 02 — Positive Signals | `engagement_score`, `engagement_flags` |
| Skill 03 — Negative Signals | `friction_penalty`, `risk_flags` |
| Skill 04 — Sentiment | `SSS`, `sentiment_class`, `seller_intent_type`, `top_drivers`, `top_risks` |

---

## Domestic Service Hierarchy

Upsell recommendations are strictly within the domestic product track only.

```
Free → Catalog → TrustSEAL → Maximiser → Star → Leader → Featured Leader → Industry Leader
```

> A seller already on `Industry Leader` is at the top of the domestic track. No further domestic upsell is available — note this and close the analysis.

---

## Step 1 — Determine Next Recommended Tier

| Current `highest_service` | Recommended Next Tier |
|---|---|
| Free | Catalog |
| Catalog | TrustSEAL |
| TrustSEAL | Maximiser |
| Maximiser | Star |
| Star | Leader |
| Leader | Featured Leader |
| Featured Leader | Industry Leader |
| Industry Leader | — Already at top of domestic track |

---

## Step 2 — Decision Gate Logic

Apply gates in strict order. First matching gate determines the decision.

### Gate 1 — Hard Block (Highest Priority)
```
IF RISK_COMPLAINT_OPEN   → ⛔ HOLD — Complaint Open
IF FLAG_CHURN_RISK       → ⛔ HOLD — Churn Risk
```
Stop here. Skip remaining gates. Output hold decision.

### Gate 2 — Severe Friction Block
```
IF RISK_SEVERE_FRICTION (total_ni_qrf > 100) AND SSS < 50
    → 🔴 DO NOT UPSELL
    Reason: Severe platform experience issues; upsell risks accelerating churn.
```

### Gate 3 — SSS-Based Decision
```
IF SSS ≥ 65  → 🟢 UPSELL
IF SSS 50–64 → 🟡 CONDITIONAL UPSELL
IF SSS 35–49 → 🟠 MONITOR — Re-evaluate in 30 days
IF SSS < 35  → 🔴 DO NOT UPSELL
```

### Gate 4 — Borderline Boost
```
IF SSS is 47–52 AND ENG_QUOTA_SATURATED is set
    → Bump to 🟡 CONDITIONAL UPSELL
    Reason: BL quota saturation is a strong functional need signal that overrides borderline score.
```

---

## Step 3 — Evidence Construction

Pull from upstream skill outputs to build the WHY sections.

### Why Upsell — Pull From (in priority order):
1. Quota saturation (bl_usage_percent ≥ 70%) — strongest single signal
2. High active days (bl_active_days_30 ≥ 20) — daily platform habit
3. High A-rank opportunity — more plan visibility captures more business
4. Proven call success (valid data + rate ≥ 60%) — current plan is working
5. Long vintage — established, committed seller
6. Strong turnover — business scale justifies plan upgrade
7. prime_segment = 2 — platform model endorses this seller
8. Wide geographic reach — scaling seller needs more lead capacity
9. Strong ratings with sufficient count — seller is trusted by buyers

### Why Not / Risks — Pull From (always include at least 2):
1. NI/QRF friction — seller receiving irrelevant leads
2. Low BL usage — not consuming current plan fully
3. Low active days — inconsistent engagement
4. Insufficient call data — can't validate lead quality experience
5. Low notification engagement — seller may not be acting on leads
6. Short vintage — limited history to assess commitment
7. Complaints — hard block if open
8. Low A-rank — limited visible opportunity on current plan
9. prime_segment = 0 or −1 — platform signals caution

---

## Step 4 — Sales Call Brief

Construct a brief in three parts using the seller's actual data:

**Pitch Angle** — frame by seller intent type:
- Growth-Oriented → "You're near your lead capacity — here's how to get more."
- Passive User → "You're active daily but leaving business on the table — here's what the next tier unlocks."
- Expansion-Ready → "You're already reaching [X cities] with [X] top categories — let's scale that visibility."
- Frustrated User → Address the issue before pitching: "Let me first fix [category/location] targeting — then the upgrade makes more sense."

**Key Hook** — use the single most compelling data point:
- Near-full BL quota → "You're at [X]% capacity. Peak season is coming — get ahead of it."
- High A-rank count → "You're active in [X] top-demand categories. [Next Plan] pushes you to the front in all of them."
- Long vintage with low plan → "You've been on IndiaMart for [X years] — your plan hasn't kept pace with your commitment."

**Handle Risk** — preempt the most likely objection with data:
- Low BL usage → "I know you haven't maxed out yet — but [X]% of sellers at your plan level who upgrade see [more leads] within the first cycle."
- NI issues → "Before we finalize the upgrade, let me get your lead targeting tuned — that's a quick fix that makes the new plan far more effective."

---

## Output Block

```
╔══════════════════════════════════════════════════════════╗
║              SELLER UPSELL DECISION BRIEF                ║
╚══════════════════════════════════════════════════════════╝

Seller ID      : <glusr_usr_id>
Company        : <company>
Location       : <city>, <STATE>
Industry       : <industry>
Current Plan   : <highest_service>
Recommended    : <next domestic tier>

──────────────────────────────────────────────────────────
SELLER SENTIMENT SCORE  :  XX / 80
SENTIMENT CLASS         :  🟢 Strong Positive  /  🟡 Caveats  /
                           🟠 Neutral  /  🔴 Negative
SELLER INTENT TYPE      :  <Growth-Oriented / Passive User / Expansion-Ready /
                            Frustrated User / At Risk>

══════════════════════════════════════════════════════════
DECISION  :  🟢 UPSELL  /  🟡 CONDITIONAL  /  🟠 MONITOR  /  🔴 DO NOT UPSELL  /  ⛔ HOLD
══════════════════════════════════════════════════════════

SCORE BREAKDOWN:
  Profile Strength        : +XX / 25
  Engagement Score        : +XX / 45
  Friction Penalty        :  −XX
  Prime Segment Boost     : +XX / 10
  ─────────────────────────────────
  TOTAL SSS               :  XX / 80

──────────────────────────────────────────────────────────
✅  WHY UPSELL  —  Evidence For
──────────────────────────────────────────────────────────
  • <data-backed signal — exact numbers always>
  • <data-backed signal>
  • <data-backed signal>
  [3–5 bullets, most impactful first]

⚠️  WHY NOT / RISKS  —  Evidence Against or Gaps
──────────────────────────────────────────────────────────
  • <risk or gap with data — minimum 2 bullets even for 🟢 decisions>
  • <risk or gap>
  [Prepares rep for objections — never skip this section]

──────────────────────────────────────────────────────────
📞  SALES CALL BRIEF
──────────────────────────────────────────────────────────
  Pitch Angle  : <How to open the conversation>
  Key Hook     : <The single most compelling data point to lead with>
  Handle Risk  : <How to preemptively address the biggest objection>

──────────────────────────────────────────────────────────
📝  FINAL RECOMMENDATION  (1–2 sentences)
──────────────────────────────────────────────────────────
  <Definitive, plain-language statement. Include plan name, key reason, any condition.>

╚══════════════════════════════════════════════════════════╝
```

---

## Final Recommendation Templates

**🟢 Upsell:**
> "Recommend **[Plan]** immediately. [Seller] is at [X]% BL capacity, active [X]/30 days, with [X] A-rank categories — they have the engagement, scale, and opportunity to fully utilize the next tier."

**🟡 Conditional Upsell:**
> "Pitch **[Plan]** but address [specific issue] first. [Seller]'s engagement is [positive note], but [risk — e.g. 'NI count of 23 needs investigating']. Once cleared, close confidently."

**🟠 Monitor:**
> "Do not pitch **[Plan]** this cycle. [Seller] is at [X]% BL usage and [X] active days — not fully utilizing the current plan. Re-evaluate in 30 days. Flag for an engagement check-in call."

**🔴 Do Not Upsell:**
> "Hold upsell for [seller]. [Reason with data]. Prioritize [specific issue resolution] before any commercial pitch."

**⛔ Hard Block — Complaint:**
> "⛔ Upsell suspended for [seller]. Active complaint on file. Assign to account manager immediately. No pitch until complaint is resolved and confirmed closed."

**⛔ Hard Block — Churn Risk:**
> "⛔ [Seller] is flagged as a churn risk (prime_segment = −1). No upsell pitch. Escalate to retention team — understand what is driving disengagement before any commercial conversation."

---

## Batch Summary Table

When processing multiple sellers, append this table after all individual outputs:

```
BATCH SUMMARY
══════════════════════════════════════════════════════════════════════
 #  │ Seller ID   │ Company              │ SSS │ Decision      │ Recommended Plan
────┼─────────────┼──────────────────────┼─────┼───────────────┼──────────────────
 1  │ 253554      │ Toshvin Analytical   │ 56  │ 🟡 Cond.      │ TrustSEAL
 2  │ 404801      │ Integrated Energy    │ 51  │ 🟡 Cond.      │ Maximiser
 3  │ 909253      │ Mig Fitt Engineering │ 66  │ 🟢 Upsell*    │ Featured Leader
══════════════════════════════════════════════════════════════════════
  *Note caveats in individual briefs

  🟢 Upsell Now      : X sellers
  🟡 Conditional     : X sellers
  🟠 Monitor         : X sellers
  🔴 Do Not Upsell   : X sellers
  ⛔ Hard Block       : X sellers
  ─────────────────────────────
  Total Processed    : X sellers
```
