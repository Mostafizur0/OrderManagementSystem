from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Order(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(nullable=False)
    product_id: Mapped[int] = mapped_column(nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)
