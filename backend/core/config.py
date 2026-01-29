"""
Configuration settings for the application
Loads from environment variables
"""
from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    Supports 7 microservices databases architecture
    """
    # Application
    APP_NAME: str = "CRM-AI-Agent"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    DEMO_MODE: bool = True
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # =========================================================================
    # MICROSERVICES DATABASES (7 MySQL Containers)
    # =========================================================================
    
    # 1. Identity Database (Users, Auth) - Port 3310
    IDENTITY_DB_HOST: str = "localhost"
    IDENTITY_DB_PORT: int = 3310
    IDENTITY_DB_USER: str = "identity_user"
    IDENTITY_DB_PASSWORD: str = "identity_pass"
    IDENTITY_DB_NAME: str = "crm_identity_db"
    
    # 2. Product Database (Products, Categories) - Port 3311
    PRODUCT_DB_HOST: str = "localhost"
    PRODUCT_DB_PORT: int = 3311
    PRODUCT_DB_USER: str = "product_user"
    PRODUCT_DB_PASSWORD: str = "product_pass"
    PRODUCT_DB_NAME: str = "crm_product_db"
    
    # 3. Order Database (Orders, OrderItems, Carts) - Port 3312
    ORDER_DB_HOST: str = "localhost"
    ORDER_DB_PORT: int = 3312
    ORDER_DB_USER: str = "order_user"
    ORDER_DB_PASSWORD: str = "order_pass"
    ORDER_DB_NAME: str = "crm_order_db"
    
    # 4. Support Database (Tickets, TicketMessages) - Port 3313
    SUPPORT_DB_HOST: str = "localhost"
    SUPPORT_DB_PORT: int = 3313
    SUPPORT_DB_USER: str = "support_user"
    SUPPORT_DB_PASSWORD: str = "support_pass"
    SUPPORT_DB_NAME: str = "crm_support_db"
    
    # 5. Knowledge Database (KB Articles, Conversations) - Port 3314
    KNOWLEDGE_DB_HOST: str = "localhost"
    KNOWLEDGE_DB_PORT: int = 3314
    KNOWLEDGE_DB_USER: str = "knowledge_user"
    KNOWLEDGE_DB_PASSWORD: str = "knowledge_pass"
    KNOWLEDGE_DB_NAME: str = "crm_knowledge_db"
    
    # 6. Analytics Database (Logs, Events) - Port 3315
    ANALYTICS_DB_HOST: str = "localhost"
    ANALYTICS_DB_PORT: int = 3315
    ANALYTICS_DB_USER: str = "analytics_user"
    ANALYTICS_DB_PASSWORD: str = "analytics_pass"
    ANALYTICS_DB_NAME: str = "crm_analytics_db"
    
    # 7. Marketing Database (Campaigns, Promotions) - Port 3316
    MARKETING_DB_HOST: str = "localhost"
    MARKETING_DB_PORT: int = 3316
    MARKETING_DB_USER: str = "marketing_user"
    MARKETING_DB_PASSWORD: str = "marketing_pass"
    MARKETING_DB_NAME: str = "crm_marketing_db"
    
    # Primary/Default Database (backward compatibility - uses Identity)
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3310
    MYSQL_USER: str = "identity_user"
    MYSQL_PASSWORD: str = "identity_pass"
    MYSQL_DATABASE: str = "crm_identity_db"
    
    # =========================================================================
    # DATABASE URL PROPERTIES
    # =========================================================================
    
    @property
    def DATABASE_URL(self) -> str:
        """Primary database URL (Identity DB for backward compatibility)"""
        return self.IDENTITY_DATABASE_URL
    
    @property
    def IDENTITY_DATABASE_URL(self) -> str:
        """Identity DB URL - Users, Authentication"""
        return f"mysql+pymysql://{self.IDENTITY_DB_USER}:{self.IDENTITY_DB_PASSWORD}@{self.IDENTITY_DB_HOST}:{self.IDENTITY_DB_PORT}/{self.IDENTITY_DB_NAME}"
    
    @property
    def PRODUCT_DATABASE_URL(self) -> str:
        """Product DB URL - Products, Categories"""
        return f"mysql+pymysql://{self.PRODUCT_DB_USER}:{self.PRODUCT_DB_PASSWORD}@{self.PRODUCT_DB_HOST}:{self.PRODUCT_DB_PORT}/{self.PRODUCT_DB_NAME}"
    
    @property
    def ORDER_DATABASE_URL(self) -> str:
        """Order DB URL - Orders, OrderItems, Carts"""
        return f"mysql+pymysql://{self.ORDER_DB_USER}:{self.ORDER_DB_PASSWORD}@{self.ORDER_DB_HOST}:{self.ORDER_DB_PORT}/{self.ORDER_DB_NAME}"
    
    @property
    def SUPPORT_DATABASE_URL(self) -> str:
        """Support DB URL - Tickets, TicketMessages"""
        return f"mysql+pymysql://{self.SUPPORT_DB_USER}:{self.SUPPORT_DB_PASSWORD}@{self.SUPPORT_DB_HOST}:{self.SUPPORT_DB_PORT}/{self.SUPPORT_DB_NAME}"
    
    @property
    def KNOWLEDGE_DATABASE_URL(self) -> str:
        """Knowledge DB URL - KB Articles, Conversations"""
        return f"mysql+pymysql://{self.KNOWLEDGE_DB_USER}:{self.KNOWLEDGE_DB_PASSWORD}@{self.KNOWLEDGE_DB_HOST}:{self.KNOWLEDGE_DB_PORT}/{self.KNOWLEDGE_DB_NAME}"
    
    @property
    def ANALYTICS_DATABASE_URL(self) -> str:
        """Analytics DB URL - Logs, Events"""
        return f"mysql+pymysql://{self.ANALYTICS_DB_USER}:{self.ANALYTICS_DB_PASSWORD}@{self.ANALYTICS_DB_HOST}:{self.ANALYTICS_DB_PORT}/{self.ANALYTICS_DB_NAME}"
    
    @property
    def MARKETING_DATABASE_URL(self) -> str:
        """Marketing DB URL - Campaigns, Promotions"""
        return f"mysql+pymysql://{self.MARKETING_DB_USER}:{self.MARKETING_DB_PASSWORD}@{self.MARKETING_DB_HOST}:{self.MARKETING_DB_PORT}/{self.MARKETING_DB_NAME}"
    
    # Vector Database
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
    CHROMA_COLLECTION_NAME: str = "kb_articles"
    
    # Demo Mode
    DEMO_MODE: bool = False  # Set to True to use mock LLM without OpenAI
    
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
        extra = "ignore"  # Ignore extra fields from .env


# Create global settings instance
settings = Settings()
