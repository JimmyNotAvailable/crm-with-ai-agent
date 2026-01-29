"""
QR Code Generator - Tạo mã QR thanh toán
Hỗ trợ VietQR, MoMo, ZaloPay
"""
from typing import Optional
import urllib.parse


class QRGenerator:
    """
    Generator mã QR thanh toán cho các phương thức phổ biến tại VN
    """
    
    # VietQR bank codes
    BANK_CODES = {
        "VCB": "970436",  # Vietcombank
        "TCB": "970407",  # Techcombank
        "VPB": "970432",  # VPBank
        "MB": "970422",   # MB Bank
        "ACB": "970416",  # ACB
        "BIDV": "970418", # BIDV
        "VTB": "970415",  # Vietinbank
        "TPB": "970423",  # TPBank
        "STB": "970403",  # Sacombank
        "MSB": "970426",  # MSB
    }
    
    def generate_vietqr(
        self,
        bank_id: str,
        account_number: str,
        account_name: str,
        amount: float,
        message: str,
        template: str = "compact2"  # compact, compact2, qr_only
    ) -> str:
        """
        Tạo URL QR VietQR cho chuyển khoản ngân hàng.
        
        VietQR API: https://img.vietqr.io/image/{bank_id}-{account_no}-{template}.png
        
        Args:
            bank_id: Mã ngân hàng (VCB, TCB, ...)
            account_number: Số tài khoản
            account_name: Tên chủ tài khoản
            amount: Số tiền
            message: Nội dung chuyển khoản
            template: Template QR (compact, compact2, qr_only)
        
        Returns:
            URL hình ảnh QR code
        """
        bank_bin = self.BANK_CODES.get(bank_id.upper(), bank_id)
        
        # Encode message for URL
        encoded_message = urllib.parse.quote(message)
        encoded_name = urllib.parse.quote(account_name)
        
        # VietQR format
        qr_url = (
            f"https://img.vietqr.io/image/{bank_bin}-{account_number}-{template}.png"
            f"?amount={int(amount)}"
            f"&addInfo={encoded_message}"
            f"&accountName={encoded_name}"
        )
        
        return qr_url
    
    def generate_momo_qr(
        self,
        phone: str,
        amount: float,
        message: str
    ) -> str:
        """
        Tạo URL deep link MoMo.
        
        MoMo format: momo://app?action=transfer&phone={phone}&amount={amount}&note={note}
        
        Vì deep link không hiển thị được QR trực tiếp, 
        ta tạo QR từ nội dung deep link
        
        Args:
            phone: Số điện thoại nhận tiền
            amount: Số tiền
            message: Nội dung
            
        Returns:
            URL QR code (qr.io hoặc API tương tự)
        """
        encoded_message = urllib.parse.quote(message)
        
        # Deep link MoMo
        momo_link = f"momo://app?action=transfer&phone={phone}&amount={int(amount)}&note={encoded_message}"
        
        # Tạo QR từ deep link (dùng API miễn phí)
        encoded_link = urllib.parse.quote(momo_link)
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={encoded_link}"
        
        return qr_url
    
    def generate_zalopay_qr(
        self,
        amount: float,
        message: str,
        order_id: str
    ) -> str:
        """
        Tạo QR ZaloPay (demo - cần tích hợp SDK thực tế)
        
        Args:
            amount: Số tiền
            message: Nội dung
            order_id: Mã đơn hàng
            
        Returns:
            URL QR code
        """
        # ZaloPay cần tích hợp API thực tế
        # Demo: tạo QR text-based
        content = f"ZaloPay|{order_id}|{int(amount)}|{message}"
        encoded_content = urllib.parse.quote(content)
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={encoded_content}"
        
        return qr_url
    
    def generate_generic_qr(self, data: str, size: int = 300) -> str:
        """
        Tạo QR code generic từ bất kỳ dữ liệu nào
        
        Args:
            data: Dữ liệu cần encode vào QR
            size: Kích thước QR (pixels)
            
        Returns:
            URL hình ảnh QR
        """
        encoded_data = urllib.parse.quote(data)
        return f"https://api.qrserver.com/v1/create-qr-code/?size={size}x{size}&data={encoded_data}"


class PaymentQRBuilder:
    """
    Builder pattern để tạo QR thanh toán
    """
    
    def __init__(self):
        self._bank_id: Optional[str] = None
        self._account_number: Optional[str] = None
        self._account_name: Optional[str] = None
        self._amount: float = 0
        self._message: str = ""
        self._method: str = "BANK_TRANSFER"
        self._phone: Optional[str] = None
    
    def bank(self, bank_id: str) -> "PaymentQRBuilder":
        self._bank_id = bank_id
        return self
    
    def account(self, number: str, name: str) -> "PaymentQRBuilder":
        self._account_number = number
        self._account_name = name
        return self
    
    def amount(self, amount: float) -> "PaymentQRBuilder":
        self._amount = amount
        return self
    
    def message(self, msg: str) -> "PaymentQRBuilder":
        self._message = msg
        return self
    
    def method(self, method: str) -> "PaymentQRBuilder":
        self._method = method
        return self
    
    def phone(self, phone: str) -> "PaymentQRBuilder":
        self._phone = phone
        return self
    
    def build(self) -> str:
        """Build và trả về URL QR"""
        generator = QRGenerator()
        
        if self._method == "BANK_TRANSFER":
            return generator.generate_vietqr(
                bank_id=self._bank_id or "VCB",
                account_number=self._account_number or "",
                account_name=self._account_name or "",
                amount=self._amount,
                message=self._message
            )
        elif self._method == "MOMO":
            return generator.generate_momo_qr(
                phone=self._phone or "",
                amount=self._amount,
                message=self._message
            )
        else:
            return generator.generate_generic_qr(
                f"PAYMENT|{self._amount}|{self._message}"
            )
