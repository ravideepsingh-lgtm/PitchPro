# Intelligent Recommendation System Backend

A robust, production-style Python backend system for intelligent recommendation and prediction generation using structured enterprise Excel datasets.

## Architecture

This project follows a modular Service-Oriented Architecture (SOA):
- **API Layer**: `FastAPI` handles routing, validation, and serialization.
- **Service Layer**:
  - `data_service`: Handles Excel ingestion, merging on `glusr_usr_id`, and caching.
  - `feature_service`: Handles categorical normalization and numeric scaling.
  - `search_service`: Uses `scikit-learn` NearestNeighbors for cosine similarity search.
  - `prompt_builder`: Constructs dynamic LLM prompts.
  - `llm_service`: Integrates with an OpenAI-compatible API gateway.
- **Data Layer**: In-memory caching for now. Highly extensible to PostgreSQL/Redis later.

## Setup Instructions

1. **Clone the repository** (if applicable) and navigate to the root directory.

2. **Create a Virtual Environment** (Recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**:
   Update the `.env` file with your specific configurations.
   ```env
   OPENAI_API_KEY=sk-your-key-here
   OPENAI_BASE_URL=https://api.openai.com/v1
   LLM_MODEL=openrouter/qwen/qwen3-32b
   DATA_DIR=data
   TOP_K_SIMILAR=5
   ```

5. **Place Data Files**:
   Drop your Excel sheets into the `data/` folder. Currently, the code expects:
   - `sample_customers.xlsx`
   - `sample_companies.xlsx`
   - `sample_outcomes.xlsx`
   (Update `app/services/data_service.py` when exact filenames are known).

6. **Run the Application**:
   ```bash
   python -m app.main
   ```
   Or using uvicorn directly:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## API Usage Example

### 1. Load Data & Build Index
Initialize the system by loading the Excel files into memory and building the similarity index.

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/load-data
```
**Response:**
```json
{
  "status": "success",
  "master_rows": 3,
  "outcomes_rows": 2,
  "message": null
}
```

### 2. Predict / Recommend
Get a prediction and recommendation for a specific `glusr_usr_id`.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
     -H "Content-Type: application/json" \
     -d '{"glusr_usr_id": 1}'
```
**Response:**
```json
{
  "prediction": "High Success Probability",
  "explanation": "Based on similar historical cases, companies with this size and profile succeeded.",
  "recommendation": "Proceed with Plan A.",
  "reasoning": "Historical case 1 matched 98% and found Plan A highly effective.",
  "confidence_score": 0.92,
  "similar_cases_retrieved": 5,
  "similar_cases": [
    {
      "glusr_usr_id": 2,
      "similarity_score": 0.98,
      "company_data": {
         "glusr_usr_id": 2,
         "company_size": "Small",
         "name": "Bob"
      },
      "historical_outcome": {
         "outcome": "Success",
         "historical_recommendation": "Plan A"
      }
    }
  ]
}
```
