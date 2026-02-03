"""
Database Helper Utilities for AI Agents
Provides easy multi-database access for AI modules
"""
from typing import Dict, Any, Optional, Generator
from sqlalchemy.orm import Session
from contextlib import contextmanager

from backend.database.session import (
    IdentitySession, ProductSession, OrderSession, SupportSession,
    KnowledgeSession, AnalyticsSession, MarketingSession,
    ENGINES
)


class MultiDatabaseSession:
    """
    Multi-database session manager for AI Agents
    Allows agents to access all 7 microservices databases
    
    Usage:
        with MultiDatabaseSession() as sessions:
            user = sessions.identity.query(User).filter_by(id=1).first()
            products = sessions.product.query(Product).all()
            orders = sessions.order.query(Order).filter_by(user_id=user.id).all()
    """
    
    def __init__(self):
        self.identity = None
        self.product = None
        self.order = None
        self.support = None
        self.knowledge = None
        self.analytics = None
        self.marketing = None
        self._sessions = []
    
    def __enter__(self):
        """Open all database sessions"""
        self.identity = IdentitySession()
        self.product = ProductSession()
        self.order = OrderSession()
        self.support = SupportSession()
        self.knowledge = KnowledgeSession()
        self.analytics = AnalyticsSession()
        self.marketing = MarketingSession()
        
        self._sessions = [
            self.identity, self.product, self.order, self.support,
            self.knowledge, self.analytics, self.marketing
        ]
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close all database sessions"""
        for session in self._sessions:
            if session:
                try:
                    session.close()
                except Exception:
                    pass
    
    def commit_all(self):
        """Commit all sessions"""
        for session in self._sessions:
            if session:
                session.commit()
    
    def rollback_all(self):
        """Rollback all sessions"""
        for session in self._sessions:
            if session:
                session.rollback()


class AgentDatabaseHelper:
    """
    Simplified database helper for AI Agents
    Provides common query patterns needed by agents
    """
    
    def __init__(self):
        self.sessions = MultiDatabaseSession()
    
    @contextmanager
    def get_sessions(self) -> Generator[MultiDatabaseSession, None, None]:
        """Context manager to get all database sessions"""
        with self.sessions as sessions:
            yield sessions
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user from Identity DB"""
        with self.sessions as sessions:
            from backend.models.user import User
            user = sessions.identity.query(User).filter_by(id=user_id).first()
            if not user:
                return None
            return {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "phone": user.phone
            }
    
    def get_products(
        self, 
        category: Optional[str] = None,
        limit: int = 10
    ) -> list[Dict[str, Any]]:
        """Get products from Product DB"""
        with self.sessions as sessions:
            from backend.models.product import Product
            query = sessions.product.query(Product)
            
            if category:
                query = query.filter_by(category=category)
            
            products = query.limit(limit).all()
            
            return [{
                "id": p.id,
                "name": p.name,
                "price": p.price,
                "category": p.category,
                "stock_quantity": p.stock_quantity,
                "description": p.description
            } for p in products]
    
    def get_user_orders(
        self,
        user_id: int,
        limit: int = 10
    ) -> list[Dict[str, Any]]:
        """Get user orders from Order DB"""
        with self.sessions as sessions:
            from backend.models.order import Order
            orders = sessions.order.query(Order).filter_by(
                customer_id=user_id
            ).order_by(Order.created_at.desc()).limit(limit).all()
            
            return [{
                "id": o.id,
                "order_number": o.order_number,
                "status": o.status,
                "total_amount": o.total_amount,
                "created_at": o.created_at.isoformat(),
                "shipping_address": o.shipping_address
            } for o in orders]
    
    def get_user_tickets(
        self,
        user_id: int,
        limit: int = 10
    ) -> list[Dict[str, Any]]:
        """Get user tickets from Support DB"""
        with self.sessions as sessions:
            from backend.models.ticket import Ticket
            tickets = sessions.support.query(Ticket).filter_by(
                user_id=user_id
            ).order_by(Ticket.created_at.desc()).limit(limit).all()
            
            return [{
                "id": t.id,
                "ticket_number": t.ticket_number,
                "subject": t.subject,
                "status": t.status,
                "priority": t.priority,
                "created_at": t.created_at.isoformat()
            } for t in tickets]
    
    def get_conversations(
        self,
        user_id: int,
        limit: int = 10
    ) -> list[Dict[str, Any]]:
        """Get user conversations from Knowledge DB"""
        with self.sessions as sessions:
            from backend.models.conversation import Conversation
            conversations = sessions.knowledge.query(Conversation).filter_by(
                user_id=user_id
            ).order_by(Conversation.created_at.desc()).limit(limit).all()
            
            return [{
                "id": c.id,
                "title": c.title,
                "message_count": len(c.messages) if c.messages else 0,
                "created_at": c.created_at.isoformat(),
                "updated_at": c.updated_at.isoformat()
            } for c in conversations]
    
    def log_agent_action(
        self,
        user_id: int,
        action: str,
        details: Dict[str, Any]
    ) -> bool:
        """Log agent action to Analytics DB"""
        try:
            with self.sessions as sessions:
                from backend.models.analytics import AgentLog
                from datetime import datetime
                
                log = AgentLog(
                    user_id=user_id,
                    action=action,
                    details=str(details),
                    created_at=datetime.utcnow()
                )
                sessions.analytics.add(log)
                sessions.analytics.commit()
                return True
        except Exception as e:
            print(f"[AgentDatabaseHelper] Failed to log action: {e}")
            return False


# Global instance for easy import
agent_db_helper = AgentDatabaseHelper()


# Convenience functions for agents
def get_all_databases_for_agent() -> MultiDatabaseSession:
    """
    Get all database sessions for an agent
    Use with context manager:
    
    with get_all_databases_for_agent() as sessions:
        user = sessions.identity.query(User).first()
        products = sessions.product.query(Product).all()
    """
    return MultiDatabaseSession()
