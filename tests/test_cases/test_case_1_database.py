"""
Test Case 1: Database Connectivity Test
Kiểm tra kết nối tới 7 microservices databases
"""
import sys
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any

# Fix Unicode encoding for Windows console
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add project root
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.database.session import check_database_health, ENGINES
from backend.core.config import settings


def test_database_connectivity() -> Dict[str, Any]:
    """
    Test Case 1: Database Connectivity
    Kiểm tra kết nối tới 7 databases
    """
    print("\n" + "="*80)
    print("TEST CASE 1: DATABASE CONNECTIVITY TEST")
    print("="*80)
    
    results = {
        "test_name": "Database Connectivity",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": settings.ENVIRONMENT,
        "databases": {},
        "summary": {
            "total": 7,
            "passed": 0,
            "failed": 0
        }
    }
    
    # Test each database
    health = check_database_health()
    
    for db_name, is_healthy in health.items():
        status = "PASS" if is_healthy else "FAIL"
        results["databases"][db_name] = {
            "status": status,
            "healthy": is_healthy
        }
        
        if is_healthy:
            results["summary"]["passed"] += 1
            print(f"✅ PASS: {db_name.upper()} Database")
        else:
            results["summary"]["failed"] += 1
            print(f"❌ FAIL: {db_name.upper()} Database")
    
    # Overall result
    results["overall_status"] = "PASS" if results["summary"]["failed"] == 0 else "FAIL"
    
    print(f"\n{'='*80}")
    print(f"Summary: {results['summary']['passed']}/{results['summary']['total']} databases connected")
    print(f"Overall Status: {results['overall_status']}")
    print("="*80)
    
    return results


def main():
    """Run test and save results"""
    results = test_database_connectivity()
    
    # Save to JSON
    output_file = Path(__file__).parent / "results" / "test_case_1_database_connectivity.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Results saved to: {output_file}")
    
    return results["overall_status"] == "PASS"


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
