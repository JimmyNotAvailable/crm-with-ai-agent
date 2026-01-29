"""
Ticket models for customer support system
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database.session import Base
import enum


class TicketStatus(str, enum.Enum):
    """Ticket status enumeration"""
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    WAITING_CUSTOMER = "WAITING_CUSTOMER"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class TicketPriority(str, enum.Enum):
    """Ticket priority enumeration"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class TicketCategory(str, enum.Enum):
    """Ticket category enumeration"""
    GENERAL_INQUIRY = "GENERAL_INQUIRY"
    ORDER_ISSUE = "ORDER_ISSUE"
    PRODUCT_QUESTION = "PRODUCT_QUESTION"
    COMPLAINT = "COMPLAINT"
    TECHNICAL_SUPPORT = "TECHNICAL_SUPPORT"
    REFUND_REQUEST = "REFUND_REQUEST"


class Ticket(Base):
    """
    Support ticket model
    Stores customer support conversations
    """
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    ticket_number = Column(String(50), unique=True, index=True, nullable=False)
    
    # Customer reference
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"))  # Staff member
    
    # Ticket details
    subject = Column(String(255), nullable=False)
    category = Column(Enum(TicketCategory), default=TicketCategory.GENERAL_INQUIRY)
    status = Column(Enum(TicketStatus), default=TicketStatus.OPEN, index=True)
    priority = Column(Enum(TicketPriority), default=TicketPriority.MEDIUM)
    
    # Related order (if applicable)
    order_id = Column(Integer, ForeignKey("orders.id"))
    
    # AI Analysis
    sentiment_score = Column(Float)  # -1 to 1 (negative to positive)
    sentiment_label = Column(String(20))  # POSITIVE, NEUTRAL, NEGATIVE
    ai_suggested_category = Column(String(50))
    
    # Channel
    channel = Column(String(50), default="WEB")  # WEB, EMAIL, TELEGRAM, FACEBOOK
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    resolved_at = Column(DateTime(timezone=True))
    closed_at = Column(DateTime(timezone=True))
    
    # Relationships
    messages = relationship("TicketMessage", back_populates="ticket", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Ticket {self.ticket_number} - {self.status}>"


class TicketMessage(Base):
    """
    Individual messages within a support ticket
    """
    __tablename__ = "ticket_messages"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    
    # Sender
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_staff = Column(Integer, default=False)  # True if sent by staff/AI
    is_ai_generated = Column(Integer, default=False)  # True if AI response
    
    # Message content
    message = Column(Text, nullable=False)
    
    # AI metadata
    rag_sources = Column(Text)  # JSON string of source documents used
    agent_thoughts = Column(Text)  # JSON string of agent reasoning process
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    ticket = relationship("Ticket", back_populates="messages")
    
    def __repr__(self):
        return f"<TicketMessage {self.id} for Ticket {self.ticket_id}>"
