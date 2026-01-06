from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, func, ForeignKey

from app.models.base import Base
from app.models.users import User


class RefreshToken(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id), nullable=False, index=True)
    token: Mapped[str] = mapped_column(unique=True, nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_revoked: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="refreshtoken")
