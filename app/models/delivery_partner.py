from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class DeliveryPartner(Base):
    __tablename__ = "delivery_partners"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    vehicle_type = Column(String(50))

    vehicle_number = Column(String(30))

    current_status = Column(String(20), default="AVAILABLE")

    current_latitude = Column(Float)

    current_longitude = Column(Float)

    user = relationship("User", back_populates="delivery_partner")
orders = relationship(
    "Order",
    back_populates="delivery_partner"
)    