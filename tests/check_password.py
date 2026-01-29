"""Check user credentials"""
import sys
from pathlib import Path

# Add project root
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.database.session import IdentitySession
from sqlalchemy import text
from backend.utils.security import verify_password


def check_user_password():
    """Check user password hash and verify"""
    db = IdentitySession()
    result = db.execute(text("SELECT email, password_hash FROM users LIMIT 1")).fetchone()
    print(f"Email: {result[0]}")
    print(f"Hash: {result[1]}")
    db.close()

    # Test if password is 'password123'
    if result[1]:
        test = verify_password("password123", result[1])
        print(f"Is password 'password123'? {test}")
        
        test2 = verify_password("password", result[1])
        print(f"Is password 'password'? {test2}")


if __name__ == "__main__":
    print("=" * 60)
    print("User Password Check")
    print("=" * 60)
    check_user_password()
