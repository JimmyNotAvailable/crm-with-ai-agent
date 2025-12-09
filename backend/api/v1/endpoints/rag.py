"""
RAG API Endpoints with AI Agent Tools
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Depends
from sqlalchemy.orm import Session
from backend.services.rag_pipeline import RAGPipeline
from backend.services.agent_tools import AgentTools, detect_intent_and_extract_params
from backend.database.session import get_db
from backend.models.conversation import Conversation, ConversationMessage
from backend.models.user import User
from backend.schemas.conversation import ChatRequest, ChatResponse, ConversationResponse
from backend.utils.security import get_current_user
from typing import List, Optional, Dict, Any
import os
import json

router = APIRouter()
_rag_service: Optional[RAGPipeline] = None

def get_rag_service() -> RAGPipeline:
    """Get or create RAG service instance"""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGPipeline()
    return _rag_service


def format_tool_response(tool_name: str, tool_result: Dict[str, Any]) -> str:
    """
    Format tool execution result into human-readable response
    """
    if not tool_result.get("success"):
        return f"❌ {tool_result.get('message', 'Lỗi không xác định')}"
    
    if tool_name == "lookup_order":
        order = tool_result
        status_emoji = {
            "PENDING": "⏳",
            "CONFIRMED": "✅",
            "SHIPPED": "🚚",
            "DELIVERED": "📦",
            "CANCELLED": "❌"
        }
        emoji = status_emoji.get(order["status"], "📋")
        
        return f"""🔍 **Thông tin đơn hàng {order['order_number']}**

{emoji} Trạng thái: {order['status']}
💰 Tổng tiền: {order['total_amount']:,.0f} VNĐ
📅 Ngày đặt: {order['created_at'][:10]}
📦 Số sản phẩm: {order['items_count']}
🏠 Địa chỉ giao: {order['shipping_address']}

{'' if not order['can_cancel'] else '💡 Bạn có thể hủy đơn hàng này.'}"""
    
    elif tool_name == "recommend_products":
        products = tool_result.get("products", [])
        lines = [f"🔍 **Tìm thấy {len(products)} sản phẩm phù hợp với '{tool_result['keyword']}':**\n"]
        
        for i, p in enumerate(products, 1):
            lines.append(f"{i}. **{p['name']}** - {p['price']:,.0f} VNĐ")
            lines.append(f"   📦 Kho: {p['stock']} sản phẩm | 🏷️ {p['category']}")
            if p['description']:
                lines.append(f"   ℹ️ {p['description']}")
            lines.append("")
        
        lines.append("💡 Nhấn 'Thêm vào giỏ' ở trang Sản phẩm để mua!")
        return "\n".join(lines)
    
    elif tool_name == "create_support_ticket":
        return f"""✅ **{tool_result['message']}**

Mã ticket: {tool_result['ticket_number']}
📧 Nhân viên hỗ trợ sẽ phản hồi qua email trong 24h.
🎫 Bạn có thể theo dõi ticket tại trang 'Hỗ trợ'."""
    
    elif tool_name == "get_my_recent_orders":
        orders = tool_result.get("orders", [])
        lines = [f"📋 **{len(orders)} đơn hàng gần nhất của bạn:**\n"]
        
        status_emoji = {
            "PENDING": "⏳",
            "CONFIRMED": "✅",
            "SHIPPED": "🚚",
            "DELIVERED": "📦"
        }
        
        for o in orders:
            emoji = status_emoji.get(o['status'], "📋")
            lines.append(f"{emoji} **{o['order_number']}** - {o['total']:,.0f} VNĐ")
            lines.append(f"   Trạng thái: {o['status']} | Ngày: {o['created'][:10]}")
            lines.append("")
        
        return "\n".join(lines)
    
    return tool_result.get("message", "Đã thực hiện thành công")

@router.post("/upload", status_code=status.HTTP_201_CREATED)
def upload_document(file: UploadFile = File(...), description: str = Form(None)):
    """
    Upload a document, chunk, embed, and store in ChromaDB
    """
    rag_service = get_rag_service()
    file_path = f"./uploaded_docs/{file.filename}"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    count = rag_service.upload_and_index(file_path, metadata={"description": description})
    return {"message": "Document uploaded and indexed", "chunks": count}

@router.post("/chat")
def chat_rag(
    query: str = Form(...),
    top_k: int = Form(3),
    conversation_id: Optional[int] = Form(None),
    use_crm_context: bool = Form(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Query RAG pipeline and get synthesized answer from LLM with conversation memory
    Optionally include CRM context (customer info, orders, tickets)
    """
    rag_service = get_rag_service()
    
    # Get or create conversation
    if conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        ).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        # Create new conversation
        conversation = Conversation(
            user_id=current_user.id,
            title=query[:50] if len(query) > 50 else query
        )
        db.add(conversation)
        db.flush()
    
    # Save user message
    user_message = ConversationMessage(
        conversation_id=conversation.id,
        role="user",
        content=query
    )
    db.add(user_message)
    
    # AI Agent: Detect intent and check if tool execution is needed
    tool_result = None
    tool_used = None
    intent_detected = detect_intent_and_extract_params(query)
    
    if intent_detected:
        # Execute tool
        agent_tools = AgentTools(db, current_user)
        tool_name = intent_detected["tool"]
        tool_params = intent_detected["params"]
        
        tool_result = agent_tools.execute_tool(tool_name, **tool_params)
        tool_used = tool_name
        
        # Save tool execution in message metadata
        user_message.metadata = json.dumps({
            "tool_detected": tool_name,
            "tool_params": tool_params,
            "tool_result": tool_result
        })
    
    # Get CRM context if requested
    crm_context = None
    if use_crm_context:
        crm_context = rag_service.query_crm_entities(db, current_user.id)
    
    # Generate answer with CRM context and tool results
    if tool_result and tool_result.get("success"):
        # If tool executed successfully, format the result as answer
        answer = format_tool_response(tool_name, tool_result)
    else:
        # Regular RAG answer
        answer = rag_service.generate_answer(query, top_k=top_k, crm_context=crm_context)
    
    # Save assistant message
    assistant_message = ConversationMessage(
        conversation_id=conversation.id,
        role="assistant",
        content=answer,
        metadata=json.dumps({"tool_used": tool_used}) if tool_used else None
    )
    db.add(assistant_message)
    db.commit()
    
    return {
        "query": query,
        "answer": answer,
        "conversation_id": conversation.id,
        "crm_context_used": use_crm_context,
        "tool_used": tool_used,
        "tool_result": tool_result if tool_result else None
    }

