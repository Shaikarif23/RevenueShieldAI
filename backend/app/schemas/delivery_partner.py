from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


# ======================================
# CREATE DELIVERY PARTNER
# ======================================

class DeliveryPartnerCreate(BaseModel):
    phone: str = Field(
        ...,
        pattern=r"^[6-9]\d{9}$",
        description="10-digit Indian mobile number"
    )

    vehicle_number: str = Field(
        ...,
        min_length=5,
        max_length=20,
        description="Vehicle registration number"
    )

    vehicle_type: str = Field(
        ...,
        min_length=2,
        max_length=30,
        description="Vehicle type (Bike, Scooter, Cycle, etc.)"
    )

    is_available: bool = True


# ======================================
# UPDATE DELIVERY PARTNER
# ======================================

class DeliveryPartnerUpdate(BaseModel):
    phone: Optional[str] = Field(
        None,
        pattern=r"^[6-9]\d{9}$"
    )

    vehicle_number: Optional[str] = Field(
        None,
        min_length=5,
        max_length=20
    )

    vehicle_type: Optional[str] = Field(
        None,
        min_length=2,
        max_length=30
    )

    is_available: Optional[bool] = None


# ======================================
# DELIVERY PARTNER RESPONSE
# ======================================

class DeliveryPartnerResponse(BaseModel):
    id: int
    user_id: int
    phone: str
    vehicle_number: str
    vehicle_type: str
    is_available: bool

    model_config = ConfigDict(
        from_attributes=True
    )