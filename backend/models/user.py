"""
User model for authentication and authorization
Matches crm_identity_db.users schema
"""
from sqlalchemy import Column, String, Boolean, DateTime, Enum, Integer, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database.session import Base
import enum


class UserType(str, enum.Enum):
    """User type enumeration - matches database ENUM"""
    CUSTOMER = "CUSTOMER"
    STAFF = "STAFF"
    ADMIN = "ADMIN"


class UserStatus(str, enum.Enum):
    """User status enumeration - matches database ENUM"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"


# Alias for backward compatibility
UserRole = UserType


class User(Base):
    """
    User model for system authentication
    Matches crm_identity_db.users schema (microservices architecture)
    """
    __tablename__ = "users"

    # UUID primary key (CHAR(36) in database)
    id = Column(String(36), primary_key=True, index=True)
    email = Column(String(320), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    phone = Column(String(50))
    full_name = Column(String(255))
    avatar_url = Column(Text)
    
    # Role-based access control
    user_type = Column(Enum(UserType), default=UserType.CUSTOMER, nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    
    # Verification
    email_verified = Column(Boolean, default=False)
    phone_verified = Column(Boolean, default=False)
    
    # Locale
    locale = Column(String(10), default="vi")
    timezone = Column(String(64), default="Asia/Ho_Chi_Minh")
    
    # Login tracking
    last_login_at = Column(DateTime)
    last_login_ip = Column(String(45))
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime)
    password_changed_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships (may need to adjust foreign keys)
    # conversations = relationship("Conversation", back_populates="user")
    
    # Compatibility properties
    @property
    def role(self):
        """Backward compatibility: return user_type as role"""
        return self.user_type
    
    @property
    def is_active(self):
        """Backward compatibility: check if status is ACTIVE"""
        return self.status == UserStatus.ACTIVE
    
    @property
    def is_verified(self):
        """Backward compatibility: check if email is verified"""
        return self.email_verified
    
    @property
    def hashed_password(self):
        """Backward compatibility: alias for password_hash"""
        return self.password_hash
    
    @property
    def username(self):
        """Backward compatibility: use email as username"""
        return self.email
    
    @property
    def last_login(self):
        """Backward compatibility: alias for last_login_at"""
        return self.last_login_at
    
    def __repr__(self):
        return f"<User {self.email} ({self.user_type})>"
