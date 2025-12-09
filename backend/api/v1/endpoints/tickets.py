"""
Ticket management endpoints for customer support
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from backend.database.session import get_db
from backend.models.ticket import Ticket, TicketMessage, TicketStatus, TicketPriority
from backend.models.user import User
from backend.schemas.ticket import (
    TicketCreate, TicketUpdate, TicketResponse,
    TicketMessageCreate, TicketMessageResponse
)
from backend.utils.security import get_current_user, require_role
from backend.services.rag_pipeline import RAGPipeline
import random
import string
import json

router = APIRouter()


def generate_ticket_number() -> str:
    """Generate unique ticket number"""
    timestamp = datetime.now().strftime("%Y%m%d")
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"TKT-{timestamp}-{random_suffix}"


def analyze_sentiment(message: str) -> tuple[float, str]:
    """
    Simple sentiment analysis (mock implementation for demo)
    In production, use proper NLP model
    """
    negative_keywords = ["bad", "terrible", "worst", "hate", "angry", "disappointing", 
                         "awful", "horrible", "poor", "xấu", "tệ", "tồi", "ghét"]
    positive_keywords = ["good", "great", "excellent", "love", "amazing", "wonderful",
                         "fantastic", "perfect", "tốt", "tuyệt", "hay"]
    
    message_lower = message.lower()
    
    neg_count = sum(1 for word in negative_keywords if word in message_lower)
    pos_count = sum(1 for word in positive_keywords if word in message_lower)
    
    if neg_count > pos_count:
        return -0.5, "NEGATIVE"
    elif pos_count > neg_count:
        return 0.5, "POSITIVE"
    else:
        return 0.0, "NEUTRAL"


@router.post("/", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket(
    ticket_data: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create new support ticket
    """
    # Analyze sentiment of initial message
    sentiment_score, sentiment_label = analyze_sentiment(ticket_data.initial_message)
    
    # Auto-escalate if negative sentiment
    priority = TicketPriority.MEDIUM
    if sentiment_label == "NEGATIVE":
        priority = TicketPriority.HIGH
    
    # Create ticket
    new_ticket = Ticket(
        ticket_number=generate_ticket_number(),
        customer_id=current_user.id,
        subject=ticket_data.subject,
        category=ticket_data.category,
        status=TicketStatus.OPEN,
        priority=priority,
        order_id=ticket_data.order_id,
        sentiment_score=sentiment_score,
        sentiment_label=sentiment_label,
        channel=ticket_data.channel
    )
    
    db.add(new_ticket)
    db.flush()
    
    # Create initial message
    initial_message = TicketMessage(
        ticket_id=new_ticket.id,
        sender_id=current_user.id,
        is_staff=False,
        message=ticket_data.initial_message
    )
    db.add(initial_message)
    
    # Auto-assign to staff if high priority (simple round-robin)
    if priority in [TicketPriority.HIGH, TicketPriority.URGENT]:
        staff_members = db.query(User).filter(User.role == "STAFF").all()
        if staff_members:
            assigned_staff = random.choice(staff_members)
            new_ticket.assigned_to = assigned_staff.id
    
    db.commit()
    db.refresh(new_ticket)
    
    return new_ticket


@router.get("/", response_model=List[TicketResponse])
def list_tickets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    status_filter: Optional[TicketStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List tickets
    - Customers see only their tickets
    - Staff/Admin see all or assigned tickets
    """
    query = db.query(Ticket)
    
    if current_user.role.value == "CUSTOMER":
        query = query.filter(Ticket.customer_id == current_user.id)
    elif current_user.role.value == "STAFF":
        # Staff can see tickets assigned to them or unassigned
        query = query.filter(
            (Ticket.assigned_to == current_user.id) | 
            (Ticket.assigned_to == None)
        )
    
    if status_filter:
        query = query.filter(Ticket.status == status_filter)
    
    tickets = query.order_by(Ticket.created_at.desc()).offset(skip).limit(limit).all()
    return tickets


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get ticket by ID with messages
    """
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Check permissions
    if current_user.role.value == "CUSTOMER" and int(ticket.customer_id) != int(current_user.id):  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this ticket"
        )
    
    return ticket


