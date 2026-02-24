from pydantic import BaseModel, Field, computed_field, ConfigDict
from datetime import datetime
from app.models.batch import BatchStatus


# =========================
# CREATE / UPDATE
# =========================

class BatchCreate(BaseModel):
    batch_code: str = Field(..., min_length=3, max_length=50)
    manufacture_date: datetime
    expiry_date: datetime | None = None
    material_info: str | None = Field(None, max_length=500)
    manufacturing_location: str | None = Field(None, max_length=100)
    base_carbon_footprint: float | None = Field(None, ge=0)


class BatchUpdate(BaseModel):
    batch_code: str | None = Field(None, min_length=3, max_length=50)
    manufacture_date: datetime | None = None
    expiry_date: datetime | None = None
    material_info: str | None = Field(None, max_length=500)
    manufacturing_location: str | None = Field(None, max_length=100)
    base_carbon_footprint: float | None = Field(None, ge=0)


# =========================
# PRODUCT MINI (Nested)
# =========================

class ProductMini(BaseModel):
    id: int
    name: str
    brand: str

    model_config = ConfigDict(from_attributes=True)


# =========================
# RESPONSE
# =========================

class BatchResponse(BaseModel):
    id: int
    product_id: int
    batch_code: str
    status: BatchStatus
    created_at: datetime
    product: ProductMini

    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def qr_url(self) -> str:
        return f"http://localhost:5173/public/batch/{self.id}"


class BatchListResponse(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int
    items: list[BatchResponse]