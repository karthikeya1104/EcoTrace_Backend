from pydantic import BaseModel, Field, computed_field, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.models.batch import BatchStatus
from app.core.config import APP_BASE_URL


# =========================
# CREATE / UPDATE
# =========================

class BatchMaterialInput(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    percentage: float
    source: Optional[str] = None


class BatchCreate(BaseModel):
    batch_code: str = Field(..., min_length=3, max_length=50)
    manufacture_date: datetime
    expiry_date: Optional[datetime] = None
    materials: Optional[List[BatchMaterialInput]] = None
    manufacturing_location: Optional[str] = Field(None, max_length=100)
    base_carbon_footprint: Optional[float] = Field(None, ge=0)


class BatchUpdate(BaseModel):
    batch_code: Optional[str] = Field(None, min_length=3, max_length=50)
    manufacture_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    materials: Optional[List[BatchMaterialInput]] = None
    manufacturing_location: Optional[str] = Field(None, max_length=100)
    base_carbon_footprint: Optional[float] = Field(None, ge=0)


# =========================
# PRODUCT MINI (Nested)
# =========================

class ProductMini(BaseModel):
    id: int
    name: str
    brand: str

    model_config = ConfigDict(from_attributes=True)


# =========================
# MATERIALS (Nested Correctly)
# =========================

class MaterialMini(BaseModel):
    id: int
    name: str
    common_name: Optional[str] = None
    risk_level: Optional[str] = None
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class BatchMaterialResponse(BaseModel):
    id: int
    percentage: float
    source_country: Optional[str] = None
    source_info_provided: bool
    material: MaterialMini

    model_config = ConfigDict(from_attributes=True)


# =========================
# RESPONSE
# =========================

class BatchListItem(BaseModel):
    id: int
    batch_code: str
    manufacture_date: datetime
    expiry_date: Optional[datetime]
    status: BatchStatus
    created_at: datetime

    product: ProductMini  # keep minimal product info

    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def qr_url(self) -> str:
        return f"{APP_BASE_URL}/public/batch/{self.id}"


class BatchResponse(BaseModel):
    id: int
    product_id: int
    batch_code: str
    manufacture_date: datetime
    expiry_date: Optional[datetime]
    manufacturing_location: Optional[str]
    base_carbon_footprint: Optional[float]
    status: BatchStatus
    created_at: datetime

    product: ProductMini
    materials: List[BatchMaterialResponse]

    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def qr_url(self) -> str:
        return f"{APP_BASE_URL}/public/batch/{self.id}"


# =========================
# PAGINATED RESPONSE
# =========================

class BatchListResponse(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int
    items: List[BatchListItem]