from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AnalysisResultBase(BaseModel):
    filename: str
    has_motion: bool
    processing_time_seconds: float
    error_message: Optional[str] = None

class AnalysisResultOut(AnalysisResultBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
