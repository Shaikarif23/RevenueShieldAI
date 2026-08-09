from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db

from app.models.order_item import OrderItem
from app.models.order import Order
from app.models.menu import Menu
from app.models.user import User
from app.models.customer import Customer

from app.schemas.order_item import (
    OrderItemCreate,
    OrderItemUpdate,
    OrderItemResponse
)

from app.utils.roles import require_role


router = APIRouter(
    prefix="/order-items",
    tags=["Order Items"]
)


# ======================================
# RECALCULATE ORDER TOTAL
# ======================================

def recalculate_order(
    order_id: int,
    db: Session
):

    order = (
        db.query(Order)
        .filter(Order.id == order_id)
        .first()
    )

    if order is None:
        return


    items = (
        db.query(OrderItem)
        .filter(OrderItem.order_id == order_id)
        .all()
    )


    subtotal = sum(
        item.total_price
        for item in items
    )

    tax = round(
        subtotal * 0.05,
        2
    )

    delivery_charge = 30

    total_amount = (
        subtotal
        + tax
        + delivery_charge
    )


    order.subtotal = subtotal
    order.tax = tax
    order.delivery_charge = delivery_charge
    order.total_amount = total_amount



# ======================================
# CHECK ORDER OWNERSHIP
# ======================================

def verify_customer_order(
    order_id: int,
    current_user: User,
    db: Session
):

    customer = (
        db.query(Customer)
        .filter(
            Customer.user_id == current_user.id
        )
        .first()
    )


    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer profile not found"
        )


    order = (
        db.query(Order)
        .filter(
            Order.id == order_id
        )
        .first()
    )


    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )


    if order.customer_id != customer.id:
        raise HTTPException(
            status_code=403,
            detail="You cannot modify another customer's order"
        )


    return order



# ======================================
# CREATE ORDER ITEM
# CUSTOMER ONLY
# ======================================

@router.post(
    "/",
    response_model=OrderItemResponse,
    status_code=status.HTTP_201_CREATED
)
def create_order_item(
    item: OrderItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("CUSTOMER")
    )
):

    order = verify_customer_order(
        item.order_id,
        current_user,
        db
    )


    menu = (
        db.query(Menu)
        .filter(Menu.id == item.menu_id)
        .first()
    )


    if menu is None:
        raise HTTPException(
            status_code=404,
            detail="Menu item not found"
        )


    if menu.is_available != "YES":
        raise HTTPException(
            status_code=400,
            detail="Menu item is not available"
        )


    unit_price = menu.price

    total_price = (
        unit_price
        * item.quantity
    )


    new_item = OrderItem(
        order_id=order.id,
        menu_id=menu.id,
        quantity=item.quantity,
        unit_price=unit_price,
        total_price=total_price
    )


    db.add(new_item)

    db.flush()


    recalculate_order(
        order.id,
        db
    )


    db.commit()

    db.refresh(new_item)


    return new_item




# ======================================
# GET ALL ORDER ITEMS
# ======================================

@router.get(
    "/",
    response_model=List[OrderItemResponse]
)
def get_order_items(
    db: Session = Depends(get_db)
):

    return (
        db.query(OrderItem)
        .all()
    )




# ======================================
# GET ORDER ITEM BY ID
# CUSTOMER ONLY
# ======================================

@router.get(
    "/{item_id}",
    response_model=OrderItemResponse
)
def get_order_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("CUSTOMER")
    )
):

    item = (
        db.query(OrderItem)
        .filter(
            OrderItem.id == item_id
        )
        .first()
    )


    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Order item not found"
        )


    verify_customer_order(
        item.order_id,
        current_user,
        db
    )


    return item




# ======================================
# GET ITEMS OF AN ORDER
# CUSTOMER ONLY
# ======================================

@router.get(
    "/order/{order_id}",
    response_model=List[OrderItemResponse]
)
def get_items_by_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("CUSTOMER")
    )
):

    verify_customer_order(
        order_id,
        current_user,
        db
    )


    return (
        db.query(OrderItem)
        .filter(
            OrderItem.order_id == order_id
        )
        .all()
    )




# ======================================
# UPDATE ORDER ITEM
# CUSTOMER ONLY
# ======================================

@router.put(
    "/{item_id}",
    response_model=OrderItemResponse
)
def update_order_item(
    item_id: int,
    item_data: OrderItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("CUSTOMER")
    )
):

    item = (
        db.query(OrderItem)
        .filter(
            OrderItem.id == item_id
        )
        .first()
    )


    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Order item not found"
        )


    verify_customer_order(
        item.order_id,
        current_user,
        db
    )


    item.quantity = item_data.quantity

    item.total_price = (
        item.unit_price
        * item.quantity
    )


    recalculate_order(
        item.order_id,
        db
    )


    db.commit()

    db.refresh(item)


    return item




# ======================================
# DELETE ORDER ITEM
# CUSTOMER ONLY
# ======================================

@router.delete("/{item_id}")
def delete_order_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("CUSTOMER")
    )
):

    item = (
        db.query(OrderItem)
        .filter(
            OrderItem.id == item_id
        )
        .first()
    )


    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Order item not found"
        )


    verify_customer_order(
        item.order_id,
        current_user,
        db
    )


    order_id = item.order_id


    db.delete(item)

    db.flush()


    recalculate_order(
        order_id,
        db
    )


    db.commit()


    return {
        "message": "Order item deleted successfully"
    }