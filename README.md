# PitchPro

Ab andaza nahi, smart pitch hogi.

PitchPro is a full-stack seller upsell recommendation app. It combines a React + Vite frontend with a FastAPI backend that loads seller Excel data, runs a five-skill upsell analysis pipeline, and returns a clear sales recommendation for a selected GLID.

The repository contains both projects together:

```text
PitchPro/
|-- hackathon 10X/              # Frontend: React + Vite dashboard
|-- hackathon 10X backend/      # Backend: FastAPI + seller analysis agents
|-- .gitignore                  # Shared ignore rules for secrets/data/build files
`-- README.md                   # This GitHub setup guide
```

## What The App Does

- Shows seller/service segments in the frontend dashboard.
- Lets a user select a seller and click `Analyze`.
- Calls the backend endpoint `POST /api/seller/analyze`.
- Runs seller profile, positive signal, negative signal, sentiment, and upsell decision analysis.
- Displays `response.final_analysis` clearly in the UI:
  - upsell decision
  - current plan
  - recommended next tier
  - sentiment score
  - score breakdown
  - upsell reasons
  - risks
  - sales call brief
  - final recommendation

## Internal Source References

The original local/internal skills README is stored at:

```text
G:\.shortcut-targets-by-id\1iJjMP2iLsOSP_ZuLA_P96PJqppjOnxoI\BJP (Beyond Just Product) - 10X Productivity\Skills\README.md
```

The important content from that skills README is included below in the **Skill System** section so GitHub users can understand the pipeline without needing access to the internal Drive path.

## Prerequisites

Install these before running the project:

- Git
- Node.js 20 or newer
- Python 3.11
- Access to the private seller Excel data files
- An OpenAI-compatible LLM API key and base URL

## Data Files

The seller Excel data is required for real analysis, but the actual data files are not committed to GitHub.

Reasons:

- They may contain private seller/client information.
- They may be large.
- They should be shared only through approved internal channels.

Download the data files from the shared Drive link:

```text
DATA_DRIVE_LINK_HERE
```

After downloading, place the data files here:

```text
hackathon 10X backend/data/
```

The backend currently searches for an Excel file whose name contains:

```text
Paid Clients
```

Example:

```text
Paid Clients 20260515.xlsb
```

The backend reads this sheet:

```text
Client Base
```

If the filename changes, either keep `Paid Clients` in the filename or update the loader:

```text
hackathon 10X backend/app/data/excel_loader.py
```

## Environment Variables

Do not commit actual `.env` files or real secret values.

The backend includes:

```text
hackathon 10X backend/.env.example
```

Create your local env file:

```powershell
cd "C:\path\to\PitchPro\hackathon 10X backend"
copy .env.example .env
```

Required env keys:

```env
EXCEL_DATA_FOLDER=./data
OPENAI_BASE_URL=your-openai-compatible-base-url
OPENAI_API_KEY=your-api-key
OPENAI_MODEL=your-model-name
MAX_CONCURRENT_LLM_CALLS=5
BATCH_SIZE=100
```

Notes:

- `EXCEL_DATA_FOLDER` should point to the folder containing the Excel data files.
- `OPENAI_BASE_URL` should be the LLM gateway or OpenAI-compatible endpoint.
- `OPENAI_API_KEY` must be set locally only.
- `OPENAI_MODEL` should match the model available on your gateway.
- `.env` is ignored by Git.

## Backend Setup

Open a terminal:

```powershell
cd "C:\path\to\PitchPro\hackathon 10X backend"
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Check backend health:

```powershell
Invoke-WebRequest http://localhost:8000/health
```

Expected response:

```json
{"status":"ok"}
```

Load the Excel data into backend memory:

```powershell
Invoke-WebRequest -Method POST http://localhost:8000/api/data/load
```

## Frontend Setup

Open a second terminal:

```powershell
cd "C:\path\to\PitchPro\hackathon 10X"
npm install
npm run dev
```

Open the frontend:

```text
http://localhost:5173
```

The frontend uses the Vite proxy in:

```text
hackathon 10X/vite.config.js
```

During local development:

```text
/api    -> http://localhost:8000
/health -> http://localhost:8000
```

## Main API

Analyze one seller:

