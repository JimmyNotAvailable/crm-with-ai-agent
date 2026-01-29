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


class OperationsAgent(BaseAgent):
    """
    Agent 2: Operations Agent
    
    Xử lý các yêu cầu:
    - Tra cứu đơn hàng
    - Tạo/quản lý ticket hỗ trợ
    - Phân tích sentiment tin nhắn
    - Phát hiện ticket trùng lặp
    """
    
    def __init__(self, db: Session, current_user=None):
        super().__init__(db, AgentType.OPERATIONS)
        self.current_user = current_user
        
        # Intent keywords mapping
        self.intent_keywords = {
            "order_lookup": ["đơn hàng", "order", "tra cứu", "kiểm tra đơn", "ORD-"],
            "order_cancel": ["hủy đơn", "cancel order", "bỏ đơn"],
            "order_history": ["lịch sử đơn", "đơn gần đây", "my orders"],
            "ticket_create": ["hỗ trợ", "khiếu nại", "báo cáo", "có vấn đề", "tạo ticket"],
            "ticket_status": ["ticket", "TKT-", "trạng thái ticket"],
        }
    
    def process_query(
        self, 
        query: str, 
        user_id: Optional[int] = None,
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
        
        order = self.db.query(Order).filter(
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
            if int(order.customer_id) != int(self.current_user.id):
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
        
        order = self.db.query(Order).filter(
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
        self.db.commit()
        
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
        
        orders = self.db.query(Order).filter(
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
        """Handle ticket creation"""
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
        
        new_ticket = Ticket(
            ticket_number=ticket_number,
            customer_id=self.current_user.id,
            subject=subject,
            category=TicketCategory.GENERAL_INQUIRY,
            status=TicketStatus.OPEN,
            priority=TicketPriority.MEDIUM,
            channel="CHAT_AI"
        )
        
        self.db.add(new_ticket)
        self.db.commit()
        
        return AgentResponse(
            success=True,
            message=f"✅ Đã tạo ticket hỗ trợ #{ticket_number}. Nhân viên sẽ phản hồi trong 24h.",
            data={"ticket_number": ticket_number},
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
