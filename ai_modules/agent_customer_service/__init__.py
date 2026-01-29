"""
Agent 1: Customer Service Agent
Chức năng:
- Tư vấn sản phẩm theo thông tin và chính sách (RAG)
- Gợi ý sản phẩm cho khách hàng (ML Recommendation)
- Tóm tắt hội thoại khách hàng
- Đặt hàng và thanh toán trong chat (Order Workflow)
- Chat Actions: buttons cho đặt hàng, khiếu nại, hỗ trợ
"""
from .agent import CustomerServiceAgent
from .rag import RAGService
from .recommendation import ProductRecommender
from .summarization import ConversationSummarizer
from .order_workflow import (
    OrderWorkflowManager, 
    OrderState, 
    OrderDraft,
    PaymentService,
    QRGenerator
)

__all__ = [
    "CustomerServiceAgent",
    "RAGService", 
    "ProductRecommender",
    "ConversationSummarizer",
    "OrderWorkflowManager",
    "OrderState",
    "OrderDraft",
    "PaymentService",
    "QRGenerator"
]
