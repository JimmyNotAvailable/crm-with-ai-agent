"""
Conversation Schemas
"""
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class ConversationMessageBase(BaseModel):
    role: str
    content: str

class ConversationMessageCreate(ConversationMessageBase):
    pass

class ConversationMessageResponse(ConversationMessageBase):
    id: str
    conversation_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationBase(BaseModel):
    title: Optional[str] = None

class ConversationCreate(ConversationBase):
    pass

class ConversationResponse(ConversationBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    messages: List[ConversationMessageResponse] = []

    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = None
    top_k: int = 3

class ChatResponse(BaseModel):
    query: str
    answer: str
    conversation_id: str
