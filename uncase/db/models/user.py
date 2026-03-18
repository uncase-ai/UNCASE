"""User and org membership database models."""

from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from uncase.db.base import Base, TimestampMixin


class UserModel(TimestampMixin, Base):
    """Individual user account."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(512), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    memberships: Mapped[list[OrgMembershipModel]] = relationship(back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<UserModel id={self.id} email={self.email}>"


class OrgMembershipModel(TimestampMixin, Base):
    """Org membership with role."""

    __tablename__ = "org_memberships"

    user_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    organization_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="member")

    user: Mapped[UserModel] = relationship(back_populates="memberships")
    organization: Mapped["OrganizationModel"] = relationship(back_populates="memberships")  # type: ignore[name-defined]  # noqa: F821, UP037

    __table_args__ = (
        UniqueConstraint("user_id", "organization_id", name="uq_user_org"),
        Index("ix_org_memberships_org_user", "organization_id", "user_id"),
    )

    def __repr__(self) -> str:
        return f"<OrgMembershipModel user={self.user_id} org={self.organization_id} role={self.role}>"
