"""
Order Workflow Manager - State Machine cho quy trình đặt hàng
"""
from enum import Enum
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid
from sqlalchemy.orm import Session


class OrderState(str, Enum):
    """Trạng thái của quy trình đặt hàng"""
    IDLE = "idle"                           # Chưa bắt đầu đặt hàng
    COLLECTING_PRODUCTS = "collecting_products"  # Thu thập sản phẩm
    COLLECTING_INFO = "collecting_info"      # Thu thập thông tin giao hàng
    DRAFT_REVIEW = "draft_review"            # Xem lại đơn nháp
    AWAITING_CONFIRM = "awaiting_confirm"    # Chờ xác nhận
    PAYMENT_PENDING = "payment_pending"      # Chờ thanh toán
    PAYMENT_CONFIRMED = "payment_confirmed"  # Đã xác nhận thanh toán
    ORDER_CREATED = "order_created"          # Đã tạo đơn chính thức
    CANCELLED = "cancelled"                  # Đã hủy


@dataclass
class OrderItem:
    """Sản phẩm trong đơn hàng"""
    product_id: int
    product_name: str
    quantity: int
    unit_price: float
    image_url: Optional[str] = None
    
    @property
    def subtotal(self) -> float:
        return self.quantity * self.unit_price


@dataclass 
class ShippingInfo:
    """Thông tin giao hàng"""
    recipient_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class OrderDraft:
    """Draft đơn hàng trước khi thanh toán"""
    draft_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[int] = None
    conversation_id: Optional[int] = None
    items: List[OrderItem] = field(default_factory=list)
    shipping: ShippingInfo = field(default_factory=ShippingInfo)
    payment_method: str = "BANK_TRANSFER"  # BANK_TRANSFER, COD, MOMO
    
    # Amounts
    subtotal: float = 0.0
    shipping_fee: float = 0.0
    discount_amount: float = 0.0
    tax_amount: float = 0.0
    
    # Payment tracking
    payment_qr_url: Optional[str] = None
    payment_ref_code: Optional[str] = None
    payment_confirmed_at: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    
    @property
    def total_amount(self) -> float:
        """Tổng tiền đơn hàng"""
        return self.subtotal + self.shipping_fee + self.tax_amount - self.discount_amount
    
    def calculate_subtotal(self):
        """Tính lại subtotal từ items"""
        self.subtotal = sum(item.subtotal for item in self.items)
    
    def add_item(self, item: OrderItem):
        """Thêm sản phẩm vào draft"""
        # Check if product already exists
        for existing in self.items:
            if existing.product_id == item.product_id:
                existing.quantity += item.quantity
                self.calculate_subtotal()
                return
        self.items.append(item)
        self.calculate_subtotal()
    
    def remove_item(self, product_id: int):
        """Xóa sản phẩm khỏi draft"""
        self.items = [i for i in self.items if i.product_id != product_id]
        self.calculate_subtotal()
    
    def update_quantity(self, product_id: int, quantity: int):
        """Cập nhật số lượng sản phẩm"""
        for item in self.items:
            if item.product_id == product_id:
                item.quantity = quantity
                break
        self.calculate_subtotal()
    
    def is_valid(self) -> tuple[bool, List[str]]:
        """Kiểm tra draft có đủ thông tin chưa"""
        missing = []
        
        if not self.items:
            missing.append("products")
        if not self.shipping.recipient_name:
            missing.append("recipient_name")
        if not self.shipping.phone:
            missing.append("phone")
        if not self.shipping.address:
            missing.append("address")
        
        return len(missing) == 0, missing


class ChatAction:
    """Action button trong chat"""
    def __init__(
        self, 
        action_id: str,
        label: str,
        action_type: str,  # button, link, qr
        data: Optional[Dict] = None,
        style: str = "primary"  # primary, secondary, danger
    ):
        self.action_id = action_id
        self.label = label
        self.action_type = action_type
        self.data = data or {}
        self.style = style
    
    def to_dict(self) -> Dict:
        return {
            "action_id": self.action_id,
            "label": self.label,
            "type": self.action_type,
            "data": self.data,
            "style": self.style
        }


