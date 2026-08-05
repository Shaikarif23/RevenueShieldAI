from sqlalchemy import Column, Integer, Float, ForeignKey

from sqlalchemy.orm import relationship

from app.database import Base


class OrderItem(Base):

    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(Integer, ForeignKey("orders.id"))

    menu_id = Column(Integer, ForeignKey("menu.id"))

    quantity = Column(Integer)

    unit_price = Column(Float)

    total_price = Column(Float)

    order = relationship(
        "Order",
        back_populates="order_items"
    )

    menu = relationship(
        "Menu",
        back_populates="order_items"
    )