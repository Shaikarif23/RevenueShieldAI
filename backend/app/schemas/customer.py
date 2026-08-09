from pydantic import BaseModel, Field, ConfigDict


# ======================================
# CREATE CUSTOMER
# ======================================

class CustomerCreate(BaseModel):
    default_address: str = Field(
        ...,
        min_length=5,
        max_length=255,
        description="Customer address"
    )

    city: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="City name"
    )

    latitude: float = Field(
        ...,
        ge=-90,
        le=90,
        description="Latitude (-90 to 90)"
    )

    longitude: float = Field(
        ...,
        ge=-180,
        le=180,
        description="Longitude (-180 to 180)"
    )


# ======================================
# CUSTOMER RESPONSE
# ======================================

class CustomerResponse(BaseModel):
    id: int
    user_id: int
    default_address: str
    city: str
    latitude: float
    longitude: float

    model_config = ConfigDict(
        from_attributes=True
    )