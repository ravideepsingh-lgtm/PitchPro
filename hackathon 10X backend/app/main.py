import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health, data, batch, seller

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Agentic Upsell Recommendation API",
    description="Backend API for predicting and recommending actions using a multi-agent architecture.",
    version="2.0.0"
)

# Allow CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(data.router, prefix="/api/data", tags=["Data Pipeline"])
app.include_router(batch.router, prefix="/api/batch", tags=["Batch Orchestration"])
app.include_router(seller.router, prefix="/api/seller", tags=["Seller Features"])

@app.on_event("startup")
async def startup_event():
    logger.info("Agentic Pipeline Application starting up...")
    logger.info("Call /api/data/load to initialize datasets from the EXCEL_DATA_FOLDER.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
