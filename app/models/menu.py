from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Menu(Base):
    __tablename__ = "menu"

    id = Column(Integer, primary_key=True, index=True)

    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))

    item_name = Column(String(100), nullable=False)

    category = Column(String(50))

    price = Column(Float, nullable=False)

    preparation_time = Column(Integer)

    ingredient_cost = Column(Float)

    is_available = Column(String(10), default="YES")

    restaurant = relationship("Restaurant", back_populates="menu_items")

    order_items = relationship("OrderItem", back_populates="menu")