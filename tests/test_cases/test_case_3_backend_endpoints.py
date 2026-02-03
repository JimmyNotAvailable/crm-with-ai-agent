"""
Test Case 3: Backend API Endpoints Test
Kiểm tra các API endpoints của backend
"""
import sys
import json
import requests
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional
# Fix Unicode encoding for Windows console
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
# Add project root
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def test_backend_endpoints(base_url: str = "http://localhost:8000") -> Dict[str, Any]:
    """
    Test Case 3: Backend API Endpoints
    Kiểm tra các endpoints chính của backend
    """
    print("\n" + "="*80)
    print("TEST CASE 3: BACKEND API ENDPOINTS TEST")
    print(f"Base URL: {base_url}")
    print("="*80)
    
    results = {
        "test_name": "Backend API Endpoints",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "base_url": base_url,
        "endpoints": {},
        "summary": {
            "total": 0,
            "passed": 0,
            "failed": 0
        }
    }
    
    # Define test endpoints
    endpoints_to_test = [
        {
            "name": "Health Check",
            "method": "GET",
            "path": "/health",
            "expected_status": 200
        },
        {
            "name": "API Root",
            "method": "GET",
            "path": "/",
            "expected_status": 200
        },
        {
            "name": "Docs",
            "method": "GET",
            "path": "/docs",
            "expected_status": 200
        }
    ]
    
    results["summary"]["total"] = len(endpoints_to_test)
    
    # Test each endpoint
    for endpoint in endpoints_to_test:
        endpoint_name = endpoint["name"]
        url = f"{base_url}{endpoint['path']}"
        
        try:
            if endpoint["method"] == "GET":
                response = requests.get(url, timeout=5)
            elif endpoint["method"] == "POST":
                response = requests.post(url, timeout=5)
            else:
                response = None
            
            if response and response.status_code == endpoint["expected_status"]:
                status = "PASS"
                results["summary"]["passed"] += 1
                print(f"✅ PASS: {endpoint_name} ({endpoint['path']})")
            else:
                status = "FAIL"
                results["summary"]["failed"] += 1
                print(f"❌ FAIL: {endpoint_name} - Status: {response.status_code if response else 'No response'}")
            
            results["endpoints"][endpoint_name] = {
                "status": status,
                "method": endpoint["method"],
                "path": endpoint["path"],
                "status_code": response.status_code if response else None,
                "response_time_ms": response.elapsed.total_seconds() * 1000 if response else None
            }
            
        except requests.exceptions.ConnectionError:
            status = "FAIL"
            results["summary"]["failed"] += 1
            results["endpoints"][endpoint_name] = {
                "status": status,
                "method": endpoint["method"],
                "path": endpoint["path"],
                "error": "Connection refused - Backend not running?"
            }
            print(f"❌ FAIL: {endpoint_name} - Connection refused")
        except Exception as e:
            status = "FAIL"
            results["summary"]["failed"] += 1
            results["endpoints"][endpoint_name] = {
                "status": status,
                "method": endpoint["method"],
                "path": endpoint["path"],
                "error": str(e)
            }
            print(f"❌ FAIL: {endpoint_name} - Error: {e}")
    
    # Overall result
    results["overall_status"] = "PASS" if results["summary"]["failed"] == 0 else "FAIL"
    
    print(f"\n{'='*80}")
    print(f"Summary: {results['summary']['passed']}/{results['summary']['total']} endpoints responding")
    print(f"Overall Status: {results['overall_status']}")
    print("="*80)
    
    return results


def main():
    """Run test and save results"""
    results = test_backend_endpoints()
    
    # Save to JSON
    output_file = Path(__file__).parent / "results" / "test_case_3_backend_endpoints.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Results saved to: {output_file}")
    
    return results["overall_status"] == "PASS"


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
