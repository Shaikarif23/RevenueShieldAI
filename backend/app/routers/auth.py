from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import TokenResponse, UserRegister, UserResponse
from app.utils.jwt_handler import create_access_token
from app.utils.security import hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])

ALLOWED_REGISTRATION_ROLES = {"CUSTOMER", "RESTAURANT", "DELIVERY_PARTNER"}


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(user: UserRegister, db: Session = Depends(get_db)):
    email = str(user.email).lower().strip()
    role = user.role.upper().strip()

    if role not in ALLOWED_REGISTRATION_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid registration role. ADMIN accounts must be provisioned by an administrator.",
        )

    if db.query(User).filter(User.email == email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    new_user = User(
        name=user.name.strip(),
        email=email,
        password=hash_password(user.password),
        role=role,
        phone=user.phone,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=TokenResponse)
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    email = form_data.username.lower().strip()
    db_user = db.query(User).filter(User.email == email).first()

    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    password_match = verify_password(form_data.password, db_user.password)

    # Backward-compatible migration for the existing seed generator, which
    # historically stored SeedPass123! as plaintext. The value is replaced
    # with a bcrypt hash immediately after a successful legacy login.
    if not password_match and db_user.password == form_data.password:
        db_user.password = hash_password(form_data.password)
        db.commit()
        password_match = True

    if not password_match:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        {"sub": db_user.email, "role": db_user.role}
    )

    return {"access_token": access_token, "token_type": "bearer"}
