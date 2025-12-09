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

from backend.api.v1.endpoints import auth, products, orders, rag, tickets, cart, kb_articles, summarization, analytics, ticket_deduplication, audit_logs, personalization, knowledge_sync

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


# Include API routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(products.router, prefix="/products", tags=["Products"])
app.include_router(orders.router, prefix="/orders", tags=["Orders"])
app.include_router(tickets.router, prefix="/tickets", tags=["Tickets"])
app.include_router(ticket_deduplication.router, prefix="/tickets", tags=["Ticket Deduplication"])
app.include_router(cart.router, prefix="/cart", tags=["Cart"])
app.include_router(rag.router, prefix="/rag", tags=["RAG"])
app.include_router(kb_articles.router, prefix="/kb", tags=["Knowledge Base"])
app.include_router(summarization.router, prefix="/ai/summarize", tags=["AI Summarization"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics & KPI"])
app.include_router(audit_logs.router, prefix="/audit", tags=["Audit Logs"])
app.include_router(personalization.router, prefix="/ai/personalization", tags=["AI Personalization"])
app.include_router(knowledge_sync.router, prefix="/kb/sync", tags=["Knowledge Sync"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disabled reload to avoid Python 3.13 multiprocessing issues
        log_level="info"
    )
