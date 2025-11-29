"""
Product schemas for API request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProductBase(BaseModel):
    """Base product schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    category: Optional[str] = None
    tags: Optional[str] = None


class ProductCreate(ProductBase):
    """Schema for product creation"""
    sku: str = Field(..., min_length=1, max_length=100)
    stock_quantity: int = Field(default=0, ge=0)
    cost: Optional[float] = Field(None, ge=0)
    image_url: Optional[str] = None


class ProductUpdate(BaseModel):
    """Schema for product update"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    cost: Optional[float] = Field(None, ge=0)
    category: Optional[str] = None
    tags: Optional[str] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    """Schema for product response"""
    id: int
    sku: str
    stock_quantity: int
    cost: Optional[float] = None
    image_url: Optional[str] = None
    is_active: bool
    is_featured: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
