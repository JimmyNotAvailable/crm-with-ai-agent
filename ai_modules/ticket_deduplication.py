"""
Ticket Deduplication Service
Detects and merges duplicate support tickets
"""
from sqlalchemy.orm import Session
from backend.models.ticket import Ticket, TicketMessage
from typing import List, Tuple, Optional
from datetime import datetime, timedelta
import difflib


class TicketDeduplicationService:
    """Service for detecting and merging duplicate tickets"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def find_similar_tickets(
        self,
        ticket_id: int,
        similarity_threshold: float = 0.7,
        time_window_hours: int = 72
    ) -> List[Tuple[Ticket, float]]:
        """
        Find tickets similar to the given ticket
        
        Args:
            ticket_id: ID of the ticket to compare against
            similarity_threshold: Minimum similarity score (0.0-1.0)
            time_window_hours: Only check tickets within this time window
            
        Returns:
            List of (Ticket, similarity_score) tuples
        """
        # Get target ticket
        target_ticket = self.db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not target_ticket:
            return []
        
        # Define time window
        cutoff_time = target_ticket.created_at - timedelta(hours=time_window_hours)
        
        # Query potential duplicates
        # Same customer, within time window, not closed
        candidates = self.db.query(Ticket).filter(
            Ticket.id != ticket_id,
            Ticket.customer_id == target_ticket.customer_id,
            Ticket.created_at >= cutoff_time,
            Ticket.status.in_(["OPEN", "IN_PROGRESS"])
        ).all()
        
        # Calculate similarity scores
        similar_tickets = []
        target_content = self._get_ticket_content(target_ticket)
        
        for candidate in candidates:
            candidate_content = self._get_ticket_content(candidate)
            similarity = self._calculate_similarity(target_content, candidate_content)
            
            if similarity >= similarity_threshold:
                similar_tickets.append((candidate, similarity))
        
        # Sort by similarity (highest first)
        similar_tickets.sort(key=lambda x: x[1], reverse=True)
        
        return similar_tickets
    
    def merge_tickets(
        self,
        primary_ticket_id: int,
        duplicate_ticket_ids: List[int],
        merge_notes: Optional[str] = None
    ) -> Ticket:
        """
        Merge duplicate tickets into primary ticket
        
        Args:
            primary_ticket_id: ID of the ticket to keep
            duplicate_ticket_ids: IDs of tickets to merge into primary
            merge_notes: Optional notes about the merge
            
        Returns:
            Updated primary ticket
        """
        # Get primary ticket
        primary_ticket = self.db.query(Ticket).filter(
            Ticket.id == primary_ticket_id
        ).first()
        if not primary_ticket:
            raise ValueError(f"Primary ticket {primary_ticket_id} not found")
        
        # Process each duplicate
        merged_count = 0
        for dup_id in duplicate_ticket_ids:
            duplicate = self.db.query(Ticket).filter(Ticket.id == dup_id).first()
            if not duplicate:
                continue
            
            # Validate same customer
            dup_cust_id = getattr(duplicate, 'customer_id', None)
            prim_cust_id = getattr(primary_ticket, 'customer_id', None)
            if dup_cust_id != prim_cust_id:
                raise ValueError(
                    f"Cannot merge tickets from different customers: "
                    f"{prim_cust_id} vs {dup_cust_id}"
                )
            
            # Move messages from duplicate to primary
            self._move_messages(duplicate, primary_ticket)
            
            # Add merge note to duplicate
            merge_note = f"[MERGED] This ticket was merged into #{primary_ticket.id}"
            if merge_notes:
                merge_note += f" - {merge_notes}"
            
            setattr(duplicate, 'admin_notes', (getattr(duplicate, 'admin_notes', None) or "") + f"\n{merge_note}")
            setattr(duplicate, 'status', "CLOSED")
            setattr(duplicate, 'resolution_notes', f"Duplicate of ticket #{primary_ticket.id}")
            setattr(duplicate, 'closed_at', datetime.utcnow())
            
            merged_count += 1
        
        # Update primary ticket notes
        primary_note = f"\n[MERGE] Merged {merged_count} duplicate ticket(s): {duplicate_ticket_ids}"
        if merge_notes:
            primary_note += f" - {merge_notes}"
        primary_ticket.admin_notes = (primary_ticket.admin_notes or "") + primary_note
        
        self.db.commit()
        self.db.refresh(primary_ticket)
        
        return primary_ticket
    
    def _get_ticket_content(self, ticket: Ticket) -> str:
        """Extract text content from ticket for comparison"""
        content_parts = [
            ticket.subject or "",
            ticket.description or "",
        ]
        
        # Add first message if available
        if ticket.messages:
            first_msg = ticket.messages[0]
            content_parts.append(first_msg.message or "")
        
        return " ".join(content_parts).lower()
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two text strings
        Uses SequenceMatcher for fuzzy matching
        
        Returns:
            Similarity score between 0.0 and 1.0
        """
        if not text1 or not text2:
            return 0.0
        
        # Use difflib's SequenceMatcher for similarity
        matcher = difflib.SequenceMatcher(None, text1, text2)
        return matcher.ratio()
    
    def _move_messages(self, source_ticket: Ticket, target_ticket: Ticket):
        """Move all messages from source ticket to target ticket"""
        for message in source_ticket.messages:
            # Add note about original ticket
            original_note = f"[From ticket #{source_ticket.id}] "
            message.message = original_note + (message.message or "")
            message.ticket_id = target_ticket.id
    
    def auto_detect_duplicates(
        self,
        similarity_threshold: float = 0.8,
        time_window_hours: int = 24
    ) -> List[Tuple[int, List[Tuple[int, float]]]]:
        """
        Automatically detect potential duplicate tickets across all open tickets
        
        Args:
            similarity_threshold: Minimum similarity score
            time_window_hours: Time window for comparison
            
        Returns:
            List of (ticket_id, [(duplicate_id, similarity_score), ...])
        """
        # Get all open tickets
        open_tickets = self.db.query(Ticket).filter(
            Ticket.status.in_(["OPEN", "IN_PROGRESS"])
        ).order_by(Ticket.created_at.desc()).all()
        
        duplicates_found = []
        processed_ids = set()
        
        for ticket in open_tickets:
            ticket_id = int(getattr(ticket, 'id', 0))
            if ticket_id in processed_ids:
                continue
            
            similar = self.find_similar_tickets(
                ticket_id,
                similarity_threshold=similarity_threshold,
                time_window_hours=time_window_hours
            )
            
            if similar:
                duplicate_list = [(t.id, score) for t, score in similar]
                duplicates_found.append((ticket.id, duplicate_list))
                
                # Mark as processed to avoid duplicate detection
                processed_ids.add(ticket.id)
                for dup_id, _ in duplicate_list:
                    processed_ids.add(dup_id)
        
        return duplicates_found
