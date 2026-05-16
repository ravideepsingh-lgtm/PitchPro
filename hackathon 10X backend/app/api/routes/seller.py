from fastapi import APIRouter, HTTPException
from app.data.feature_builder import feature_builder
from app.orchestration.batch_profile_orchestrator import batch_orchestrator
from app.schemas.seller import SellerAnalyzeRequest, SellerAnalyzeResponse
from typing import Dict, Any

router = APIRouter()

@router.get("/{glusr_usr_id}/features", response_model=Dict[str, Any])
def get_seller_features(glusr_usr_id: int):
    """
    Returns the compact seller feature JSON before agent execution.
    """
    try:
        features = feature_builder.build(glusr_usr_id)
        return features
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze", response_model=SellerAnalyzeResponse)
async def analyze_seller(request: SellerAnalyzeRequest):
    """
    Runs the five skill-backed agents for one GLID using Client Base as the primary source.
    """
    try:
        result = await batch_orchestrator.analyze_single_glid(
            glid=request.glid,
            dry_run=request.dry_run
        )
        return SellerAnalyzeResponse(**result)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