```powershell
Invoke-WebRequest `
  -Method POST `
  -Uri http://localhost:8000/api/seller/analyze `
  -ContentType "application/json" `
  -Body '{"glid":236,"dry_run":false}'
```

Request body:

```json
{
  "glid": 236,
  "dry_run": false
}
```

The frontend primarily uses:

```text
response.final_analysis
```

Response shape:

```json
{
  "success": true,
  "glid": 236,
  "source": {
    "primary_file": "Paid Clients 20260515.xlsb",
    "primary_sheet": "Client Base",
    "data_folder": "./data"
  },
  "loaded_skills": {
    "seller_profile": "SKILL 01 - Seller Profile Analyzer",
    "positive_signals": "SKILL 02 - Positive Signals Analyzer",
    "negative_signals": "SKILL 03 - Negative Signals Analyzer",
    "sentiment_analysis": "SKILL 04 - Seller Sentiment Analysis",
    "upsell_decision": "SKILL 05 - Upsell Decision Engine"
  },
  "agents": {
    "seller_profile": {},
    "positive_signals": {},
    "negative_signals": {},
    "sentiment_analysis": {},
    "upsell_decision": {}
  },
  "final_analysis": {
    "glusr_usr_id": "236",
    "decision": "UPSELL",
    "recommended_next_tier": "Leader",
    "current_plan": "Star",
    "seller_sentiment_score": 80,
    "sentiment_class": "Strong Positive",
    "seller_intent_type": "Growth-Oriented",
    "score_breakdown": {
      "profile_strength": 25,
      "engagement_score": 45,
      "friction_penalty": 0,
      "prime_segment_boost": 10,
      "total_sss": 80
    },
    "why_upsell": [],
    "why_not_risks": [],
    "sales_call_brief": {
      "pitch_angle": "",
      "key_hook": "",
      "handle_risk": ""
    },
    "final_recommendation": ""
  }
}
```

## Skill System

The backend uses a five-skill system for IndiaMart seller upsell recommendations. The scope is domestic products only.

Pipeline:

```text
Seller raw data
  |
  |-- Skill 01: Seller Profile Analyzer
  |-- Skill 02: Positive Signals Analyzer
  |-- Skill 03: Negative Signals Analyzer
  |
  `-- Skill 04: Seller Sentiment Analysis
          |
          `-- Skill 05: Upsell Decision Engine
```

### Skills Index

| # | Skill | What It Does | Output |
|---|---|---|---|
| 01 | Seller Profile Analyzer | Evaluates business identity, compliance, and scale | Profile score 0 to 25 plus profile flags |
| 02 | Positive Signals Analyzer | Evaluates platform engagement and seller behavior | Engagement score 0 to 45 plus engagement flags |
| 03 | Negative Signals Analyzer | Evaluates NI/QRF friction, complaints, and mismatch risk | Friction penalty 0 to -20 plus risk flags |
| 04 | Seller Sentiment Analysis | Combines profile, engagement, friction, and segment boost | SSS 0 to 80, sentiment class, intent type |
| 05 | Upsell Decision Engine | Makes final go/no-go decision and prepares sales brief | Upsell/Hold, recommended tier, call brief |

### Score Composition

| Component | Skill | Points |
|---|---|---|
| Profile Strength | Skill 01 | 0 to +25 |
| Engagement Score | Skill 02 | 0 to +45 |
| Friction Penalty | Skill 03 | 0 to -20 |
| Prime Segment Boost | Skill 04 | 0 to +10 |
| Total SSS | Combined | 0 to 80 |

### Decision Outcomes

| Decision | Trigger | Action |
|---|---|---|
| Upsell | SSS >= 65 and no blocks | Pitch next domestic tier now |
| Conditional | SSS 50 to 64 | Pitch with conditions; address gaps first |
| Monitor | SSS 35 to 49 | No pitch this cycle; re-evaluate in 30 days |
| Do Not Upsell | SSS < 35 or severe friction | Hold; seller is not ready |
| Hard Block | Complaint open or churn risk | Suspend upsell activity |

### Domestic Service Hierarchy

```text
Free -> Catalog -> TrustSEAL -> Maximiser -> Star -> Leader -> Featured Leader -> Industry Leader
```

Skill 05 always recommends the immediate next tier only. It should not skip tiers.

