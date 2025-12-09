"""
Knowledge Base Article schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class KBArticleCreate(BaseModel):
    """Schema for KB article creation"""
    title: str = Field(..., min_length=1, max_length=255)
    category: Optional[str] = None
    tags: Optional[str] = None


class KBArticleUpdate(BaseModel):
    """Schema for KB article update"""
    title: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    summary: Optional[str] = None
    is_active: Optional[bool] = None


class KBArticleResponse(BaseModel):
    """Schema for KB article response"""
    id: int
    title: str
    filename: str
    file_type: str
    file_size: Optional[int] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    summary: Optional[str] = None
    is_active: bool
    is_indexed: bool
    chunk_count: int
    created_at: datetime
    indexed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class KBHealthResponse(BaseModel):
    """Schema for RAG health check response"""
    total_articles: int
    active_articles: int
    indexed_articles: int
    total_chunks: int
    coverage_rate: float
    health_status: str  # HEALTHY, WARNING, CRITICAL
    issues: List[str]
    last_check: datetime
