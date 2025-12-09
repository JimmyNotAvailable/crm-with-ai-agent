"""
Shopping Cart models
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database.session import Base


class Cart(Base):
    """
    Shopping cart model
    One cart per active user session
    """
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")
    
    @property
    def total_amount(self):
        """Calculate total cart amount"""
        return sum(item.subtotal for item in self.items)
    
    @property
    def total_items(self):
        """Count total items in cart"""
        return sum(item.quantity for item in self.items)
    
    def __repr__(self):
        return f"<Cart user_id={self.user_id} items={self.total_items}>"


class CartItem(Base):
    """
    Individual items in shopping cart
    """
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # Snapshot of product info at time of adding to cart
    product_name = Column(String(255), nullable=False)
    product_sku = Column(String(100))
    unit_price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    
    # Timestamps
    added_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    cart = relationship("Cart", back_populates="items")
    product = relationship("Product")
    
    @property
    def subtotal(self):
        """Calculate item subtotal"""
        return self.unit_price * self.quantity
    
    def __repr__(self):
        return f"<CartItem {self.product_name} x{self.quantity}>"
