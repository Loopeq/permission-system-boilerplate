from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.data.database import get_db
from src.di import require_admin
from src.models import Permission, User, UserPermission
from src.schemas import (
    UserRead,
    PermissionCreate,
    PermissionRead,
    GrantPermissionRequest,
    UserPermissionRead,
)
from src.security import normalize_permission_code


router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)


@router.get("/users", response_model=list[UserRead], summary="Получить всех пользователей")
def get_users(
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    users = db.execute(
        select(User).order_by(User.id)
    ).scalars().all()

    return users


@router.get("/permissions", response_model=list[PermissionRead], summary="Получить список всех разрешений")
def get_permissions(
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    permissions = db.execute(
        select(Permission).order_by(Permission.code)
    ).scalars().all()

    return permissions


@router.post("/permissions", response_model=PermissionRead, summary="Создать новое разрешение")
def create_permission(
    payload: PermissionCreate,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    code = normalize_permission_code(payload.code)

    existing_permission = db.execute(
        select(Permission).where(Permission.code == code)
    ).scalar_one_or_none()

    if existing_permission:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Разрешение с таким кодом уже существует.",
        )

    permission = Permission(
        code=code,
        description=payload.description,
    )

    db.add(permission)
    db.commit()
    db.refresh(permission)

    return permission


@router.get(
    "/users/{user_id}/permissions",
    response_model=list[UserPermissionRead],
    summary="Получить список разрешений пользователя",
)
def get_user_permissions(
    user_id: int,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    user = db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )

    rows = db.execute(
        select(UserPermission, Permission)
        .join(Permission, Permission.id == UserPermission.permission_id)
        .where(UserPermission.user_id == user_id)
        .order_by(Permission.code)
    ).all()

    return [
        UserPermissionRead(
            permission_id=permission.id,
            code=permission.code,
            description=permission.description,
        )
        for user_permission, permission in rows
    ]


@router.post(
    "/users/{user_id}/permissions",
    response_model=UserPermissionRead,
    summary="Даровать разрешение пользователю",
)
def grant_permission(
    user_id: int,
    payload: GrantPermissionRequest,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    user = db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )

    permission = db.get(Permission, payload.permission_id)

    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Разрешение не найдено",
        )

    existing_user_permission = db.execute(
        select(UserPermission).where(
            UserPermission.user_id == user_id,
            UserPermission.permission_id == permission.id,
        )
    ).scalar_one_or_none()

    if existing_user_permission:
        return UserPermissionRead(
            permission_id=permission.id,
            code=permission.code,
            description=permission.description,
        )

    user_permission = UserPermission(
        user_id=user_id,
        permission_id=permission.id,
    )

    db.add(user_permission)
    db.commit()

    return UserPermissionRead(
        permission_id=permission.id,
        code=permission.code,
        description=permission.description,
    )


@router.delete("/users/{user_id}/permissions/{permission_id}",
    summary="Отозвать разрешение у пользователя",)
def revoke_permission(
    user_id: int,
    permission_id: int,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    user = db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ПОльзователь не найден",
        )

    user_permission = db.execute(
        select(UserPermission).where(
            UserPermission.user_id == user_id,
            UserPermission.permission_id == permission_id,
        )
    ).scalar_one_or_none()

    if not user_permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission rule not found",
        )

    db.delete(user_permission)
    db.commit()

    return {"success": True}