@router.put("/{ticket_id}", response_model=TicketResponse)
def update_ticket(
    ticket_id: int,
    ticket_data: TicketUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("STAFF"))
):
    """
    Update ticket (Staff/Admin only)
    """
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Update fields
    if ticket_data.status:
        ticket.status = ticket_data.status.value  # type: ignore
        if ticket_data.status == TicketStatus.RESOLVED:
            ticket.resolved_at = datetime.utcnow()  # type: ignore
        elif ticket_data.status == TicketStatus.CLOSED:
            ticket.closed_at = datetime.utcnow()  # type: ignore
    
    if ticket_data.priority:
        ticket.priority = ticket_data.priority.value  # type: ignore
    
    if ticket_data.assigned_to is not None:
        ticket.assigned_to = ticket_data.assigned_to  # type: ignore
    
    db.commit()
    db.refresh(ticket)
    
    return ticket


@router.post("/{ticket_id}/messages", response_model=TicketMessageResponse)
def add_ticket_message(
    ticket_id: int,
    message_data: TicketMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add message to ticket (with optional AI assistance)
    """
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Check permissions
    if current_user.role.value == "CUSTOMER" and int(ticket.customer_id) != int(current_user.id):  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add message to this ticket"
        )
    
    # Create message
    new_message = TicketMessage(
        ticket_id=ticket_id,
        sender_id=current_user.id,
        is_staff=(current_user.role.value in ["STAFF", "ADMIN"]),
        message=message_data.message
    )
    
    db.add(new_message)
    
    # Update ticket status if customer replies
    if current_user.role.value == "CUSTOMER" and str(ticket.status) == TicketStatus.WAITING_CUSTOMER.value:
        ticket.status = TicketStatus.IN_PROGRESS.value  # type: ignore
    
    db.commit()
    db.refresh(new_message)
    
    return new_message


@router.post("/{ticket_id}/ai-reply", response_model=TicketMessageResponse)
def generate_ai_reply(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("STAFF"))
):
    """
    Generate AI-powered reply for ticket using RAG
    """
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Get last customer message
    last_message = db.query(TicketMessage).filter(
        TicketMessage.ticket_id == ticket_id,
        TicketMessage.is_staff == False
    ).order_by(TicketMessage.created_at.desc()).first()
    
    if not last_message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No customer message to reply to"
        )
    
    # Use RAG to generate response
    rag = RAGPipeline()
    try:
        ai_response = rag.generate_answer(
            query=str(last_message.message),  # type: ignore
            top_k=3
        )
        
        # Create AI message
        ai_message = TicketMessage(
            ticket_id=ticket_id,
            sender_id=current_user.id,  # Logged as staff who triggered
            is_staff=True,
            is_ai_generated=True,
            message=ai_response if isinstance(ai_response, str) else ai_response.get("answer", ""),
            rag_sources=None,
            agent_thoughts=None
        )
        
        db.add(ai_message)
        ticket.status = TicketStatus.WAITING_CUSTOMER.value  # type: ignore
        
        db.commit()
        db.refresh(ai_message)
        
        return ai_message
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate AI reply: {str(e)}"
        )


@router.get("/stats/summary")
def get_ticket_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("STAFF"))
):
    """
    Get ticket statistics (Staff/Admin only)
    """
    total_tickets = db.query(Ticket).count()
    open_tickets = db.query(Ticket).filter(Ticket.status == TicketStatus.OPEN).count()
    in_progress = db.query(Ticket).filter(Ticket.status == TicketStatus.IN_PROGRESS).count()
    resolved = db.query(Ticket).filter(Ticket.status == TicketStatus.RESOLVED).count()
    
    # Sentiment distribution
    negative_tickets = db.query(Ticket).filter(Ticket.sentiment_label == "NEGATIVE").count()
    
    return {
        "total": total_tickets,
        "open": open_tickets,
        "in_progress": in_progress,
        "resolved": resolved,
        "negative_sentiment": negative_tickets
    }
