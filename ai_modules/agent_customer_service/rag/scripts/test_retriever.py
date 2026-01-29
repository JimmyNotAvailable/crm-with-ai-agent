"""
Test Retriever - Script để test retrieval từ ChromaDB
"""
from pathlib import Path
import sys

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ai_modules.agent_customer_service.rag import RAGService


def test_retriever():
    """Test the RAG retriever"""
    print("=" * 60)
    print("Testing RAG Retriever")
    print("=" * 60)
    
    # Initialize service
    rag = RAGService()
    
    # Test queries
    test_queries = [
        "Laptop văn phòng giá rẻ",
        "Chính sách đổi trả sản phẩm",
        "Laptop gaming tầm 20 triệu",
    ]
    
    for query in test_queries:
        print(f"\n[QUERY] {query}")
        print("-" * 40)
        
        result = rag.query(
            question=query,
            top_k_policy=3,
            top_k_product=3
        )
        
        print(f"Answer: {result['answer'][:200]}...")
        print(f"Sources: {len(result.get('sources', []))} documents")
        print(f"Confidence: {result.get('confidence', 0)}")
        print()


if __name__ == "__main__":
    test_retriever()
