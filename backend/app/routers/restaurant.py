from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db

from app.models.restaurant import Restaurant
from app.models.order import Order
from app.models.user import User

from app.schemas.restaurant import (
    RestaurantCreate,
    RestaurantResponse
)

from app.schemas.order import OrderResponse

from app.schemas.common import PaginatedResponse

from app.utils.roles import require_role


router = APIRouter(
    prefix="/restaurants",
    tags=["Restaurants"]
)


# ======================================
# CREATE RESTAURANT
# RESTAURANT ONLY
# ======================================

@router.post(
    "/",
    response_model=RestaurantResponse,
    status_code=status.HTTP_201_CREATED
)
def create_restaurant(
    restaurant: RestaurantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("RESTAURANT"))
):

    existing_restaurant = (
        db.query(Restaurant)
        .filter(
            Restaurant.user_id == current_user.id
        )
        .first()
    )


    if existing_restaurant:
        raise HTTPException(
            status_code=400,
            detail="Restaurant profile already exists"
        )


    new_restaurant = Restaurant(

        user_id=current_user.id,
        restaurant_name=restaurant.restaurant_name,
        address=restaurant.address,
        latitude=restaurant.latitude,
        longitude=restaurant.longitude,
        rating=restaurant.rating

    )


    db.add(new_restaurant)
    db.commit()
    db.refresh(new_restaurant)


    return new_restaurant



# ======================================
# GET ALL RESTAURANTS
# PAGINATION + SORTING
# PUBLIC
# ======================================

@router.get(
    "/",
    response_model=PaginatedResponse[RestaurantResponse]
)
def get_restaurants(

    page: int = Query(
        1,
        ge=1
    ),

    size: int = Query(
        10,
        ge=1,
        le=100
    ),

    sort: str = Query(
        "rating_desc",
        description="rating_desc, rating_asc, name_asc, name_desc"
    ),

    db: Session = Depends(get_db)

):

    query = db.query(Restaurant)



    # Sorting

    if sort == "rating_desc":

        query = query.order_by(
            Restaurant.rating.desc()
        )


    elif sort == "rating_asc":

        query = query.order_by(
            Restaurant.rating.asc()
        )


    elif sort == "name_asc":

        query = query.order_by(
            Restaurant.restaurant_name.asc()
        )


    elif sort == "name_desc":

        query = query.order_by(
            Restaurant.restaurant_name.desc()
        )


    else:

        raise HTTPException(
            status_code=400,
            detail="Invalid sorting option"
        )



    # Total records

    total = query.count()



    # Pagination

    skip = (page - 1) * size



    restaurants = (
        query
        .offset(skip)
        .limit(size)
        .all()
    )



    pages = (total + size - 1) // size



    return {

        "page": page,

        "size": size,

        "total": total,

        "pages": pages,

        "data": restaurants

    }




# ======================================
# GET SINGLE RESTAURANT
# PUBLIC
# ======================================

@router.get(
    "/{restaurant_id}",
    response_model=RestaurantResponse
)
def get_restaurant(

    restaurant_id: int,

    db: Session = Depends(get_db)

):

    restaurant = (

        db.query(Restaurant)

        .filter(
            Restaurant.id == restaurant_id
        )

        .first()

    )


    if restaurant is None:

        raise HTTPException(

            status_code=404,

            detail="Restaurant not found"

        )


    return restaurant




# ======================================
# RESTAURANT ORDER HISTORY
# OWNER ONLY
# ======================================

@router.get(
    "/{restaurant_id}/orders",
    response_model=List[OrderResponse]
)
def get_restaurant_orders(

    restaurant_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_role("RESTAURANT")
    )

):

    restaurant = (

        db.query(Restaurant)

        .filter(
            Restaurant.id == restaurant_id
        )

        .first()

    )


    if restaurant is None:

        raise HTTPException(

            status_code=404,

            detail="Restaurant not found"

        )



    if restaurant.user_id != current_user.id:

        raise HTTPException(

            status_code=403,

            detail="You cannot access another restaurant's orders"

        )



    orders = (

        db.query(Order)

        .filter(
            Order.restaurant_id == restaurant_id
        )

        .all()

    )


    return orders





# ======================================
# DELETE RESTAURANT
# OWNER ONLY
# ======================================

@router.delete("/{restaurant_id}")
def delete_restaurant(

    restaurant_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_role("RESTAURANT")
    )

):

    restaurant = (

        db.query(Restaurant)

        .filter(
            Restaurant.id == restaurant_id
        )

        .first()

    )


    if restaurant is None:

        raise HTTPException(

            status_code=404,

            detail="Restaurant not found"

        )



    if restaurant.user_id != current_user.id:

        raise HTTPException(

            status_code=403,

            detail="You cannot delete another restaurant"

        )



    db.delete(restaurant)

    db.commit()



    return {

        "message": "Restaurant deleted successfully"

    }