from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


# ======================================
# CREATE REVIEW
# ======================================

class ReviewCreate(BaseModel):

    order_id: int = Field(
        ...,
        gt=0,
        description="Order ID"
    )

    rating: int = Field(
        ...,
        ge=1,
        le=5,
        description="Rating between 1 and 5"
    )

    comment: str | None = Field(
        default=None,
        max_length=500,
        description="Customer review"
    )


# ======================================
# UPDATE REVIEW
# ======================================

class ReviewUpdate(BaseModel):

    rating: int = Field(
        ...,
        ge=1,
        le=5
    )

    comment: str | None = Field(
        default=None,
        max_length=500
    )


# ======================================
# REVIEW RESPONSE
# ======================================

class ReviewResponse(BaseModel):

    id: int
    order_id: int
    customer_id: int
    restaurant_id: int
    rating: int
    comment: str | None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )