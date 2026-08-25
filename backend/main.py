from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.dependencies import get_current_user
from app.exceptions import register_exception_handlers
from app.middleware import register_middleware
from app.models.user import User
from app.routers import (
    ai_insights,
    auth,
    cancellation,
    customer,
    dashboard,
    delivery_partner,
    menu,
    order,
    order_create,
    order_item,
    payment,
    restaurant,
    review,
    revenue_access,
    tracking,
)

app = FastAPI(title="RevenueShield AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)
register_middleware(app)

app.include_router(auth.router)
app.include_router(customer.router)

# Correct business-critical routes are registered before legacy implementations.
app.include_router(order_create.router)
app.include_router(revenue_access.router)
app.include_router(order.router)

app.include_router(restaurant.router)
app.include_router(delivery_partner.router)
app.include_router(dashboard.router)
app.include_router(ai_insights.router)
app.include_router(menu.router)
app.include_router(order_item.router)
app.include_router(tracking.router)
app.include_router(cancellation.router)
app.include_router(payment.router)
app.include_router(review.router)


@app.get("/")
def home():
    return {"message": "Revenue Shield AI Running"}


@app.get("/health")
def health():
    return {"status": "ok", "service": "revenueshield-api"}


@app.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role,
    }