### Profile Flags

| Flag | Trigger |
|---|---|
| `FLAG_NO_GST` | `gst = 0` |
| `FLAG_CHURN_RISK` | `prime_segment = -1`; hard block |
| `FLAG_NEW_SELLER` | `client_vintage_days < 180` |
| `FLAG_LOW_RATING` | `avg_ratings < 3.5` with at least 10 ratings |
| `FLAG_HIGH_SCALE` | Turnover >= 5 Cr |

### Engagement Flags

| Flag | Trigger |
|---|---|
| `ENG_QUOTA_SATURATED` | `bl_usage_percent >= 85%` |
| `ENG_HIGHLY_ACTIVE` | `bl_active_days_30 >= 20` |
| `ENG_STRONG_CALLS` | `success_call >= 10` and `call_success_percent >= 60%` |
| `ENG_NOTIF_RESPONSIVE` | `bl_notif_open >= 10` and `bl_notif_open_percent >= 40%` |
| `ENG_HIGH_OPPORTUNITY` | `rank_a_mcat >= 15` or `high_sold_a_rank >= 10` |
| `ENG_WIDE_REACH` | `major_cities >= 10` |

### Risk Flags

| Flag | Trigger |
|---|---|
| `RISK_COMPLAINT_OPEN` | `complaints_count >= 1`; hard block |
| `RISK_HIGH_NI` | `total_ni_qrf > 50` |
| `RISK_CATEGORY_MISMATCH` | `wrong_category_ni_qrf > 15` |
| `RISK_LOCATION_MISMATCH` | `location_ni_qrf > 15` |
| `RISK_RETAIL_MISMATCH` | `retail_ni_qrf > 15` |
| `RISK_SEVERE_FRICTION` | `total_ni_qrf > 100`; hard block when SSS < 50 |

### Key Rules

1. `prime_segment = -1` means churn risk. Do not upsell; route to retention.
2. `complaints_count >= 1` is a hard block. Resolve complaints first.
3. `total_ni_qrf <= 10` means NI/QRF data is noise. Do not score or comment on it.
4. `success_call < 10` means call data is unreliable. Do not score `call_success_percent`.
5. `bl_notif_open < 10` means notification data is unreliable. Do not score `bl_notif_open_percent`.
6. Recommend domestic service tiers only.
7. Recommend the immediate next tier only. Do not skip tiers.
8. Always include a why-not or risk section, even for upsell decisions.

### Historical Benchmarks

Based on 223 converted sellers:

| Metric | Average | Strong Threshold |
|---|---|---|
| GST available | 100% | Must have |
| `bl_active_days_30` | 21 days | >= 20 days |
| `bl_usage_percent` | 57% | >= 50% |
| `rank_a_mcat` | 18 | >= 15 |
| `total_ni_qrf > 10` | 8% of cases | If > 10, apply friction scoring |
| complaints | 0% of cases | Any complaint is a hard block |

## Git And Secrets

These files/folders are intentionally ignored:

- `.env` and other local environment files
- `node_modules/`
- `venv/`
- frontend `dist/`
- backend `outputs/`
- Excel and bulky data files such as `.xlsb`, `.xlsx`, `.csv`, `.parquet`, `.pkl`, `.db`
- Python cache files

Before pushing to GitHub:

```powershell
git status --short
```

If any private data file or `.env` file appears in the staged list, stop and fix `.gitignore` before pushing.

## Useful Commands

Frontend build:

```powershell
cd "hackathon 10X"
npm run build
```

Frontend lint:

```powershell
cd "hackathon 10X"
npm run lint
```

Backend run:

```powershell
cd "hackathon 10X backend"
.\venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Troubleshooting

If the frontend shows an API error, confirm the backend is running on port `8000`.

If seller analysis says the `Client Base` sheet is not loaded, call:

```powershell
Invoke-WebRequest -Method POST http://localhost:8000/api/data/load
```

If Git says the repo has unsafe ownership:

```powershell
git config --global --add safe.directory C:/hackathon
```

If data does not load, check:

- `.env` has `EXCEL_DATA_FOLDER=./data`
- the Excel file is inside `hackathon 10X backend/data/`
- the file name contains `Paid Clients`
- the workbook contains the `Client Base` sheet
