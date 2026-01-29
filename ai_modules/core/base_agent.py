"""
Base Agent - Abstract base class for all AI Agents
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
from sqlalchemy.orm import Session


class AgentType(str, Enum):
    """Types of AI Agents in the system"""
    CUSTOMER_SERVICE = "customer_service"  # Agent 1: Tư vấn, gợi ý, tóm tắt
    OPERATIONS = "operations"               # Agent 2: Đơn hàng, ticket, sentiment


@dataclass
class AgentResponse:
    """Standard response format for all agents"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    sources: Optional[List[Dict[str, Any]]] = None
    tool_used: Optional[str] = None
    confidence: float = 1.0


class BaseAgent(ABC):
    """
    Abstract base class for all AI Agents
    
    All agents must implement:
    - process_query(): Main query processing
    - get_available_tools(): List available tools
    """
    
    def __init__(self, db: Session, agent_type: AgentType):
        self.db = db
        self.agent_type = agent_type
    
    @abstractmethod
    def process_query(
        self, 
        query: str, 
        user_id: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """
        Process user query and return response
        
        Args:
            query: User's question/request
            user_id: Optional user ID for personalization
            context: Optional additional context
            
        Returns:
            AgentResponse with answer and metadata
        """
        pass
    
    @abstractmethod
    def get_available_tools(self) -> List[str]:
        """
        Get list of available tools for this agent
        
        Returns:
            List of tool names
        """
        pass
    
    def validate_permissions(self, user_id: int, action: str) -> bool:
        """
        Validate if user has permission to perform action
        Override in subclass if needed
        """
        return True
    
    def log_interaction(
        self, 
        query: str, 
        response: AgentResponse, 
        user_id: Optional[int] = None
    ) -> None:
        """
        Log agent interaction for analytics
        Override in subclass if needed
        """
        pass
