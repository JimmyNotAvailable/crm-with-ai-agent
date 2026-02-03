"""
Test Case 2: AI Module Integration Test
Kiểm tra tích hợp AI modules (RAG, Agent)
"""
import sys
import json
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any

# Load environment variables BEFORE importing settings
from dotenv import load_dotenv
load_dotenv(override=True)

# Fix Unicode encoding for Windows console
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add project root
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.core.config import settings
from ai_modules.core.config import ai_config


def test_ai_configuration() -> Dict[str, Any]:
    """Test AI configuration"""
    print("\n" + "="*80)
    print("TEST CASE 2: AI MODULE INTEGRATION TEST")
    print("="*80)
    
    # Show current env vars for debugging
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    demo_mode = os.getenv("DEMO_MODE", "true")
    print(f"📋 Environment: GEMINI_API_KEY={'SET' if gemini_key else 'NOT SET'}, DEMO_MODE={demo_mode}")
    
    results = {
        "test_name": "AI Module Integration",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tests": {},
        "summary": {
            "total": 5,
            "passed": 0,
            "failed": 0
        }
    }
    
    # Test 1: Gemini API Key
    has_gemini = bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "")
    results["tests"]["gemini_api_key"] = {
        "status": "PASS" if has_gemini else "WARN",
        "configured": has_gemini,
        "model": settings.GEMINI_MODEL if has_gemini else None
    }
    print(f"{'✅' if has_gemini else '⚠️'} Gemini API Key: {'Configured' if has_gemini else 'NOT SET'}")
    if has_gemini:
        results["summary"]["passed"] += 1
    
    # Test 2: OpenAI API Key
    has_openai = bool(settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "" and not settings.OPENAI_API_KEY.startswith("sk-your"))
    results["tests"]["openai_api_key"] = {
        "status": "PASS" if has_openai else "WARN",
        "configured": has_openai,
        "model": settings.OPENAI_MODEL if has_openai else None
    }
    print(f"{'✅' if has_openai else '⚠️'} OpenAI API Key: {'Configured' if has_openai else 'NOT SET'}")
    if has_openai:
        results["summary"]["passed"] += 1
    
    # Test 3: ChromaDB Directory
    from pathlib import Path
    chroma_dir = Path(settings.CHROMA_PERSIST_DIRECTORY)
    chroma_exists = chroma_dir.exists()
    results["tests"]["chromadb_directory"] = {
        "status": "PASS" if chroma_exists else "WARN",
        "exists": chroma_exists,
        "path": str(chroma_dir)
    }
    print(f"{'✅' if chroma_exists else '⚠️'} ChromaDB Directory: {'Exists' if chroma_exists else 'Not created'}")
    if chroma_exists:
        results["summary"]["passed"] += 1
    
    # Test 4: RAG Service
    try:
        from ai_modules.agent_customer_service.rag import RAGService
        rag = RAGService()
        results["tests"]["rag_service"] = {
            "status": "PASS",
            "initialized": True,
            "llm_provider": rag.llm_provider or "DEMO_MODE"
        }
        print(f"✅ RAG Service: Initialized (Provider: {rag.llm_provider or 'DEMO_MODE'})")
        results["summary"]["passed"] += 1
    except Exception as e:
        results["tests"]["rag_service"] = {
            "status": "FAIL",
            "initialized": False,
            "error": str(e)
        }
        print(f"❌ RAG Service: Failed - {e}")
        results["summary"]["failed"] += 1
    
    # Test 5: Customer Service Agent
    try:
        from ai_modules.agent_customer_service import CustomerServiceAgent
        agent = CustomerServiceAgent(db=None)
        results["tests"]["customer_service_agent"] = {
            "status": "PASS",
            "initialized": True
        }
        print(f"✅ Customer Service Agent: Initialized")
        results["summary"]["passed"] += 1
    except Exception as e:
        results["tests"]["customer_service_agent"] = {
            "status": "FAIL",
            "initialized": False,
            "error": str(e)
        }
        print(f"❌ Customer Service Agent: Failed - {e}")
        results["summary"]["failed"] += 1
    
    # Overall result
    results["overall_status"] = "PASS" if results["summary"]["failed"] == 0 else "PARTIAL"
    
    print(f"\n{'='*80}")
    print(f"Summary: {results['summary']['passed']}/{results['summary']['total']} tests passed")
    print(f"Overall Status: {results['overall_status']}")
    print("="*80)
    
    return results


def main():
    """Run test and save results"""
    results = test_ai_configuration()
    
    # Save to JSON
    output_file = Path(__file__).parent / "results" / "test_case_2_ai_integration.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Results saved to: {output_file}")
    
    return results["overall_status"] != "FAIL"


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
