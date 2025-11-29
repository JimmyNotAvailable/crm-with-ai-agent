"""
Knowledge Base Article model for RAG system
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from backend.database.session import Base


class KBArticle(Base):
    """
    Knowledge Base Article model
    Stores uploaded documents for RAG retrieval
    """
    __tablename__ = "kb_articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    
    # File information
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50))  # pdf, docx, txt, md
    file_size = Column(Integer)  # Size in bytes
    
    # Content
    content = Column(Text)  # Extracted text content
    summary = Column(Text)  # AI-generated summary
    
    # Categorization
    category = Column(String(100), index=True)
    tags = Column(Text)  # Comma-separated tags
    
    # Vector store reference
    vector_ids = Column(Text)  # JSON array of vector IDs in ChromaDB
    chunk_count = Column(Integer, default=0)  # Number of chunks created
    
    # Status
    is_active = Column(Boolean, default=True)
    is_indexed = Column(Boolean, default=False)  # True after vectorization complete
    
    # Metadata
    uploaded_by = Column(Integer)  # User ID
    version = Column(Integer, default=1)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    indexed_at = Column(DateTime(timezone=True))
    
    def __repr__(self):
        return f"<KBArticle {self.title} ({self.file_type})>"
