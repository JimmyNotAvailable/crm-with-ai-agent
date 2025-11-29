"""
Configuration settings for the application
Loads from environment variables
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    # Application
    APP_NAME: str = "CRM-AI-Agent"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database (MySQL)
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "crm_user"
    MYSQL_PASSWORD: str = "password"
    MYSQL_DATABASE: str = "crm_ai_db"
    
    @property
    def DATABASE_URL(self) -> str:
        """Generate database URL from components"""
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
    
    # Vector Database
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
    CHROMA_COLLECTION_NAME: str = "kb_articles"
    
    # AI/LLM Settings
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    # RAG Settings
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RETRIEVAL: int = 5
    SIMILARITY_THRESHOLD: float = 0.7
    
    # Authentication
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # File Upload
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10485760  # 10MB
    
    @property
    def ALLOWED_EXTENSIONS(self) -> List[str]:
        """Parse allowed extensions from env or use default"""
        return ["pdf", "docx", "txt", "md"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"
    
    # CORS
    @property
    def CORS_ORIGINS(self) -> List[str]:
        """Parse CORS origins from env or use default"""
        return [
            "http://localhost:3000",
            "http://localhost:5173"
        ]
    CORS_ALLOW_CREDENTIALS: bool = True
    
    # Agent Settings
    AGENT_MAX_ITERATIONS: int = 5
    AGENT_TIMEOUT_SECONDS: int = 30
    
    # Sentiment Analysis
    SENTIMENT_MODEL: str = "textblob"  # Options: textblob, transformers
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()
