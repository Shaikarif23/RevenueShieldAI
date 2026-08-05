
from fastapi import FastAPI

from app.database import Base, engine
from app.routers import auth

# Import ALL models
from app.models import (
    User,
    Restaurant,
    Customer,
    DeliveryPartner,
    Menu,
    Order,
    OrderItem,
    Tracking,
    Cancellation,
    RevenueLeakage,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="RevenueShield AI",
    version="1.0.0"
)

app.include_router(auth.router)

@app.get("/")
def home():
    return {"message": "RevenueShield AI Running"}