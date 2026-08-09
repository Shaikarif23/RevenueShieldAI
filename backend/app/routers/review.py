from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db

from app.models.review import Review
from app.models.order import Order
from app.models.customer import Customer
from app.models.restaurant import Restaurant
from app.models.order_status import OrderStatus
from app.models.user import User

from app.schemas.review import (
    ReviewCreate,
    ReviewUpdate,
    ReviewResponse
)

from app.utils.roles import require_role

router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"]
)


# ======================================
# CREATE REVIEW
# CUSTOMER ONLY
# ======================================

@router.post(
    "/",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED
)
def create_review(
    review: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("CUSTOMER"))
):

    customer = (
        db.query(Customer)
        .filter(Customer.user_id == current_user.id)
        .first()
    )

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer profile not found"
        )

    order = (
        db.query(Order)
        .filter(Order.id == review.order_id)
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
            detail="You cannot review another customer's order"
        )

    if order.status != OrderStatus.DELIVERED:
        raise HTTPException(
            status_code=400,
            detail="Only delivered orders can be reviewed"
        )

    existing_review = (
        db.query(Review)
        .filter(Review.order_id == order.id)
        .first()
    )

    if existing_review:
        raise HTTPException(
            status_code=400,
            detail="Review already exists for this order"
        )

    new_review = Review(
        order_id=order.id,
        customer_id=customer.id,
        restaurant_id=order.restaurant_id,
        rating=review.rating,
        comment=review.comment
    )

    db.add(new_review)
    db.commit()
    db.refresh(new_review)

    return new_review


# ======================================
# GET ALL REVIEWS
# ADMIN ONLY
# ======================================

@router.get(
    "/",
    response_model=List[ReviewResponse]
)
def get_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN"))
):
    return db.query(Review).all()


# ======================================
# GET REVIEW BY ID
# ======================================

@router.get(
    "/{review_id}",
    response_model=ReviewResponse
)
def get_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "CUSTOMER"))
):

    review = (
        db.query(Review)
        .filter(Review.id == review_id)
        .first()
    )

    if review is None:
        raise HTTPException(
            status_code=404,
            detail="Review not found"
        )

    if current_user.role == "CUSTOMER":
        customer = (
            db.query(Customer)
            .filter(Customer.user_id == current_user.id)
            .first()
        )

        if customer is None or review.customer_id != customer.id:
            raise HTTPException(
                status_code=403,
                detail="Access denied"
            )

    return review


# ======================================
# UPDATE REVIEW
# CUSTOMER ONLY
# ======================================

@router.put(
    "/{review_id}",
    response_model=ReviewResponse
)
def update_review(
    review_id: int,
    review_data: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("CUSTOMER"))
):

    customer = (
        db.query(Customer)
        .filter(Customer.user_id == current_user.id)
        .first()
    )

    review = (
        db.query(Review)
        .filter(Review.id == review_id)
        .first()
    )

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer profile not found"
        )

    if review is None:
        raise HTTPException(
            status_code=404,
            detail="Review not found"
        )

    if review.customer_id != customer.id:
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    review.rating = review_data.rating
    review.comment = review_data.comment

    db.commit()
    db.refresh(review)

    return review


# ======================================
# DELETE REVIEW
# ADMIN ONLY
# ======================================

@router.delete("/{review_id}")
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN"))
):

    review = (
        db.query(Review)
        .filter(Review.id == review_id)
        .first()
    )

    if review is None:
        raise HTTPException(
            status_code=404,
            detail="Review not found"
        )

    db.delete(review)
    db.commit()

    return {
        "message": "Review deleted successfully"
    }


# ======================================
# RESTAURANT AVERAGE RATING
# ======================================

@router.get("/restaurant/{restaurant_id}/average-rating")
def average_rating(
    restaurant_id: int,
    db: Session = Depends(get_db)
):

    reviews = (
        db.query(Review)
        .filter(Review.restaurant_id == restaurant_id)
        .all()
    )

    if not reviews:
        return {
            "restaurant_id": restaurant_id,
            "average_rating": 0,
            "total_reviews": 0
        }

    average = sum(r.rating for r in reviews) / len(reviews)

    return {
        "restaurant_id": restaurant_id,
        "average_rating": round(average, 2),
        "total_reviews": len(reviews)
    }