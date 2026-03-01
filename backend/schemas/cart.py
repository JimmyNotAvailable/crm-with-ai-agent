"""
Cart schemas for API request/response validation
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class CartItemCreate(BaseModel):
    """Schema for adding item to cart"""
    product_id: str
    quantity: int = Field(1, ge=1)


class CartItemUpdate(BaseModel):
    """Schema for updating cart item quantity"""
    quantity: int = Field(1, ge=1)


class CartItemResponse(BaseModel):
    """Schema for cart item response"""
    id: str
    product_id: str
    product_name: str
    product_sku: Optional[str] = None
    unit_price: float
    quantity: int
    subtotal: float
    added_at: datetime
    
    class Config:
        from_attributes = True


class CartResponse(BaseModel):
    """Schema for cart response"""
    id: str
    user_id: str
    items: List[CartItemResponse] = []
    total_items: int
    total_amount: float
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CheckoutRequest(BaseModel):
    """Schema for checkout request"""
    shipping_address: str = Field(..., min_length=1)
    shipping_city: str = Field(..., min_length=1)
    shipping_phone: str = Field(..., min_length=10)
    payment_method: str = "COD"
    customer_notes: Optional[str] = None
