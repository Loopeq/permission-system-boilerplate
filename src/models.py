from sqlalchemy import (
    String,
    Boolean,
    Integer,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)

from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)

from datetime import datetime, timezone

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    full_name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))

    role: Mapped[str] = mapped_column(String(50), default="user")

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    token_version: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    permissions: Mapped[list["UserPermission"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    code: Mapped[str] = mapped_column(String(255), unique=True, index=True)

    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    users: Mapped[list["UserPermission"]] = relationship(
        back_populates="permission",
        cascade="all, delete-orphan",
    )


class UserPermission(Base):
    __tablename__ = "user_permissions"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )

    permission_id: Mapped[int] = mapped_column(
        ForeignKey("permissions.id", ondelete="CASCADE"),
        index=True,
    )

    user: Mapped["User"] = relationship(back_populates="permissions")
    permission: Mapped["Permission"] = relationship(back_populates="users")

    __table_args__ = (
        UniqueConstraint("user_id", "permission_id", name="uq_user_permission"),
    )
