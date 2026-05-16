from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class PredictRequest(BaseModel):
    glusr_usr_id: Optional[int] = None
    company_data: Optional[Dict[str, Any]] = None

class ProfileAnalysisRequest(BaseModel):
    glusr_usr_id: int

class ProfileAnalysisResponse(BaseModel):
    status: str
    glusr_usr_id: Optional[int] = None
    profile_data_used: Optional[Dict[str, Any]] = None
    analysis: Optional[Dict[str, Any]] = None
    message: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    message: str

class LoadDataResponse(BaseModel):
    status: str
    master_rows: Optional[int] = 0
    outcomes_rows: Optional[int] = 0
    message: Optional[str] = None
