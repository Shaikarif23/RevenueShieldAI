
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    UserRegister,
    UserLogin,
    UserResponse
)
from app.utils.security import (
    hash_password,
    verify_password
)
from app.utils.token import create_access_token
from app.config import settings

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post(
    "/register",
    response_model=UserResponse
)

def register_user(
    user: UserRegister,
    db: Session = Depends(get_db)
):
    print("✅ Step 1: Register API called")

    existing_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )
    print("✅ Step 2: Checked existing user")

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    hashed_password = hash_password(user.password)
    print("✅ Step 3: Password hashed")

    new_user = User(
        name=user.name,
        email=user.email,
        password=hashed_password,
        role=user.role
    )
    print("✅ Step 4: User object created")

    db.add(new_user)
    print("✅ Step 5: User added to session")

    db.commit()
    print("✅ Step 6: Database committed")

    db.refresh(new_user)
    print("✅ Step 7: User refreshed")

    return new_user

@router.post("/login")
def login_user(
    user: UserLogin,
    db: Session = Depends(get_db)
):
    db_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        user.password,
        db_user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        data={
            "sub": db_user.email,
            "role": db_user.role
        },
        expires_delta=timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }