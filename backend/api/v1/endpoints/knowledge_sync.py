"""
Knowledge Sync API Endpoints
Manage automated knowledge base synchronization
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from backend.database.session import get_db
from backend.models.user import User
from backend.utils.security import get_current_user, require_role
from backend.services.knowledge_sync import KnowledgeSyncService

router = APIRouter()


class SyncFromDirectoryRequest(BaseModel):
    """Request schema for directory sync"""
    directory_path: str
    category: str = "AUTO_SYNC"
    auto_activate: bool = True


class SyncFromURLRequest(BaseModel):
    """Request schema for URL sync"""
    url: HttpUrl
    title: str
    category: str = "WEB_SYNC"
    auto_activate: bool = True


class SyncStatsResponse(BaseModel):
    """Response schema for sync statistics"""
    added: int
    updated: int
    unchanged: int
    errors: List[str]


class SyncResultResponse(BaseModel):
    """Response schema for sync result"""
    status: str
    article_id: Optional[int] = None
    message: str


@router.post("/directory", response_model=SyncStatsResponse)
def sync_from_directory(
    request: SyncFromDirectoryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN"))
):
    """
    Sync knowledge base from directory
    Admin only
    """
    sync_service = KnowledgeSyncService(db)
    
    stats = sync_service.sync_from_directory(
        directory_path=request.directory_path,
        category=request.category,
        auto_activate=request.auto_activate
    )
    
    return SyncStatsResponse(**stats)


@router.post("/url", response_model=SyncResultResponse)
def sync_from_url(
    request: SyncFromURLRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN"))
):
    """
    Sync knowledge article from URL
    Admin only
    """
    sync_service = KnowledgeSyncService(db)
    
    result = sync_service.sync_from_url(
        url=str(request.url),
        title=request.title,
        category=request.category,
        auto_activate=request.auto_activate
    )
    
    return SyncResultResponse(**result)


@router.post("/all", response_model=dict)
def sync_all_sources(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN"))
):
    """
    Sync from all configured sources
    Runs in background
    Admin only
    """
    def run_sync():
        sync_service = KnowledgeSyncService(db)
        stats = sync_service.sync_all_sources()
        print(f"Knowledge sync completed: {stats}")
    
    background_tasks.add_task(run_sync)
    
    return {
        "status": "sync_started",
        "message": "Knowledge base sync running in background"
    }


@router.get("/status", response_model=dict)
def get_sync_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN"))
):
    """
    Get current sync status and configuration
    Admin only
    """
    from backend.models.kb_article import KBArticle
    from sqlalchemy import func
    
    # Get article statistics
    total_articles = db.query(func.count(KBArticle.id)).scalar()
    active_articles = db.query(func.count(KBArticle.id)).filter(
        KBArticle.is_active == True
    ).scalar()
    
    # Get last sync time (approximate from most recent article update)
    last_sync = db.query(func.max(KBArticle.updated_at)).scalar()
    
    return {
        "total_articles": total_articles or 0,
        "active_articles": active_articles or 0,
        "last_sync": last_sync.isoformat() if last_sync else None,
        "sync_enabled": True,
        "auto_sync_interval": "24 hours",  # Configuration placeholder
        "sources_configured": [
            {"type": "directory", "path": "uploads/"},
            # Add more sources as configured
        ]
    }
