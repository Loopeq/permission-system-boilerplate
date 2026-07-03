from sqlalchemy import select
from sqlalchemy.orm import Session

from src.data.repository import get_user_by_email
from src.models import Permission, User, UserPermission
from src.security import hash_password


def seed_boilerplate_data(db: Session):
    permissions_data = [
        ("document:read", "Чтение документов"),
        ("document:create", "Создание документов"),
        ("document:delete", "Удаление документов"),
        ("profile:update", "Обновление профиля"),
    ]

    codes = [code.lower().strip() for code, _ in permissions_data]
    code_to_description = {code: desc for code, desc in permissions_data}

    existing_permissions = db.execute(
        select(Permission).where(Permission.code.in_(codes))
    ).scalars().all()

    existing_codes = {p.code: p for p in existing_permissions}

    new_permissions = []
    for code in codes:
        if code not in existing_codes:
            new_permissions.append(
                Permission(code=code, description=code_to_description[code])
            )

    if new_permissions:
        db.add_all(new_permissions)
        db.flush()

    created_permissions = {p.code: p for p in existing_permissions + new_permissions}

    admin = get_user_by_email(db, "admin@example.com")

    if not admin:
        admin = User(
            full_name="Admin One",
            email="admin@example.com",
            hashed_password=hash_password("admin123"),
            role="admin",
            is_active=True,
        )
        db.add(admin)
        db.flush()

    demo_user = get_user_by_email(db, "user@example.com")

    if not demo_user:
        demo_user = User(
            full_name="User one",
            email="user@example.com",
            hashed_password=hash_password("user123"),
            role="user",
            is_active=True,
        )
        db.add(demo_user)
        db.flush()

    read_permission = created_permissions["document:read"]

    existing_user_permission = db.execute(
        select(UserPermission).where(
            UserPermission.user_id == demo_user.id,
            UserPermission.permission_id == read_permission.id,
        )
    ).scalar_one_or_none()

    if not existing_user_permission:
        db.add(
            UserPermission(
                user_id=demo_user.id,
                permission_id=read_permission.id,
            )
        )

    db.commit()
