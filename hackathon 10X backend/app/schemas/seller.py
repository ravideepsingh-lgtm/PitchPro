from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class BatchProfileRequest(BaseModel):
    limit: int = 100
    offset: int = 0
    glids: Optional[List[int]] = None
    save_output: bool = True
    dry_run: bool = False

class BatchProfileResponse(BaseModel):
    success: bool
    total_glids_available: int
    processed_count: int
    error_count: int
    offset: int
    limit: int
    results: List[Dict[str, Any]]
    errors: List[Dict[str, Any]]
    output_path: Optional[str] = None
    
class LoadDataResponse(BaseModel):
    success: bool
    files_loaded: List[str]
    total_sellers: int

class SellerAnalyzeRequest(BaseModel):
    glid: int
    dry_run: bool = False

class SellerAnalyzeResponse(BaseModel):
    success: bool
    glid: int
    source: Dict[str, Any]
    loaded_skills: Optional[Dict[str, str]] = None
    agents: Dict[str, Any]
    final_analysis: Dict[str, Any]
