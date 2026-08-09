from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    restaurant_name = Column(String(100), nullable=False)

    address = Column(String(255))

    latitude = Column(Float)

    longitude = Column(Float)

    rating = Column(Float, default=5.0)

    user = relationship(
        "User",
        back_populates="restaurant"
    )

    menu_items = relationship(
        "Menu",
        back_populates="restaurant",
        cascade="all, delete-orphan"
    )

    orders = relationship(
        "Order",
        back_populates="restaurant",
        cascade="all, delete-orphan"
    )