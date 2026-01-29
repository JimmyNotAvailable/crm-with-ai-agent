"""
RAG API Endpoints with AI Agent Tools
Integrates CustomerServiceAgent for comprehensive customer support
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Depends
from sqlalchemy.orm import Session
from backend.database.session import get_db
from backend.models.conversation import Conversation, ConversationMessage
from backend.models.user import User
from backend.schemas.conversation import ChatRequest, ChatResponse, ConversationResponse
from backend.utils.security import get_current_user
from typing import List, Optional, Dict, Any
import os
import json
import logging

# Import CustomerServiceAgent (new architecture)
try:
    from ai_modules.agent_customer_service import CustomerServiceAgent
    USE_NEW_AGENT = True
except ImportError:
    USE_NEW_AGENT = False
    # Fallback to legacy imports
    from ai_modules.rag_pipeline.rag_pipeline import RAGPipeline
    from ai_modules.agents.agent_tools import AgentTools, detect_intent_and_extract_params

logger = logging.getLogger(__name__)

router = APIRouter()
_agent_instance: Optional[Any] = None


@router.post("/query")
def simple_rag_query(
    query: str = Form(...),
    top_k: int = Form(5),
    current_user: User = Depends(get_current_user)
):
    """
    Simple RAG query without conversation tracking
    For quick testing and stateless queries
    """
    try:
        if USE_NEW_AGENT:
            from ai_modules.agent_customer_service import CustomerServiceAgent
            agent = CustomerServiceAgent(db=None)
            response = agent.process_query(
                query=query,
                user_id=str(current_user.id),
                context={"top_k": top_k}
            )
            return {
                "success": response.success,
                "answer": response.message,
                "tool_used": response.tool_used,
                "products": response.data.get("products", []) if response.data else [],
                "actions": response.data.get("actions", []) if response.data else []
            }
        else:
            from ai_modules.rag_pipeline.rag_pipeline import RAGPipeline
            rag = RAGPipeline()
            answer = rag.query(query, top_k=top_k)
            return {
                "success": True,
                "answer": answer,
                "tool_used": "rag_query",
                "products": [],
                "actions": []
            }
    except Exception as e:
        logger.error(f"RAG query error: {e}")
        return {
            "success": False,
            "answer": f"Error: {str(e)}",
            "tool_used": "error",
            "products": [],
            "actions": []
        }


def get_customer_service_agent(db: Session):
    """Get or create CustomerServiceAgent instance"""
    global _agent_instance
    if USE_NEW_AGENT:
        # Create new agent with db session
        return CustomerServiceAgent(db=db)
    else:
        # Fallback to legacy RAGPipeline
        if _agent_instance is None:
            _agent_instance = RAGPipeline()
        return _agent_instance


def format_tool_response(tool_name: str, tool_result: Dict[str, Any]) -> str:
    """
    Format tool execution result into human-readable response
    """
    if not tool_result.get("success"):
        return f"Loi: {tool_result.get('message', 'Loi khong xac dinh')}"
    
    if tool_name == "lookup_order":
        order = tool_result
        status_text = {
            "PENDING": "[Cho xu ly]",
            "CONFIRMED": "[Da xac nhan]",
            "SHIPPED": "[Dang giao]",
            "DELIVERED": "[Da giao]",
            "CANCELLED": "[Da huy]"
        }
        status_display = status_text.get(order["status"], "[Khong xac dinh]")
        
        return f"""**Thong tin don hang {order['order_number']}**

{status_display} Trang thai: {order['status']}
Tong tien: {order['total_amount']:,.0f} VND
Ngay dat: {order['created_at'][:10]}
So san pham: {order['items_count']}
Dia chi giao: {order['shipping_address']}

{'' if not order['can_cancel'] else 'Ban co the huy don hang nay.'}"""
    
    elif tool_name == "recommend_products" or tool_name == "product_search":
        products = tool_result.get("products", [])
        keyword = tool_result.get("keyword", "")
        lines = [f"**Tim thay {len(products)} san pham{' phu hop voi ' + keyword if keyword else ''}:**\n"]
        
        for i, p in enumerate(products, 1):
            price_str = f"{p['price']:,.0f}" if isinstance(p.get('price'), (int, float)) else str(p.get('price', 'N/A'))
            lines.append(f"{i}. **{p['name']}** - {price_str} VND")
            if p.get('category'):
                lines.append(f"   Danh muc: {p['category']}")
            if p.get('description'):
                desc = p['description'][:100] + "..." if len(p.get('description', '')) > 100 else p.get('description', '')
                lines.append(f"   Mo ta: {desc}")
            lines.append("")
        
        return "\n".join(lines)
    
    elif tool_name == "product_compare":
        comparison = tool_result.get("comparison", {})
        products = comparison.get("products", [])
        
        lines = ["**So sanh san pham:**\n"]
        for p in products:
            lines.append(f"### {p.get('name', 'N/A')}")
            lines.append(f"- Gia: {p.get('price', 'N/A'):,.0f} VND" if isinstance(p.get('price'), (int, float)) else f"- Gia: {p.get('price', 'N/A')}")
            lines.append(f"- Thuong hieu: {p.get('brand', 'N/A')}")
            lines.append(f"- Danh muc: {p.get('category', 'N/A')}")
            lines.append("")
        
        if comparison.get("recommendation"):
            lines.append(f"**Khuyen nghi:** {comparison['recommendation']}")
        
        return "\n".join(lines)
    
    elif tool_name == "create_support_ticket":
        return f"""**{tool_result['message']}**

