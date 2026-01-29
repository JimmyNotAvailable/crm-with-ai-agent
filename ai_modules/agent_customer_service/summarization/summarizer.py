"""
Conversation Summarizer - AI-powered conversation summarization
Tóm tắt hội thoại để:
- Lưu trữ context
- Handover cho nhân viên
- Analytics
"""
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
import os

from ai_modules.core.config import ai_config


class ConversationSummarizer:
    """
    AI-powered Conversation Summarizer
    
    Chức năng:
    - Tóm tắt cuộc hội thoại
    - Trích xuất intent chính
    - Xác định action items
    - Phân tích sentiment tổng thể
    """
    
    def __init__(self):
        self.demo_mode = ai_config.demo_mode
        self._init_llm_client()
    
    def _init_llm_client(self):
        """Initialize LLM client"""
        self.llm_client = None
        self.llm_provider = None
        
        if self.demo_mode:
            return
        
        if ai_config.openai_api_key:
            try:
                from openai import OpenAI
                self.llm_client = OpenAI(api_key=ai_config.openai_api_key)
                self.llm_provider = "openai"
            except ImportError:
                pass
    
    def summarize_conversation(
        self, 
        conversation_id: int, 
        db: Session
    ) -> str:
        """
        Summarize a conversation by ID
        
        Args:
            conversation_id: ID of the conversation
            db: Database session
            
        Returns:
            Summary string
        """
        from backend.models.conversation import Conversation, ConversationMessage
        
        # Get conversation
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        
        if not conversation:
            return "Không tìm thấy cuộc hội thoại"
        
        # Get messages
        messages = db.query(ConversationMessage).filter(
            ConversationMessage.conversation_id == conversation_id
        ).order_by(ConversationMessage.created_at).all()
        
        if not messages:
            return "Chưa có nội dung hội thoại"
        
        return self._generate_summary(messages)
    
    def summarize_messages(
        self, 
        messages: List[Dict[str, Any]]
    ) -> str:
        """
        Summarize a list of messages
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            
        Returns:
            Summary string
        """
        if not messages:
            return "Không có tin nhắn để tóm tắt"
        
        return self._generate_summary_from_dicts(messages)
    
    def extract_key_points(
        self, 
        conversation_id: int, 
        db: Session
    ) -> Dict[str, Any]:
        """
        Extract key points from conversation
        
        Args:
            conversation_id: ID of the conversation
            db: Database session
            
        Returns:
            Dict with main_topic, questions, issues, actions
        """
        from backend.models.conversation import ConversationMessage
        
        messages = db.query(ConversationMessage).filter(
            ConversationMessage.conversation_id == conversation_id
        ).order_by(ConversationMessage.created_at).all()
        
        if not messages:
            return {
                "main_topic": "N/A",
                "questions": [],
                "issues": [],
                "action_items": []
            }
        
        # Extract user messages
        user_messages = [m for m in messages if getattr(m, 'role', '') == "user"]
        
        # Simple extraction (can be enhanced with NLP)
        questions = []
        issues = []
        
        for msg in user_messages:
            content = str(getattr(msg, 'content', ''))
            if '?' in content:
                questions.append(content[:100])
            if any(kw in content.lower() for kw in ['lỗi', 'vấn đề', 'không được', 'hỏng']):
                issues.append(content[:100])
        
        # Determine main topic from first user message
        main_topic = "Tư vấn chung"
        if user_messages:
            first_msg = str(getattr(user_messages[0], 'content', ''))[:50]
            main_topic = first_msg
        
        return {
            "main_topic": main_topic,
            "questions": questions[:5],
            "issues": issues[:3],
            "action_items": self._extract_action_items(messages),
            "message_count": len(messages),
            "user_message_count": len(user_messages)
        }
    
    def _generate_summary(self, messages) -> str:
        """Generate summary from message objects"""
        # Convert to text
        conversation_text = []
        for msg in messages:
            role = getattr(msg, 'role', 'unknown')
            content = getattr(msg, 'content', '')
            conversation_text.append(f"{role.upper()}: {content}")
        
        full_text = "\n".join(conversation_text)
        
        if self.demo_mode or not self.llm_client:
            return self._generate_mock_summary(messages)
        
        return self._generate_llm_summary(full_text)
    
    def _generate_summary_from_dicts(self, messages: List[Dict]) -> str:
        """Generate summary from message dicts"""
        conversation_text = []
        for msg in messages:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            conversation_text.append(f"{role.upper()}: {content}")
        
        full_text = "\n".join(conversation_text)
        
        if self.demo_mode or not self.llm_client:
            return self._generate_mock_summary_from_dicts(messages)
        
        return self._generate_llm_summary(full_text)
    
    def _generate_llm_summary(self, conversation_text: str) -> str:
        """Generate summary using LLM"""
        prompt = f"""
Tóm tắt cuộc hội thoại sau một cách ngắn gọn, súc tích:

{conversation_text}

TÓM TẮT (3-5 câu):
"""
        try:
            if self.llm_provider == "openai":
                response = self.llm_client.chat.completions.create(
                    model=ai_config.openai_model,
                    messages=[
                        {"role": "system", "content": "Bạn là trợ lý tóm tắt hội thoại chuyên nghiệp."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=256,
                    temperature=0.5
                )
                return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Lỗi tạo tóm tắt: {str(e)}"
        
        return "Không thể tạo tóm tắt."
    
    def _generate_mock_summary(self, messages) -> str:
        """Generate mock summary for demo mode"""
        user_msgs = [m for m in messages if getattr(m, 'role', '') == "user"]
        assistant_msgs = [m for m in messages if getattr(m, 'role', '') == "assistant"]
        
        summary_parts = [
            "**TÓM TẮT HỘI THOẠI** [DEMO MODE]\n",
            f"- Tổng số tin nhắn: {len(messages)}",
            f"- Tin nhắn khách hàng: {len(user_msgs)}",
            f"- Phản hồi hệ thống: {len(assistant_msgs)}",
        ]
        
        if user_msgs:
            first_topic = str(getattr(user_msgs[0], 'content', ''))[:50]
            summary_parts.append(f"\n**Chủ đề chính:** {first_topic}...")
        
        return "\n".join(summary_parts)
    
    def _generate_mock_summary_from_dicts(self, messages: List[Dict]) -> str:
        """Generate mock summary from message dicts"""
        user_msgs = [m for m in messages if m.get('role') == "user"]
        
        summary_parts = [
            "**TÓM TẮT** [DEMO MODE]\n",
            f"- Tổng số tin nhắn: {len(messages)}",
        ]
        
        if user_msgs:
            first_topic = user_msgs[0].get('content', '')[:50]
            summary_parts.append(f"- Chủ đề: {first_topic}...")
        
        return "\n".join(summary_parts)
    
    def _extract_action_items(self, messages) -> List[str]:
        """Extract action items from conversation"""
        action_items = []
        
        # Look for action keywords in assistant messages
        action_keywords = ['sẽ', 'cần', 'phải', 'nên', 'hãy']
        
        for msg in messages:
            if getattr(msg, 'role', '') == "assistant":
                content = str(getattr(msg, 'content', ''))
                for kw in action_keywords:
                    if kw in content.lower():
                        # Extract sentence containing keyword
                        sentences = content.split('.')
                        for s in sentences:
                            if kw in s.lower() and len(s) > 10:
                                action_items.append(s.strip()[:100])
                                break
        
        return action_items[:5]  # Limit to 5 action items
