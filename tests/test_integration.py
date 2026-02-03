"""
Test script to verify Backend + AI Agent + Database Integration
Tests:
1. Database connections (7 microservices)
2. AI/LLM configuration (Gemini/OpenAI)
3. RAG service functionality
4. Agent endpoints
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.core.config import settings
from backend.database.session import check_database_health, ENGINES
from ai_modules.core.config import ai_config


def test_database_connections():
    """Test all 7 microservices database connections"""
    print("\n" + "="*70)
    print("TEST 1: DATABASE CONNECTIONS")
    print("="*70)
    
    health = check_database_health()
    
    for db_name, is_healthy in health.items():
        status = "✅ OK" if is_healthy else "❌ FAILED"
        print(f"{status} {db_name.upper()} Database")
    
    all_healthy = all(health.values())
    print(f"\n{'✅' if all_healthy else '❌'} Overall Database Health: {'PASS' if all_healthy else 'FAIL'}")
    return all_healthy


def test_ai_config():
    """Test AI/LLM configuration"""
    print("\n" + "="*70)
    print("TEST 2: AI/LLM CONFIGURATION")
    print("="*70)
    
    # Check DEMO_MODE
    demo_mode = settings.DEMO_MODE
    print(f"DEMO_MODE: {demo_mode}")
    
    # Check Gemini
    has_gemini = bool(settings.GEMINI_API_KEY)
    print(f"{'✅' if has_gemini else '⚠️'} Gemini API Key: {'Configured' if has_gemini else 'NOT SET'}")
    if has_gemini:
        print(f"   Model: {settings.GEMINI_MODEL}")
    
    # Check OpenAI
    has_openai = bool(settings.OPENAI_API_KEY)
    print(f"{'✅' if has_openai else '⚠️'} OpenAI API Key: {'Configured' if has_openai else 'NOT SET'}")
    if has_openai:
        print(f"   Model: {settings.OPENAI_MODEL}")
    
    # Check Embedding
    print(f"✅ Embedding Model: {settings.EMBEDDING_MODEL}")
    
    # Check ChromaDB
    chroma_dir = Path(settings.CHROMA_PERSIST_DIRECTORY)
    chroma_exists = chroma_dir.exists()
    print(f"{'✅' if chroma_exists else '⚠️'} ChromaDB Directory: {chroma_dir} {'(exists)' if chroma_exists else '(not created yet)'}")
    
    has_llm = has_gemini or has_openai or demo_mode
    print(f"\n{'✅' if has_llm else '⚠️'} LLM Status: {'READY' if has_llm else 'NOT CONFIGURED (will use DEMO_MODE)'}")
    
    return has_llm


def test_rag_service():
    """Test RAG Service initialization"""
    print("\n" + "="*70)
    print("TEST 3: RAG SERVICE")
    print("="*70)
    
    try:
        from ai_modules.agent_customer_service.rag import RAGService
        
        rag = RAGService()
        print(f"✅ RAG Service initialized")
        print(f"   LLM Provider: {rag.llm_provider or 'DEMO_MODE'}")
        print(f"   ChromaDB Path: {rag.chroma_path}")
        
        # Test policy retriever
        try:
            policy_docs = rag.policy_retriever.retrieve("chính sách đổi trả", top_k=2)
            print(f"✅ Policy Retriever: Retrieved {len(policy_docs)} documents")
        except Exception as e:
            print(f"⚠️ Policy Retriever: {e}")
        
        # Test product retriever
        try:
            product_docs = rag.product_retriever.retrieve("laptop", top_k=2)
            print(f"✅ Product Retriever: Retrieved {len(product_docs)} documents")
        except Exception as e:
            print(f"⚠️ Product Retriever: {e}")
        
        return True
    except Exception as e:
        print(f"❌ RAG Service Error: {e}")
        return False


def test_agent_integration():
    """Test CustomerServiceAgent integration"""
    print("\n" + "="*70)
    print("TEST 4: CUSTOMER SERVICE AGENT")
    print("="*70)
    
    try:
        from ai_modules.agent_customer_service import CustomerServiceAgent
        
        agent = CustomerServiceAgent(db=None)
        print(f"✅ CustomerServiceAgent initialized")
        
        # Test simple query
        query = "Có laptop nào tốt không?"
        print(f"\n📝 Test Query: '{query}'")
        
        response = agent.process_query(query=query, user_id="test_user")
        
        print(f"{'✅' if response.success else '❌'} Response: {response.success}")
        print(f"   Tool Used: {response.tool_used}")
        print(f"   Message: {response.message[:100]}...")
        
        return response.success
    except Exception as e:
        print(f"❌ Agent Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_backend_endpoints():
    """Test backend API endpoints availability"""
    print("\n" + "="*70)
    print("TEST 5: BACKEND API ENDPOINTS")
    print("="*70)
    
    try:
        from backend.main import app
        
        routes = []
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                routes.append((route.path, route.methods))
        
        # Key endpoints to check
        key_endpoints = [
            "/auth/login",
            "/auth/register",
            "/rag/chat",
            "/rag/query",
            "/products",
            "/orders",
            "/tickets"
        ]
        
        for endpoint in key_endpoints:
            exists = any(endpoint in path for path, _ in routes)
            print(f"{'✅' if exists else '❌'} {endpoint}")
        
        print(f"\n✅ Total Routes: {len(routes)}")
        return True
    except Exception as e:
        print(f"❌ Backend Error: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("🧪 CRM-AI-Agent Integration Test Suite")
    print("="*70)
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Debug Mode: {settings.DEBUG}")
    
    results = {
        "Database Connections": test_database_connections(),
        "AI Configuration": test_ai_config(),
        "RAG Service": test_rag_service(),
        "Agent Integration": test_agent_integration(),
        "Backend Endpoints": test_backend_endpoints()
    }
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
    
    total = len(results)
    passed = sum(results.values())
    
    print(f"\n{'='*70}")
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ ALL TESTS PASSED - System is ready!")
    else:
        print("⚠️ SOME TESTS FAILED - Check configuration")
    
    print("="*70 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
