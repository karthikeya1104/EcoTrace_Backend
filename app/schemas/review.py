from pydantic import BaseModel


class ReviewCreate(BaseModel):
    rating: int
    comment: str | None = None

class ReviewSummary(BaseModel):
    total_reviews: int
    average_rating: float | None = None