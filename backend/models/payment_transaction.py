"""
Payment Transaction model - Persisted payment records (Order DB)
"""
import uuid
from sqlalchemy import Column, String, Float, DateTime, Text, Enum as SAEnum
from sqlalchemy.sql import func
from backend.database.session import Base
import enum


class PaymentStatusEnum(str, enum.Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class PaymentTransactionModel(Base):
    """
    Persisted payment transaction.
    Stored in Order DB alongside orders.
    """
    __tablename__ = "payment_transactions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    draft_id = Column(String(36), nullable=False, index=True)
    user_id = Column(String(36), nullable=False, index=True)  # Cross-DB, no FK
    order_id = Column(String(36), nullable=True, index=True)  # Linked after order creation

    amount = Column(Float, nullable=False)
    method = Column(String(50), nullable=False)  # BANK_TRANSFER, MOMO, COD
    status = Column(
        SAEnum(PaymentStatusEnum),
        default=PaymentStatusEnum.PENDING,
        nullable=False,
        index=True
    )
    ref_code = Column(String(100), unique=True, nullable=False, index=True)
    qr_url = Column(Text, nullable=True)
    note = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<PaymentTransaction {self.ref_code} - {self.status}>"
