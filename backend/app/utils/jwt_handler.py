from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

from app.config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({'exp': expire})

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

def decode_access_token(token: str):
    print("=" * 60)
    print("TOKEN:", token)
    print("SECRET_KEY:", SECRET_KEY)
    print("ALGORITHM:", ALGORITHM)

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        print("PAYLOAD:", payload)
        print("=" * 60)
        return payload

    except Exception as e:
        print("JWT ERROR:", repr(e))
        print("=" * 60)
        return None