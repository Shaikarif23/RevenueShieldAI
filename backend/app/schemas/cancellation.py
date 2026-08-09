from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


# ======================================
# CREATE CANCELLATION
# ======================================

class CancellationCreate(BaseModel):
    order_id: int = Field(
        ...,
        gt=0,
        description="Order ID"
    )

    cancelled_by: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Cancelled by (CUSTOMER, RESTAURANT, DELIVERY_PARTNER)"
    )

    reason: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="Reason for cancellation"
    )

    refund_amount: float = Field(
        ...,
        ge=0,
        description="Refund amount"
    )

    cancellation_fee: float = Field(
        ...,
        ge=0,
        description="Cancellation fee"
    )


# ======================================
# UPDATE CANCELLATION
# ======================================

class CancellationUpdate(BaseModel):
    reason: str = Field(
        ...,
        min_length=5,
        max_length=500
    )

    refund_amount: float = Field(
        ...,
        ge=0
    )

    cancellation_fee: float = Field(
        ...,
        ge=0
    )


# ======================================
# CANCELLATION RESPONSE
# ======================================

class CancellationResponse(BaseModel):
    id: int
    order_id: int
    cancelled_by: str
    reason: str
    refund_amount: float
    cancellation_fee: float
    cancelled_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )