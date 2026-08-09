from pydantic import BaseModel
from datetime import datetime


class TrackingCreate(BaseModel):
    order_id: int
    status: str
    latitude: float
    longitude: float


class TrackingUpdate(BaseModel):
    status: str
    latitude: float
    longitude: float


class TrackingResponse(BaseModel):
    id: int
    order_id: int
    status: str
    latitude: float
    longitude: float
    updated_at: datetime

    class Config:
        from_attributes = True