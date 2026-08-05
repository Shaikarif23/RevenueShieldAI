from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    default_address = Column(String(255))

    city = Column(String(100))

    latitude = Column(Float)

    longitude = Column(Float)

    user = relationship("User", back_populates="customer")
orders = relationship(
    "Order",
    back_populates="customer"
)    