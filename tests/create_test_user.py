"""Test user registration directly without HTTP"""
import sys
from pathlib import Path

# Add project root
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import uuid
from datetime import datetime
from backend.database.session import IdentitySession
from backend.models.user import User, UserType, UserStatus
from backend.utils.security import get_password_hash


def create_test_user():
    """Create a test user for API testing"""
    db = IdentitySession()

    try:
        # Check if test user exists
        existing = db.query(User).filter(User.email == "test@example.com").first()
        if existing:
            print(f"User already exists: {existing.id}")
            db.delete(existing)
            db.commit()
            print("Deleted existing user")

        # Create new user with proper bcrypt hash
        now = datetime.utcnow()
        new_user = User(
            id=str(uuid.uuid4()),
            email="test@example.com",
            password_hash=get_password_hash("password123"),
            full_name="Test User",
            phone="0123456789",
            user_type=UserType.CUSTOMER,
            status=UserStatus.ACTIVE,
            email_verified=False,
            created_at=now,
            updated_at=now
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print(f"Created user: {new_user.id}")
        print(f"Email: {new_user.email}")
        print(f"Hash: {new_user.password_hash[:50]}...")
        
        # Verify password works
        from backend.utils.security import verify_password
        test = verify_password("password123", new_user.password_hash)
        print(f"Password verification: {test}")
        
        return new_user
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Create Test User")
    print("=" * 60)
    user = create_test_user()
    if user:
        print()
        print("✓ Test user created successfully!")
    else:
        print()
        print("✗ Failed to create test user")
