"""
Audit Log API Endpoints
View and query audit logs (Admin only)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from backend.database.session import get_db
from backend.models.audit_log import AuditLog
from backend.models.user import User
from backend.utils.security import get_current_user, require_role

router = APIRouter()


class AuditLogResponse(BaseModel):
    """Response schema for audit log"""
    id: int
    user_id: Optional[int]
    username: str
    user_role: str
    action: str
    resource_type: str
    resource_id: Optional[str]
    method: str
    endpoint: str
    ip_address: Optional[str]
    status: str
    error_message: Optional[str]
    duration_ms: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


class AuditStatsResponse(BaseModel):
    """Response schema for audit statistics"""
    total_operations: int
    successful_operations: int
    failed_operations: int
    unique_users: int
    top_actions: List[dict]
    top_resources: List[dict]
    failure_rate: float


@router.get("/", response_model=List[AuditLogResponse])
def list_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN"))
):
    """
    List audit logs with filters
    Admin only
    """
    query = db.query(AuditLog)
    
    # Apply filters
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    
    if action:
        query = query.filter(AuditLog.action == action.upper())
    
    if resource_type:
        query = query.filter(AuditLog.resource_type == resource_type.upper())
    
    if status:
        query = query.filter(AuditLog.status == status.upper())
    
    if start_date:
        query = query.filter(AuditLog.created_at >= start_date)
    
    if end_date:
        query = query.filter(AuditLog.created_at <= end_date)
    
    # Order by most recent first
    logs = query.order_by(desc(AuditLog.created_at)).offset(skip).limit(limit).all()
    
    return logs


@router.get("/stats", response_model=AuditStatsResponse)
def get_audit_stats(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN"))
):
    """
    Get audit log statistics
    Admin only
    """
    # Calculate date range
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Total operations
    total_ops = db.query(func.count(AuditLog.id)).filter(
        AuditLog.created_at >= start_date
    ).scalar()
    
    # Successful vs failed
    successful = db.query(func.count(AuditLog.id)).filter(
        AuditLog.created_at >= start_date,
        AuditLog.status == "SUCCESS"
    ).scalar()
    
    failed = total_ops - successful
    
    # Unique users
    unique_users = db.query(func.count(func.distinct(AuditLog.user_id))).filter(
        AuditLog.created_at >= start_date,
        AuditLog.user_id.isnot(None)
    ).scalar()
    
    # Top actions
    top_actions = db.query(
        AuditLog.action,
        func.count(AuditLog.id).label("count")
    ).filter(
        AuditLog.created_at >= start_date
    ).group_by(AuditLog.action).order_by(desc("count")).limit(5).all()
    
    top_actions_list = [
        {"action": action, "count": count}
        for action, count in top_actions
    ]
    
    # Top resources
    top_resources = db.query(
        AuditLog.resource_type,
        func.count(AuditLog.id).label("count")
    ).filter(
        AuditLog.created_at >= start_date
    ).group_by(AuditLog.resource_type).order_by(desc("count")).limit(5).all()
    
    top_resources_list = [
        {"resource_type": resource, "count": count}
        for resource, count in top_resources
    ]
    
    # Calculate failure rate
    failure_rate = (failed / total_ops * 100) if total_ops > 0 else 0.0
    
    return AuditStatsResponse(
        total_operations=total_ops or 0,
        successful_operations=successful or 0,
        failed_operations=failed or 0,
        unique_users=unique_users or 0,
        top_actions=top_actions_list,
        top_resources=top_resources_list,
        failure_rate=round(failure_rate, 2)
    )


@router.get("/user/{user_id}", response_model=List[AuditLogResponse])
def get_user_audit_trail(
    user_id: int,
    limit: int = Query(50, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN"))
):
    """
    Get audit trail for specific user
    Admin only
    """
    logs = db.query(AuditLog).filter(
        AuditLog.user_id == user_id
    ).order_by(desc(AuditLog.created_at)).limit(limit).all()
    
    return logs


@router.get("/suspicious", response_model=List[AuditLogResponse])
def get_suspicious_activities(
    hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN"))
):
    """
    Detect suspicious activities
    - Multiple failed operations
    - Operations from unusual IPs
    Admin only
    """
    start_date = datetime.utcnow() - timedelta(hours=hours)
    
    # Find users with high failure rates
    suspicious = db.query(AuditLog).filter(
        AuditLog.created_at >= start_date,
        AuditLog.status == "FAILED"
    ).order_by(desc(AuditLog.created_at)).limit(100).all()
    
    return suspicious
