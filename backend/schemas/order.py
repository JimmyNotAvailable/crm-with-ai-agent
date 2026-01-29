"""
Order schemas for API request/response validation
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from backend.models.order import OrderStatus


class OrderItemCreate(BaseModel):
    """Schema for creating order item"""
    product_id: int
    quantity: int = Field(..., gt=0)


class OrderItemResponse(BaseModel):
    """Schema for order item response"""
    id: int
    product_id: int
    product_name: str
    product_sku: Optional[str] = None
    quantity: int
    unit_price: float
    subtotal: float
    
    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    """Schema for order creation"""
    items: List[OrderItemCreate]
    shipping_address: str
    shipping_city: str
    shipping_phone: str
    payment_method: str = "COD"
    customer_notes: Optional[str] = None


class RefundRequest(BaseModel):
    """Schema for refund request"""
    reason: str = Field(..., min_length=10, max_length=500)
    refund_amount: Optional[float] = None  # If partial refund
    admin_notes: Optional[str] = None


class ReturnRequest(BaseModel):
    """Schema for return request"""
    reason: str = Field(..., min_length=10, max_length=500)
    item_ids: List[int]  # Which items to return
    return_type: str = Field(..., pattern="^(EXCHANGE|REFUND)$")
    admin_notes: Optional[str] = None


class OrderUpdate(BaseModel):
    """Schema for order update"""
    status: Optional[OrderStatus] = None
    admin_notes: Optional[str] = None


class OrderResponse(BaseModel):
    """Schema for order response"""
    id: int
    order_number: str
    customer_id: int
    status: OrderStatus
    total_amount: float
    tax_amount: float
    shipping_fee: float
    discount_amount: float
    shipping_address: str
    shipping_city: str
    shipping_phone: str
    payment_method: str
    payment_status: str
    customer_notes: Optional[str] = None
    admin_notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[OrderItemResponse] = []
    
    class Config:
        from_attributes = True