@dataclass
class WorkflowResponse:
    """Response từ workflow"""
    state: OrderState
    message: str
    draft: Optional[OrderDraft] = None
    actions: List[ChatAction] = field(default_factory=list)
    payment_info: Optional[Dict] = None
    order_number: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "state": self.state.value,
            "message": self.message,
            "draft": self._draft_to_dict() if self.draft else None,
            "actions": [a.to_dict() for a in self.actions],
            "payment_info": self.payment_info,
            "order_number": self.order_number
        }
    
    def _draft_to_dict(self) -> Optional[Dict]:
        if not self.draft:
            return None
        return {
            "draft_id": self.draft.draft_id,
            "items": [
                {
                    "product_id": i.product_id,
                    "product_name": i.product_name,
                    "quantity": i.quantity,
                    "unit_price": i.unit_price,
                    "subtotal": i.subtotal,
                    "image_url": i.image_url
                }
                for i in self.draft.items
            ],
            "shipping": {
                "recipient_name": self.draft.shipping.recipient_name,
                "phone": self.draft.shipping.phone,
                "address": self.draft.shipping.address,
                "city": self.draft.shipping.city,
                "notes": self.draft.shipping.notes
            },
            "subtotal": self.draft.subtotal,
            "shipping_fee": self.draft.shipping_fee,
            "discount_amount": self.draft.discount_amount,
            "total_amount": self.draft.total_amount,
            "payment_method": self.draft.payment_method
        }


