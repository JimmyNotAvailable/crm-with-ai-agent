"""
Audit Log Model
Track all system operations for security and compliance
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from backend.database.session import Base


class AuditLog(Base):
    """
    Audit log for tracking system operations
    Records who did what, when, and from where
    """
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    
    # User information
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Null for system operations
    username = Column(String(100))
    user_role = Column(String(20))
    
    # Operation details
    action = Column(String(50), nullable=False, index=True)  # CREATE, READ, UPDATE, DELETE, LOGIN, LOGOUT
    resource_type = Column(String(50), nullable=False, index=True)  # User, Product, Order, Ticket, etc.
    resource_id = Column(String(100))  # ID of affected resource
    
    # Request details
    method = Column(String(10))  # HTTP method: GET, POST, PUT, DELETE
    endpoint = Column(String(255))  # API endpoint
    ip_address = Column(String(45))  # IPv4 or IPv6
    user_agent = Column(String(500))
    
    # Data changes (for UPDATE operations)
    old_values = Column(JSON)  # Previous values (with PII masked)
    new_values = Column(JSON)  # New values (with PII masked)
    
    # Status
    status = Column(String(20), default="SUCCESS")  # SUCCESS, FAILED
    error_message = Column(Text)  # If failed
    
    # Metadata
    duration_ms = Column(Integer)  # Request duration in milliseconds
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, resource={self.resource_type}, user={self.username})>"
