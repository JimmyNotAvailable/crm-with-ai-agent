"""
AI Summarization Service (DEPRECATED)

NOTE: This module is deprecated. New code should use:
    from ai_modules.agent_customer_service.summarization.summarizer import ConversationSummarizer

Retained for backward compatibility only.
"""
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.models.ticket import Ticket, TicketMessage
from backend.models.conversation import Conversation, ConversationMessage
from backend.models.user import User
from backend.models.order import Order
import os


class SummarizationService:
    """
    Service for AI-powered summarization
    """
    
    def __init__(self):
        self.demo_mode = os.getenv("DEMO_MODE", "false").lower() == "true"
    
    def summarize_ticket(self, ticket: Ticket, db: Session) -> str:
        """
        Summarize ticket conversation
        Returns concise summary of ticket issue and resolution status
        """
        # Get all messages
        messages = db.query(TicketMessage).filter(
            TicketMessage.ticket_id == ticket.id
        ).order_by(TicketMessage.created_at).all()
        
        if not messages:
            return "Chưa có nội dung trao đổi"
        
        # Extract key info
        customer_messages = [m for m in messages if not getattr(m, 'is_staff', False)]
        staff_messages = [m for m in messages if getattr(m, 'is_staff', False)]
        
        # Build summary
        summary_parts = []
        
        # Issue description from first message
        if customer_messages:
            first_msg = customer_messages[0].message[:200]  # type: ignore
            summary_parts.append(f"**Vấn đề:** {first_msg}...")
        
        # Response count
        summary_parts.append(f"**Trao đổi:** {len(customer_messages)} tin từ khách, {len(staff_messages)} phản hồi nhân viên")
        
        # Status
        summary_parts.append(f"**Trạng thái:** {ticket.status.value}")
        
        # Sentiment
        sentiment_label = getattr(ticket, 'sentiment_label', None)
        if sentiment_label:
            sentiment_emoji = {"POSITIVE": "😊", "NEUTRAL": "😐", "NEGATIVE": "😠"}
            emoji = sentiment_emoji.get(str(sentiment_label), "")
            summary_parts.append(f"**Cảm xúc:** {emoji} {sentiment_label}")
        
        # Use AI for better summary in production
        if not self.demo_mode:
            summary_parts.append("\n[AI Summary would be generated here in production mode]")
        
        return "\n".join(summary_parts)
    
    def summarize_conversation(self, conversation: Conversation, db: Session) -> str:
        """
        Summarize chat conversation
        Returns key topics discussed and actions taken
        """
        messages = db.query(ConversationMessage).filter(
            ConversationMessage.conversation_id == conversation.id
        ).order_by(ConversationMessage.created_at).all()
        
        if not messages:
            return "Chưa có cuộc hội thoại"
        
        # Extract user questions and assistant responses
        user_msgs = [m for m in messages if getattr(m, 'role', '') == "user"]
        assistant_msgs = [m for m in messages if getattr(m, 'role', '') == "assistant"]
        
        summary_parts = []
        summary_parts.append(f"**Tổng số tin nhắn:** {len(messages)} ({len(user_msgs)} từ người dùng)")
        
        # Extract topics from first few messages
        if user_msgs:
            topics = []
            for msg in user_msgs[:3]:
                content = str(msg.content)[:50]  # type: ignore
                topics.append(f"- {content}...")
            
            summary_parts.append(f"\n**Chủ đề chính:**\n" + "\n".join(topics))
        
        # Check if any tools were used
        tool_used_count = sum(1 for m in assistant_msgs if hasattr(m, 'metadata') and m.metadata and 'tool_used' in str(m.metadata))
        if tool_used_count > 0:
            summary_parts.append(f"\n**Hành động AI:** {tool_used_count} công cụ được sử dụng")
        
        return "\n".join(summary_parts)
    
    def summarize_customer_behavior(self, user_id: int, db: Session) -> Dict[str, Any]:
        """
        Summarize customer behavior and patterns
        Returns insights about purchase history, support interactions, preferences
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": "User not found"}
        
        # Get orders
        orders = db.query(Order).filter(Order.customer_id == user_id).all()
        total_orders = len(orders)
        total_spent = sum([float(o.total_amount) for o in orders if o.total_amount])  # type: ignore
        
        # Get tickets
        tickets = db.query(Ticket).filter(Ticket.customer_id == user_id).all()
        total_tickets = len(tickets)
        negative_tickets = sum(1 for t in tickets if getattr(t, 'sentiment_label', None) == "NEGATIVE")
        
        # Get conversations
        conversations = db.query(Conversation).filter(Conversation.user_id == user_id).all()
        total_conversations = len(conversations)
        
        # Build behavior summary
        behavior_summary = {
            "customer_name": user.full_name,
            "customer_email": user.email,
            "total_orders": total_orders,
            "total_spent": total_spent,
            "average_order_value": total_spent / total_orders if total_orders > 0 else 0,
            "total_support_tickets": total_tickets,
            "negative_sentiment_count": negative_tickets,
            "total_chat_conversations": total_conversations,
            "customer_segment": self._classify_customer_segment(total_orders, total_spent, negative_tickets),
            "risk_level": "HIGH" if negative_tickets > 2 else "LOW",
            "engagement_level": "ACTIVE" if total_conversations > 5 else "MODERATE" if total_conversations > 0 else "PASSIVE"
        }
        
        return behavior_summary
    
    def _classify_customer_segment(self, total_orders: int, total_spent: float, negative_tickets: int) -> str:
        """
        Classify customer into segments
        """
        if total_spent > 10000000 and total_orders > 5:
            return "VIP"
        elif total_spent > 5000000 or total_orders > 3:
            return "LOYAL"
        elif total_orders > 0:
            return "REGULAR"
        else:
            return "NEW"
    
    def summarize_ticket_batch(self, ticket_ids: List[int], db: Session) -> List[Dict[str, Any]]:
        """
        Summarize multiple tickets at once
        Useful for dashboard overview
        """
        summaries = []
        
        for ticket_id in ticket_ids:
            ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
            if ticket:
                summary = self.summarize_ticket(ticket, db)
                summaries.append({
                    "ticket_id": ticket_id,
                    "ticket_number": ticket.ticket_number,
                    "summary": summary,
                    "status": ticket.status.value
                })
        
        return summaries
