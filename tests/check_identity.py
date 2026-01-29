"""Check identity database schema"""
import sys
from pathlib import Path

# Add project root
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.database.session import identity_engine
from sqlalchemy import inspect

def check_identity_db():
    """Check identity database tables and schema"""
    inspector = inspect(identity_engine)
    tables = inspector.get_table_names()
    print("Tables in crm_identity_db:")
    for t in tables:
        print(f"  - {t}")
        
    if "users" in tables:
        print()
        print("Columns in users table:")
        cols = inspector.get_columns("users")
        for c in cols:
            print(f"  {c['name']}: {c['type']}")
    else:
        print("\nWARNING: 'users' table not found!")
        print("\nSearching for user-related tables...")
        for t in tables:
            if "user" in t.lower():
                print(f"  Found: {t}")


if __name__ == "__main__":
    print("=" * 60)
    print("Identity Database Schema Check")
    print("=" * 60)
    check_identity_db()