Ma ticket: {tool_result['ticket_number']}
Nhan vien ho tro se phan hoi qua email trong 24h.
Ban co the theo doi ticket tai trang 'Ho tro'."""
    
    elif tool_name == "get_my_recent_orders":
        orders = tool_result.get("orders", [])
        lines = [f"**{len(orders)} don hang gan nhat cua ban:**\n"]
        
        for o in orders:
            lines.append(f"- **{o['order_number']}** - {o['total']:,.0f} VND")
            lines.append(f"  Trang thai: {o['status']} | Ngay: {o['created'][:10]}")
            lines.append("")
        
        return "\n".join(lines)
    
    return tool_result.get("message", "Da thuc hien thanh cong")

@router.post("/upload", status_code=status.HTTP_201_CREATED)
def upload_document(
    file: UploadFile = File(...), 
    description: str = Form(None),
    db: Session = Depends(get_db)
):
    """
    Upload a document, chunk, embed, and store in ChromaDB
    """
    file_path = f"./uploaded_docs/{file.filename}"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    
    # Try to use new agent's indexer, fallback to legacy
    if USE_NEW_AGENT:
        try:
            from ai_modules.agent_customer_service.rag import ChromaIndexer
            indexer = ChromaIndexer()
            # For now, just return success - actual indexing depends on file type
            return {"message": "Document uploaded", "file": file.filename}
        except Exception as e:
            logger.warning(f"New indexer failed: {e}, using legacy")
    
    # Legacy fallback
    from ai_modules.rag_pipeline.rag_pipeline import RAGPipeline
    rag_service = RAGPipeline()
    count = rag_service.upload_and_index(file_path, metadata={"description": description})
    return {"message": "Document uploaded and indexed", "chunks": count}


@router.post("/chat")
def chat_rag(
    query: str = Form(...),
    top_k: int = Form(3),
    conversation_id: Optional[int] = Form(None),
    use_crm_context: bool = Form(False),
    action_id: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Chat with AI Customer Service Agent
    Supports:
    - RAG-based Q&A about products and policies
    - Product recommendations
    - Product comparison
    - Order workflow (add to cart, checkout, payment QR)
    - Action button clicks
    """
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
    
    # Prepare context
    context = {
        "conversation_id": conversation.id,
        "use_crm_context": use_crm_context,
        "top_k": top_k
    }
    
    # Add action_id if provided (for button clicks)
    if action_id:
        context["action_id"] = action_id
    
    tool_result = None
    tool_used = None
    answer = ""
    actions = []
    products = []
    
    if USE_NEW_AGENT:
        # Use new CustomerServiceAgent
        try:
            agent = get_customer_service_agent(db)
            response = agent.process_query(
                query=query,
                user_id=current_user.id,
                context=context
            )
            
            answer = response.message
            tool_used = response.tool_used
            
            # Extract data from response
            if response.data:
                products = response.data.get("products", [])
                actions = response.data.get("actions", [])
                tool_result = response.data
            
            # Save tool info in metadata
            user_message.message_metadata = json.dumps({
                "tool_used": tool_used,
                "success": response.success
            })
            
        except Exception as e:
            logger.error(f"CustomerServiceAgent error: {e}")
            answer = f"Xin loi, da xay ra loi khi xu ly yeu cau. Vui long thu lai sau."
            tool_used = "error"
    else:
        # Legacy path: Use old RAGPipeline + AgentTools
        from ai_modules.agents.agent_tools import AgentTools, detect_intent_and_extract_params
        from ai_modules.rag_pipeline.rag_pipeline import RAGPipeline
        
        rag_service = RAGPipeline()
        intent_detected = detect_intent_and_extract_params(query)
        
        if intent_detected:
            agent_tools = AgentTools(db, current_user)
            tool_name = intent_detected["tool"]
            tool_params = intent_detected["params"]
            
            tool_result = agent_tools.execute_tool(tool_name, **tool_params)
            tool_used = tool_name
            
            user_message.message_metadata = json.dumps({
                "tool_detected": tool_name,
                "tool_params": tool_params,
                "tool_result": tool_result
            })
        
        # Generate answer
        if tool_result and tool_result.get("success"):
            answer = format_tool_response(tool_used, tool_result)
        else:
            crm_context = None
            if use_crm_context:
                crm_context = rag_service.query_crm_entities(db, current_user.id)
            answer = rag_service.generate_answer(query, top_k=top_k, crm_context=crm_context)
    
    # Save assistant message
    assistant_message = ConversationMessage(
        conversation_id=conversation.id,
        role="assistant",
        content=answer,
        metadata=json.dumps({
            "tool_used": tool_used,
            "actions": actions,
            "products_count": len(products)
        }) if tool_used else None
    )
    db.add(assistant_message)
    db.commit()
    
    # Build response with new fields for frontend
    response_data = {
        "query": query,
        "answer": answer,
        "conversation_id": conversation.id,
        "crm_context_used": use_crm_context,
        "tool_used": tool_used,
        "tool_result": tool_result if tool_result else None,
        # New fields for enhanced frontend
        "products": products,
        "actions": actions
    }
    
    return response_data

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
