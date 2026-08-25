from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.payment_status import PaymentStatus


class PaymentCreate(BaseModel):
    order_id: int = Field(..., gt=0)
    amount: float = Field(..., gt=0)
    payment_method: str = Field(..., min_length=2, max_length=50)


class PaymentUpdate(BaseModel):
    status: PaymentStatus


class PaymentResponse(BaseModel):
    id: int
    order_id: int
    amount: float
    payment_method: str
    transaction_id: str
    status: PaymentStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
