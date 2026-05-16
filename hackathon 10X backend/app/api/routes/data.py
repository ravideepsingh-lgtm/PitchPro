from fastapi import APIRouter
from app.data.excel_loader import excel_loader
from app.data.seller_repository import seller_repository
from app.schemas.seller import LoadDataResponse

router = APIRouter()

@router.post("/load", response_model=LoadDataResponse)
def load_data():
    """
    Loads Excel files from configured folder, normalizes columns, and caches data in memory.
    """
    loaded_files = excel_loader.load_all()
    total_sellers = seller_repository.get_total_count()
    
    return LoadDataResponse(
        success=True,
        files_loaded=loaded_files,
        total_sellers=total_sellers
    )
