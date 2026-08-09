from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Cancellation(Base):
    __tablename__ = "cancellations"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(Integer, ForeignKey("orders.id"))

    cancelled_by = Column(String(30))

    reason = Column(String(255))

    refund_amount = Column(Float)

    cancellation_fee = Column(Float)

    cancelled_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    order = relationship(
        "Order",
        back_populates="cancellation"
    )