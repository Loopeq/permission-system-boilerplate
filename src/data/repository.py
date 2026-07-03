from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models import User


def get_user_by_email(db: Session, email: str) -> User | None:
    email = email.lower().strip()
    return db.execute(
        select(User).where(User.email == email)
    ).scalar_one_or_none()
