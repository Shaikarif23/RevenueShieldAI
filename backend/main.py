from fastapi import FastAPI, Depends
from app.routers import order
from app.routers import restaurant
from app.routers import auth
from app.routers import delivery_partner
from app.routers import customer
from app.dependencies import get_current_user
from app.models.user import User
from app.routers import dashboard
from app.routers import ai_insights
from app.exceptions import register_exception_handlers
from app.middleware import register_middleware
from app.routers import menu
from app.routers import order_item
from app.routers import tracking
from app.routers import cancellation
from app.routers import payment
from app.models.payment import Payment
from app.routers import review


app = FastAPI(
    title="RevenueShield AI",
    version="1.0.0"
)
# Register Global Exception Handlers
register_exception_handlers(app)
register_middleware(app)

app.include_router(auth.router)
app.include_router(customer.router)
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
    return {"message": "RevenueShield AI Running"}

@app.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role
    }