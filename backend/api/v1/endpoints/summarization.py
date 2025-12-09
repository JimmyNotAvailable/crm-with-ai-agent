"""
AI Summarization Endpoints
Auto-summarize tickets, conversations, and customer behaviors
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.database.session import get_db
from backend.models.user import User
from backend.models.ticket import Ticket
from backend.models.conversation import Conversation
from backend.utils.security import get_current_user, require_role
from backend.services.summarization import SummarizationService

router = APIRouter()


@router.get("/ticket/{ticket_id}")
def summarize_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate AI summary for a ticket
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
            detail="Not authorized"
        )
    
    summarizer = SummarizationService()
    summary = summarizer.summarize_ticket(ticket, db)
    
    return {
        "ticket_id": ticket_id,
        "ticket_number": ticket.ticket_number,
        "summary": summary
    }


@router.get("/conversation/{conversation_id}")
def summarize_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate AI summary for a conversation
    """
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Check permissions
    if conversation.user_id != current_user.id and current_user.role.value not in ["ADMIN", "STAFF"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    summarizer = SummarizationService()
    summary = summarizer.summarize_conversation(conversation, db)
    
    return {
        "conversation_id": conversation_id,
        "summary": summary
    }


@router.get("/customer-behavior/{user_id}")
def summarize_customer_behavior(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("STAFF"))
):
    """
    Generate customer behavior summary (Staff/Admin only)
    Includes purchase history, support patterns, engagement level
    """
    summarizer = SummarizationService()
    behavior = summarizer.summarize_customer_behavior(user_id, db)
    
    if "error" in behavior:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=behavior["error"]
        )
    
    return behavior


@router.get("/customer-behavior/me")
def summarize_my_behavior(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's behavior summary
    """
    summarizer = SummarizationService()
    behavior = summarizer.summarize_customer_behavior(int(current_user.id), db)  # type: ignore
    
    return behavior


@router.post("/tickets/batch")
def summarize_tickets_batch(
    ticket_ids: List[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("STAFF"))
):
    """
    Summarize multiple tickets at once (Staff/Admin only)
    """
    summarizer = SummarizationService()
    summaries = summarizer.summarize_ticket_batch(ticket_ids, db)
    
    return {
        "count": len(summaries),
        "summaries": summaries
    }
