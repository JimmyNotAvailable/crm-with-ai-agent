"""
Ticket schemas for API request/response validation
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from backend.models.ticket import TicketStatus, TicketPriority, TicketCategory


class TicketMessageCreate(BaseModel):
    """Schema for creating ticket message"""
    message: str = Field(..., min_length=1)


class TicketMessageResponse(BaseModel):
    """Schema for ticket message response"""
    id: int
    ticket_id: int
    sender_id: int
    is_staff: bool
    is_ai_generated: bool
    message: str
    rag_sources: Optional[str] = None
    agent_thoughts: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class TicketCreate(BaseModel):
    """Schema for ticket creation"""
    subject: str = Field(..., min_length=1, max_length=255)
    category: TicketCategory = TicketCategory.GENERAL_INQUIRY
    order_id: Optional[int] = None
    initial_message: str = Field(..., min_length=1)
    channel: str = "WEB"


class TicketUpdate(BaseModel):
    """Schema for ticket update"""
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    assigned_to: Optional[int] = None


class TicketResponse(BaseModel):
    """Schema for ticket response"""
    id: int
    ticket_number: str
    customer_id: int
    assigned_to: Optional[int] = None
    subject: str
    category: TicketCategory
    status: TicketStatus
    priority: TicketPriority
    order_id: Optional[int] = None
    sentiment_score: Optional[float] = None
    sentiment_label: Optional[str] = None
    channel: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    messages: List[TicketMessageResponse] = []
    
    class Config:
        from_attributes = True
