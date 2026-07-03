from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.data.database import get_db
from src.models import Permission, User, UserPermission
from src.security import ALGORITHM, SECRET_KEY, normalize_permission_code

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    unauthorized_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Доступ запрещен.",
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        token_version = int(payload.get("token_version"))
    except (JWTError, TypeError, ValueError):
        raise unauthorized_exception

    user = db.get(User, user_id)

    if not user:
        raise unauthorized_exception

    if not user.is_active:
        raise unauthorized_exception

    if user.token_version != token_version:
        raise unauthorized_exception

    return user


def require_admin(
    user: User = Depends(get_current_user),
) -> User:
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен. Требуется роль администратора.",
        )

    return user


def require_permission(permission_code: str):
    def checker(
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> User:
        if user.role == "admin":
            return user

        permission_code_normalized = normalize_permission_code(permission_code)

        user_permission = db.execute(
            select(UserPermission)
            .join(Permission, Permission.id == UserPermission.permission_id)
            .where(
                UserPermission.user_id == user.id,
                Permission.code == permission_code_normalized,
            )
        ).scalar_one_or_none()

        if not user_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Доступ запрещен.",
            )

        return user

    return checker
