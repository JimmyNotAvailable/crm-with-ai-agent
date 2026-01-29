"""
AI Agent Tools for Conversational CRM
Tools that the AI can use to perform actions
"""
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.models.product import Product
from backend.models.order import Order
from backend.models.ticket import Ticket, TicketStatus
from backend.models.user import User
import json


class AgentTools:
    """
    Collection of tools that AI Agent can use
    """
    
    def __init__(self, db: Session, current_user: User):
        self.db = db
        self.current_user = current_user
    
    def lookup_order(self, order_number: str) -> Dict[str, Any]:
        """
        Tool: Lookup order status by order number
        Returns order details including status, items, tracking
        """
        try:
            order = self.db.query(Order).filter(
                Order.order_number == order_number
            ).first()
            
            if not order:
                return {
                    "success": False,
                    "message": f"Không tìm thấy đơn hàng {order_number}"
                }
            
            # Check permission
            if self.current_user.role.value == "CUSTOMER" and int(order.customer_id) != int(self.current_user.id):  # type: ignore
                return {
                    "success": False,
                    "message": "Bạn không có quyền xem đơn hàng này"
                }
            
            return {
                "success": True,
                "order_number": order.order_number,
                "status": order.status.value,
                "total_amount": float(order.total_amount) if order.total_amount else 0.0,  # type: ignore
                "created_at": order.created_at.isoformat(),
                "items_count": len(order.items),
                "shipping_address": f"{order.shipping_address}, {order.shipping_city}",
                "can_cancel": order.can_cancel
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Lỗi tra cứu đơn hàng: {str(e)}"
            }
    
    def recommend_products(self, keyword: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Tool: Search and recommend products based on keyword
        Returns list of matching products
        """
        try:
            query = self.db.query(Product).filter(
                Product.is_active == True
            )
            
            # Search by name, description, or category
            if keyword:
                search_filter = (
                    Product.name.ilike(f"%{keyword}%") |
                    Product.description.ilike(f"%{keyword}%") |
                    Product.category.ilike(f"%{keyword}%")
                )
                query = query.filter(search_filter)
            
            products = query.limit(max_results).all()
            
            if not products:
                return {
                    "success": False,
                    "message": f"Không tìm thấy sản phẩm phù hợp với '{keyword}'"
                }
            
            return {
                "success": True,
                "keyword": keyword,
                "count": len(products),
                "products": [
                    {
                        "id": p.id,
                        "name": p.name,
                        "price": float(p.price) if p.price else 0.0,  # type: ignore
                        "stock": int(p.stock_quantity) if p.stock_quantity else 0,  # type: ignore
                        "category": p.category,
                        "description": (str(p.description)[:100] if p.description else "")  # type: ignore
                    }
                    for p in products
                ]
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Lỗi tìm kiếm sản phẩm: {str(e)}"
            }
    
    def create_support_ticket(self, subject: str, message: str, category: str = "GENERAL_INQUIRY") -> Dict[str, Any]:
        """
        Tool: Create support ticket
        Automatically creates ticket for customer
        """
        try:
            from backend.models.ticket import TicketCategory, TicketMessage, TicketPriority
            from datetime import datetime
            import random
            import string
            
            # Generate ticket number
            timestamp = datetime.now().strftime("%Y%m%d")
            random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            ticket_number = f"TKT-{timestamp}-{random_suffix}"
            
            # Map category string to enum
            category_map = {
                "general": TicketCategory.GENERAL_INQUIRY,
                "order": TicketCategory.ORDER_ISSUE,
                "product": TicketCategory.PRODUCT_QUESTION,
                "complaint": TicketCategory.COMPLAINT,
                "technical": TicketCategory.TECHNICAL_SUPPORT,
                "refund": TicketCategory.REFUND_REQUEST
            }
            
            ticket_category = category_map.get(category.lower(), TicketCategory.GENERAL_INQUIRY)
            
            # Create ticket
            new_ticket = Ticket(
                ticket_number=ticket_number,
                customer_id=self.current_user.id,
                subject=subject,
                category=ticket_category,
                status=TicketStatus.OPEN,
                priority=TicketPriority.MEDIUM,
                channel="CHAT_AI"
            )
            
            self.db.add(new_ticket)
            self.db.flush()
            
            # Add initial message
            initial_message = TicketMessage(
                ticket_id=new_ticket.id,
                sender_id=self.current_user.id,
                is_staff=False,
                is_ai_generated=False,
                message=message
            )
            self.db.add(initial_message)
            self.db.commit()
            
            return {
                "success": True,
                "ticket_number": ticket_number,
                "message": f"Đã tạo ticket hỗ trợ #{ticket_number}. Nhân viên sẽ phản hồi trong 24h."
            }
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"Lỗi tạo ticket: {str(e)}"
            }
    
    def get_my_recent_orders(self, limit: int = 3) -> Dict[str, Any]:
        """
        Tool: Get customer's recent orders
        Returns list of recent orders for current user
        """
        try:
            orders = self.db.query(Order).filter(
                Order.customer_id == self.current_user.id
            ).order_by(Order.created_at.desc()).limit(limit).all()
            
            if not orders:
                return {
                    "success": False,
                    "message": "Bạn chưa có đơn hàng nào"
                }
            
            return {
                "success": True,
                "count": len(orders),
                "orders": [
                    {
                        "order_number": o.order_number,
                        "status": o.status.value,
                        "total": float(o.total_amount) if o.total_amount else 0.0,  # type: ignore
                        "created": o.created_at.isoformat(),
                        "items_count": len(o.items)
                    }
                    for o in orders
                ]
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Lỗi tra cứu đơn hàng: {str(e)}"
            }
    
    def get_available_tools(self) -> List[Dict[str, str]]:
        """
        Return list of available tools for the AI
        """
        return [
            {
                "name": "lookup_order",
                "description": "Tra cứu thông tin đơn hàng theo mã đơn",
                "parameters": "order_number: str"
            },
            {
                "name": "recommend_products",
                "description": "Tìm kiếm và gợi ý sản phẩm theo từ khóa",
                "parameters": "keyword: str, max_results: int"
            },
            {
                "name": "create_support_ticket",
                "description": "Tạo ticket hỗ trợ cho khách hàng",
                "parameters": "subject: str, message: str, category: str"
            },
            {
                "name": "get_my_recent_orders",
                "description": "Xem danh sách đơn hàng gần đây của khách hàng",
                "parameters": "limit: int"
            }
        ]
    
    def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a tool by name with parameters
        """
        tools_map = {
            "lookup_order": self.lookup_order,
            "recommend_products": self.recommend_products,
            "create_support_ticket": self.create_support_ticket,
            "get_my_recent_orders": self.get_my_recent_orders
        }
        
        if tool_name not in tools_map:
            return {
                "success": False,
                "message": f"Tool '{tool_name}' không tồn tại"
            }
        
        try:
            return tools_map[tool_name](**kwargs)
        except Exception as e:
            return {
                "success": False,
                "message": f"Lỗi thực thi tool: {str(e)}"
            }


def detect_intent_and_extract_params(message: str) -> Optional[Dict[str, Any]]:
    """
    Simple intent detection and parameter extraction
    In production, use NLU model (Rasa, DialogFlow, etc.)
    """
    message_lower = message.lower()
    
    # Intent: Lookup order
    if any(keyword in message_lower for keyword in ["đơn hàng", "order", "tra cứu", "kiểm tra đơn"]):
        # Extract order number (pattern: ORD-YYYYMMDD-XXXXXX)
        import re
        order_pattern = r'(ORD-\d{8}-\d{6})'
        match = re.search(order_pattern, message.upper())
        if match:
            return {
                "tool": "lookup_order",
                "params": {"order_number": match.group(1)}
            }
        elif "đơn hàng" in message_lower and "của tôi" in message_lower:
            return {
                "tool": "get_my_recent_orders",
                "params": {"limit": 3}
            }
    
    # Intent: Product search
    if any(keyword in message_lower for keyword in ["tìm", "search", "sản phẩm", "mua", "có bán", "gợi ý"]):
        # Extract product keywords
        exclude_words = ["tôi", "muốn", "cần", "cho", "mua", "sản phẩm", "tìm", "có", "bán", "không"]
        words = message_lower.split()
        keywords = [w for w in words if w not in exclude_words and len(w) > 2]
        
        if keywords:
            return {
                "tool": "recommend_products",
                "params": {"keyword": " ".join(keywords[:3]), "max_results": 5}
            }
    
    # Intent: Create ticket
    if any(keyword in message_lower for keyword in ["khiếu nại", "complaint", "góp ý", "phản ánh", "không hài lòng", "tệ", "kém"]):
        return {
            "tool": "create_support_ticket",
            "params": {
                "subject": message[:100],
                "message": message,
                "category": "complaint"
            }
        }
    
    # Intent: Help/Support
    if any(keyword in message_lower for keyword in ["hỗ trợ", "help", "giúp đỡ", "trợ giúp"]):
        return {
            "tool": "create_support_ticket",
            "params": {
                "subject": "Yêu cầu hỗ trợ",
                "message": message,
                "category": "general"
            }
        }
    
    return None
