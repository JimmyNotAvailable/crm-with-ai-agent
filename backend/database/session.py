"""
Database session management for 7 Microservices Architecture

This module provides:
- 7 separate SQLAlchemy engines for each microservice database
- Connection pooling with health checks
- Session factories for each database
- Dependency injection functions for FastAPI

Database Architecture:
- Identity DB (3310): Users, Authentication
- Product DB (3311): Products, Categories
- Order DB (3312): Orders, OrderItems, Carts
- Support DB (3313): Tickets, TicketMessages
- Knowledge DB (3314): KB Articles, Conversations
- Analytics DB (3315): Logs, Events
- Marketing DB (3316): Campaigns, Promotions
"""
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from typing import Dict, Generator
import logging

from backend.core.config import settings

logger = logging.getLogger(__name__)

# =========================================================================
# CONNECTION POOL CONFIGURATION
# Optimized for microservices architecture
# =========================================================================
POOL_CONFIG = {
    'poolclass': QueuePool,
    'pool_size': 5,              # Core connections per database
    'max_overflow': 10,          # Max additional connections
    'pool_recycle': 3600,        # Recycle connections every hour
    'pool_pre_ping': True,       # Test connection before using
    'pool_timeout': 30,          # Timeout waiting for connection
    'echo': settings.DEBUG,      # Log SQL in debug mode
}

# =========================================================================
# DATABASE ENGINES (7 Microservices)
# Each engine manages connections to a specific database
# =========================================================================

def _create_engine_safe(url: str, db_name: str):
    """Create engine with error handling"""
    try:
        engine = create_engine(url, **POOL_CONFIG)
        logger.info(f"[OK] Created engine for {db_name}")
        return engine
    except Exception as e:
        logger.error(f"[FAILED] Failed to create engine for {db_name}: {e}")
        raise

# 1. Identity Database - Users, Authentication
identity_engine = _create_engine_safe(
    settings.IDENTITY_DATABASE_URL,
    "Identity DB"
)

# 2. Product Database - Products, Categories
product_engine = _create_engine_safe(
    settings.PRODUCT_DATABASE_URL,
    "Product DB"
)

# 3. Order Database - Orders, OrderItems, Carts
order_engine = _create_engine_safe(
    settings.ORDER_DATABASE_URL,
    "Order DB"
)

# 4. Support Database - Tickets, TicketMessages
support_engine = _create_engine_safe(
    settings.SUPPORT_DATABASE_URL,
    "Support DB"
)

# 5. Knowledge Database - KB Articles, Conversations
knowledge_engine = _create_engine_safe(
    settings.KNOWLEDGE_DATABASE_URL,
    "Knowledge DB"
)

# 6. Analytics Database - Logs, Events
analytics_engine = _create_engine_safe(
    settings.ANALYTICS_DATABASE_URL,
    "Analytics DB"
)

# 7. Marketing Database - Campaigns, Promotions
marketing_engine = _create_engine_safe(
    settings.MARKETING_DATABASE_URL,
    "Marketing DB"
)

# Primary engine (Identity for backward compatibility)
engine = identity_engine

# Engine registry for dynamic access
ENGINES: Dict[str, any] = {
    'identity': identity_engine,
    'product': product_engine,
    'order': order_engine,
    'support': support_engine,
    'knowledge': knowledge_engine,
    'analytics': analytics_engine,
    'marketing': marketing_engine,
}

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


# =========================================================================
# HEALTH CHECK FUNCTIONS
# =========================================================================

def check_database_health(db_name: str = None) -> Dict[str, bool]:
    """
    Check database connectivity
    
    Args:
        db_name: Specific database to check (identity, product, etc.)
                 If None, checks all databases
    
    Returns:
        Dict with database name and health status
    """
    results = {}
    
    engines_to_check = {db_name: ENGINES[db_name]} if db_name else ENGINES
    
    for name, engine in engines_to_check.items():
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            results[name] = True
            logger.debug(f"[OK] {name} database healthy")
        except Exception as e:
            results[name] = False
            logger.error(f"[FAILED] {name} database unhealthy: {e}")
    
    return results


def get_engine(db_type: str):
    """
    Get engine for specific database type
    
    Args:
        db_type: identity, product, order, support, knowledge, analytics, marketing
    
    Returns:
        SQLAlchemy engine
    """
    if db_type not in ENGINES:
        raise ValueError(f"Unknown database type: {db_type}. Valid types: {list(ENGINES.keys())}")
    return ENGINES[db_type]


def get_session_for_model(model_class):
    """
    Get appropriate session based on model's __tablename__
    
    Usage:
        session = get_session_for_model(User)
        session = get_session_for_model(Product)
    """
    table_name = getattr(model_class, '__tablename__', None)
    
    # Mapping table names to databases
    table_db_mapping = {
        # Identity DB
        'users': 'identity',
        'user_roles': 'identity',
        
        # Product DB  
        'products': 'product',
        'categories': 'product',
        'product_images': 'product',
        
        # Order DB
        'orders': 'order',
        'order_items': 'order',
        'carts': 'order',
        'cart_items': 'order',
        
        # Support DB
        'tickets': 'support',
        'ticket_messages': 'support',
        
        # Knowledge DB
        'kb_articles': 'knowledge',
        'conversations': 'knowledge',
        'conversation_messages': 'knowledge',
        
        # Analytics DB
        'audit_logs': 'analytics',
        'user_events': 'analytics',
        
        # Marketing DB
        'campaigns': 'marketing',
        'promotions': 'marketing',
    }
    
    db_type = table_db_mapping.get(table_name, 'identity')
    session_map = {
        'identity': IdentitySession,
        'product': ProductSession,
        'order': OrderSession,
        'support': SupportSession,
        'knowledge': KnowledgeSession,
        'analytics': AnalyticsSession,
        'marketing': MarketingSession,
    }
    
    return session_map[db_type]()
