from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base
from app.models.order_status import OrderStatus


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)

    customer_id = Column(Integer, ForeignKey("customers.id"))

    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))

    delivery_partner_id = Column(
        Integer,
        ForeignKey("delivery_partners.id"),
        nullable=True
    )

    subtotal = Column(Float, default=0, nullable=False)

    tax = Column(Float, default=0, nullable=False)

    delivery_charge = Column(Float, default=0, nullable=False)

    total_amount = Column(Float, default=0, nullable=False)

    status = Column(
        Enum(OrderStatus),
        default=OrderStatus.PLACED
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    customer = relationship(
        "Customer",
        back_populates="orders"
    )

    restaurant = relationship(
        "Restaurant",
        back_populates="orders"
    )

    delivery_partner = relationship(
        "DeliveryPartner",
        back_populates="orders"
    )

    order_items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )

    tracking_history = relationship(
        "Tracking",
        back_populates="order",
        cascade="all, delete-orphan"
    )

    cancellation = relationship(
        "Cancellation",
        back_populates="order",
        uselist=False,
        cascade="all, delete-orphan"
    )

    revenue = relationship(
        "RevenueLeakage",
        back_populates="order",
        uselist=False,
        cascade="all, delete-orphan"
    )
    payment = relationship(
    "Payment",
    back_populates="order",
    uselist=False,
    cascade="all, delete-orphan"
    )
    
    review = relationship(
    "Review",
    back_populates="order",
    uselist=False,
    cascade="all, delete-orphan"
    )