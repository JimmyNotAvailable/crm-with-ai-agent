"""
Payment Service - Xử lý thanh toán và xác minh
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import uuid


class PaymentStatus(str, Enum):
    """Trạng thái thanh toán"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


@dataclass
class PaymentTransaction:
    """Transaction thanh toán"""
    transaction_id: str
    draft_id: str
    user_id: int
    amount: float
    method: str  # BANK_TRANSFER, MOMO, COD
    status: PaymentStatus
    ref_code: str
    qr_url: Optional[str] = None
    created_at: datetime = None
    expires_at: datetime = None
    confirmed_at: Optional[datetime] = None
    note: Optional[str] = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now()
        if not self.expires_at:
            self.expires_at = self.created_at + timedelta(minutes=15)
    
    @property
    def is_expired(self) -> bool:
        return datetime.now() > self.expires_at
    
    def to_dict(self) -> Dict:
        return {
            "transaction_id": self.transaction_id,
            "draft_id": self.draft_id,
            "user_id": self.user_id,
            "amount": self.amount,
            "method": self.method,
            "status": self.status.value,
            "ref_code": self.ref_code,
            "qr_url": self.qr_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "confirmed_at": self.confirmed_at.isoformat() if self.confirmed_at else None
        }


class PaymentService:
    """
    Service xử lý thanh toán.
    
    Trong production:
    - Tích hợp VNPay, MoMo, ZaloPay APIs
    - Webhook để nhận callback từ payment gateway
    - Verify signature từ payment provider
    
    Demo mode:
    - Cho phép xác nhận manual
    - Kiểm tra timeout
    """
    
    # Demo bank info
    DEFAULT_BANK_CONFIG = {
        "bank_id": "VCB",
        "bank_name": "Vietcombank",
        "account_number": "1234567890123",
        "account_name": "CONG TY TNHH CRM AI",
        "branch": "Chi nhánh TP.HCM"
    }
    
    # Demo MoMo config
    DEFAULT_MOMO_CONFIG = {
        "phone": "0901234567",
        "name": "CRM AI Shop"
    }
    
    def __init__(self, demo_mode: bool = True):
        self.demo_mode = demo_mode
        self._transactions: Dict[str, PaymentTransaction] = {}
    
    def create_payment(
        self,
        draft_id: str,
        user_id: int,
        amount: float,
        method: str = "BANK_TRANSFER"
    ) -> PaymentTransaction:
        """
        Tạo payment transaction mới.
        
        Args:
            draft_id: ID của order draft
            user_id: ID user
            amount: Số tiền
            method: Phương thức thanh toán
            
        Returns:
            PaymentTransaction object
        """
        transaction_id = str(uuid.uuid4())
        ref_code = self._generate_ref_code()
        
        # Generate QR
        from .qr_generator import QRGenerator
        qr_gen = QRGenerator()
        
        if method == "BANK_TRANSFER":
            qr_url = qr_gen.generate_vietqr(
                bank_id=self.DEFAULT_BANK_CONFIG["bank_id"],
                account_number=self.DEFAULT_BANK_CONFIG["account_number"],
                account_name=self.DEFAULT_BANK_CONFIG["account_name"],
                amount=amount,
                message=ref_code
            )
        elif method == "MOMO":
            qr_url = qr_gen.generate_momo_qr(
                phone=self.DEFAULT_MOMO_CONFIG["phone"],
                amount=amount,
                message=ref_code
            )
        else:
            qr_url = None
        
        transaction = PaymentTransaction(
            transaction_id=transaction_id,
            draft_id=draft_id,
            user_id=user_id,
            amount=amount,
            method=method,
            status=PaymentStatus.PENDING,
            ref_code=ref_code,
            qr_url=qr_url
        )
        
        self._transactions[transaction_id] = transaction
        
        return transaction
    
    def verify_payment(self, transaction_id: str) -> Dict[str, Any]:
        """
        Xác minh thanh toán.
        
        Trong production sẽ gọi API payment gateway.
        Demo mode cho phép verify manual.
        
        Args:
            transaction_id: ID transaction
            
        Returns:
            {
                "verified": bool,
                "status": str,
                "message": str
            }
        """
        transaction = self._transactions.get(transaction_id)
        
        if not transaction:
            return {
                "verified": False,
                "status": "not_found",
                "message": "Không tìm thấy giao dịch"
            }
        
        if transaction.is_expired:
            transaction.status = PaymentStatus.EXPIRED
            return {
                "verified": False,
                "status": "expired",
                "message": "Giao dịch đã hết hạn"
            }
        
        if transaction.status == PaymentStatus.COMPLETED:
            return {
                "verified": True,
                "status": "completed",
                "message": "Thanh toán đã được xác nhận"
            }
        
        # Demo mode: simulate checking
        if self.demo_mode:
            # Trong demo, user sẽ confirm manual
            return {
                "verified": False,
                "status": "pending",
                "message": "Đang chờ xác nhận thanh toán"
            }
        
        # Production: call payment gateway API
        # result = self._call_payment_gateway(transaction)
        # return result
        
        return {
            "verified": False,
            "status": "pending",
            "message": "Đang xử lý..."
        }
    
    def confirm_payment_manual(
        self, 
        transaction_id: str,
        confirmed_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Xác nhận thanh toán thủ công (demo mode / admin confirm).
        
        Args:
            transaction_id: ID transaction
            confirmed_by: Người xác nhận (admin/system)
            
        Returns:
            Result dict
        """
        transaction = self._transactions.get(transaction_id)
        
        if not transaction:
            return {
                "success": False,
                "message": "Không tìm thấy giao dịch"
            }
        
        if transaction.is_expired:
            transaction.status = PaymentStatus.EXPIRED
            return {
                "success": False,
                "message": "Giao dịch đã hết hạn"
            }
        
        transaction.status = PaymentStatus.COMPLETED
        transaction.confirmed_at = datetime.now()
        transaction.note = f"Xác nhận bởi: {confirmed_by or 'system'}"
        
        return {
            "success": True,
            "message": "Đã xác nhận thanh toán thành công",
            "transaction": transaction.to_dict()
        }
    
    def cancel_payment(self, transaction_id: str) -> Dict[str, Any]:
        """
        Hủy giao dịch thanh toán.
        
        Args:
            transaction_id: ID transaction
            
        Returns:
            Result dict
        """
        transaction = self._transactions.get(transaction_id)
        
        if not transaction:
            return {
                "success": False,
                "message": "Không tìm thấy giao dịch"
            }
        
        if transaction.status == PaymentStatus.COMPLETED:
            return {
                "success": False,
                "message": "Không thể hủy giao dịch đã hoàn thành"
            }
        
        transaction.status = PaymentStatus.CANCELLED
        
        return {
            "success": True,
            "message": "Đã hủy giao dịch"
        }
    
    def get_transaction(self, transaction_id: str) -> Optional[PaymentTransaction]:
        """Lấy thông tin transaction"""
        return self._transactions.get(transaction_id)
    
    def get_transaction_by_ref(self, ref_code: str) -> Optional[PaymentTransaction]:
        """Tìm transaction theo ref code"""
        for t in self._transactions.values():
            if t.ref_code == ref_code:
                return t
        return None
    
    def get_payment_info(self, method: str) -> Dict[str, Any]:
        """
        Lấy thông tin thanh toán cho một phương thức.
        
        Args:
            method: BANK_TRANSFER, MOMO, COD
            
        Returns:
            Payment info dict
        """
        if method == "BANK_TRANSFER":
            return {
                "method": "BANK_TRANSFER",
                "method_name": "Chuyển khoản ngân hàng",
                "bank_info": self.DEFAULT_BANK_CONFIG,
                "instructions": [
                    "Quét mã QR hoặc chuyển khoản theo thông tin",
                    "Nhập đúng nội dung chuyển khoản",
                    "Thanh toán trong vòng 15 phút",
                    "Bấm 'Tôi đã thanh toán' sau khi chuyển tiền"
                ]
            }
        elif method == "MOMO":
            return {
                "method": "MOMO",
                "method_name": "Ví điện tử MoMo",
                "momo_info": self.DEFAULT_MOMO_CONFIG,
                "instructions": [
                    "Mở app MoMo và quét mã QR",
                    "Hoặc chuyển tiền đến số điện thoại",
                    "Nhập đúng nội dung ghi chú",
                    "Bấm 'Tôi đã thanh toán' sau khi chuyển tiền"
                ]
            }
        elif method == "COD":
            return {
                "method": "COD",
                "method_name": "Thanh toán khi nhận hàng",
                "instructions": [
                    "Kiểm tra hàng khi nhận",
                    "Thanh toán tiền mặt cho shipper",
                    "Giữ biên lai để đổi/trả nếu cần"
                ]
            }
        
        return {"method": method, "method_name": method}
    
    def _generate_ref_code(self) -> str:
        """Tạo mã tham chiếu thanh toán"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_part = str(uuid.uuid4())[:6].upper()
        return f"CRM{timestamp}{unique_part}"
    
    def cleanup_expired(self) -> int:
        """
        Dọn dẹp các transaction đã hết hạn.
        Chạy định kỳ để giải phóng memory.
        
        Returns:
            Số transaction đã xóa
        """
        expired_ids = [
            tid for tid, t in self._transactions.items()
            if t.is_expired and t.status not in [PaymentStatus.COMPLETED, PaymentStatus.CANCELLED]
        ]
        
        for tid in expired_ids:
            self._transactions[tid].status = PaymentStatus.EXPIRED
            del self._transactions[tid]
        
        return len(expired_ids)
