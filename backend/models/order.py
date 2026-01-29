"""
Order models for e-commerce transactions
"""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database.session import Base
import enum


class OrderStatus(str, enum.Enum):
    """Order status enumeration"""
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    PROCESSING = "PROCESSING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"


class Order(Base):
    """
    Order model for customer purchases
    """
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, index=True, nullable=False)
    
    # Customer reference
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Order details
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False, index=True)
    total_amount = Column(Float, nullable=False)
    tax_amount = Column(Float, default=0)
    shipping_fee = Column(Float, default=0)
    discount_amount = Column(Float, default=0)
    
    # Shipping information
    shipping_address = Column(Text)
    shipping_city = Column(String(100))
    shipping_phone = Column(String(20))
    
    # Payment
    payment_method = Column(String(50))
    payment_status = Column(String(50), default="PENDING")
    
    # Notes
    customer_notes = Column(Text)
    admin_notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    confirmed_at = Column(DateTime(timezone=True))
    shipped_at = Column(DateTime(timezone=True))
    delivered_at = Column(DateTime(timezone=True))
    
    # Relationships
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Order {self.order_number} - {self.status}>"
    
    @property
    def can_cancel(self):
        """Check if order can be cancelled"""
        return self.status in [OrderStatus.PENDING, OrderStatus.CONFIRMED]


class OrderItem(Base):
    """
    Order item model - line items in an order
    """
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # Item details (snapshot at order time)
    product_name = Column(String(255), nullable=False)
    product_sku = Column(String(100))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    order = relationship("Order", back_populates="items")
    
    def __repr__(self):
        return f"<OrderItem {self.product_name} x{self.quantity}>"
