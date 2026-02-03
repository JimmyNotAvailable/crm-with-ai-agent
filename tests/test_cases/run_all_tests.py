"""
Test Runner - Chạy tất cả test cases
"""
import sys
import json
from pathlib import Path
from datetime import datetime
import subprocess

# Fix Unicode encoding for Windows console
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def run_all_tests():
    """Chạy tất cả test cases"""
    print("\n" + "="*80)
    print("🧪 CRM-AI-AGENT TEST SUITE")
    print("="*80)
    print(f"Start Time: {datetime.now().isoformat()}")
    
    # Mapping: test file -> JSON result file name
    test_cases = {
        "test_case_1_database.py": "test_case_1_database_connectivity.json",
        "test_case_2_ai_integration.py": "test_case_2_ai_integration.json",
        "test_case_3_backend_endpoints.py": "test_case_3_backend_endpoints.json",
        "test_case_4_rag_faq.py": "test_case_4_rag_faq.json"
    }
    
    results = {
        "suite_name": "CRM-AI-Agent Full Integration Test",
        "timestamp": datetime.now().isoformat(),
        "test_cases": {},
        "summary": {
            "total": len(test_cases),
            "passed": 0,
            "failed": 0
        }
    }
    
    test_dir = Path(__file__).parent
    
    for test_file, json_result_name in test_cases.items():
        test_path = test_dir / test_file
        test_name = test_file.replace(".py", "")
        
        print(f"\n{'='*80}")
        print(f"Running: {test_name}")
        print("="*80)
        
        try:
            result = subprocess.run(
                [sys.executable, str(test_path)],
                capture_output=True,
                text=True,
                timeout=60,  # Increase timeout for AI tests
                encoding='utf-8',  # Force UTF-8 encoding
                errors='replace'  # Replace undecodable characters
            )
            
            # Print output
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            
            # Read JSON result with correct filename mapping
            json_file = test_dir / "results" / json_result_name
            if json_file.exists():
                with open(json_file, "r", encoding="utf-8") as f:
                    test_result = json.load(f)
                    results["test_cases"][test_name] = test_result
                    
                    if test_result.get("overall_status") in ["PASS", "PARTIAL"]:
                        results["summary"]["passed"] += 1
                    else:
                        results["summary"]["failed"] += 1
            else:
                results["test_cases"][test_name] = {
                    "status": "FAIL",
                    "error": "No JSON result file generated"
                }
                results["summary"]["failed"] += 1
                
        except subprocess.TimeoutExpired:
            print(f"❌ TIMEOUT: {test_name}")
            results["test_cases"][test_name] = {
                "status": "FAIL",
                "error": "Test timeout"
            }
            results["summary"]["failed"] += 1
        except Exception as e:
            print(f"❌ ERROR: {test_name} - {e}")
            results["test_cases"][test_name] = {
                "status": "FAIL",
                "error": str(e)
            }
            results["summary"]["failed"] += 1
    
    # Overall summary
    results["overall_status"] = "PASS" if results["summary"]["failed"] == 0 else "FAIL"
    
    print("\n" + "="*80)
    print("📊 TEST SUITE SUMMARY")
    print("="*80)
    print(f"Total Test Cases: {results['summary']['total']}")
    print(f"Passed: {results['summary']['passed']}")
    print(f"Failed: {results['summary']['failed']}")
    print(f"Overall Status: {results['overall_status']}")
    print("="*80)
    
    # Save suite results
    output_file = test_dir / "results" / "test_suite_summary.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Suite results saved to: {output_file}")
    
    return results["overall_status"] == "PASS"


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
