from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    if not password:
        raise ValueError("Password cannot be empty")
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password without allowing malformed legacy values to crash login."""
    if not plain_password or not hashed_password:
        return False

    try:
        return pwd_context.verify(plain_password, hashed_password)
    except (ValueError, TypeError):
        # Existing seed data may contain legacy plaintext passwords. Login
        # handles that migration explicitly; malformed values must never turn
        # into a 500 response.
        return False
