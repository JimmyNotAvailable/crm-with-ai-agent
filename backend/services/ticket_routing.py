"""
Ticket Routing Service - Auto-route tickets dựa trên routing_rules từ DB

Flow:
1. Ticket được tạo → gọi route_ticket()
2. Lấy tất cả routing_rules (is_active=1) sắp xếp theo priority
3. Evaluate predicate trên ticket
4. Áp dụng action (assign queue, set priority, assign staff)
5. Tạo assignment record

Predicate format:
{
    "category": ["COMPLAINT", "REFUND_REQUEST"],
    "priority": ["HIGH", "URGENT"],
    "keywords": ["hoàn tiền", "lỗi"],
    "channel": ["EMAIL"],
    "sentiment_below": -0.3
}

Action format:
{
    "assign_queue": "ESCALATION",
    "set_priority": "URGENT",
    "assign_to": "<user_uuid>",
    "add_tags": ["urgent"]
}
"""
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
import logging

from backend.models.ticket import Ticket, TicketPriority
from backend.models.ticket_routing import RoutingRule, WorkQueue, Assignment

logger = logging.getLogger(__name__)


class TicketRoutingService:
    """
    Service auto-routing tickets dựa trên routing_rules trong Support DB.
    
    Usage:
        service = TicketRoutingService(support_db)
        result = service.route_ticket(ticket)
    """

    def __init__(self, db: Session):
        self.db = db

    def route_ticket(self, ticket: Ticket) -> Dict[str, Any]:
        """
        Auto-route ticket dựa trên routing_rules.
        
        Args:
            ticket: Ticket object cần route
            
        Returns:
            Dict với matched_rule, assignment, actions_applied
        """
        # Load active rules sorted by priority (lower = higher)
        rules = (
            self.db.query(RoutingRule)
            .filter(RoutingRule.is_active == 1)
            .order_by(RoutingRule.priority.asc())
            .all()
        )

        if not rules:
            logger.info(f"[TicketRouting] No active rules found for ticket {ticket.id}")
            return {
                "routed": False,
                "message": "No routing rules configured",
                "ticket_id": ticket.id
            }

        # Evaluate each rule
        for rule in rules:
            if self._evaluate_predicate(rule.predicate, ticket):
                # Apply actions
                result = self._apply_action(rule, ticket)
                return {
                    "routed": True,
                    "matched_rule": {
                        "id": rule.id,
                        "code": rule.code,
                        "name": rule.name,
                        "priority": rule.priority
                    },
                    "actions_applied": result,
                    "ticket_id": ticket.id
                }

        logger.info(f"[TicketRouting] No rule matched for ticket {ticket.id}")
        return {
            "routed": False,
            "message": "No matching rule found",
            "ticket_id": ticket.id
        }

    def _evaluate_predicate(self, predicate: Dict, ticket: Ticket) -> bool:
        """
        Evaluate a predicate dict against a ticket.
        All specified conditions must match (AND logic).
        """
        if not predicate or not isinstance(predicate, dict):
            return False

        # Check category
        if "category" in predicate:
            allowed = predicate["category"]
            ticket_cat = ticket.category.value if ticket.category else None
            if ticket_cat not in allowed:
                return False

        # Check priority
        if "priority" in predicate:
            allowed = predicate["priority"]
            ticket_pri = ticket.priority.value if ticket.priority else None
            if ticket_pri not in allowed:
                return False

        # Check channel
        if "channel" in predicate:
            allowed = predicate["channel"]
            ticket_ch = ticket.channel or ""
            if ticket_ch not in allowed:
                return False

        # Check keywords (any keyword in subject or first message)
        if "keywords" in predicate:
            keywords = predicate["keywords"]
            text = (ticket.subject or "").lower()
            if ticket.messages:
                text += " " + (ticket.messages[0].message or "").lower()
            if not any(kw.lower() in text for kw in keywords):
                return False

        # Check sentiment threshold
        if "sentiment_below" in predicate:
            threshold = float(predicate["sentiment_below"])
            score = ticket.sentiment_score
            if score is None or score >= threshold:
                return False

        return True

    def _apply_action(self, rule: RoutingRule, ticket: Ticket) -> Dict[str, Any]:
        """
        Apply routing action to ticket.
        Creates an Assignment record.
        """
        action = rule.action or {}
        applied = {}

        # Set priority
        if "set_priority" in action:
            try:
                new_priority = TicketPriority(action["set_priority"])
                ticket.priority = new_priority
                applied["priority"] = new_priority.value
            except (ValueError, KeyError):
                pass

        # Assign to queue
        queue_id = None
        if "assign_queue" in action:
            queue_code = action["assign_queue"]
            queue = self.db.query(WorkQueue).filter(WorkQueue.code == queue_code).first()
            if queue:
                queue_id = queue.id
                applied["queue"] = queue_code

        # Assign to specific staff
        assignee_id = action.get("assign_to")
        if assignee_id:
            ticket.assigned_to = assignee_id
            applied["assigned_to"] = assignee_id

        # Create assignment record
        assignment = Assignment(
            ticket_id=ticket.id,
            queue_id=queue_id,
            assignee_id=assignee_id,
            decided_by_rule=rule.id
        )
        self.db.add(assignment)

        try:
            self.db.commit()
            self.db.refresh(ticket)
            logger.info(
                f"[TicketRouting] Ticket {ticket.id} routed by rule '{rule.code}' "
                f"→ queue={queue_id}, assignee={assignee_id}"
            )
        except Exception as e:
            self.db.rollback()
            logger.error(f"[TicketRouting] Failed to apply routing: {e}")
            applied["error"] = str(e)

        return applied

    def get_active_rules(self) -> List[Dict[str, Any]]:
        """List all active routing rules"""
        rules = (
            self.db.query(RoutingRule)
            .filter(RoutingRule.is_active == 1)
            .order_by(RoutingRule.priority.asc())
            .all()
        )
        return [
            {
                "id": r.id,
                "code": r.code,
                "name": r.name,
                "priority": r.priority,
                "predicate": r.predicate,
                "action": r.action
            }
            for r in rules
        ]

    def get_queues(self) -> List[Dict[str, Any]]:
        """List all work queues"""
        queues = self.db.query(WorkQueue).all()
        return [
            {"id": q.id, "code": q.code, "name": q.name}
            for q in queues
        ]
