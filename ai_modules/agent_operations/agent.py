"""
Operations Agent - Main orchestrator for operations tasks
Điều phối các chức năng:
1. Order Management: Tra cứu, hủy đơn
2. Ticket Management: Tạo, xử lý ticket
3. Sentiment Analysis: Phân tích cảm xúc
4. Ticket Deduplication: Phát hiện trùng lặp
"""
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from ai_modules.core.base_agent import BaseAgent, AgentType, AgentResponse
from ai_modules.core.config import ai_config
from ai_modules.sentiment import SentimentAnalyzer
from ai_modules.ticket_deduplication import TicketDeduplicationService


class OperationsAgent(BaseAgent):
    """
    Agent 2: Operations Agent
    
    Xử lý các yêu cầu:
    - Tra cứu đơn hàng
    - Tạo/quản lý ticket hỗ trợ
    - Phân tích sentiment tin nhắn
    - Phát hiện ticket trùng lặp
    """
    
    def __init__(self, db: Session, current_user=None, order_db: Optional[Session] = None):
        """
        Initialize OperationsAgent with multi-DB support.
        
        Args:
            db: Support DB session (primary - tickets, routing, assignments)
            current_user: Current authenticated user
            order_db: Order DB session for order queries. Falls back to db if not provided.
        """
        super().__init__(db, AgentType.OPERATIONS)
        self.current_user = current_user
        self.order_db = order_db or db  # Fallback for backward compatibility
        
        # Initialize sub-services
        self.sentiment_analyzer = SentimentAnalyzer()
        self.dedup_service = TicketDeduplicationService(db)
        
        # Intent keywords mapping
        self.intent_keywords = {
            "order_lookup": ["đơn hàng", "order", "tra cứu", "kiểm tra đơn", "ORD-"],
            "order_cancel": ["hủy đơn", "cancel order", "bỏ đơn"],
            "order_history": ["lịch sử đơn", "đơn gần đây", "my orders"],
            "ticket_create": ["hỗ trợ", "khiếu nại", "báo cáo", "có vấn đề", "tạo ticket"],
            "ticket_status": ["ticket", "TKT-", "trạng thái ticket"],
            "analyze_sentiment": [
                "cảm xúc", "sentiment", "phân tích cảm xúc", "tâm trạng",
                "analyze sentiment", "mood", "cảm nhận"
            ],
            "find_duplicates": [
                "trùng lặp", "duplicate", "trùng", "ticket giống",
                "ticket tương tự", "similar ticket", "gộp ticket", "merge"
            ],
        }
    
    def process_query(
        self, 
        query: str, 
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """
        Process operations query and route to appropriate handler
        """
        query_lower = query.lower()
        
        # Detect intent
        intent = self._detect_intent(query_lower)
        
        try:
            if intent == "order_lookup":
                order_number = self._extract_order_number(query)
                return self._handle_order_lookup(order_number)
            
            elif intent == "order_cancel":
                order_number = self._extract_order_number(query)
                return self._handle_order_cancel(order_number)
            
            elif intent == "order_history":
                return self._handle_order_history(user_id)
            
            elif intent == "ticket_create":
                return self._handle_ticket_create(query, context)
            
            elif intent == "ticket_status":
                ticket_number = self._extract_ticket_number(query)
                return self._handle_ticket_status(ticket_number)
            
            elif intent == "analyze_sentiment":
                return self._handle_analyze_sentiment(query, context)
            
            elif intent == "find_duplicates":
                return self._handle_find_duplicates(query, context)
            
            else:
                return AgentResponse(
                    success=False,
                    message="Không hiểu yêu cầu. Vui lòng thử lại với từ khóa cụ thể hơn.",
                    tool_used=None
                )
                
        except Exception as e:
            return AgentResponse(
                success=False,
                message=f"Lỗi xử lý yêu cầu: {str(e)}",
                tool_used=intent
            )
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tools"""
        return [
            "lookup_order",
            "cancel_order",
            "get_order_history",
            "create_ticket",
            "get_ticket_status",
            "analyze_sentiment",
            "find_duplicate_tickets"
        ]
    
    def _detect_intent(self, query: str) -> str:
        """Detect user intent from query"""
        for intent, keywords in self.intent_keywords.items():
            if any(kw.lower() in query for kw in keywords):
                return intent
        return "unknown"
    
    def _extract_order_number(self, query: str) -> Optional[str]:
        """Extract order number from query"""
        import re
        pattern = r'ORD-\d{8}-[A-Z0-9]+'
        match = re.search(pattern, query.upper())
        return match.group(0) if match else None
    
    def _extract_ticket_number(self, query: str) -> Optional[str]:
        """Extract ticket number from query"""
        import re
        pattern = r'TKT-\d{8}-[A-Z0-9]+'
        match = re.search(pattern, query.upper())
        return match.group(0) if match else None
    
    def _handle_order_lookup(self, order_number: Optional[str]) -> AgentResponse:
        """Handle order lookup"""
        if not order_number:
            return AgentResponse(
                success=False,
                message="Vui lòng cung cấp mã đơn hàng (VD: ORD-20250128-001)",
                tool_used="lookup_order"
            )
        
        from backend.models.order import Order
        
        order = self.order_db.query(Order).filter(
            Order.order_number == order_number
        ).first()
        
        if not order:
            return AgentResponse(
                success=False,
                message=f"Không tìm thấy đơn hàng {order_number}",
                tool_used="lookup_order"
            )
        
        # Check permission
        if self.current_user and self.current_user.role.value == "CUSTOMER":
            if str(order.customer_id) != str(self.current_user.id):
                return AgentResponse(
                    success=False,
                    message="Bạn không có quyền xem đơn hàng này",
                    tool_used="lookup_order"
                )
        
        order_data = {
            "order_number": order.order_number,
            "status": order.status.value,
            "total_amount": float(order.total_amount) if order.total_amount else 0,
            "created_at": order.created_at.isoformat(),
            "items_count": len(order.items),
            "can_cancel": order.can_cancel
        }
        
        message = self._format_order_response(order_data)
        
        return AgentResponse(
            success=True,
            message=message,
            data=order_data,
            tool_used="lookup_order"
        )
    
    def _handle_order_cancel(self, order_number: Optional[str]) -> AgentResponse:
        """Handle order cancellation"""
        if not order_number:
            return AgentResponse(
                success=False,
                message="Vui lòng cung cấp mã đơn hàng cần hủy",
                tool_used="cancel_order"
            )
        
        from backend.models.order import Order, OrderStatus
        
        order = self.order_db.query(Order).filter(
            Order.order_number == order_number
        ).first()
        
        if not order:
            return AgentResponse(
                success=False,
                message=f"Không tìm thấy đơn hàng {order_number}",
                tool_used="cancel_order"
            )
        
        if not order.can_cancel:
            return AgentResponse(
                success=False,
                message=f"Đơn hàng {order_number} không thể hủy (trạng thái: {order.status.value})",
                tool_used="cancel_order"
            )
        
        # Cancel order
        order.status = OrderStatus.CANCELLED
        self.order_db.commit()
        
        return AgentResponse(
            success=True,
            message=f"✅ Đã hủy đơn hàng {order_number} thành công",
            data={"order_number": order_number, "new_status": "CANCELLED"},
            tool_used="cancel_order"
        )
    
    def _handle_order_history(self, user_id: Optional[int]) -> AgentResponse:
        """Handle order history request"""
        if not user_id and self.current_user:
            user_id = self.current_user.id
        
        if not user_id:
            return AgentResponse(
                success=False,
                message="Cần đăng nhập để xem lịch sử đơn hàng",
                tool_used="get_order_history"
            )
        
        from backend.models.order import Order
        
        orders = self.order_db.query(Order).filter(
            Order.customer_id == user_id
        ).order_by(Order.created_at.desc()).limit(5).all()
        
        if not orders:
            return AgentResponse(
                success=True,
                message="Bạn chưa có đơn hàng nào",
                data={"orders": []},
                tool_used="get_order_history"
            )
        
        orders_data = [
            {
                "order_number": o.order_number,
                "status": o.status.value,
                "total": float(o.total_amount) if o.total_amount else 0,
                "created": o.created_at.isoformat()
            }
            for o in orders
        ]
        
        message = self._format_orders_list(orders_data)
        
        return AgentResponse(
            success=True,
            message=message,
            data={"orders": orders_data},
            tool_used="get_order_history"
        )
    
    def _handle_ticket_create(
        self, 
        query: str, 
        context: Optional[Dict[str, Any]]
    ) -> AgentResponse:
        """Handle ticket creation with auto-routing and sentiment analysis"""
        if not self.current_user:
            return AgentResponse(
                success=False,
                message="Cần đăng nhập để tạo ticket hỗ trợ",
                tool_used="create_ticket"
            )
        
        from backend.models.ticket import Ticket, TicketStatus, TicketCategory, TicketPriority
        from datetime import datetime
        import random
        import string
        
        # Generate ticket number
        timestamp = datetime.now().strftime("%Y%m%d")
        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        ticket_number = f"TKT-{timestamp}-{random_suffix}"
        
        # Create ticket
        subject = context.get("subject", query[:50]) if context else query[:50]
        
        # Analyze sentiment on the query/subject
        sentiment_result = self.sentiment_analyzer.analyze_text(query)
        
        # Auto-detect priority from sentiment
        initial_priority = TicketPriority.MEDIUM
        if sentiment_result.score < -0.5:
            initial_priority = TicketPriority.HIGH
        elif sentiment_result.score < -0.7:
            initial_priority = TicketPriority.URGENT
        
        new_ticket = Ticket(
            ticket_number=ticket_number,
            customer_id=str(self.current_user.id),
            subject=subject,
            category=TicketCategory.GENERAL_INQUIRY,
            status=TicketStatus.OPEN,
            priority=initial_priority,
            channel="CHAT_AI",
            sentiment_score=sentiment_result.score,
            sentiment_label=sentiment_result.label.value
        )
        
        self.db.add(new_ticket)
        self.db.flush()  # Get ID before routing
        
        # Auto-route ticket
        routing_info = None
        try:
            from backend.services.ticket_routing import TicketRoutingService
            routing_service = TicketRoutingService(self.db)
            routing_info = routing_service.route_ticket(new_ticket)
        except Exception as e:
            # Routing failure should not block ticket creation
            print(f"[OperationsAgent] Auto-routing failed (non-blocking): {e}")
        
        self.db.commit()
        
        # Build response message
        message = f"✅ Đã tạo ticket hỗ trợ **#{ticket_number}**. Nhân viên sẽ phản hồi trong 24h."
        
        if routing_info and routing_info.get("routed"):
            rule = routing_info.get("matched_rule", {})
            actions = routing_info.get("actions_applied", {})
            route_details = []
            if "queue" in actions:
                route_details.append(f"Queue: {actions['queue']}")
            if "priority" in actions:
                route_details.append(f"Priority: {actions['priority']}")
            if route_details:
                message += f"\n📋 Auto-routed: {', '.join(route_details)}"
        
        sentiment_emoji = {"POSITIVE": "😊", "NEUTRAL": "😐", "NEGATIVE": "😟"}
        message += f"\n📊 Sentiment: {sentiment_emoji.get(sentiment_result.label.value, '😐')} {sentiment_result.label.value}"
        
        return AgentResponse(
            success=True,
            message=message,
            data={
                "ticket_number": ticket_number,
                "sentiment": sentiment_result.to_dict(),
                "routing": routing_info
            },
            tool_used="create_ticket"
        )
    
    def _handle_ticket_status(self, ticket_number: Optional[str]) -> AgentResponse:
        """Handle ticket status inquiry"""
        if not ticket_number:
            return AgentResponse(
                success=False,
                message="Vui lòng cung cấp mã ticket (VD: TKT-20250128-ABC123)",
                tool_used="get_ticket_status"
            )
        
        from backend.models.ticket import Ticket
        
        ticket = self.db.query(Ticket).filter(
            Ticket.ticket_number == ticket_number
        ).first()
        
        if not ticket:
            return AgentResponse(
                success=False,
                message=f"Không tìm thấy ticket {ticket_number}",
                tool_used="get_ticket_status"
            )
        
        ticket_data = {
            "ticket_number": ticket.ticket_number,
            "subject": ticket.subject,
            "status": ticket.status.value,
            "priority": ticket.priority.value if ticket.priority else "MEDIUM",
            "created_at": ticket.created_at.isoformat()
        }
        
        return AgentResponse(
            success=True,
            message=f"🎫 Ticket {ticket_number}\n• Trạng thái: {ticket.status.value}\n• Tiêu đề: {ticket.subject}",
            data=ticket_data,
            tool_used="get_ticket_status"
        )
    
    def _handle_analyze_sentiment(
        self,
        query: str,
        context: Optional[Dict[str, Any]]
    ) -> AgentResponse:
        """Handle sentiment analysis request"""
        # Check if ticket_id or text is provided via context
        ticket_id = context.get("ticket_id") if context else None
        text_to_analyze = context.get("text") if context else None

        if ticket_id:
            # Analyze entire ticket
            result = self.sentiment_analyzer.analyze_ticket(ticket_id, db=self.db)
            if "error" in result:
                return AgentResponse(
                    success=False,
                    message=result["error"],
                    tool_used="analyze_sentiment"
                )

            overall = result["overall_sentiment"]
            trend = result.get("trend", "stable")
            trend_emoji = {"improving": "📈", "declining": "📉", "stable": "➡️"}.get(trend, "➡️")

            message = (
                f"📊 **Phân tích cảm xúc Ticket #{result.get('ticket_number', ticket_id)}**\n\n"
                f"• Sentiment: {overall['label']} (score: {overall['score']:.2f})\n"
                f"• Xu hướng: {trend_emoji} {trend}\n"
                f"• Tin nhắn KH: {result.get('customer_message_count', 0)}/{result.get('message_count', 0)}"
            )
            return AgentResponse(
                success=True,
                message=message,
                data=result,
                tool_used="analyze_sentiment",
                confidence=overall.get("confidence", 0.8)
            )

        # Analyze the query text itself (or provided text)
        text = text_to_analyze or query
        # Remove the intent trigger keywords from text if analyzing query directly
        if not text_to_analyze:
            for kw in self.intent_keywords.get("analyze_sentiment", []):
                text = text.replace(kw, "").strip()

        if not text:
            return AgentResponse(
                success=False,
                message="Vui lòng cung cấp nội dung cần phân tích cảm xúc.",
                tool_used="analyze_sentiment"
            )

        result = self.sentiment_analyzer.analyze_text(text)
        label_emoji = {
            "POSITIVE": "😊",
            "NEUTRAL": "😐",
            "NEGATIVE": "😟"
        }.get(result.label.value, "😐")

        message = (
            f"📊 **Phân tích cảm xúc:**\n\n"
            f"{label_emoji} Kết quả: **{result.label.value}** (score: {result.score:.2f})\n"
            f"• Độ tin cậy: {result.confidence:.1%}\n"
            f"• Provider: {result.provider}"
        )

        if result.emotions:
            emotions_text = ", ".join(
                f"{k}: {v:.1%}" for k, v in result.emotions.items() if v > 0
            )
            if emotions_text:
                message += f"\n• Cảm xúc chi tiết: {emotions_text}"

        return AgentResponse(
            success=True,
            message=message,
            data=result.to_dict(),
            tool_used="analyze_sentiment",
            confidence=result.confidence
        )

    def _handle_find_duplicates(
        self,
        query: str,
        context: Optional[Dict[str, Any]]
    ) -> AgentResponse:
        """Handle ticket deduplication request"""
        ticket_id = context.get("ticket_id") if context else None

        if ticket_id:
            # Find duplicates for a specific ticket
            similar = self.dedup_service.find_similar_tickets(
                ticket_id=ticket_id,
                similarity_threshold=0.7,
                time_window_hours=72
            )

            if not similar:
                return AgentResponse(
                    success=True,
                    message=f"✅ Không tìm thấy ticket trùng lặp với ticket {ticket_id}",
                    data={"ticket_id": ticket_id, "duplicates": []},
                    tool_used="find_duplicate_tickets"
                )

            duplicates_data = []
            lines = [f"🔍 **Tìm thấy {len(similar)} ticket tương tự:**\n"]
            for ticket, score in similar:
                dup_info = {
                    "ticket_id": ticket.id,
                    "ticket_number": getattr(ticket, "ticket_number", "N/A"),
                    "subject": getattr(ticket, "subject", "N/A"),
                    "similarity": round(score, 2)
                }
                duplicates_data.append(dup_info)
                lines.append(
                    f"• **{dup_info['ticket_number']}** - {dup_info['subject'][:40]}\n"
                    f"  Độ tương đồng: {score:.0%}"
                )

            lines.append("\n💡 Bạn có thể yêu cầu gộp các ticket trùng lặp.")

            return AgentResponse(
                success=True,
                message="\n".join(lines),
                data={"ticket_id": ticket_id, "duplicates": duplicates_data},
                tool_used="find_duplicate_tickets"
            )

        # Auto-detect duplicates across all open tickets
        try:
            all_dups = self.dedup_service.auto_detect_duplicates(
                similarity_threshold=0.8,
                time_window_hours=24
            )
        except Exception as e:
            return AgentResponse(
                success=False,
                message=f"Lỗi phát hiện ticket trùng lặp: {str(e)}",
                tool_used="find_duplicate_tickets"
            )

        if not all_dups:
            return AgentResponse(
                success=True,
                message="✅ Không phát hiện ticket trùng lặp trong hệ thống.",
                data={"groups": []},
                tool_used="find_duplicate_tickets"
            )

        groups_data = []
        lines = [f"🔍 **Phát hiện {len(all_dups)} nhóm ticket có thể trùng lặp:**\n"]
        for i, (tid, dups) in enumerate(all_dups, 1):
            group = {
                "primary_ticket_id": tid,
                "duplicates": [{"id": d_id, "similarity": round(s, 2)} for d_id, s in dups]
            }
            groups_data.append(group)
            dup_ids = ", ".join(str(d_id)[:8] for d_id, _ in dups)
            lines.append(f"{i}. Ticket {str(tid)[:8]}... → trùng với: {dup_ids}")

        lines.append("\n💡 Sử dụng chức năng gộp ticket để xử lý.")

        return AgentResponse(
            success=True,
            message="\n".join(lines),
            data={"groups": groups_data},
            tool_used="find_duplicate_tickets"
        )

    def _format_order_response(self, order: Dict) -> str:
        """Format order data as readable message"""
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

{'💡 Bạn có thể hủy đơn hàng này.' if order['can_cancel'] else ''}"""
    
    def _format_orders_list(self, orders: List[Dict]) -> str:
        """Format orders list as readable message"""
        lines = [f"📋 **{len(orders)} đơn hàng gần nhất:**\n"]
        
        status_emoji = {
            "PENDING": "⏳",
            "CONFIRMED": "✅",
            "SHIPPED": "🚚",
            "DELIVERED": "📦",
            "CANCELLED": "❌"
        }
        
        for o in orders:
            emoji = status_emoji.get(o['status'], "📋")
            lines.append(f"{emoji} **{o['order_number']}** - {o['total']:,.0f} VNĐ")
            lines.append(f"   Trạng thái: {o['status']} | Ngày: {o['created'][:10]}")
            lines.append("")
        
        return "\n".join(lines)
