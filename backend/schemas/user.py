"""
User schemas for API request/response validation
Matches crm_identity_db.users schema
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from backend.models.user import UserType, UserStatus

# Alias for backward compatibility
UserRole = UserType


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None


class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(..., min_length=6)
    user_type: UserType = UserType.CUSTOMER


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user response - matches database schema"""
    id: str  # UUID in database
    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    user_type: UserType
    status: UserStatus
    email_verified: bool = False
    created_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None
    
    # Backward compatibility properties
    @property
    def username(self) -> str:
        return self.email
    
    @property
    def role(self) -> UserType:
        return self.user_type
    
    @property
    def is_active(self) -> bool:
        return self.status == UserStatus.ACTIVE
    
    @property
    def is_verified(self) -> bool:
        return self.email_verified
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    """Token payload data"""
    user_id: str  # UUID
    username: str
    role: UserType
