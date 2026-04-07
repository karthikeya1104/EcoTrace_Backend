from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class BatchMini(BaseModel):
    id: int
    batch_code: str
    manufacturing_location: str
    expiry_date: datetime

    class Config:
        from_attributes = True


class AnalysisSection(BaseModel):
    title: str
    content: str


class LabReportCreate(BaseModel):
    analysis_data: List[AnalysisSection]
    certifications: str | None = None
    notes: str | None = None
    safety_status: str = Field(..., pattern="^(safe|caution|unsafe)$")
    lab_score: float = Field(..., ge=0, le=5)


class LabReportUpdate(BaseModel):
    analysis_data: Optional[List[AnalysisSection]] = None
    certifications: Optional[str] = None
    notes: Optional[str] = None
    safety_status: Optional[str] = Field(None, pattern="^(safe|caution|unsafe)$")
    lab_score: Optional[float] = Field(None, ge=0, le=5)


class LabReportResponse(BaseModel):
    id: int
    analysis_data: List[AnalysisSection]
    certifications: str | None
    safety_status: str
    notes: str | None
    lab_score: float
    verified: bool
    created_at: datetime

    batch: BatchMini

    class Config:
        from_attributes = True