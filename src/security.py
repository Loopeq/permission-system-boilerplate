import os
from datetime import datetime, timedelta, timezone

from jose import jwt

from passlib.hash import bcrypt_sha256

from src.models import User

SECRET_KEY = os.getenv("SECRET_KEY", '12345')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30


def normalize_permission_code(code: str) -> str:
    return code.strip().lower()

def hash_password(password: str) -> str:
    return bcrypt_sha256.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt_sha256.verify(password, hashed_password)

def create_access_token(user: User) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
        "token_version": user.token_version,
        "exp": expires_at,
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
