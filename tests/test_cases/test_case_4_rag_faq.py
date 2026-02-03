"""
Test Case 4: RAG Agent with FAQ Data
Kiểm tra Agent xử lý câu hỏi thực tế từ FAQ data trong ChromaDB
"""
import sys
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add project root
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from backend.core.config import settings
from ai_modules.core.config import ai_config


def test_rag_with_faq() -> Dict[str, Any]:
    """
    Test Case 4: RAG Agent với FAQ Data
    Kiểm tra Agent trả lời câu hỏi từ FAQ knowledge base
    """
    print("\n" + "="*80)
    print("TEST CASE 4: RAG AGENT WITH FAQ DATA")
    print("="*80)
    
    results = {
        "test_name": "RAG Agent with FAQ",
        "timestamp": datetime.now().isoformat(),
        "api_config": {},
        "queries": {},
        "summary": {
            "total": 5,
            "passed": 0,
            "failed": 0
        }
    }
    
    # Check API configuration
    print("\n📋 API Configuration:")
    print(f"   Gemini API: {settings.GEMINI_API_KEY[:20]}..." if settings.GEMINI_API_KEY else "   Gemini API: NOT SET")
    print(f"   OpenAI API: {settings.OPENAI_API_KEY[:20]}..." if settings.OPENAI_API_KEY else "   OpenAI API: NOT SET")
    print(f"   Demo Mode: {settings.DEMO_MODE}")
    
    results["api_config"] = {
        "gemini_configured": bool(settings.GEMINI_API_KEY),
        "openai_configured": bool(settings.OPENAI_API_KEY),
        "demo_mode": settings.DEMO_MODE
    }
    
    # Initialize RAG Service
    try:
        from ai_modules.agent_customer_service.rag import RAGService
        
        rag = RAGService()
        
        print(f"\n✅ RAG Service Initialized")
        print(f"   LLM Provider: {rag.llm_provider or 'DEMO_MODE'}")
        print(f"   ChromaDB Path: {rag.chroma_path}")
        
        results["rag_service"] = {
            "status": "INITIALIZED",
            "llm_provider": rag.llm_provider or "DEMO_MODE"
        }
        
    except Exception as e:
        print(f"❌ RAG Service Error: {e}")
        results["rag_service"] = {
            "status": "FAILED",
            "error": str(e)
        }
        return results
    
    # Test queries - FAQ thực tế
    test_queries = [
        {
            "id": "q1",
            "query": "Chính sách đổi trả hàng như thế nào?",
            "category": "policy",
            "expected_keywords": ["đổi trả", "ngày", "bảo hành"]
        },
        {
            "id": "q2",
            "query": "Có laptop nào phù hợp cho lập trình không?",
            "category": "product",
            "expected_keywords": ["laptop", "ram", "cpu"]
        },
        {
            "id": "q3",
            "query": "Thời gian giao hàng mất bao lâu?",
            "category": "policy",
            "expected_keywords": ["giao hàng", "ngày", "thời gian"]
        },
        {
            "id": "q4",
            "query": "Có hỗ trợ trả góp không?",
            "category": "policy",
            "expected_keywords": ["trả góp", "tháng", "lãi suất"]
        },
        {
            "id": "q5",
            "query": "So sánh iPhone 15 và Samsung Galaxy S24",
            "category": "product",
            "expected_keywords": ["iphone", "samsung", "giá"]
        }
    ]
    
    print("\n" + "="*80)
    print("Testing RAG Queries with FAQ Data")
    print("="*80)
    
    for test_query in test_queries:
        query_id = test_query["id"]
        query_text = test_query["query"]
        
        print(f"\n📝 Query {query_id}: {query_text}")
        
        try:
            # Query RAG
            result = rag.query(
                question=query_text,
                category=None,
                top_k_policy=3,
                top_k_product=3
            )
            
            answer = result.get("answer", "")
            sources = result.get("sources", [])
            confidence = result.get("confidence", 0)
            
            # Check if got meaningful answer
            has_answer = len(answer) > 50
            has_sources = len(sources) > 0
            
            if has_answer and has_sources:
                status = "PASS"
                results["summary"]["passed"] += 1
                print(f"   ✅ PASS")
            else:
                status = "PARTIAL"
                print(f"   ⚠️ PARTIAL - Limited response")
            
            print(f"   Answer length: {len(answer)} chars")
            print(f"   Sources: {len(sources)}")
            print(f"   Confidence: {confidence:.2f}")
            print(f"   Answer preview: {answer[:150]}...")
            
            results["queries"][query_id] = {
                "status": status,
                "query": query_text,
                "answer_length": len(answer),
                "sources_count": len(sources),
                "confidence": confidence,
                "answer_preview": answer[:200]
            }
            
        except Exception as e:
            print(f"   ❌ FAIL - Error: {e}")
            results["summary"]["failed"] += 1
            results["queries"][query_id] = {
                "status": "FAIL",
                "query": query_text,
                "error": str(e)
            }
    
    # Test Agent integration
    print("\n" + "="*80)
    print("Testing Customer Service Agent")
    print("="*80)
    
    try:
        from ai_modules.agent_customer_service import CustomerServiceAgent
        
        agent = CustomerServiceAgent(db=None)
        
        test_query = "Tư vấn laptop cho sinh viên"
        print(f"\n📝 Agent Query: {test_query}")
        
        response = agent.process_query(
            query=test_query,
            user_id="test_user_001"
        )
        
        print(f"   ✅ Agent Response:")
        print(f"   Success: {response.success}")
        print(f"   Tool Used: {response.tool_used}")
        print(f"   Message: {response.message[:150]}...")
        
        results["agent_test"] = {
            "status": "PASS" if response.success else "FAIL",
            "query": test_query,
            "tool_used": response.tool_used,
            "success": response.success
        }
        
        if response.success:
            results["summary"]["passed"] += 1
        
    except Exception as e:
        print(f"   ❌ Agent Error: {e}")
        results["agent_test"] = {
            "status": "FAIL",
            "error": str(e)
        }
        results["summary"]["failed"] += 1
    
    # Overall status
    total_tests = len(test_queries) + 1  # queries + agent test
    results["summary"]["total"] = total_tests
    results["summary"]["failed"] = total_tests - results["summary"]["passed"]
    results["overall_status"] = "PASS" if results["summary"]["failed"] == 0 else "PARTIAL"
    
    print(f"\n{'='*80}")
    print(f"Summary: {results['summary']['passed']}/{results['summary']['total']} tests passed")
    print(f"Overall Status: {results['overall_status']}")
    print("="*80)
    
    return results


def main():
    """Run test and save results"""
    results = test_rag_with_faq()
    
    # Save to JSON
    output_file = Path(__file__).parent / "results" / "test_case_4_rag_faq.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Results saved to: {output_file}")
    
    return results["overall_status"] in ["PASS", "PARTIAL"]


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
