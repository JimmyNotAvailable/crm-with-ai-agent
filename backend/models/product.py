"""
Product model for e-commerce catalog
"""
from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime
from sqlalchemy.sql import func
from backend.database.session import Base


class Product(Base):
    """
    Product catalog model
    Stores product information and inventory
    """
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    
    # Pricing
    price = Column(Float, nullable=False)
    cost = Column(Float)  # Cost price for profit calculation
    
    # Inventory
    stock_quantity = Column(Integer, default=0)
    low_stock_threshold = Column(Integer, default=10)
    
    # Categorization
    category = Column(String(100), index=True)
    tags = Column(Text)  # Comma-separated tags for search
    
    # Media
    image_url = Column(String(500))
    
    # Status
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Product {self.sku}: {self.name}>"
    
    @property
    def is_low_stock(self):
        """Check if product is low on stock"""
        return self.stock_quantity <= self.low_stock_threshold
    
    @property
    def is_in_stock(self):
        """Check if product is in stock"""
        return self.stock_quantity > 0
