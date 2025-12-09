"""
Knowledge Base Synchronization Service
Automatically sync knowledge base from external sources
"""
from sqlalchemy.orm import Session
from backend.models.kb_article import KBArticle
from backend.services.rag_pipeline import RAGPipeline
from typing import List, Dict, Optional
from datetime import datetime
import os
import hashlib
import requests
from pathlib import Path


class KnowledgeSyncService:
    """Service for syncing knowledge base from external sources"""
    
    def __init__(self, db: Session):
        self.db = db
        self.rag_pipeline = RAGPipeline()
        self.uploads_dir = Path("uploads")
        self.uploads_dir.mkdir(exist_ok=True)
    
    def sync_from_directory(
        self,
        directory_path: str,
        category: str = "AUTO_SYNC",
        auto_activate: bool = True
    ) -> Dict:
        """
        Sync knowledge base articles from a directory
        
        Args:
            directory_path: Path to directory containing markdown/text files
            category: Category to assign to synced articles
            auto_activate: Whether to auto-activate new articles
            
        Returns:
            Sync statistics (added, updated, unchanged)
        """
        stats = {
            "added": 0,
            "updated": 0,
            "unchanged": 0,
            "errors": []
        }
        
        directory = Path(directory_path)
        if not directory.exists() or not directory.is_dir():
            stats["errors"].append(f"Directory not found: {directory_path}")
            return stats
        
        # Find all markdown and text files
        file_patterns = ["*.md", "*.txt", "*.markdown"]
        files = []
        for pattern in file_patterns:
            files.extend(directory.glob(pattern))
        
        for file_path in files:
            try:
                # Read file content
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Calculate content hash for change detection
                content_hash = self._calculate_hash(content)
                
                # Check if article already exists
                existing = self.db.query(KBArticle).filter(
                    KBArticle.file_path == str(file_path)
                ).first()
                
                if existing:
                    # Check if content changed
                    existing_content = getattr(existing, 'content', None) or ""
                    existing_hash = self._calculate_hash(str(existing_content))
                    
                    if content_hash != existing_hash:
                        # Update existing article
                        setattr(existing, 'content', content)
                        setattr(existing, 'updated_at', datetime.utcnow())
                        
                        # Re-index in vector store (skip if method doesn't exist)
                        if hasattr(self.rag_pipeline, 'index_knowledge_article'):
                            self.rag_pipeline.index_knowledge_article(
                                article_id=getattr(existing, 'id', 0),
                                title=getattr(existing, 'title', ''),
                                content=content,
                                category=getattr(existing, 'category', '')
                            )
                        
                        stats["updated"] += 1
                    else:
                        stats["unchanged"] += 1
                else:
                    # Create new article
                    title = file_path.stem.replace("_", " ").title()
                    
                    new_article = KBArticle(
                        title=title,
                        content=content,
                        category=category,
                        file_path=str(file_path),
                        is_active=auto_activate
                    )
                    
                    self.db.add(new_article)
                    self.db.flush()
                    
                    # Index in vector store (skip if method doesn't exist)
                    if hasattr(self.rag_pipeline, 'index_knowledge_article'):
                        self.rag_pipeline.index_knowledge_article(
                            article_id=getattr(new_article, 'id', 0),
                            title=title,
                            content=content,
                            category=category
                        )
                    
                    stats["added"] += 1
            
            except Exception as e:
                stats["errors"].append(f"Error processing {file_path.name}: {str(e)}")
        
        self.db.commit()
        return stats
    
    def sync_from_url(
        self,
        url: str,
        title: str,
        category: str = "WEB_SYNC",
        auto_activate: bool = True
    ) -> Dict:
        """
        Sync knowledge article from URL
        
        Args:
            url: URL to fetch content from
            title: Title for the article
            category: Category to assign
            auto_activate: Whether to auto-activate
            
        Returns:
            Sync result
        """
        try:
            # Fetch content from URL
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            content = response.text
            
            # Calculate hash
            content_hash = self._calculate_hash(content)
            
            # Check if exists by URL
            existing = self.db.query(KBArticle).filter(
                KBArticle.source_url == url
            ).first()
            
            if existing:
                # Check if changed
                existing_content = getattr(existing, 'content', None) or ""
                existing_hash = self._calculate_hash(str(existing_content))
                
                if content_hash != existing_hash:
                    # Update
                    setattr(existing, 'content', content)
                    setattr(existing, 'updated_at', datetime.utcnow())
                    
                    # Re-index (skip if method doesn't exist)
                    if hasattr(self.rag_pipeline, 'index_knowledge_article'):
                        self.rag_pipeline.index_knowledge_article(
                            article_id=getattr(existing, 'id', 0),
                            title=getattr(existing, 'title', ''),
                            content=content,
                            category=getattr(existing, 'category', '')
                        )
                    
                    self.db.commit()
                    
                    return {
                        "status": "updated",
                        "article_id": existing.id,
                        "message": f"Updated article '{title}' from {url}"
                    }
                else:
                    return {
                        "status": "unchanged",
                        "article_id": existing.id,
                        "message": f"No changes detected for '{title}'"
                    }
            else:
                # Create new
                new_article = KBArticle(
                    title=title,
                    content=content,
                    category=category,
                    source_url=url,
                    is_active=auto_activate
                )
                
                self.db.add(new_article)
                self.db.flush()
                
                # Index (skip if method doesn't exist)
                if hasattr(self.rag_pipeline, 'index_knowledge_article'):
                    self.rag_pipeline.index_knowledge_article(
                        article_id=getattr(new_article, 'id', 0),
                        title=title,
                        content=content,
                        category=category
                    )
                
                self.db.commit()
                
                return {
                    "status": "created",
                    "article_id": new_article.id,
                    "message": f"Created article '{title}' from {url}"
                }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to sync from {url}: {str(e)}"
            }
    
    def sync_all_sources(self) -> Dict:
        """
        Sync from all configured sources
        
        Returns:
            Overall sync statistics
        """
        overall_stats = {
            "total_added": 0,
            "total_updated": 0,
            "total_unchanged": 0,
            "sources_synced": 0,
            "errors": []
        }
        
        # Sync from uploads directory
        if self.uploads_dir.exists():
            stats = self.sync_from_directory(
                directory_path=str(self.uploads_dir),
                category="DOCS",
                auto_activate=True
            )
            
            overall_stats["total_added"] += stats["added"]
            overall_stats["total_updated"] += stats["updated"]
            overall_stats["total_unchanged"] += stats["unchanged"]
            overall_stats["errors"].extend(stats["errors"])
            overall_stats["sources_synced"] += 1
        
        # TODO: Add more sync sources
        # - External API endpoints
        # - Git repositories
        # - Cloud storage (S3, Azure Blob)
        # - Documentation websites
        
        return overall_stats
    
    def _calculate_hash(self, content: str) -> str:
        """Calculate SHA256 hash of content for change detection"""
        return hashlib.sha256(content.encode()).hexdigest()
    
    def schedule_sync(self, interval_hours: int = 24):
        """
        Schedule periodic knowledge base sync
        
        NOTE: In production, use proper scheduler like Celery, APScheduler, or cron
        This is a placeholder for the scheduling logic
        """
        # Placeholder for scheduling logic
        # In production, integrate with:
        # - Celery for distributed task queue
        # - APScheduler for in-process scheduling
        # - System cron for simple periodic execution
        
        print(f"Knowledge sync scheduled every {interval_hours} hours")
        print("Use Celery or APScheduler for production deployment")
