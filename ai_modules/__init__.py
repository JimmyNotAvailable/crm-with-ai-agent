# AI Modules Package
"""
AI Core Logic for CRM-AI-Agent

Cấu trúc 2 Agent:
- Agent 1 (Customer Service): RAG, Recommendation, Summarization
- Agent 2 (Operations): Order Management, Ticket, Sentiment

Modules:
├── core/                           # Shared utilities & base classes
├── agent_customer_service/         # Agent 1 - Customer Service
│   ├── rag/                        # RAG Pipeline (KB, Policy, FAQ)
│   ├── recommendation/             # Product Recommendation (ML)
│   └── summarization/              # Conversation Summarization
├── agent_operations/               # Agent 2 - Operations
│   ├── order_lookup/               # Order Management
│   ├── ticket_management/          # Ticket CRUD
│   └── sentiment/                  # Sentiment Analysis
└── (legacy modules)                # Backward compatibility
"""

__version__ = "2.0.0"

# Core exports
from ai_modules.core.config import ai_config, AIConfig
from ai_modules.core.base_agent import BaseAgent, AgentType, AgentResponse

# Agent 1: Customer Service
from ai_modules.agent_customer_service import (
    CustomerServiceAgent,
    RAGService,
    ProductRecommender,
    ConversationSummarizer
)

# Agent 2: Operations
from ai_modules.agent_operations import OperationsAgent

# Legacy exports (backward compatibility)
from ai_modules.summarization import SummarizationService
from ai_modules.ticket_deduplication import TicketDeduplicationService

__all__ = [
    # Config
    "ai_config",
    "AIConfig",
    
    # Base classes
    "BaseAgent",
    "AgentType", 
    "AgentResponse",
    
    # Agent 1
    "CustomerServiceAgent",
    "RAGService",
    "ProductRecommender",
    "ConversationSummarizer",
    
    # Agent 2
    "OperationsAgent",
    
    # Legacy
    "SummarizationService",
    "TicketDeduplicationService",
]
