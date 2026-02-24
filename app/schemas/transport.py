from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class BatchMini(BaseModel):
    id: int
    batch_code: str

    model_config = ConfigDict(from_attributes=True)

class TransportCreate(BaseModel):
    batch_id: int
    origin: str = Field(min_length=2, max_length=100)
    destination: str = Field(min_length=2, max_length=100)
    distance_km: float = Field(gt=0)
    fuel_type: str
    vehicle_type: str | None = None
    notes: str | None = None


class TransportUpdate(BaseModel):
    origin: str | None = None
    destination: str | None = None
    distance_km: float | None = Field(default=None, gt=0)
    fuel_type: str | None = None
    vehicle_type: str | None = None
    notes: str | None = None


class TransportResponse(BaseModel):
    id: int
    batch_id: int
    batch: BatchMini | None = None   # NEW
    transporter_id: int
    origin: str
    destination: str
    distance_km: float
    fuel_type: str
    vehicle_type: str | None
    transport_emission: float
    notes: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TransportListResponse(BaseModel):
    total: int
    items: list[TransportResponse]

    model_config = ConfigDict(from_attributes=True)
