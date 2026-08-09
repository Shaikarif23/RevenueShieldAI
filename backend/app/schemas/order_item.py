from pydantic import BaseModel, Field, ConfigDict


# ======================================
# CREATE ORDER ITEM
# ======================================

class OrderItemCreate(BaseModel):

    order_id: int = Field(
        ...,
        gt=0,
        description="Order ID"
    )

    menu_id: int = Field(
        ...,
        gt=0,
        description="Menu Item ID"
    )

    quantity: int = Field(
        ...,
        ge=1,
        le=100,
        description="Quantity"
    )


# ======================================
# UPDATE ORDER ITEM
# ======================================

class OrderItemUpdate(BaseModel):

    quantity: int = Field(
        ...,
        ge=1,
        le=100
    )


# ======================================
# RESPONSE
# ======================================

class OrderItemResponse(BaseModel):

    id: int
    order_id: int
    menu_id: int
    quantity: int
    unit_price: float
    total_price: float

    model_config = ConfigDict(
        from_attributes=True
    )