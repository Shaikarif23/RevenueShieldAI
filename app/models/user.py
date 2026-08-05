from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)

    email = Column(String(100), unique=True, nullable=False)

    password = Column(String(255), nullable=False)

    phone = Column(String(20))

    role = Column(String(20), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    restaurant = relationship("Restaurant", back_populates="user", uselist=False)

    customer = relationship("Customer", back_populates="user", uselist=False)

    delivery_partner = relationship(
        "DeliveryPartner",
        back_populates="user",
        uselist=False
    )