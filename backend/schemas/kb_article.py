"""
Knowledge Base Article schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class KBArticleCreate(BaseModel):
    """Schema for KB article creation"""
    title: str = Field(..., min_length=1, max_length=255)
    category: Optional[str] = None
    tags: Optional[str] = None


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
