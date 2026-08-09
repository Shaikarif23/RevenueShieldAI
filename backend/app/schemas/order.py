from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from app.models.order_status import OrderStatus


# ======================================
# CREATE ORDER ITEM INPUT
# ======================================

class OrderItemInput(BaseModel):
    menu_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1, le=100)


# ======================================
# CREATE ORDER
# ======================================

class OrderCreate(BaseModel):
    restaurant_id: int = Field(
        ...,
        gt=0,
        description="Restaurant ID"
    )

    items: List[OrderItemInput] = Field(
        ...,
        min_length=1,
        description="Menu items to purchase"
    )


# ======================================
# UPDATE ORDER STATUS
# ======================================

class OrderStatusUpdate(BaseModel):
    status: OrderStatus = Field(
        ...,
        description="Order status"
    )


# ======================================
# ORDER RESPONSE
# ======================================

class OrderResponse(BaseModel):
    id: int
    customer_id: int
    restaurant_id: int
    delivery_partner_id: Optional[int] = None

    subtotal: float
    tax: float
    delivery_charge: float
    total_amount: float

    status: OrderStatus

    model_config = ConfigDict(
        from_attributes=True
    )