class OrderWorkflowManager:
    """
    Quản lý state machine cho order workflow trong chat.
    
    Flow:
    IDLE → COLLECTING_PRODUCTS → COLLECTING_INFO → DRAFT_REVIEW 
    → AWAITING_CONFIRM → PAYMENT_PENDING → PAYMENT_CONFIRMED → ORDER_CREATED
    """
    
    # Shipping fee tính theo vùng
    SHIPPING_FEES = {
        "Hà Nội": 15000,
        "TP.HCM": 15000,
        "default": 30000
    }
    
    def __init__(self, db: Session, user_id: int, conversation_id: int):
        self.db = db
        self.user_id = user_id
        self.conversation_id = conversation_id
        self.state = OrderState.IDLE
        self.draft = OrderDraft(
            user_id=user_id,
            conversation_id=conversation_id
        )
    
    def start_order(self, product_id: Optional[int] = None) -> WorkflowResponse:
        """Bắt đầu quy trình đặt hàng"""
        self.state = OrderState.COLLECTING_PRODUCTS
        
        if product_id:
            # Nếu có product_id, thêm luôn vào draft
            product = self._get_product(product_id)
            if product:
                self.draft.add_item(OrderItem(
                    product_id=product.id,
                    product_name=product.name,
                    quantity=1,
                    unit_price=product.price,
                    image_url=product.image_url if hasattr(product, 'image_url') else None
                ))
                return self._handle_collecting_products()
        
        return WorkflowResponse(
            state=self.state,
            message="Bạn muốn đặt sản phẩm nào? Hãy cho tôi biết tên hoặc mã sản phẩm.",
            actions=[
                ChatAction("browse_products", "Xem sản phẩm", "button"),
                ChatAction("cancel_order", "Hủy", "button", style="danger")
            ]
        )
    
    def add_product(self, product_id: int, quantity: int = 1) -> WorkflowResponse:
        """Thêm sản phẩm vào đơn"""
        product = self._get_product(product_id)
        if not product:
            return WorkflowResponse(
                state=self.state,
                message="Không tìm thấy sản phẩm. Vui lòng thử lại.",
                actions=[
                    ChatAction("browse_products", "Xem sản phẩm", "button")
                ]
            )
        
        # Check stock
        if hasattr(product, 'stock_quantity') and product.stock_quantity < quantity:
            return WorkflowResponse(
                state=self.state,
                message=f"Sản phẩm {product.name} chỉ còn {product.stock_quantity} sản phẩm.",
                actions=[
                    ChatAction("reduce_quantity", f"Đặt {product.stock_quantity} sản phẩm", "button", 
                              data={"product_id": product_id, "quantity": product.stock_quantity})
                ]
            )
        
        self.draft.add_item(OrderItem(
            product_id=product.id,
            product_name=product.name,
            quantity=quantity,
            unit_price=product.price,
            image_url=product.image_url if hasattr(product, 'image_url') else None
        ))
        
        return self._handle_collecting_products()
    
    def _handle_collecting_products(self) -> WorkflowResponse:
        """Xử lý trạng thái thu thập sản phẩm"""
        items_text = self._format_items_list()
        
        return WorkflowResponse(
            state=self.state,
            message=f"**Giỏ hàng hiện tại:**\n{items_text}\n\n**Tạm tính:** {self.draft.subtotal:,.0f} VNĐ\n\nBạn muốn thêm sản phẩm khác không?",
            draft=self.draft,
            actions=[
                ChatAction("add_more", "Thêm sản phẩm", "button"),
                ChatAction("proceed_checkout", "Tiếp tục đặt hàng", "button", style="primary"),
                ChatAction("clear_cart", "Xóa giỏ hàng", "button", style="danger")
            ]
        )
    
    def proceed_to_checkout(self) -> WorkflowResponse:
        """
 Chuyển sang thu thập thông tin giao hàng"""
        if not self.draft.items:
            return WorkflowResponse(
                state=self.state,
                message="Giỏ hàng trống. Vui lòng thêm sản phẩm trước.",
                actions=[
                    ChatAction("browse_products", "Xem sản phẩm", "button")
                ]
            )
        
        self.state = OrderState.COLLECTING_INFO
        
        # Load user info if exists
        user = self._get_user_info()
        if user:
            self.draft.shipping.recipient_name = user.get('full_name')
            self.draft.shipping.phone = user.get('phone')
            self.draft.shipping.address = user.get('address')
            self.draft.shipping.city = user.get('city')
        
        # Check what info is missing
        is_valid, missing = self.draft.is_valid()
        
        if is_valid:
            return self._show_draft_review()
        
        return self._ask_for_missing_info(missing)
    
    def update_shipping_info(
        self, 
        recipient_name: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[str] = None,
        city: Optional[str] = None,
        notes: Optional[str] = None
    ) -> WorkflowResponse:
        """Cập nhật thông tin giao hàng"""
        if recipient_name:
            self.draft.shipping.recipient_name = recipient_name
        if phone:
            self.draft.shipping.phone = phone
        if address:
            self.draft.shipping.address = address
        if city:
            self.draft.shipping.city = city
            # Cập nhật phí ship
            self.draft.shipping_fee = self.SHIPPING_FEES.get(city, self.SHIPPING_FEES["default"])
        if notes:
            self.draft.shipping.notes = notes
        
        # Check if all required info is collected
        is_valid, missing = self.draft.is_valid()
        
        if is_valid:
            return self._show_draft_review()
        
        return self._ask_for_missing_info(missing)
    
    def _ask_for_missing_info(self, missing: List[str]) -> WorkflowResponse:
        """Yêu cầu thông tin còn thiếu"""
        field_prompts = {
            "recipient_name": "Vui lòng cho biết **họ tên người nhận**:",
            "phone": "Vui lòng cho biết **số điện thoại** liên hệ:",
            "address": "Vui lòng cho biết **địa chỉ giao hàng** chi tiết:",
        }
        
        first_missing = missing[0]
        prompt = field_prompts.get(first_missing, f"Vui lòng cung cấp {first_missing}:")
        
        return WorkflowResponse(
            state=self.state,
            message=f"{prompt}",
            draft=self.draft,
            actions=[
                ChatAction("cancel_order", "Hủy đơn", "button", style="danger")
            ]
        )
    
    def _show_draft_review(self) -> WorkflowResponse:
        """Hiển thị xem lại đơn hàng"""
        self.state = OrderState.DRAFT_REVIEW
        
        # Calculate shipping fee based on city
        if self.draft.shipping.city:
            self.draft.shipping_fee = self.SHIPPING_FEES.get(
                self.draft.shipping.city, 
                self.SHIPPING_FEES["default"]
            )
        
        order_summary = self._format_order_summary()
        
        return WorkflowResponse(
            state=self.state,
            message=f"**XÁC NHẬN ĐƠN HÀNG**\n\n{order_summary}",
            draft=self.draft,
            actions=[
                ChatAction("confirm_order", "Xác nhận đặt hàng", "button", style="primary"),
                ChatAction("edit_info", "Sửa thông tin", "button"),
                ChatAction("edit_cart", "Sửa giỏ hàng", "button"),
                ChatAction("cancel_order", "Hủy đơn", "button", style="danger")
            ]
        )
    
    def confirm_order(self) -> WorkflowResponse:
        """Xác nhận đơn hàng và chuyển sang thanh toán"""
        self.state = OrderState.AWAITING_CONFIRM
        
        return WorkflowResponse(
            state=self.state,
            message="Vui lòng chọn phương thức thanh toán:",
            draft=self.draft,
            actions=[
                ChatAction("pay_bank_transfer", "Chuyển khoản ngân hàng", "button", style="primary",
                          data={"method": "BANK_TRANSFER"}),
                ChatAction("pay_momo", "Ví MoMo", "button",
                          data={"method": "MOMO"}),
                ChatAction("pay_cod", "Thanh toán khi nhận hàng (COD)", "button",
                          data={"method": "COD"}),
                ChatAction("cancel_order", "Hủy", "button", style="danger")
            ]
        )
    
    def select_payment_method(self, method: str) -> WorkflowResponse:
        """Chọn phương thức thanh toán"""
        self.draft.payment_method = method
        self.state = OrderState.PAYMENT_PENDING
        
        if method == "COD":
            # COD - tạo đơn luôn
            return self._create_order()
        
        # Bank transfer / MoMo - generate QR
        payment_info = self._generate_payment_info(method)
        
        return WorkflowResponse(
            state=self.state,
            message=f"**THANH TOÁN**\n\nQuét mã QR hoặc chuyển khoản theo thông tin bên dưới:\n\n**Số tiền:** {self.draft.total_amount:,.0f} VNĐ\n**Nội dung CK:** {payment_info['ref_code']}\n\nĐơn hàng sẽ tự động hủy sau 15 phút nếu không thanh toán.",
            draft=self.draft,
            payment_info=payment_info,
            actions=[
                ChatAction("confirm_payment", "Tôi đã thanh toán", "button", style="primary"),
                ChatAction("change_payment", "Đổi phương thức", "button"),
                ChatAction("cancel_order", "Hủy đơn", "button", style="danger")
            ]
        )
    
    def confirm_payment(self) -> WorkflowResponse:
        """Xác nhận đã thanh toán"""
        # Trong thực tế sẽ verify với payment gateway
        # Demo mode: chấp nhận luôn
        self.draft.payment_confirmed_at = datetime.now()
        self.state = OrderState.PAYMENT_CONFIRMED
        
        return self._create_order()
    
    def _create_order(self) -> WorkflowResponse:
        """Tạo đơn hàng chính thức"""
        try:
            from backend.models.order import Order, OrderItem as OrderItemModel, OrderStatus
            from backend.models.product import Product
            
            # Generate order number
            order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
            
            # Create order
            order = Order(
                order_number=order_number,
                customer_id=self.user_id,
                status=OrderStatus.PENDING if self.draft.payment_method == "COD" else OrderStatus.CONFIRMED,
                total_amount=self.draft.total_amount,
                tax_amount=self.draft.tax_amount,
                shipping_fee=self.draft.shipping_fee,
                discount_amount=self.draft.discount_amount,
                shipping_address=self.draft.shipping.address,
                shipping_city=self.draft.shipping.city,
                shipping_phone=self.draft.shipping.phone,
                payment_method=self.draft.payment_method,
                payment_status="PAID" if self.draft.payment_confirmed_at else "PENDING",
                customer_notes=self.draft.shipping.notes
            )
            
            self.db.add(order)
            self.db.flush()  # Get order.id
            
            # Create order items
            for item in self.draft.items:
                order_item = OrderItemModel(
                    order_id=order.id,
                    product_id=item.product_id,
                    product_name=item.product_name,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    subtotal=item.subtotal
                )
                self.db.add(order_item)
                
                # Update stock
                product = self.db.query(Product).filter(Product.id == item.product_id).first()
                if product and hasattr(product, 'stock_quantity'):
                    product.stock_quantity -= item.quantity
            
            self.db.commit()
            
            self.state = OrderState.ORDER_CREATED
            
            return WorkflowResponse(
                state=self.state,
                message=f"**ĐẶT HÀNG THÀNH CÔNG!**\n\nMã đơn hàng: **{order_number}**\n\nChúng tôi sẽ xử lý đơn hàng trong thời gian sớm nhất.\n\nNếu cần hỗ trợ, hãy liên hệ với chúng tôi!",
                order_number=order_number,
                actions=[
                    ChatAction("track_order", "Theo dõi đơn hàng", "button", 
                              data={"order_number": order_number}),
                    ChatAction("continue_shopping", "Tiếp tục mua sắm", "button"),
                    ChatAction("contact_support", "Liên hệ hỗ trợ", "button")
                ]
            )
            
        except Exception as e:
            self.db.rollback()
            return WorkflowResponse(
                state=OrderState.DRAFT_REVIEW,
                message=f"Lỗi tạo đơn hàng: {str(e)}. Vui lòng thử lại.",
                draft=self.draft,
                actions=[
                    ChatAction("retry_create", "Thử lại", "button"),
                    ChatAction("contact_support", "Liên hệ hỗ trợ", "button")
                ]
            )
    
    def cancel_order(self) -> WorkflowResponse:
        """Hủy đơn hàng"""
        self.state = OrderState.CANCELLED
        self.draft = OrderDraft(user_id=self.user_id, conversation_id=self.conversation_id)
        
        return WorkflowResponse(
            state=self.state,
            message="Đã hủy đơn hàng. Bạn có thể tiếp tục mua sắm hoặc liên hệ hỗ trợ nếu cần.",
            actions=[
                ChatAction("new_order", "Đặt hàng mới", "button"),
                ChatAction("browse_products", "Xem sản phẩm", "button"),
                ChatAction("contact_support", "Liên hệ hỗ trợ", "button")
            ]
        )
    
    # === Helper Methods ===
    
    def _get_product(self, product_id: int):
        """Lấy thông tin sản phẩm từ DB"""
        try:
            from backend.models.product import Product
            return self.db.query(Product).filter(Product.id == product_id).first()
        except Exception:
            return None
    
    def _get_user_info(self) -> Optional[Dict]:
        """Lấy thông tin user"""
        try:
            from backend.models.user import User
            user = self.db.query(User).filter(User.id == self.user_id).first()
            if user:
                return {
                    "full_name": user.full_name if hasattr(user, 'full_name') else None,
                    "phone": user.phone if hasattr(user, 'phone') else None,
                    "address": user.address if hasattr(user, 'address') else None,
                    "city": user.city if hasattr(user, 'city') else None
                }
        except Exception:
            pass
        return None
    
    def _format_items_list(self) -> str:
        """Format danh sách sản phẩm"""
        lines = []
        for i, item in enumerate(self.draft.items, 1):
            lines.append(f"{i}. {item.product_name} x{item.quantity} = {item.subtotal:,.0f}₫")
        return "\n".join(lines)
    
    def _format_order_summary(self) -> str:
        """Format tóm tắt đơn hàng"""
        items_text = self._format_items_list()
        
        return f"""**Sản phẩm:**
{items_text}

**Giao hàng đến:**
- Người nhận: {self.draft.shipping.recipient_name}
- SĐT: {self.draft.shipping.phone}
- Địa chỉ: {self.draft.shipping.address}
{f"- Ghi chú: {self.draft.shipping.notes}" if self.draft.shipping.notes else ""}

**Chi phí:**
- Tạm tính: {self.draft.subtotal:,.0f}₫
- Phí vận chuyển: {self.draft.shipping_fee:,.0f}₫
{f"- Giảm giá: -{self.draft.discount_amount:,.0f}₫" if self.draft.discount_amount > 0 else ""}
- **Tổng cộng: {self.draft.total_amount:,.0f}₫**"""
    
    def _generate_payment_info(self, method: str) -> Dict:
        """Tạo thông tin thanh toán"""
        ref_code = f"DH{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:4].upper()}"
        self.draft.payment_ref_code = ref_code
        
        # Demo bank info
        bank_info = {
            "bank_name": "VietcomBank",
            "account_number": "1234567890",
            "account_name": "CONG TY CRM AI",
            "branch": "Chi nhánh TP.HCM"
        }
        
        from .qr_generator import QRGenerator
        qr_gen = QRGenerator()
        
        if method == "BANK_TRANSFER":
            qr_url = qr_gen.generate_vietqr(
                bank_id="VCB",
                account_number=bank_info["account_number"],
                account_name=bank_info["account_name"],
                amount=self.draft.total_amount,
                message=ref_code
            )
        elif method == "MOMO":
            qr_url = qr_gen.generate_momo_qr(
                phone="0901234567",
                amount=self.draft.total_amount,
                message=ref_code
            )
        else:
            qr_url = None
        
        self.draft.payment_qr_url = qr_url
        
        return {
            "method": method,
            "ref_code": ref_code,
            "amount": self.draft.total_amount,
            "qr_url": qr_url,
            "bank_info": bank_info if method == "BANK_TRANSFER" else None,
            "expires_in_minutes": 15
        }
    
    def get_suggested_actions(self, context: str = "general") -> List[ChatAction]:
        """Lấy các action gợi ý dựa theo context"""
        actions = {
            "general": [
                ChatAction("start_order", "Đặt hàng", "button"),
                ChatAction("browse_products", "Xem sản phẩm", "button"),
                ChatAction("track_order", "Tra cứu đơn hàng", "button"),
                ChatAction("contact_support", "Liên hệ hỗ trợ", "button")
            ],
            "after_recommendation": [
                ChatAction("order_product", "Đặt hàng ngay", "button", style="primary"),
                ChatAction("more_info", "Xem chi tiết", "button"),
                ChatAction("similar_products", "Sản phẩm tương tự", "button")
            ],
            "complaint": [
                ChatAction("create_ticket", "Tạo yêu cầu hỗ trợ", "button", style="primary"),
                ChatAction("contact_staff", "Gặp nhân viên", "button"),
                ChatAction("view_order", "Xem đơn hàng", "button")
            ]
        }
        return actions.get(context, actions["general"])
