from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


# ======================================
# CREATE MENU ITEM
# ======================================

class MenuCreate(BaseModel):
    restaurant_id: int = Field(
        ...,
        gt=0,
        description="Restaurant ID"
    )

    item_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Menu item name"
    )

    category: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Menu category"
    )

    price: float = Field(
        ...,
        gt=0,
        description="Item price"
    )

    preparation_time: int = Field(
        ...,
        ge=1,
        le=180,
        description="Preparation time in minutes"
    )

    ingredient_cost: float = Field(
        ...,
        ge=0,
        description="Ingredient cost"
    )

    is_available: bool = True


# ======================================
# UPDATE MENU ITEM
# ======================================

class MenuUpdate(BaseModel):
    item_name: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    category: str = Field(
        ...,
        min_length=2,
        max_length=50
    )

    price: float = Field(
        ...,
        gt=0
    )

    preparation_time: int = Field(
        ...,
        ge=1,
        le=180
    )

    ingredient_cost: float = Field(
        ...,
        ge=0
    )

    is_available: bool


# ======================================
# MENU RESPONSE
# ======================================

class MenuResponse(BaseModel):
    id: int
    restaurant_id: int
    item_name: str
    category: str
    price: float
    preparation_time: int
    ingredient_cost: float
    is_available: bool

    model_config = ConfigDict(
        from_attributes=True
    )