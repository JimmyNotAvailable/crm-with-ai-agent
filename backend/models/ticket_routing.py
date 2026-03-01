"""
Ticket Routing models for auto-routing rules & assignments
Tables: routing_rules, work_queues, assignments (Support DB)
"""
import uuid
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database.session import Base


class RoutingRule(Base):
    """
    Routing rule for automatic ticket assignment.
    
    predicate JSON format:
    {
        "category": ["COMPLAINT", "REFUND_REQUEST"],
        "priority": ["HIGH", "URGENT"],
        "keywords": ["hoàn tiền", "lỗi"],
        "channel": ["EMAIL"],
        "sentiment_below": -0.3
    }
    
    action JSON format:
    {
        "assign_queue": "ESCALATION",
        "set_priority": "URGENT",
        "assign_to": "<user_uuid>",
        "add_tags": ["urgent", "vip-customer"]
    }
    """
    __tablename__ = "routing_rules"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(64), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    priority = Column(Integer, default=100, nullable=False, comment="Lower = higher priority")
    predicate = Column(JSON, nullable=False, comment="Conditions to match")
    action = Column(JSON, nullable=False, comment="Actions to take")
    is_active = Column(Integer, default=1, nullable=False)

    def __repr__(self):
        return f"<RoutingRule {self.code} (priority={self.priority})>"


class WorkQueue(Base):
    """Work queue for ticket routing"""
    __tablename__ = "work_queues"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(64), unique=True, nullable=False)
    name = Column(String(255), nullable=False)

    def __repr__(self):
        return f"<WorkQueue {self.code}>"


class Assignment(Base):
    """Ticket assignment record"""
    __tablename__ = "assignments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ticket_id = Column(String(36), ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False)
    queue_id = Column(String(36), ForeignKey("work_queues.id", ondelete="SET NULL"), nullable=True)
    assignee_id = Column(String(36), nullable=True, comment="User ID (no FK, cross-DB)")
    assigned_by = Column(String(36), nullable=True, comment="User ID who assigned (no FK)")
    decided_by_rule = Column(
        String(36), ForeignKey("routing_rules.id", ondelete="SET NULL"), nullable=True
    )
    assigned_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships (same DB)
    ticket = relationship("Ticket", backref="assignments")
    queue = relationship("WorkQueue")
    rule = relationship("RoutingRule")

    def __repr__(self):
        return f"<Assignment ticket={self.ticket_id} queue={self.queue_id}>"
