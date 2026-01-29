"""
Customer Service Agent - Main orchestrator
Điều phối các chức năng:
1. RAG: Tư vấn theo KB, chính sách, FAQ
2. Recommendation: Gợi ý sản phẩm ML
3. Summarization: Tóm tắt hội thoại
4. Order Workflow: Đặt hàng, thanh toán QR
5. Chat Actions: Buttons cho các thao tác nhanh
"""
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from ai_modules.core.base_agent import BaseAgent, AgentType, AgentResponse
from ai_modules.core.config import ai_config
from .rag import RAGService
from .recommendation import ProductRecommender
from .summarization import ConversationSummarizer
from .order_workflow import OrderWorkflowManager, OrderState, ChatAction


class CustomerServiceAgent(BaseAgent):
    """
    Agent 1: Customer Service Agent
    
    Xử lý các yêu cầu:
    - Hỏi đáp về sản phẩm, chính sách, FAQ
    - Gợi ý sản phẩm phù hợp
    - Tóm tắt cuộc hội thoại
    - Đặt hàng và thanh toán trong chat
    - Actions: khiếu nại, gặp nhân viên, tra cứu đơn
    """
    
    # Mapping conversation_id -> OrderWorkflowManager
    _order_workflows: Dict[int, OrderWorkflowManager] = {}
    
    def __init__(self, db: Session):
        super().__init__(db, AgentType.CUSTOMER_SERVICE)
        
        # Initialize sub-services
        self.rag_service = RAGService()
        self.recommender = ProductRecommender(db)
        self.summarizer = ConversationSummarizer()
        
        # Intent keywords mapping
        self.intent_keywords = {
            "rag_query": ["chính sách", "policy", "hướng dẫn", "faq", "làm sao", "thế nào", "là gì"],
            "product_recommend": ["gợi ý", "recommend", "phù hợp", "tốt nhất", "nên mua", "đề xuất"],
            "product_search": ["tìm", "search", "có bán", "giá", "sản phẩm"],
            "product_compare": ["so sánh", "compare", "khác gì", "khác nhau", "hơn", "thua", "vs", "hay", "hoặc", "chọn cái nào", "nên chọn"],
            "summarize": ["tóm tắt", "summary", "tổng kết"],
            "order": ["đặt hàng", "mua", "order", "đặt mua", "thêm vào giỏ", "mua ngay"],
            "payment": ["thanh toán", "chuyển khoản", "payment", "trả tiền"],
            "track_order": ["tra cứu đơn", "đơn hàng", "kiểm tra đơn", "theo dõi đơn"],
            "complaint": ["khiếu nại", "phản ánh", "không hài lòng", "lỗi", "hỏng"],
            "support": ["gặp nhân viên", "hỗ trợ", "tư vấn viên", "support", "liên hệ"]
        }
    
    def process_query(
        self, 
        query: str, 
        user_id: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """
        Process customer query and route to appropriate service
        """
        query_lower = query.lower()
        context = context or {}
        
        # Check for action button click
        if context.get("action_id"):
            return self._handle_action(context["action_id"], user_id, context)
        
        # Detect intent
        intent = self._detect_intent(query_lower)
        
        try:
            if intent == "product_recommend":
                return self._handle_recommendation(query, user_id, context)
            elif intent == "product_compare":
                return self._handle_product_compare(query, user_id, context)
            elif intent == "summarize":
                return self._handle_summarization(context)
            elif intent == "order":
                return self._handle_order_intent(query, user_id, context)
            elif intent == "payment":
                return self._handle_payment_intent(user_id, context)
            elif intent == "track_order":
                return self._handle_track_order(query, user_id, context)
            elif intent == "complaint":
                return self._handle_complaint(query, user_id, context)
            elif intent == "support":
                return self._handle_support_request(user_id, context)
            else:
                # Default: RAG query for product/policy info
                return self._handle_rag_query(query, user_id, context)
                
        except Exception as e:
            return AgentResponse(
                success=False,
                message=f"Lỗi xử lý yêu cầu: {str(e)}",
                tool_used=intent,
                data={"actions": self._get_error_actions()}
            )
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tools"""
        return [
            "rag_query",              # Hỏi đáp KB/Policy
            "product_search",         # Tìm kiếm sản phẩm
            "product_recommend",      # Gợi ý sản phẩm
            "summarize_conversation", # Tóm tắt hội thoại
            "start_order",            # Bắt đầu đặt hàng
            "add_to_cart",           # Thêm sản phẩm vào giỏ
            "checkout",              # Thanh toán
            "create_ticket",         # Tạo ticket hỗ trợ
            "contact_staff"          # Gặp nhân viên
        ]
    
    def _detect_intent(self, query: str) -> str:
        """Detect user intent from query"""
        for intent, keywords in self.intent_keywords.items():
            if any(kw in query for kw in keywords):
                return intent
        return "rag_query"  # Default intent
    
    def _handle_rag_query(
        self, 
        query: str, 
        user_id: Optional[int],
        context: Optional[Dict[str, Any]]
    ) -> AgentResponse:
        """Handle RAG-based Q&A"""
        # Get category from context if available
        category = context.get("category") if context else None
        
        result = self.rag_service.query(
            question=query,
            category=category,
            top_k_policy=4,
            top_k_product=6
        )
        
        # Add suggested actions after RAG response
        actions = [
            {"action_id": "order_product", "label": "Đặt hàng", "type": "button"},
            {"action_id": "more_info", "label": "Thêm thông tin", "type": "button"},
            {"action_id": "contact_support", "label": "Hỗ trợ", "type": "button"}
        ]
        
        return AgentResponse(
            success=True,
            message=result["answer"],
            sources=result.get("sources"),
            tool_used="rag_query",
            confidence=result.get("confidence", 0.8),
            data={"actions": actions}
        )
    
    def _handle_product_compare(
        self, 
        query: str, 
        user_id: Optional[int],
        context: Optional[Dict[str, Any]]
    ) -> AgentResponse:
        """Handle product comparison requests"""
        # Extract product names from query
        product_names = self._extract_product_names_for_compare(query)
        
        if len(product_names) < 2:
            # Try to get more products from context or use RAG to find similar
            result = self.rag_service.compare_products(
                query=query,
                product_names=product_names,
                category=context.get("category") if context else None
            )
        else:
            result = self.rag_service.compare_products(
                query=query,
                product_names=product_names,
                category=context.get("category") if context else None
            )
        
        if not result.get("products"):
            return AgentResponse(
                success=False,
                message="Không tìm thấy sản phẩm để so sánh. Vui lòng cho biết tên cụ thể hơn.",
                tool_used="product_compare",
                data={"actions": [
                    {"action_id": "browse_products", "label": "Xem sản phẩm", "type": "button"},
                    {"action_id": "contact_support", "label": "Hỗ trợ tư vấn", "type": "button"}
                ]}
            )
        
        # Build actions for each compared product
        actions = []
        for p in result.get("products", [])[:3]:
            actions.append({
                "action_id": f"order_product_{p.get('id', '')}",
                "label": f"Đặt {p.get('name', '')[:15]}...",
                "type": "button",
                "data": {"product_id": p.get("id")}
            })
        actions.append({"action_id": "contact_support", "label": "Tư vấn thêm", "type": "button"})
        
        return AgentResponse(
            success=True,
            message=result["comparison"],
            tool_used="product_compare",
            data={
                "products": result.get("products", []),
                "comparison_table": result.get("comparison_table"),
                "actions": actions
            },
            confidence=result.get("confidence", 0.8)
        )
    
    def _extract_product_names_for_compare(self, query: str) -> List[str]:
        """Extract product names mentioned in comparison query"""
        import re
        
        # Common comparison patterns
        # "so sánh A và B", "A hay B", "A hoặc B", "A vs B", "A với B"
        patterns = [
            r'so sánh\s+(.+?)\s+(?:và|với|hay|hoặc|vs)\s+(.+?)(?:\s|$|\.|\?)',
            r'(.+?)\s+(?:và|với|hay|hoặc|vs)\s+(.+?)\s+(?:khác|hơn|thua|cái nào)',
            r'(?:nên chọn|chọn)\s+(.+?)\s+(?:hay|hoặc)\s+(.+?)(?:\s|$|\.|\?)',
            r'(.+?)\s+hay\s+(.+?)\s+(?:tốt hơn|rẻ hơn|đáng mua)',
        ]
        
        product_names = []
        query_lower = query.lower()
        
        for pattern in patterns:
            match = re.search(pattern, query_lower, re.IGNORECASE)
            if match:
                for g in match.groups():
                    name = g.strip()
                    # Clean up common words
                    for word in ['cái', 'chiếc', 'con', 'bộ', 'sản phẩm']:
                        name = name.replace(word, '').strip()
                    if name and len(name) > 2:
                        product_names.append(name)
                break
        
        # If no pattern matched, try to extract known product keywords
        if not product_names:
            # Look for product indicators
            keywords = ['iphone', 'samsung', 'macbook', 'laptop', 'điện thoại', 'tablet', 
                       'airpods', 'galaxy', 'xiaomi', 'oppo', 'realme', 'asus', 'dell', 'hp']
            for kw in keywords:
                if kw in query_lower:
                    # Extract the full product name context
                    idx = query_lower.find(kw)
                    # Get surrounding context
                    start = max(0, idx - 5)
                    end = min(len(query), idx + len(kw) + 15)
                    snippet = query[start:end].strip()
                    product_names.append(snippet)
        
        return list(set(product_names))[:5]  # Max 5 products to compare
    
    def _handle_recommendation(
        self, 
        query: str, 
        user_id: Optional[int],
        context: Optional[Dict[str, Any]]
    ) -> AgentResponse:
        """Handle product recommendation"""
        # Extract preferences from query
        preferences = self._extract_preferences(query)
        
        products = self.recommender.recommend(
            user_id=user_id,
            preferences=preferences,
            limit=5
        )
        
        if not products:
            return AgentResponse(
                success=False,
                message="Không tìm thấy sản phẩm phù hợp với yêu cầu của bạn.",
                tool_used="product_recommend",
                data={"actions": [
                    {"action_id": "browse_all", "label": "Xem tất cả sản phẩm", "type": "button"},
                    {"action_id": "contact_support", "label": "Liên hệ hỗ trợ", "type": "button"}
                ]}
            )
        
        # Add order actions for each product
        actions = []
        for p in products:
            actions.append({
                "action_id": f"order_product_{p.get('id')}",
                "label": f"Đặt {p.get('name', 'sản phẩm')[:20]}...",
                "type": "button",
                "data": {"product_id": p.get("id")}
            })
        actions.append({"action_id": "contact_support", "label": "Tư vấn thêm", "type": "button"})
        
        return AgentResponse(
            success=True,
            message=self._format_recommendations(products),
            data={"products": products, "actions": actions},
            tool_used="product_recommend"
        )
    
    def _handle_summarization(
        self, 
        context: Optional[Dict[str, Any]]
    ) -> AgentResponse:
        """Handle conversation summarization"""
        if not context or "conversation_id" not in context:
            return AgentResponse(
                success=False,
                message="Cần cung cấp conversation_id để tóm tắt",
                tool_used="summarize_conversation"
            )
        
        summary = self.summarizer.summarize_conversation(
            conversation_id=context["conversation_id"],
            db=self.db
        )
        
        return AgentResponse(
            success=True,
            message=summary,
            tool_used="summarize_conversation"
        )
    
    # === ORDER WORKFLOW HANDLERS ===
    
    def _get_or_create_workflow(self, user_id: int, conversation_id: int) -> OrderWorkflowManager:
        """Get existing or create new order workflow for conversation"""
        if conversation_id not in self._order_workflows:
            self._order_workflows[conversation_id] = OrderWorkflowManager(
                db=self.db,
                user_id=user_id,
                conversation_id=conversation_id
            )
        return self._order_workflows[conversation_id]
    
    def _handle_order_intent(
        self, 
        query: str, 
        user_id: Optional[int],
        context: Dict[str, Any]
    ) -> AgentResponse:
        """Handle order-related intents"""
        if not user_id:
            return AgentResponse(
                success=False,
                message="Vui lòng đăng nhập để đặt hàng.",
                tool_used="order",
                data={"actions": [{"action_id": "login", "label": "Đăng nhập", "type": "button"}]}
            )
        
        conversation_id = context.get("conversation_id", 0)
        workflow = self._get_or_create_workflow(user_id, conversation_id)
        
        # Check if product_id is provided
        product_id = context.get("product_id")
        
        if workflow.state == OrderState.IDLE:
            result = workflow.start_order(product_id)
        elif product_id:
            quantity = context.get("quantity", 1)
            result = workflow.add_product(product_id, quantity)
        else:
            # Show current cart status
            result = workflow._handle_collecting_products()
        
        return self._workflow_to_response(result, "order")
    
    def _handle_payment_intent(
        self, 
        user_id: Optional[int],
        context: Dict[str, Any]
    ) -> AgentResponse:
        """Handle payment-related intents"""
        if not user_id:
            return AgentResponse(
                success=False,
                message="Vui lòng đăng nhập để thanh toán.",
                tool_used="payment"
            )
        
        conversation_id = context.get("conversation_id", 0)
        workflow = self._order_workflows.get(conversation_id)
        
        if not workflow or workflow.state == OrderState.IDLE:
            return AgentResponse(
                success=False,
                message="Bạn chưa có đơn hàng nào. Hãy chọn sản phẩm trước.",
                tool_used="payment",
                data={"actions": [
                    {"action_id": "browse_products", "label": "Xem sản phẩm", "type": "button"}
                ]}
            )
        
        payment_method = context.get("payment_method", "BANK_TRANSFER")
        result = workflow.select_payment_method(payment_method)
        
        return self._workflow_to_response(result, "payment")
    
    def _handle_track_order(
        self, 
        query: str, 
        user_id: Optional[int],
        context: Dict[str, Any]
    ) -> AgentResponse:
        """Handle order tracking"""
        if not user_id:
            return AgentResponse(
                success=False,
                message="Vui lòng đăng nhập để tra cứu đơn hàng.",
                tool_used="track_order"
            )
        
        # Extract order number from query or context
        order_number = context.get("order_number")
        
        if not order_number:
            # Try to extract from query
            import re
            match = re.search(r'ORD-\d{8}-[A-Z0-9]+', query.upper())
            if match:
                order_number = match.group()
        
        if order_number:
            # Lookup order
            from backend.models.order import Order
            order = self.db.query(Order).filter(
                Order.order_number == order_number,
                Order.customer_id == user_id
            ).first()
            
            if order:
                status_emoji = {
                    "PENDING": "[Đang chờ]",
                    "CONFIRMED": "[Xác nhận]",
                    "PROCESSING": "[Đang xử lý]",
                    "SHIPPED": "[Đang giao]",
                    "DELIVERED": "[Đã giao]",
                    "CANCELLED": "[Đã hủy]"
                }
                return AgentResponse(
                    success=True,
                    message=f"""**Thông tin đơn hàng {order_number}**

{status_emoji.get(order.status.value, "[Trạng thái]")} Trạng thái: **{order.status.value}**
Tổng tiền: {order.total_amount:,.0f}₫
Địa chỉ: {order.shipping_address}
Ngày đặt: {order.created_at.strftime('%d/%m/%Y %H:%M')}""",
                    tool_used="track_order",
                    data={
                        "order": {
                            "order_number": order.order_number,
                            "status": order.status.value,
                            "total_amount": order.total_amount
                        },
                        "actions": [
                            {"action_id": "contact_support", "label": "Hỗ trợ về đơn này", "type": "button"},
                            {"action_id": "new_order", "label": "Đặt hàng mới", "type": "button"}
                        ]
                    }
                )
            else:
                return AgentResponse(
                    success=False,
                    message=f"Không tìm thấy đơn hàng {order_number}",
                    tool_used="track_order"
                )
        
        # List recent orders
        from backend.models.order import Order
        orders = self.db.query(Order).filter(
            Order.customer_id == user_id
        ).order_by(Order.created_at.desc()).limit(5).all()
        
        if orders:
            lines = ["**Đơn hàng gần đây:**\n"]
            for o in orders:
                lines.append(f"- {o.order_number} - {o.status.value} - {o.total_amount:,.0f}₫")
            return AgentResponse(
                success=True,
                message="\n".join(lines),
                tool_used="track_order",
                data={"actions": [
                    {"action_id": f"view_order_{o.order_number}", "label": f"Xem {o.order_number}", "type": "button"}
                    for o in orders[:3]
                ]}
            )
        
        return AgentResponse(
            success=True,
            message="Bạn chưa có đơn hàng nào.",
            tool_used="track_order",
            data={"actions": [
                {"action_id": "start_order", "label": "Đặt hàng ngay", "type": "button"}
            ]}
        )
    
    def _handle_complaint(
        self, 
        query: str, 
        user_id: Optional[int],
        context: Dict[str, Any]
    ) -> AgentResponse:
        """Handle complaint/issue reporting"""
        return AgentResponse(
            success=True,
            message="""Rất tiếc vì trải nghiệm không tốt của bạn.

Bạn có thể:
1. **Tạo yêu cầu hỗ trợ** để chúng tôi xử lý
2. **Gặp nhân viên** để được hỗ trợ trực tiếp

Vui lòng chọn cách thức bên dưới:""",
            tool_used="complaint",
            data={"actions": [
                {"action_id": "create_ticket", "label": "Tạo yêu cầu hỗ trợ", "type": "button", "style": "primary"},
                {"action_id": "contact_staff", "label": "Gặp nhân viên", "type": "button"},
                {"action_id": "track_order", "label": "Xem đơn hàng liên quan", "type": "button"}
            ]}
        )
    
    def _handle_support_request(
        self, 
        user_id: Optional[int],
        context: Dict[str, Any]
    ) -> AgentResponse:
        """Handle request to contact support staff"""
        return AgentResponse(
            success=True,
            message="""**Kết nối với nhân viên hỗ trợ**

Nhân viên sẽ tiếp nhận cuộc trò chuyện này trong giây lát.

Thời gian hỗ trợ: 8:00 - 22:00 (T2-CN)
Hotline: 1900-xxxx

Trong khi chờ, bạn có thể mô tả vấn đề của mình.""",
            tool_used="support",
            data={
                "transfer_to_human": True,
                "actions": [
                    {"action_id": "create_ticket", "label": "Để lại tin nhắn", "type": "button"},
                    {"action_id": "call_hotline", "label": "Gọi hotline", "type": "button"}
                ]
            }
        )
    
    def _handle_action(
        self, 
        action_id: str, 
        user_id: Optional[int],
        context: Dict[str, Any]
    ) -> AgentResponse:
        """Handle button/action clicks"""
        # Parse action_id
        if action_id.startswith("order_product_"):
            product_id = int(action_id.replace("order_product_", ""))
            context["product_id"] = product_id
            return self._handle_order_intent("", user_id, context)
        
        elif action_id.startswith("view_order_"):
            order_number = action_id.replace("view_order_", "")
            context["order_number"] = order_number
            return self._handle_track_order("", user_id, context)
        
        elif action_id == "start_order":
            return self._handle_order_intent("đặt hàng", user_id, context)
        
        elif action_id == "proceed_checkout":
            conversation_id = context.get("conversation_id", 0)
            workflow = self._order_workflows.get(conversation_id)
            if workflow:
                result = workflow.proceed_to_checkout()
                return self._workflow_to_response(result, "checkout")
        
        elif action_id == "confirm_order":
            conversation_id = context.get("conversation_id", 0)
            workflow = self._order_workflows.get(conversation_id)
            if workflow:
                result = workflow.confirm_order()
                return self._workflow_to_response(result, "confirm_order")
        
        elif action_id == "confirm_payment":
            conversation_id = context.get("conversation_id", 0)
            workflow = self._order_workflows.get(conversation_id)
            if workflow:
                result = workflow.confirm_payment()
                return self._workflow_to_response(result, "payment")
        
        elif action_id == "cancel_order":
            conversation_id = context.get("conversation_id", 0)
            workflow = self._order_workflows.get(conversation_id)
            if workflow:
                result = workflow.cancel_order()
                return self._workflow_to_response(result, "cancel")
        
        elif action_id in ["pay_bank_transfer", "pay_momo", "pay_cod"]:
            method_map = {
                "pay_bank_transfer": "BANK_TRANSFER",
                "pay_momo": "MOMO",
                "pay_cod": "COD"
            }
            context["payment_method"] = method_map[action_id]
            return self._handle_payment_intent(user_id, context)
        
        elif action_id == "contact_support":
            return self._handle_support_request(user_id, context)
        
        elif action_id == "create_ticket":
            return self._handle_create_ticket(user_id, context)
        
        elif action_id == "contact_staff":
            return self._handle_support_request(user_id, context)
        
        elif action_id == "track_order":
            return self._handle_track_order("", user_id, context)
        
        # Default: unknown action
        return AgentResponse(
            success=False,
            message="Thao tác không được hỗ trợ.",
            tool_used="action"
        )
    
    def _handle_create_ticket(
        self, 
        user_id: Optional[int],
        context: Dict[str, Any]
    ) -> AgentResponse:
        """Create support ticket"""
        if not user_id:
            return AgentResponse(
                success=False,
                message="Vui lòng đăng nhập để tạo yêu cầu hỗ trợ.",
                tool_used="create_ticket"
            )
        
        subject = context.get("subject", "Yêu cầu hỗ trợ từ chat")
        description = context.get("description", "Khách hàng yêu cầu hỗ trợ từ cuộc trò chuyện")
        
        try:
            from backend.models.ticket import Ticket, TicketStatus, TicketPriority
            
            ticket = Ticket(
                customer_id=user_id,
                subject=subject,
                description=description,
                status=TicketStatus.OPEN,
                priority=TicketPriority.MEDIUM,
                source="chat"
            )
            self.db.add(ticket)
            self.db.commit()
            
            return AgentResponse(
                success=True,
                message=f"""**Đã tạo yêu cầu hỗ trợ #{ticket.id}**

Chúng tôi sẽ phản hồi trong thời gian sớm nhất.
Bạn có thể theo dõi trạng thái tại mục "Hỗ trợ" trong tài khoản.""",
                tool_used="create_ticket",
                data={"ticket_id": ticket.id}
            )
        except Exception as e:
            return AgentResponse(
                success=False,
                message=f"Lỗi tạo yêu cầu: {str(e)}",
                tool_used="create_ticket"
            )
    
    def _workflow_to_response(self, result, tool_used: str) -> AgentResponse:
        """Convert workflow result to AgentResponse"""
        return AgentResponse(
            success=True,
            message=result.message,
            tool_used=tool_used,
            data=result.to_dict()
        )
    
    def _get_error_actions(self) -> List[Dict]:
        """Get default actions for error states"""
        return [
            {"action_id": "retry", "label": "Thử lại", "type": "button"},
            {"action_id": "contact_support", "label": "Hỗ trợ", "type": "button"}
        ]
    
    def _extract_preferences(self, query: str) -> Dict[str, Any]:
        """Extract product preferences from query"""
        preferences = {}
        
        # Simple keyword extraction (can be enhanced with NLP)
        price_keywords = ["dưới", "trên", "khoảng", "tầm"]
        for kw in price_keywords:
            if kw in query:
                preferences["has_price_constraint"] = True
                break
        
        return preferences
    
    def _format_recommendations(self, products: List[Dict[str, Any]]) -> str:
        """Format product recommendations as readable text"""
        lines = ["**Sản phẩm gợi ý cho bạn:**\n"]
        
        for i, p in enumerate(products, 1):
            lines.append(f"{i}. **{p.get('name', 'N/A')}**")
            if p.get('price'):
                lines.append(f"   Giá: {p['price']:,.0f} VNĐ")
            if p.get('category'):
                lines.append(f"   Danh mục: {p['category']}")
            lines.append("")
        
        return "\n".join(lines)