@router.get("/conversations", response_model=List[ConversationResponse])
def list_conversations(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all conversations for current user
    """
    conversations = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).order_by(Conversation.updated_at.desc()).offset(skip).limit(limit).all()
    return conversations

@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get conversation by ID with all messages
    """
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation

@router.delete("/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a conversation
    """
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    db.delete(conversation)
    db.commit()
    return {"message": "Conversation deleted successfully"}

@router.get("/analytics")
def get_rag_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get RAG analytics and statistics for current user
    """
    from sqlalchemy import func
    
    # Total conversations
    total_conversations = db.query(func.count(Conversation.id)).filter(
        Conversation.user_id == current_user.id
    ).scalar()
    
    # Total messages
    total_messages = db.query(func.count(ConversationMessage.id)).join(Conversation).filter(
        Conversation.user_id == current_user.id
    ).scalar()
    
    # Messages by role
    user_messages = db.query(func.count(ConversationMessage.id)).join(Conversation).filter(
        Conversation.user_id == current_user.id,
        ConversationMessage.role == "user"
    ).scalar()
    
    assistant_messages = db.query(func.count(ConversationMessage.id)).join(Conversation).filter(
        Conversation.user_id == current_user.id,
        ConversationMessage.role == "assistant"
    ).scalar()
    
    # Recent conversations
    recent_conversations = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).order_by(Conversation.updated_at.desc()).limit(5).all()
    
    return {
        "total_conversations": total_conversations,
        "total_messages": total_messages,
        "user_messages": user_messages,
        "assistant_messages": assistant_messages,
        "recent_conversations": [
            {
                "id": conv.id,
                "title": conv.title,
                "created_at": conv.created_at,
                "updated_at": conv.updated_at,
                "message_count": len(conv.messages)
            } for conv in recent_conversations
        ]
    }

@router.get("/analytics/admin")
def get_admin_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get RAG analytics for all users (Admin only)
    """
    from sqlalchemy import func
    from backend.models.user import UserRole
    
    # Check admin permission
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Total system-wide stats
    total_conversations = db.query(func.count(Conversation.id)).scalar()
    total_messages = db.query(func.count(ConversationMessage.id)).scalar()
    total_users_with_conversations = db.query(func.count(func.distinct(Conversation.user_id))).scalar()
    
    # Most active users
    most_active = db.query(
        User.id,
        User.username,
        User.email,
        func.count(Conversation.id).label("conversation_count")
    ).join(Conversation).group_by(User.id, User.username, User.email).order_by(
        func.count(Conversation.id).desc()
    ).limit(10).all()
    
    return {
        "total_conversations": total_conversations,
        "total_messages": total_messages,
        "total_users_with_conversations": total_users_with_conversations,
        "most_active_users": [
            {
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "conversation_count": user.conversation_count
            } for user in most_active
        ]
    }

@router.post("/query-chunks", response_model=List[str])
def query_chunks(query: str = Form(...), top_k: int = Form(3)):
    """
    Query RAG pipeline and get relevant document chunks (without LLM synthesis)
    """
    rag_service = get_rag_service()
    results = rag_service.query(query, top_k=top_k)
    if not results:
        raise HTTPException(status_code=404, detail="No relevant documents found")
    return results
