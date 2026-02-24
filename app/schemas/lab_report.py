from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class BatchMini(BaseModel):
    id: int
    batch_code: str
    manufacturing_location: str
    expiry_date: datetime

    class Config:
        from_attributes = True

class LabReportCreate(BaseModel):
    test_summary: str
    certifications: str | None = None
    eco_rating: int
    lab_score: float = Field(..., ge=0, le=100)


class LabReportUpdate(BaseModel):
    test_summary: Optional[str] = None
    certifications: Optional[str] = None
    eco_rating: Optional[int] = None
    lab_score: Optional[float] = Field(None, ge=0, le=100)


class LabReportResponse(BaseModel):
    id: int
    test_summary: str
    certifications: str | None
    eco_rating: int
    lab_score: float
    verified: bool
    created_at: datetime

    batch: BatchMini

    class Config:
        from_attributes = True