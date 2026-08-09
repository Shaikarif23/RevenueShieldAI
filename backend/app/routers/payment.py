import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.payment import Payment
from app.models.payment_status import PaymentStatus
from app.models.order import Order
from app.models.customer import Customer
from app.models.user import User
from app.schemas.payment import (
    PaymentCreate,
    PaymentUpdate,
    PaymentResponse
)
from app.utils.roles import require_role

router = APIRouter(
    prefix="/payments",
    tags=["Payments"]
)

@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(
    payment: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("CUSTOMER"))
):
    customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer profile not found")

    order = db.query(Order).filter(Order.id == payment.order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.customer_id != customer.id:
        raise HTTPException(status_code=403, detail="You cannot pay for another customer's order")

    existing_payment = db.query(Payment).filter(Payment.order_id == order.id).first()
    if existing_payment:
        raise HTTPException(status_code=400, detail="Payment already exists for this order")

    new_payment = Payment(
        order_id=order.id,
        amount=order.total_amount,
        payment_method=payment.payment_method,
        transaction_id=str(uuid.uuid4())[:12],
        status=PaymentStatus.SUCCESS
    )

    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)
    return new_payment

@router.get("/", response_model=List[PaymentResponse])
def get_payments(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN"))
):
    return db.query(Payment).all()

@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "CUSTOMER"))
):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")

    if current_user.role == "CUSTOMER":
        customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()
        if customer is None:
            raise HTTPException(status_code=404, detail="Customer profile not found")
        order = db.query(Order).filter(Order.id == payment.order_id).first()
        if order.customer_id != customer.id:
            raise HTTPException(status_code=403, detail="Access denied")

    return payment

@router.put("/{payment_id}", response_model=PaymentResponse)
def update_payment(
    payment_id: int,
    payment_data: PaymentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN"))
):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")

    payment.status = payment_data.status
    db.commit()
    db.refresh(payment)
    return payment

@router.delete("/{payment_id}")
def delete_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN"))
):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")

    db.delete(payment)
    db.commit()
    return {"message": "Payment deleted successfully"}