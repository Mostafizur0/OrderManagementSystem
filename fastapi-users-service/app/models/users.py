from typing import List
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class User(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=True)
    phone: Mapped[str] = mapped_column(nullable=True)
    password_hash: Mapped[str] = mapped_column(nullable=False)

    refreshtoken: Mapped[List["RefreshToken"]] = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan"
    )
