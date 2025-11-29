"""
Main FastAPI Application Entry Point
"""
import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.api.v1.endpoints import auth, products, orders, rag

# Import database session
from backend.database.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle events for FastAPI application
    """
    # Startup
    print("Starting CRM-AI-Agent Backend...")
    # Note: Database initialization should be done manually
    # Run: python -m backend.database.init_db after setting up MySQL
    print("Backend started successfully!")
    # TODO: Initialize Vector Store
    # initialize_vector_store()
    
    yield
    
    # Shutdown
    print("Shutting down CRM-AI-Agent Backend...")


# Initialize FastAPI app
app = FastAPI(
    title="CRM-AI-Agent API",
    description="AI-Powered Omni-channel CRM System with RAG & Agent Capabilities",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React default
        "http://localhost:5173",  # Vite default
        "http://localhost:8080",  # Vue default
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/", tags=["Health"])
async def root():
    """
    Root endpoint - Health check
    """
    return {
        "status": "healthy",
        "message": "CRM-AI-Agent API is running",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Detailed health check endpoint
    """
    # TODO: Add database connection check
    # TODO: Add vector store connection check
    return {
        "status": "healthy",
        "services": {
            "api": "running",
            "database": "pending",  # TODO: Implement check
            "vector_store": "pending",  # TODO: Implement check
        }
    }


# RAG endpoints
app.include_router(rag.router, prefix="/api/v1/rag", tags=["rag"])
# TODO: Implement remaining routers
# app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])
# app.include_router(kb.router, prefix="/api/v1/kb", tags=["Knowledge Base"])
# app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
