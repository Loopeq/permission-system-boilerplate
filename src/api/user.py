from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.data.database import get_db
from src.data.repository import get_user_by_email
from src.di import get_current_user
from src.models import User
from src.schemas import UserRead, UserUpdate
from src.security import hash_password

router = APIRouter(
    tags=["users"],
)


@router.get("/me", response_model=UserRead, summary='Пользователь')
def get_me(
    user: User = Depends(get_current_user),
):
    return user


@router.patch("/me", response_model=UserRead, summary='Обновить пользователя')
def update_me(
    payload: UserUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.full_name is not None:
        user.full_name = payload.full_name.strip()

    if payload.email is not None:
        new_email = payload.email.strip().lower()

        existing_user = get_user_by_email(db, new_email)

        if existing_user and existing_user.id != user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email уже занят.",
            )

        user.email = new_email

    if payload.password is not None:
        user.hashed_password = hash_password(payload.password)
        user.token_version += 1

    db.commit()
    db.refresh(user)

    return user


@router.delete("/me", summary='Удалить пользователя')
def delete_me(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user.is_active = False
    user.token_version += 1

    db.commit()

    return {"success": True}
