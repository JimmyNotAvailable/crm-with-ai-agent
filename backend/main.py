"""
Main FastAPI Application Entry Point
"""
import sys
import os
from pathlib import Path

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.api.v1.endpoints import auth, products, orders, rag, tickets, cart, kb_articles, summarization, analytics, ticket_deduplication, audit_logs, personalization, knowledge_sync

# Import database session
from backend.database.session import init_db

# Import JSON logging
from backend.core.logging_config import setup_logging, get_logger

# Setup logging based on environment
LOG_FORMAT = os.getenv("LOG_FORMAT", "json")  # "json" or "pretty"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", None)

# Initialize logging
app_logger = setup_logging(
    log_level=LOG_LEVEL,
    json_format=(LOG_FORMAT.lower() == "json"),
    log_file=LOG_FILE,
    app_name="crm-backend"
)

logger = get_logger("crm-backend.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle events for FastAPI application
    """
    # Startup
    logger.info("Starting CRM-AI-Agent Backend...", extra={
        "event": "startup",
        "log_format": LOG_FORMAT,
        "log_level": LOG_LEVEL
    })
    logger.info("Backend started successfully!", extra={"event": "startup_complete"})
    
    yield
    
    # Shutdown
    logger.info("Shutting down CRM-AI-Agent Backend...", extra={"event": "shutdown"})


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
    Detailed health check endpoint for all 7 microservices databases
    """
    from backend.database.session import check_database_health
    
    # Check all databases
    db_health = check_database_health()
    
    # Determine overall status
    all_healthy = all(db_health.values())
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "services": {
            "api": "running",
            "databases": {
                "identity": "healthy" if db_health.get("identity") else "unhealthy",
                "product": "healthy" if db_health.get("product") else "unhealthy",
                "order": "healthy" if db_health.get("order") else "unhealthy",
                "support": "healthy" if db_health.get("support") else "unhealthy",
                "knowledge": "healthy" if db_health.get("knowledge") else "unhealthy",
                "analytics": "healthy" if db_health.get("analytics") else "unhealthy",
                "marketing": "healthy" if db_health.get("marketing") else "unhealthy",
            },
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
