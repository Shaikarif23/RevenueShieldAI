from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


# ======================================
# CREATE RESTAURANT
# ======================================

class RestaurantCreate(BaseModel):
    restaurant_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Restaurant name"
    )

    address: Optional[str] = Field(
        None,
        min_length=5,
        max_length=255
    )

    latitude: Optional[float] = Field(
        None,
        ge=-90,
        le=90
    )

    longitude: Optional[float] = Field(
        None,
        ge=-180,
        le=180
    )

    rating: Optional[float] = Field(
        0,
        ge=0,
        le=5,
        description="Restaurant rating"
    )


# ======================================
# RESTAURANT RESPONSE
# ======================================

class RestaurantResponse(BaseModel):
    id: int
    user_id: int
    restaurant_name: str
    address: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    rating: Optional[float]

    model_config = ConfigDict(
        from_attributes=True
    )