"""
Database session management for 7 Microservices Architecture
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.core.config import settings

# =========================================================================
# DATABASE ENGINES (7 Microservices)
# =========================================================================

# 1. Identity Database - Users, Authentication
identity_engine = create_engine(
    settings.IDENTITY_DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# 2. Product Database - Products, Categories
product_engine = create_engine(
    settings.PRODUCT_DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# 3. Order Database - Orders, OrderItems, Carts
order_engine = create_engine(
    settings.ORDER_DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# 4. Support Database - Tickets, TicketMessages
support_engine = create_engine(
    settings.SUPPORT_DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# 5. Knowledge Database - KB Articles, Conversations
knowledge_engine = create_engine(
    settings.KNOWLEDGE_DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# 6. Analytics Database - Logs, Events
analytics_engine = create_engine(
    settings.ANALYTICS_DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# 7. Marketing Database - Campaigns, Promotions
marketing_engine = create_engine(
    settings.MARKETING_DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Primary engine (Identity for backward compatibility)
engine = identity_engine

# =========================================================================
# SESSION FACTORIES
# =========================================================================

IdentitySession = sessionmaker(autocommit=False, autoflush=False, bind=identity_engine)
ProductSession = sessionmaker(autocommit=False, autoflush=False, bind=product_engine)
OrderSession = sessionmaker(autocommit=False, autoflush=False, bind=order_engine)
SupportSession = sessionmaker(autocommit=False, autoflush=False, bind=support_engine)
KnowledgeSession = sessionmaker(autocommit=False, autoflush=False, bind=knowledge_engine)
AnalyticsSession = sessionmaker(autocommit=False, autoflush=False, bind=analytics_engine)
MarketingSession = sessionmaker(autocommit=False, autoflush=False, bind=marketing_engine)

# Default session (Identity for backward compatibility)
SessionLocal = IdentitySession

# Base class for models
Base = declarative_base()


# =========================================================================
# DEPENDENCY FUNCTIONS
# =========================================================================

def get_db():
    """Default database dependency (Identity DB)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_identity_db():
    """Identity database session - Users, Auth"""
    db = IdentitySession()
    try:
        yield db
    finally:
        db.close()


def get_product_db():
    """Product database session - Products, Categories"""
    db = ProductSession()
    try:
        yield db
    finally:
        db.close()


def get_order_db():
    """Order database session - Orders, Carts"""
    db = OrderSession()
    try:
        yield db
    finally:
        db.close()


def get_support_db():
    """Support database session - Tickets"""
    db = SupportSession()
    try:
        yield db
    finally:
        db.close()


def get_knowledge_db():
    """Knowledge database session - KB Articles, Conversations"""
    db = KnowledgeSession()
    try:
        yield db
    finally:
        db.close()


def get_analytics_db():
    """Analytics database session - Logs, Events"""
    db = AnalyticsSession()
    try:
        yield db
    finally:
        db.close()


def get_marketing_db():
    """Marketing database session - Campaigns"""
    db = MarketingSession()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables (if needed)
    Note: Tables should already exist from SQL migrations
    """
    pass  # Tables managed by SQL files in migrations/
