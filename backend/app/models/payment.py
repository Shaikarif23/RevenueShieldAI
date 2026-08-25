from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    ForeignKey,
    DateTime,
    Enum,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base
from app.models.payment_status import PaymentStatus


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(
        Integer,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    amount = Column(Float, nullable=False)

    payment_method = Column(String(50), nullable=False)

    transaction_id = Column(String(100), unique=True, nullable=False, index=True)

    status = Column(
        Enum(PaymentStatus),
        default=PaymentStatus.PENDING,
        nullable=False,
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Must match Order.payments = relationship(..., back_populates="order")
    order = relationship("Order", back_populates="payments")
