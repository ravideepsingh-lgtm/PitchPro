from fastapi import APIRouter, HTTPException
from app.orchestration.batch_profile_orchestrator import batch_orchestrator
from app.schemas.seller import BatchProfileRequest, BatchProfileResponse

router = APIRouter()

@router.post("/profile", response_model=BatchProfileResponse)
async def run_batch_profile(request: BatchProfileRequest):
    """
    Runs the Profile Status Agent in batch mode over multiple GLIDs.
    """
    result = await batch_orchestrator.run_batch(
        limit=request.limit,
        offset=request.offset,
        glids=request.glids,
        save_output=request.save_output,
        dry_run=request.dry_run
    )
    return BatchProfileResponse(**result)

@router.post("/profile/dry-run", response_model=BatchProfileResponse)
async def run_batch_profile_dry_run(request: BatchProfileRequest):
    """
    Runs the Batch Profile in Dry Run mode (no LLM calls).
    """
    request.dry_run = True
    result = await batch_orchestrator.run_batch(
        limit=request.limit,
        offset=request.offset,
        glids=request.glids,
        save_output=request.save_output,
        dry_run=True
    )
    return BatchProfileResponse(**result)
