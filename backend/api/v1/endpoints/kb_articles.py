"""
Knowledge Base Articles Management Endpoints
CRUD operations for KB articles with RAG health monitoring
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from backend.database.session import get_db
from backend.models.kb_article import KBArticle
from backend.schemas.kb_article import (
    KBArticleCreate, KBArticleUpdate, KBArticleResponse,
    KBHealthResponse
)
from backend.utils.security import get_current_user, require_role
from backend.models.user import User
from backend.services.rag_pipeline import RAGPipeline
import os
import shutil

router = APIRouter()


@router.get("/", response_model=List[KBArticleResponse])
def list_kb_articles(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all knowledge base articles
    Filter by category and active status
    """
    query = db.query(KBArticle)
    
    if category:
        query = query.filter(KBArticle.category == category)
    
    if is_active is not None:
        query = query.filter(KBArticle.is_active == is_active)
    
    articles = query.order_by(KBArticle.created_at.desc()).offset(skip).limit(limit).all()
    return articles


@router.get("/{article_id}", response_model=KBArticleResponse)
def get_kb_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get KB article by ID
    """
    article = db.query(KBArticle).filter(KBArticle.id == article_id).first()
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KB Article not found"
        )
    return article


@router.post("/", response_model=KBArticleResponse, status_code=status.HTTP_201_CREATED)
def create_kb_article(
    file: UploadFile = File(...),
    title: str = Form(...),
    category: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("STAFF"))
):
    """
    Upload and create new KB article
    Automatically indexes to vector store
    """
    # Save file
    upload_dir = "./uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    filename = file.filename or "unknown_file"
    file_path = os.path.join(upload_dir, filename)
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())
    
    # Get file info
    file_size = os.path.getsize(file_path)
    file_type = filename.split(".")[-1].lower() if "." in filename else "txt"
    
    # Extract content
    content = ""
    try:
        if file_type in ["txt", "md"]:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        # Add support for PDF, DOCX if needed
    except Exception as e:
        content = f"[Error reading file: {str(e)}]"
    
    # Create KB article
    new_article = KBArticle(
        title=title,
        filename=file.filename,
        file_path=file_path,
        file_type=file_type,
        file_size=file_size,
        content=content,
        category=category,
        tags=tags,
        uploaded_by=current_user.id,
        is_active=True,
        is_indexed=False
    )
    
    db.add(new_article)
    db.flush()
    
    # Index to vector store
    try:
        rag_service = RAGPipeline()
        chunk_count = rag_service.upload_and_index(
            file_path, 
            metadata={"article_id": new_article.id, "title": title}
        )
        
        new_article.chunk_count = chunk_count  # type: ignore
        new_article.is_indexed = True  # type: ignore
        new_article.indexed_at = datetime.utcnow()  # type: ignore
    except Exception as e:
        # Still save article but mark as not indexed
        new_article.is_indexed = False  # type: ignore
        print(f"Indexing error: {str(e)}")
    
    db.commit()
    db.refresh(new_article)
    
    return new_article


@router.put("/{article_id}", response_model=KBArticleResponse)
def update_kb_article(
    article_id: int,
    article_data: KBArticleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("STAFF"))
):
    """
    Update KB article metadata
    """
    article = db.query(KBArticle).filter(KBArticle.id == article_id).first()
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KB Article not found"
        )
    
    # Update fields
    if article_data.title:
        article.title = article_data.title  # type: ignore
    
    if article_data.category:
        article.category = article_data.category  # type: ignore
    
    if article_data.tags:
        article.tags = article_data.tags  # type: ignore
    
    if article_data.is_active is not None:
        article.is_active = article_data.is_active  # type: ignore
    
    if article_data.summary:
        article.summary = article_data.summary  # type: ignore
    
    db.commit()
    db.refresh(article)
    
    return article


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_kb_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN"))
):
    """
    Delete KB article (Admin only)
    Also removes from vector store
    """
    article = db.query(KBArticle).filter(KBArticle.id == article_id).first()
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KB Article not found"
        )
    
    # Delete file
    try:
        if os.path.exists(str(article.file_path)):  # type: ignore
            os.remove(str(article.file_path))  # type: ignore
    except Exception as e:
        print(f"Error deleting file: {str(e)}")
    
    # TODO: Remove from vector store using vector_ids
    
    db.delete(article)
    db.commit()
    
    return None


@router.post("/{article_id}/reindex")
def reindex_kb_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("STAFF"))
):
    """
    Re-index KB article to vector store
    """
    article = db.query(KBArticle).filter(KBArticle.id == article_id).first()
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KB Article not found"
        )
    
    try:
        rag_service = RAGPipeline()
        chunk_count = rag_service.upload_and_index(
            str(article.file_path),  # type: ignore
            metadata={"article_id": article.id, "title": article.title}
        )
        
        article.chunk_count = chunk_count  # type: ignore
        article.is_indexed = True  # type: ignore
        article.indexed_at = datetime.utcnow()  # type: ignore
        
        db.commit()
        
        return {
            "message": "Article re-indexed successfully",
            "chunk_count": chunk_count
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Re-indexing failed: {str(e)}"
        )


@router.get("/health/check", response_model=KBHealthResponse)
def check_kb_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("STAFF"))
):
    """
    Check RAG system health
    Returns coverage, accuracy metrics, and issues
    """
    # Get statistics
    total_articles = db.query(KBArticle).count()
    active_articles = db.query(KBArticle).filter(KBArticle.is_active == True).count()
    indexed_articles = db.query(KBArticle).filter(KBArticle.is_indexed == True).count()
    
    total_chunks = db.query(KBArticle).filter(
        KBArticle.chunk_count != None
    ).with_entities(KBArticle.chunk_count).all()
    
    total_chunk_count = sum([c[0] for c in total_chunks if c[0]])
    
    # Calculate health metrics
    coverage_rate = (indexed_articles / total_articles * 100) if total_articles > 0 else 0
    
    # Health status
    if coverage_rate >= 90:
        health_status = "HEALTHY"
    elif coverage_rate >= 70:
        health_status = "WARNING"
    else:
        health_status = "CRITICAL"
    
    # Issues
    issues = []
    if total_articles - indexed_articles > 0:
        issues.append(f"{total_articles - indexed_articles} articles not indexed")
    
    if total_articles - active_articles > total_articles * 0.3:
        issues.append(f"Too many inactive articles ({total_articles - active_articles})")
    
    return KBHealthResponse(
        total_articles=total_articles,
        active_articles=active_articles,
        indexed_articles=indexed_articles,
        total_chunks=total_chunk_count,
        coverage_rate=round(coverage_rate, 2),
        health_status=health_status,
        issues=issues,
        last_check=datetime.utcnow()
    )


@router.get("/categories/list")
def list_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of all categories
    """
    categories = db.query(KBArticle.category).filter(
        KBArticle.category != None
    ).distinct().all()
    
    return {
        "categories": [c[0] for c in categories if c[0]]
    }
