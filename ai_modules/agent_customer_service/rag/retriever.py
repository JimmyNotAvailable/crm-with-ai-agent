"""
Retrievers - Retrieve relevant documents from ChromaDB
"""
from typing import Dict, Any, List, Optional
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions

from ai_modules.core.config import ai_config

# Default paths
DEFAULT_CHROMA_PATH = str(Path(__file__).parent / "chroma")
DEFAULT_COLLECTION_NAME = "knowledge_base"

# Distance thresholds (tuned for sentence-transformers)
MAX_DISTANCE_POLICY = 0.45
MAX_DISTANCE_PRODUCT = 1.4  # product docs are longer → higher distance is normal


class BaseRetriever:
    """Base class for document retrievers"""
    
    def __init__(self, chroma_path: Optional[str] = None, collection_name: str = DEFAULT_COLLECTION_NAME):
        self.chroma_path = chroma_path or DEFAULT_CHROMA_PATH
        self.collection_name = collection_name
        
        # Initialize embedding function
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=ai_config.embedding_model
        )
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=self.chroma_path)
        
        try:
            self.collection = self.client.get_collection(
                name=collection_name,
                embedding_function=self.embedding_fn
            )
        except Exception:
            # Collection doesn't exist yet
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                embedding_function=self.embedding_fn
            )
    
    def retrieve(self, query: str, top_k: int = 5, **kwargs) -> List[Dict[str, Any]]:
        """Retrieve relevant documents"""
        raise NotImplementedError
    
    def _post_filter(self, docs: List[Dict], max_distance: float) -> List[Dict]:
        """Filter documents by max distance threshold"""
        return [d for d in docs if d["distance"] <= max_distance]


class PolicyRetriever(BaseRetriever):
    """
    Retriever cho Policy/FAQ documents
    Filter by type="policy"
    """
    
    def __init__(self, chroma_path: Optional[str] = None, collection_name: str = DEFAULT_COLLECTION_NAME):
        super().__init__(chroma_path, collection_name)
    
    def retrieve(
        self, 
        query: str, 
        top_k: int = 4,
        domain: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve policy documents
        
        Args:
            query: Search query
            top_k: Number of results
            domain: Optional filter by policy domain
            
        Returns:
            List of policy documents with content, metadata, distance
        """
        try:
            # Build where filter
            where_filter = {"type": "policy"}
            if domain:
                where_filter["domain"] = domain
            
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k,
                where=where_filter,
                include=["documents", "metadatas", "distances"]
            )
            
            docs = []
            if results["documents"] and results["documents"][0]:
                for i in range(len(results["documents"][0])):
                    docs.append({
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "distance": results["distances"][0][i] if results["distances"] else 0.0
                    })
            
            # Apply distance threshold filter
            return self._post_filter(docs, MAX_DISTANCE_POLICY)
            
        except Exception as e:
            print(f"[PolicyRetriever] Error: {e}")
            return []


class ProductRetriever(BaseRetriever):
    """
    Retriever cho Product documents
    Filter by type="product" and optional category
    """
    
    def __init__(self, chroma_path: Optional[str] = None, collection_name: str = DEFAULT_COLLECTION_NAME):
        super().__init__(chroma_path, collection_name)
    
    def retrieve(
        self, 
        query: str, 
        top_k: int = 6,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve product documents
        
        Args:
            query: Search query
            top_k: Number of results
            category: Optional filter by product category
            
        Returns:
            List of product documents with content, metadata, distance
        """
        try:
            # Build where filter
            where_filter = {"type": "product"}
            
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k,
                where=where_filter,
                include=["documents", "metadatas", "distances"]
            )
            
            docs = []
            if results["documents"] and results["documents"][0]:
                for i in range(len(results["documents"][0])):
                    doc = {
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "distance": results["distances"][0][i] if results["distances"] else 0.0
                    }
                    
                    # Soft boost category match (don't hard filter)
                    if category and doc["metadata"].get("category") == category:
                        doc["distance"] *= 0.8
                    
                    docs.append(doc)
            
            # Apply distance threshold filter
            return self._post_filter(docs, MAX_DISTANCE_PRODUCT)
            
        except Exception as e:
            print(f"[ProductRetriever] Error: {e}")
            return []
