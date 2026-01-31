"""
Knowledge Microservice Sync for RAG
Kết nối RAG với mysql-knowledge microservice
"""
from typing import List, Dict, Any, Optional
from pathlib import Path
import json

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from ai_modules.core.config import ai_config
from ai_modules.agent_customer_service.rag.indexer import ChromaIndexer


def get_knowledge_db_url() -> str:
    """Get knowledge database URL from environment"""
    import os
    host = os.getenv("KNOWLEDGE_DB_HOST", "localhost")
    port = os.getenv("KNOWLEDGE_DB_PORT", "3314")
    user = os.getenv("KNOWLEDGE_DB_USER", "knowledge_user")
    password = os.getenv("KNOWLEDGE_DB_PASSWORD", "knowledge_pass")
    database = os.getenv("KNOWLEDGE_DB_NAME", "crm_knowledge_db")
    
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"


class KnowledgeMicroserviceSync:
    """
    Sync Knowledge Base từ MySQL microservice vào ChromaDB
    
    Flow:
    1. Lấy KB Articles từ mysql-knowledge
    2. Convert sang text chunks
    3. Index vào ChromaDB vector store
    """
    
    def __init__(self, chroma_path: Optional[str] = None):
        self.chroma_path = chroma_path or str(
            Path(__file__).parent.parent / "agent_customer_service" / "rag" / "chroma"
        )
        
        # Initialize ChromaDB indexer
        self.indexer = ChromaIndexer(
            chroma_path=self.chroma_path,
            collection_name="knowledge_base"
        )
        
        # Knowledge DB connection
        self._engine = None
        self._session_factory = None
    
    def _get_session(self):
        """Get database session for knowledge microservice"""
        if self._engine is None or self._session_factory is None:
            try:
                self._engine = create_engine(
                    get_knowledge_db_url(),
                    pool_pre_ping=True,
                    pool_size=2,
                    max_overflow=5
                )
                self._session_factory = sessionmaker(bind=self._engine)
            except Exception as e:
                raise ConnectionError(f"Failed to connect to knowledge database: {e}")
        
        return self._session_factory()
    
    def sync_kb_articles(self, force_rebuild: bool = False) -> Dict[str, Any]:
        """
        Sync KB Articles từ MySQL vào ChromaDB
        
        Args:
            force_rebuild: Xóa tất cả và rebuild index
            
        Returns:
            Stats về sync operation
        """
        stats = {
            "total": 0,
            "indexed": 0,
            "skipped": 0,
            "errors": []
        }
        
        try:
            session = self._get_session()
            
            # Query active KB articles
            result = session.execute(text("""
                SELECT 
                    id,
                    title,
                    content,
                    category,
                    tags,
                    status,
                    view_count,
                    helpful_count,
                    created_at,
                    updated_at
                FROM kb_articles 
                WHERE status = 'published'
                ORDER BY helpful_count DESC, view_count DESC
            """))
            
            articles = []
            for row in result:
                articles.append({
                    "id": f"kb_{row[0]}",
                    "title": row[1],
                    "content": row[2],
                    "category": row[3],
                    "tags": row[4],
                    "view_count": row[6],
                    "helpful_count": row[7]
                })
            
            stats["total"] = len(articles)
            
            if force_rebuild:
                self.indexer.clear_collection()
            
            # Index articles
            indexed = self.indexer.index_kb_articles(articles)
            stats["indexed"] = indexed
            stats["skipped"] = stats["total"] - indexed
            
            session.close()
            
        except Exception as e:
            stats["errors"].append(str(e))
        
        return stats
    
    def sync_policies(self, force_rebuild: bool = False) -> Dict[str, Any]:
        """
        Sync Policies/FAQs từ MySQL vào ChromaDB
        
        Returns:
            Stats về sync operation
        """
        stats = {
            "total": 0,
            "indexed": 0,
            "errors": []
        }
        
        try:
            session = self._get_session()
            
            # Query policies/FAQs
            result = session.execute(text("""
                SELECT 
                    id,
                    question,
                    answer,
                    category,
                    tags
                FROM faqs 
                WHERE is_active = 1
            """))
            
            policies = []
            for row in result:
                policies.append({
                    "id": f"faq_{row[0]}",
                    "content": f"Câu hỏi: {row[1]}\nTrả lời: {row[2]}",
                    "metadata": {
                        "type": "policy",
                        "domain": row[3],
                        "topic": row[3]
                    }
                })
            
            stats["total"] = len(policies)
            
            # Index as policy documents
            docs, metas, ids = [], [], []
            for p in policies:
                docs.append(p["content"])
                metas.append({
                    "type": "policy",
                    "domain": p["metadata"]["domain"],
                    "topic": p["metadata"]["topic"],
                    "source": "knowledge_db"
                })
                ids.append(str(p["id"]))
            
            if docs:
                if force_rebuild:
                    # Delete existing policies
                    try:
                        existing = self.indexer.collection.get(
                            where={"type": "policy"},
                            include=[]
                        )["ids"]
                        if existing:
                            self.indexer.collection.delete(ids=existing)
                    except Exception:
                        pass
                
                self.indexer.collection.add(
                    documents=docs,
                    metadatas=metas,
                    ids=ids
                )
                stats["indexed"] = len(docs)
            
            session.close()
            
        except Exception as e:
            stats["errors"].append(str(e))
        
        return stats
    
    def full_sync(self, force_rebuild: bool = False) -> Dict[str, Any]:
        """
        Full sync: KB Articles + Policies
        
        Returns:
            Combined stats
        """
        kb_stats = self.sync_kb_articles(force_rebuild)
        policy_stats = self.sync_policies(force_rebuild)
        
        return {
            "kb_articles": kb_stats,
            "policies": policy_stats,
            "total_indexed": kb_stats.get("indexed", 0) + policy_stats.get("indexed", 0)
        }
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync status"""
        try:
            collection_info = self.indexer.collection.get(include=[])
            return {
                "collection_name": self.indexer.collection_name,
                "total_documents": len(collection_info["ids"]),
                "chroma_path": self.chroma_path,
                "status": "connected"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }


# Singleton instance
_sync_service: Optional[KnowledgeMicroserviceSync] = None


def get_knowledge_sync_service() -> KnowledgeMicroserviceSync:
    """Get singleton sync service"""
    global _sync_service
    if _sync_service is None:
        _sync_service = KnowledgeMicroserviceSync()
    return _sync_service
