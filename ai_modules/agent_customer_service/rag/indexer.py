"""
ChromaDB Indexer - Build and index vectors
"""
from typing import Dict, Any, List, Optional
from pathlib import Path
import json
import chromadb
from chromadb.utils import embedding_functions

from ai_modules.core.config import ai_config


class ChromaIndexer:
    """
    ChromaDB Indexer for building and managing vector index
    
    Chức năng:
    - Index policy/FAQ documents
    - Index product information
    - Manage collections
    """
    
    def __init__(
        self, 
        chroma_path: Optional[str] = None,
        collection_name: str = "knowledge_base"
    ):
        self.chroma_path = chroma_path or ai_config.chroma_persist_directory
        self.collection_name = collection_name
        
        # Initialize embedding function
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=ai_config.embedding_model
        )
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=self.chroma_path)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn
        )
    
    def clear_collection(self) -> int:
        """
        Clear all documents in collection
        
        Returns:
            Number of documents deleted
        """
        existing = self.collection.get(include=[])["ids"]
        if existing:
            self.collection.delete(ids=existing)
            return len(existing)
        return 0
    
    def index_policies(self, policy_file: str) -> int:
        """
        Index policy documents from JSON file
        
        Args:
            policy_file: Path to policy JSON file
            
        Returns:
            Number of documents indexed
        """
        with open(policy_file, "r", encoding="utf-8") as f:
            policies = json.load(f)
        
        docs, metas, ids = [], [], []
        
        for p in policies:
            if not p.get("id") or not p.get("content"):
                continue
            
            docs.append(p["content"])
            metas.append(self._clean_metadata({
                "type": "policy",
                "domain": p.get("metadata", {}).get("domain"),
                "topic": p.get("metadata", {}).get("topic"),
                "source": p.get("metadata", {}).get("source", "CRM")
            }))
            ids.append(str(p["id"]))
        
        if docs:
            self.collection.add(
                documents=docs,
                metadatas=metas,
                ids=ids
            )
        
        return len(docs)
    
    def index_products(
        self, 
        product_file: str,
        product_to_text_fn: Optional[callable] = None
    ) -> int:
        """
        Index product documents from JSON file
        
        Args:
            product_file: Path to product JSON file
            product_to_text_fn: Optional function to convert product to text
            
        Returns:
            Number of documents indexed
        """
        with open(product_file, "r", encoding="utf-8") as f:
            products = json.load(f)
        
        docs, metas, ids = [], [], []
        
        for p in products:
            product_id = p.get("id") or p.get("_id")
            if not product_id:
                continue
            
            # Convert product to text
            if product_to_text_fn:
                text = product_to_text_fn(p)
            else:
                text = self._default_product_to_text(p)
            
            if not text:
                continue
            
            docs.append(text)
            metas.append(self._clean_metadata({
                "type": "product",
                "product_id": str(product_id),
                "title": p.get("title") or p.get("name"),
                "category": p.get("_meta", {}).get("category") or p.get("category"),
                "brand": p.get("_meta", {}).get("brand") or p.get("brand"),
                "price": p.get("_meta", {}).get("price") or p.get("price")
            }))
            ids.append(f"product_{product_id}")
        
        if docs:
            self.collection.add(
                documents=docs,
                metadatas=metas,
                ids=ids
            )
        
        return len(docs)
    
    def index_kb_articles(self, articles: List[Dict[str, Any]]) -> int:
        """
        Index Knowledge Base articles from database
        
        Args:
            articles: List of KB article dictionaries
            
        Returns:
            Number of documents indexed
        """
        docs, metas, ids = [], [], []
        
        for article in articles:
            article_id = article.get("id")
            content = article.get("content") or article.get("body")
            
            if not article_id or not content:
                continue
            
            docs.append(content)
            metas.append(self._clean_metadata({
                "type": "kb_article",
                "article_id": str(article_id),
                "title": article.get("title"),
                "category": article.get("category"),
                "tags": str(article.get("tags", []))
            }))
            ids.append(f"kb_{article_id}")
        
        if docs:
            self.collection.add(
                documents=docs,
                metadatas=metas,
                ids=ids
            )
        
        return len(docs)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        count = self.collection.count()
        return {
            "collection_name": self.collection_name,
            "total_documents": count,
            "chroma_path": self.chroma_path
        }
    
    def _clean_metadata(self, meta: Dict) -> Dict:
        """Clean metadata to ensure ChromaDB compatibility"""
        cleaned = {}
        for k, v in meta.items():
            if v is None:
                continue
            if isinstance(v, (str, int, float, bool)):
                cleaned[k] = v
            else:
                cleaned[k] = str(v)
        return cleaned
    
    def _default_product_to_text(self, product: Dict) -> str:
        """Default product to text conversion"""
        parts = []
        
        if product.get("title") or product.get("name"):
            parts.append(f"Sản phẩm: {product.get('title') or product.get('name')}")
        
        meta = product.get("_meta", {})
        if meta.get("brand") or product.get("brand"):
            parts.append(f"Thương hiệu: {meta.get('brand') or product.get('brand')}")
        
        if meta.get("category") or product.get("category"):
            parts.append(f"Danh mục: {meta.get('category') or product.get('category')}")
        
        if meta.get("price") or product.get("price"):
            parts.append(f"Giá: {meta.get('price') or product.get('price')} VNĐ")
        
        if product.get("description"):
            parts.append(f"Mô tả: {product.get('description')}")
        
        return "\n".join(parts)
