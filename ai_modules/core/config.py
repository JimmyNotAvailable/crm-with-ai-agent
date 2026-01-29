"""
AI Configuration - Centralized config for all AI modules
"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class AIConfig:
    """
    Centralized configuration for AI modules
    """
    # Demo Mode
    demo_mode: bool = False
    
    # LLM Settings
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-3.5-turbo"
    gemini_api_key: Optional[str] = None
    gemini_model: str = "gemini-flash-latest"
    
    # Embedding Settings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    openai_embedding_model: str = "text-embedding-3-small"
    
    # ChromaDB Settings
    chroma_persist_directory: str = "./chroma_db"
    chroma_collection_name: str = "knowledge_base"
    
    # RAG Settings
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k_retrieval: int = 5
    similarity_threshold: float = 0.7
    
    # Agent Settings
    agent_max_iterations: int = 5
    agent_timeout_seconds: int = 30
    
    @classmethod
    def from_env(cls) -> "AIConfig":
        """Load config from environment variables"""
        return cls(
            demo_mode=os.getenv("DEMO_MODE", "false").lower() == "true",
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            gemini_api_key=os.getenv("GEMINI_API_KEY"),
            gemini_model=os.getenv("GEMINI_MODEL", "gemini-flash-latest"),
            embedding_model=os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
            openai_embedding_model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
            chroma_persist_directory=os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db"),
            chroma_collection_name=os.getenv("CHROMA_COLLECTION_NAME", "knowledge_base"),
            chunk_size=int(os.getenv("CHUNK_SIZE", "1000")),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "200")),
            top_k_retrieval=int(os.getenv("TOP_K_RETRIEVAL", "5")),
            similarity_threshold=float(os.getenv("SIMILARITY_THRESHOLD", "0.7")),
            agent_max_iterations=int(os.getenv("AGENT_MAX_ITERATIONS", "5")),
            agent_timeout_seconds=int(os.getenv("AGENT_TIMEOUT_SECONDS", "30")),
        )


# Global config instance
ai_config = AIConfig.from_env()
