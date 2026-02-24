from pydantic import BaseModel, Field
from datetime import datetime


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    brand: str | None = Field(None, max_length=100)
    category: str | None = Field(None, max_length=50)
    description: str | None = Field(None, max_length=500)


class ProductUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=100)
    brand: str | None = Field(None, max_length=100)
    category: str | None = Field(None, max_length=50)
    description: str | None = Field(None, max_length=500)


class ProductResponse(BaseModel):
    id: int
    name: str
    brand: str | None
    category: str | None
    description: str | None
    manufacturer_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class BatchMini(BaseModel):
    id: int
    batch_code: str
    created_at: datetime

    class Config:
        from_attributes = True


class ProductWithBatches(ProductResponse):
    batches: list[BatchMini] = Field(default_factory=list)