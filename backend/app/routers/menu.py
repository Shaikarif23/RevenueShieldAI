from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db

from app.models.menu import Menu
from app.models.restaurant import Restaurant
from app.models.user import User

from app.schemas.menu import (
    MenuCreate,
    MenuUpdate,
    MenuResponse
)

from app.schemas.common import PaginatedResponse

from app.utils.roles import require_role


router = APIRouter(
    prefix="/menu",
    tags=["Menu"]
)


# ======================================
# CREATE MENU ITEM
# RESTAURANT ONLY
# ======================================

@router.post(
    "/",
    response_model=MenuResponse,
    status_code=status.HTTP_201_CREATED
)
def create_menu_item(
    menu: MenuCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("RESTAURANT"))
):

    restaurant = (
        db.query(Restaurant)
        .filter(Restaurant.id == menu.restaurant_id)
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
            detail="You cannot add menu items to another restaurant"
        )


    new_menu = Menu(
        restaurant_id=menu.restaurant_id,
        item_name=menu.item_name,
        category=menu.category,
        price=menu.price,
        preparation_time=menu.preparation_time,
        ingredient_cost=menu.ingredient_cost,
        is_available=menu.is_available
    )


    db.add(new_menu)
    db.commit()
    db.refresh(new_menu)


    return new_menu



# ======================================
# GET ALL MENU ITEMS
# SEARCH + FILTER + PAGINATION
# ======================================

@router.get(
    "/",
    response_model=PaginatedResponse[MenuResponse]
)
def get_menu_items(

    page: int = Query(
        1,
        ge=1
    ),

    size: int = Query(
        10,
        ge=1,
        le=100
    ),

    restaurant_id: int = Query(None),

    category: str = Query(None),

    item_name: str = Query(None),

    available: str = Query(None),

    db: Session = Depends(get_db)

):

    query = db.query(Menu)



    # Filter restaurant

    if restaurant_id:

        query = query.filter(
            Menu.restaurant_id == restaurant_id
        )



    # Filter category

    if category:

        query = query.filter(
            Menu.category.ilike(
                f"%{category}%"
            )
        )



    # Search item name

    if item_name:

        query = query.filter(
            Menu.item_name.ilike(
                f"%{item_name}%"
            )
        )



    # Availability filter

    if available:

        query = query.filter(
            Menu.is_available == available
        )



    # Total records

    total = query.count()



    # Pagination

    skip = (page - 1) * size



    menu_items = (
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

        "data": menu_items

    }




# ======================================
# GET MENU ITEM BY ID
# ======================================

@router.get(
    "/{menu_id}",
    response_model=MenuResponse
)
def get_menu_item(
    menu_id: int,
    db: Session = Depends(get_db)
):

    menu = (
        db.query(Menu)
        .filter(Menu.id == menu_id)
        .first()
    )

    if menu is None:
        raise HTTPException(
            status_code=404,
            detail="Menu item not found"
        )

    return menu



# ======================================
# GET MENU OF RESTAURANT
# ======================================

@router.get(
    "/restaurant/{restaurant_id}",
    response_model=List[MenuResponse]
)
def get_restaurant_menu(
    restaurant_id: int,
    db: Session = Depends(get_db)
):

    return (
        db.query(Menu)
        .filter(Menu.restaurant_id == restaurant_id)
        .all()
    )



# ======================================
# UPDATE MENU ITEM
# ======================================

@router.put(
    "/{menu_id}",
    response_model=MenuResponse
)
def update_menu_item(
    menu_id: int,
    menu_data: MenuUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("RESTAURANT"))
):

    menu = (
        db.query(Menu)
        .filter(Menu.id == menu_id)
        .first()
    )


    if menu is None:
        raise HTTPException(
            status_code=404,
            detail="Menu item not found"
        )


    restaurant = (
        db.query(Restaurant)
        .filter(Restaurant.id == menu.restaurant_id)
        .first()
    )


    if restaurant.user_id != current_user.id:

        raise HTTPException(
            status_code=403,
            detail="You cannot update another restaurant's menu"
        )


    menu.item_name = menu_data.item_name
    menu.category = menu_data.category
    menu.price = menu_data.price
    menu.preparation_time = menu_data.preparation_time
    menu.ingredient_cost = menu_data.ingredient_cost
    menu.is_available = menu_data.is_available


    db.commit()
    db.refresh(menu)


    return menu



# ======================================
# DELETE MENU ITEM
# ======================================

@router.delete("/{menu_id}")
def delete_menu_item(
    menu_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("RESTAURANT"))
):

    menu = (
        db.query(Menu)
        .filter(Menu.id == menu_id)
        .first()
    )


    if menu is None:
        raise HTTPException(
            status_code=404,
            detail="Menu item not found"
        )


    restaurant = (
        db.query(Restaurant)
        .filter(Restaurant.id == menu.restaurant_id)
        .first()
    )


    if restaurant.user_id != current_user.id:

        raise HTTPException(
            status_code=403,
            detail="You cannot delete another restaurant's menu"
        )


    db.delete(menu)
    db.commit()


    return {
        "message": "Menu item deleted successfully"
    }