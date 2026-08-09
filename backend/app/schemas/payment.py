from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

from app.models.payment_status import PaymentStatus


# ======================================
# CREATE PAYMENT
# ======================================

class PaymentCreate(BaseModel):

    order_id: int = Field(
        ...,
        gt=0,
        description="Order ID"
    )

    payment_method: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Payment Method"
    )


# ======================================
# UPDATE PAYMENT STATUS
# ======================================

class PaymentUpdate(BaseModel):

    status: PaymentStatus


# ======================================
# PAYMENT RESPONSE
# ======================================

class PaymentResponse(BaseModel):

    id: int
    order_id: int
    amount: float
    payment_method: str
    transaction_id: str
    status: PaymentStatus
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )