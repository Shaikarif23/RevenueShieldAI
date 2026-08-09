from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class RevenueLeakage(Base):
    __tablename__ = "revenue_leakage"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(Integer, ForeignKey("orders.id"))

    ingredient_cost = Column(Float)

    labour_cost = Column(Float)

    packaging_cost = Column(Float)

    utility_cost = Column(Float)

    cancellation_fee = Column(Float)

    salvage_value = Column(Float)

    loss_amount = Column(Float)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    order = relationship(
        "Order",
        back_populates="revenue"
    )