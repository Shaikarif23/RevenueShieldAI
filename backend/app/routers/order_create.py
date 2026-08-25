from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.customer import Customer
from app.models.menu import Menu
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.restaurant import Restaurant
from app.models.user import User
from app.models.order_status import OrderStatus
from app.schemas.order import OrderCreate, OrderResponse

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "CUSTOMER":
        raise HTTPException(status_code=403, detail="Only customers can create orders")

    customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer profile not found")

    restaurant = db.query(Restaurant).filter(Restaurant.id == order.restaurant_id).first()
    if restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    menu_ids = [item.menu_id for item in order.items]
    menu_items = db.query(Menu).filter(Menu.id.in_(menu_ids)).all()
    menu_by_id = {item.id: item for item in menu_items}

    if len(menu_by_id) != len(set(menu_ids)):
        raise HTTPException(status_code=400, detail="One or more menu items do not exist")

    subtotal = 0.0
    calculated_items = []

    for requested in order.items:
        menu = menu_by_id[requested.menu_id]
        if menu.restaurant_id != restaurant.id:
            raise HTTPException(
                status_code=400,
                detail=f"Menu item {menu.id} does not belong to the selected restaurant",
            )
        if str(menu.is_available).upper() != "YES":
            raise HTTPException(status_code=400, detail=f"Menu item {menu.id} is not available")

        line_total = round(float(menu.price) * requested.quantity, 2)
        subtotal += line_total
        calculated_items.append((menu, requested.quantity, line_total))

    subtotal = round(subtotal, 2)
    tax = round(subtotal * 0.05, 2)
    delivery_charge = 30.0
    total_amount = round(subtotal + tax + delivery_charge, 2)

    new_order = Order(
        customer_id=customer.id,
        restaurant_id=restaurant.id,
        delivery_partner_id=None,
        subtotal=subtotal,
        tax=tax,
        delivery_charge=delivery_charge,
        total_amount=total_amount,
        status=OrderStatus.PLACED,
    )
    db.add(new_order)
    db.flush()

    for menu, quantity, line_total in calculated_items:
        db.add(
            OrderItem(
                order_id=new_order.id,
                menu_id=menu.id,
                quantity=quantity,
                unit_price=float(menu.price),
                total_price=line_total,
            )
        )

    db.commit()
    db.refresh(new_order)
    return new_order
