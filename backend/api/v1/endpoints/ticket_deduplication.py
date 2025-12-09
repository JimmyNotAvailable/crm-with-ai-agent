"""
Ticket deduplication endpoints
Detect and merge duplicate support tickets
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from backend.database.session import get_db
from backend.models.user import User
from backend.utils.security import get_current_user, require_role
from backend.services.ticket_deduplication import TicketDeduplicationService

router = APIRouter()


class SimilarTicketResponse(BaseModel):
    """Response schema for similar tickets"""
    ticket_id: int
    ticket_number: str
    subject: str
    similarity_score: float
    created_at: str
    
    class Config:
        from_attributes = True


class DuplicateDetectionResponse(BaseModel):
    """Response for duplicate detection"""
    primary_ticket_id: int
    primary_ticket_number: str
    duplicates: List[SimilarTicketResponse]


class MergeTicketsRequest(BaseModel):
    """Request schema for merging tickets"""
    primary_ticket_id: int
    duplicate_ticket_ids: List[int] = Field(..., min_items=1)
    merge_notes: Optional[str] = None


class MergeTicketsResponse(BaseModel):
    """Response schema for merge operation"""
    primary_ticket_id: int
    merged_count: int
    message: str


@router.get("/{ticket_id}/similar", response_model=List[SimilarTicketResponse])
def find_similar_tickets(
    ticket_id: int,
    similarity_threshold: float = Query(0.7, ge=0.0, le=1.0),
    time_window_hours: int = Query(72, ge=1, le=720),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("STAFF"))
):
    """
    Find tickets similar to the given ticket
    Staff/Admin only
    """
    dedup_service = TicketDeduplicationService(db)
    
    similar_tickets = dedup_service.find_similar_tickets(
        ticket_id=ticket_id,
        similarity_threshold=similarity_threshold,
        time_window_hours=time_window_hours
    )
    
    if not similar_tickets:
        return []
    
    # Format response
    response = []
    for ticket, similarity in similar_tickets:
        response.append(SimilarTicketResponse(
            ticket_id=ticket.id,
            ticket_number=ticket.ticket_number,
            subject=ticket.subject or "",
            similarity_score=round(similarity, 3),
            created_at=ticket.created_at.isoformat()
        ))
    
    return response


@router.post("/merge", response_model=MergeTicketsResponse)
def merge_tickets(
    merge_request: MergeTicketsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("STAFF"))
):
    """
    Merge duplicate tickets into primary ticket
    Staff/Admin only
    """
    dedup_service = TicketDeduplicationService(db)
    
    try:
        primary_ticket = dedup_service.merge_tickets(
            primary_ticket_id=merge_request.primary_ticket_id,
            duplicate_ticket_ids=merge_request.duplicate_ticket_ids,
            merge_notes=merge_request.merge_notes
        )
        
        return MergeTicketsResponse(
            primary_ticket_id=primary_ticket.id,
            merged_count=len(merge_request.duplicate_ticket_ids),
            message=f"Successfully merged {len(merge_request.duplicate_ticket_ids)} ticket(s) into #{primary_ticket.ticket_number}"
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to merge tickets: {str(e)}"
        )


@router.get("/duplicates/detect", response_model=List[DuplicateDetectionResponse])
def auto_detect_duplicates(
    similarity_threshold: float = Query(0.8, ge=0.0, le=1.0),
    time_window_hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("STAFF"))
):
    """
    Auto-detect potential duplicate tickets
    Staff/Admin only
    """
    dedup_service = TicketDeduplicationService(db)
    
    duplicates_found = dedup_service.auto_detect_duplicates(
        similarity_threshold=similarity_threshold,
        time_window_hours=time_window_hours
    )
    
    if not duplicates_found:
        return []
    
    # Format response
    response = []
    for primary_id, duplicate_list in duplicates_found:
        # Get primary ticket details
        from backend.models.ticket import Ticket
        primary_ticket = db.query(Ticket).filter(Ticket.id == primary_id).first()
        if not primary_ticket:
            continue
        
        duplicates = []
        for dup_id, similarity in duplicate_list:
            dup_ticket = db.query(Ticket).filter(Ticket.id == dup_id).first()
            if dup_ticket:
                duplicates.append(SimilarTicketResponse(
                    ticket_id=dup_ticket.id,
                    ticket_number=dup_ticket.ticket_number,
                    subject=dup_ticket.subject or "",
                    similarity_score=round(similarity, 3),
                    created_at=dup_ticket.created_at.isoformat()
                ))
        
        if duplicates:
            response.append(DuplicateDetectionResponse(
                primary_ticket_id=primary_ticket.id,
                primary_ticket_number=primary_ticket.ticket_number,
                duplicates=duplicates
            ))
    
    return response
