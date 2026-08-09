from sqlalchemy import (
    Column,
    Integer,
    Float,
    ForeignKey
)
from sqlalchemy.orm import relationship

from app.database import Base


class OrderItem(Base):

    __tablename__ = "order_items"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    order_id = Column(
        Integer,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False
    )

    menu_id = Column(
        Integer,
        ForeignKey("menu.id"),
        nullable=False
    )

    quantity = Column(
        Integer,
        nullable=False
    )

    unit_price = Column(
        Float,
        nullable=False
    )

    total_price = Column(
        Float,
        nullable=False
    )


    # Relationship with Order
    order = relationship(
        "Order",
        back_populates="order_items"
    )


    # Relationship with Menu
    menu = relationship(
        "Menu",
        back_populates="order_items"
    )