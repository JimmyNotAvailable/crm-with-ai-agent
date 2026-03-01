"""
Comprehensive Seed Data Script for CRM-AI-Agent
Seeds all 7 microservices databases with realistic Vietnamese demo data.

Usage:
    python scripts/seed_data.py
    python scripts/seed_data.py --reset  # Drop & recreate tables first

Databases:
    1. Identity   (3310) - Users
    2. Product    (3311) - Products
    3. Order      (3312) - Orders, OrderItems, Carts, CartItems
    4. Support    (3313) - Tickets, TicketMessages
    5. Knowledge  (3314) - Conversations, ConversationMessages, KBArticles
    6. Analytics  (3315) - AuditLogs
    7. Marketing  (3316) - (future)
"""
import sys
import uuid
import random
from pathlib import Path
from datetime import datetime, timedelta

# ── Path setup ──────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from sqlalchemy.exc import IntegrityError
from backend.database.session import (
    IdentitySession, ProductSession, OrderSession,
    SupportSession, KnowledgeSession, AnalyticsSession,
    ENGINES, Base,
)
from backend.models.user import User, UserType, UserStatus
from backend.models.product import Product
from backend.models.order import Order, OrderItem, OrderStatus
from backend.models.ticket import (
    Ticket, TicketMessage,
    TicketStatus, TicketPriority, TicketCategory,
)
from backend.models.conversation import Conversation, ConversationMessage
from backend.models.kb_article import KBArticle
from backend.models.cart import Cart, CartItem
from backend.models.audit_log import AuditLog
from backend.utils.security import get_password_hash

# ════════════════════════════════════════════════════════════════════
# DETERMINISTIC UUIDs — pre-generated so cross-DB references work
# ════════════════════════════════════════════════════════════════════

# ── Users (Identity DB) ────────────────────────────────────────────
USER_IDS = {
    "admin":      "a0000000-0000-4000-8000-000000000001",
    "staff1":     "a0000000-0000-4000-8000-000000000002",
    "staff2":     "a0000000-0000-4000-8000-000000000003",
    "customer1":  "c0000000-0000-4000-8000-000000000001",
    "customer2":  "c0000000-0000-4000-8000-000000000002",
    "customer3":  "c0000000-0000-4000-8000-000000000003",
    "customer4":  "c0000000-0000-4000-8000-000000000004",
    "customer5":  "c0000000-0000-4000-8000-000000000005",
    "customer6":  "c0000000-0000-4000-8000-000000000006",
    "customer7":  "c0000000-0000-4000-8000-000000000007",
    "customer8":  "c0000000-0000-4000-8000-000000000008",
    "customer9":  "c0000000-0000-4000-8000-000000000009",
    "customer10": "c0000000-0000-4000-8000-000000000010",
}

# ── Products (Product DB) ──────────────────────────────────────────
PRODUCT_IDS = {f"prod{i}": f"p0000000-0000-4000-8000-{i:012d}" for i in range(1, 26)}

# ── Orders (Order DB) ──────────────────────────────────────────────
ORDER_IDS = {f"order{i}": f"d0000000-0000-4000-8000-{i:012d}" for i in range(1, 31)}
ORDER_ITEM_IDS = {f"oi{i}": f"e0000000-0000-4000-8000-{i:012d}" for i in range(1, 61)}

# ── Tickets (Support DB) ───────────────────────────────────────────
TICKET_IDS = {f"ticket{i}": f"f0000000-0000-4000-8000-{i:012d}" for i in range(1, 21)}
TICKET_MSG_IDS = {f"tm{i}": f"f1000000-0000-4000-8000-{i:012d}" for i in range(1, 41)}

# ── Conversations (Knowledge DB) ───────────────────────────────────
CONV_IDS = {f"conv{i}": f"b0000000-0000-4000-8000-{i:012d}" for i in range(1, 16)}
CONV_MSG_IDS = {f"cm{i}": f"b1000000-0000-4000-8000-{i:012d}" for i in range(1, 51)}
KB_IDS = {f"kb{i}": f"b2000000-0000-4000-8000-{i:012d}" for i in range(1, 11)}

# ── Audit Logs (Analytics DB) ──────────────────────────────────────
AUDIT_IDS = {f"audit{i}": f"10000000-0000-4000-8000-{i:012d}" for i in range(1, 21)}

# ── Carts (Order DB) ──────────────────────────────────────────────
CART_IDS = {f"cart{i}": f"ca000000-0000-4000-8000-{i:012d}" for i in range(1, 6)}
CART_ITEM_IDS = {f"ci{i}": f"cb000000-0000-4000-8000-{i:012d}" for i in range(1, 11)}


# ════════════════════════════════════════════════════════════════════
# HELPER
# ════════════════════════════════════════════════════════════════════

def ts(days_ago: int = 0, hours_ago: int = 0) -> datetime:
    """Generate a past datetime."""
    return datetime.utcnow() - timedelta(days=days_ago, hours=hours_ago)


def safe_add(session, obj, label: str):
    """Add object to session, skip on IntegrityError."""
    try:
        session.add(obj)
        session.flush()
        return True
    except IntegrityError:
        session.rollback()
        print(f"  [SKIP] {label} already exists")
        return False


# ════════════════════════════════════════════════════════════════════
# 1. IDENTITY DB — Users
# ════════════════════════════════════════════════════════════════════

def seed_users():
    print("\n{'='*60}")
    print("1. IDENTITY DB — Seeding Users")
    print("{'='*60}")
    db = IdentitySession()
    try:
        users = [
            # Admin
            User(
                id=USER_IDS["admin"],
                email="admin@crm-demo.com",
                password_hash=get_password_hash("admin123"),
                full_name="Nguyễn Văn Admin",
                user_type=UserType.ADMIN,
                status=UserStatus.ACTIVE,
                phone="0901000001",
                email_verified=True,
                locale="vi",
                timezone="Asia/Ho_Chi_Minh",
            ),
            # Staff
            User(
                id=USER_IDS["staff1"],
                email="staff1@crm-demo.com",
                password_hash=get_password_hash("staff123"),
                full_name="Trần Thị Hỗ Trợ",
                user_type=UserType.STAFF,
                status=UserStatus.ACTIVE,
                phone="0901000002",
                email_verified=True,
            ),
            User(
                id=USER_IDS["staff2"],
                email="staff2@crm-demo.com",
                password_hash=get_password_hash("staff123"),
                full_name="Lê Văn Kỹ Thuật",
                user_type=UserType.STAFF,
                status=UserStatus.ACTIVE,
                phone="0901000003",
                email_verified=True,
            ),
        ]

        # Customers
        customer_names = [
            ("Phạm Minh Khách", "0912000001"),
            ("Hoàng Thị Lan", "0912000002"),
            ("Vũ Đức Mạnh", "0912000003"),
            ("Ngô Thanh Hà", "0912000004"),
            ("Đỗ Quang Huy", "0912000005"),
            ("Bùi Thị Mai", "0912000006"),
            ("Lý Tuấn Anh", "0912000007"),
            ("Đinh Ngọc Ánh", "0912000008"),
            ("Trương Văn Nam", "0912000009"),
            ("Phan Thị Hương", "0912000010"),
        ]
        for i, (name, phone) in enumerate(customer_names, 1):
            users.append(User(
                id=USER_IDS[f"customer{i}"],
                email=f"customer{i}@crm-demo.com",
                password_hash=get_password_hash("customer123"),
                full_name=name,
                user_type=UserType.CUSTOMER,
                status=UserStatus.ACTIVE,
                phone=phone,
                email_verified=True,
            ))

        created = 0
        for u in users:
            existing = db.query(User).filter(User.id == u.id).first()
            if existing:
                print(f"  [SKIP] {u.email}")
                continue
            db.add(u)
            created += 1

        db.commit()
        print(f"  [OK] Created {created} users (password: admin123 / staff123 / customer123)")
    except Exception as e:
        db.rollback()
        print(f"  [ERROR] {e}")
    finally:
        db.close()


# ════════════════════════════════════════════════════════════════════
# 2. PRODUCT DB — Products
# ════════════════════════════════════════════════════════════════════

def seed_products():
    print("\n" + "=" * 60)
    print("2. PRODUCT DB — Seeding Products")
    print("=" * 60)
    db = ProductSession()
    try:
        products_data = [
            # Laptop
            ("Laptop Dell XPS 15",        "DELL-XPS15-2024",    "Laptop cao cấp Intel Core i9, RAM 32GB, SSD 1TB",            45000000, 12000000, 15, "Laptop",      True),
            ("MacBook Air M3",            "MBA-M3-2024",        "Laptop mỏng nhẹ chip Apple M3, RAM 16GB",                     35000000, 10000000, 20, "Laptop",      True),
            ("Lenovo ThinkPad X1 Carbon",  "TP-X1C-GEN12",      "Laptop doanh nhân siêu nhẹ, Intel Core Ultra 7",              38000000, 11000000, 12, "Laptop",      False),
            ("ASUS ROG Strix G16",        "ROG-G16-2024",       "Laptop gaming RTX 4070, AMD Ryzen 9",                          42000000, 13000000, 10, "Laptop",      True),
            ("HP Envy x360",              "HP-ENVY-X360",       "Laptop 2-in-1 màn hình cảm ứng OLED",                          28000000, 8000000,  18, "Laptop",      False),
            # Smartphone
            ("iPhone 15 Pro Max 256GB",   "IPHONE-15PM-256",    "Chip A17 Pro, camera 48MP, Titanium",                           32000000, 22000000, 25, "Smartphone",  True),
            ("Samsung Galaxy S24 Ultra",   "SAMSUNG-S24U-512",  "Snapdragon 8 Gen 3, camera 200MP, S Pen",                       28000000, 18000000, 30, "Smartphone",  True),
            ("Xiaomi 14 Ultra",            "XIAOMI-14U",        "Leica camera, Snapdragon 8 Gen 3",                              22000000, 12000000, 35, "Smartphone",  False),
            ("Google Pixel 8 Pro",         "PIXEL-8-PRO",       "Camera AI tốt nhất, chip Tensor G3",                            24000000, 15000000, 20, "Smartphone",  False),
            ("OPPO Find X7 Ultra",         "OPPO-FX7U",         "Camera Hasselblad, sạc nhanh 100W",                             26000000, 16000000, 22, "Smartphone",  False),
            # Tablet
            ("iPad Pro 12.9 inch M2",     "IPAD-PRO-129-M2",   "Chip M2, màn hình Liquid Retina XDR",                           28000000, 18000000, 18, "Tablet",      True),
            ("Samsung Galaxy Tab S9+",     "TAB-S9-PLUS",       "Snapdragon 8 Gen 2, S Pen, IP68",                               22000000, 14000000, 15, "Tablet",      False),
            ("iPad Air M2",               "IPAD-AIR-M2",        "Chip M2, hỗ trợ Apple Pencil Pro",                              18000000, 11000000, 25, "Tablet",      True),
            # Phụ kiện
            ("Sony WH-1000XM5",           "SONY-WH1000XM5",    "Tai nghe chống ồn chủ động cao cấp",                            8500000,  3500000,  40, "Phụ kiện",    True),
            ("AirPods Pro 2",             "AIRPODS-PRO2",       "Chip H2, chống ồn thích ứng, USB-C",                            6800000,  3000000,  50, "Phụ kiện",    True),
            ("Samsung Galaxy Buds3 Pro",   "BUDS3-PRO",         "Tai nghe TWS chống ồn, codec 360 Audio",                        5500000,  2500000,  45, "Phụ kiện",    False),
            ("Apple Watch Ultra 2",        "AW-ULTRA2",         "Đồng hồ thông minh siêu bền, GPS",                             21000000, 12000000, 12, "Smartwatch",  True),
            ("Samsung Galaxy Watch 6",     "GW6-CLASSIC",       "Wear OS, đo huyết áp, ECG",                                    8000000,  4000000,  30, "Smartwatch",  False),
            # Màn hình
            ("Dell UltraSharp U2723QE",    "DELL-U2723QE",      "Màn hình 4K 27 inch, USB-C 90W",                                14000000, 7000000,  20, "Màn hình",    False),
            ("LG UltraGear 27GP850-B",     "LG-27GP850",        "Màn hình gaming 165Hz, Nano IPS",                               12000000, 6000000,  15, "Màn hình",    True),
            # Phím chuột
            ("Logitech MX Master 3S",      "LOGI-MX3S",         "Chuột ergonomic, kết nối 3 thiết bị",                           2500000,  1200000,  60, "Phụ kiện",    False),
            ("Keychron K8 Pro",            "KEYCHRON-K8P",       "Bàn phím cơ không dây, Gateron Pro",                            2800000,  1400000,  40, "Phụ kiện",    False),
            # Lưu trữ
            ("Samsung T7 Shield 2TB",      "SAMSUNG-T7S-2TB",   "Ổ cứng di động SSD, chống nước IP65",                           4500000,  2500000,  35, "Lưu trữ",    False),
            ("WD My Passport 4TB",         "WD-MP-4TB",          "Ổ cứng di động HDD, bảo mật phần cứng",                       3200000,  1800000,  50, "Lưu trữ",    False),
            # Sạc
            ("Anker 737 GaNPrime 120W",    "ANKER-737-120W",    "Sạc nhanh 120W, 3 cổng USB-C + USB-A",                         1800000,  800000,   70, "Phụ kiện",    False),
        ]

        created = 0
        for i, (name, sku, desc, price, cost, stock, cat, featured) in enumerate(products_data, 1):
            pid = PRODUCT_IDS[f"prod{i}"]
            existing = db.query(Product).filter(Product.id == pid).first()
            if existing:
                print(f"  [SKIP] {sku}")
                continue
            db.add(Product(
                id=pid,
                sku=sku,
                name=name,
                description=desc,
                price=price,
                cost=cost,
                stock_quantity=stock,
                category=cat,
                is_active=True,
                is_featured=featured,
            ))
            created += 1

        db.commit()
        print(f"  [OK] Created {created} products")
    except Exception as e:
        db.rollback()
        print(f"  [ERROR] {e}")
    finally:
        db.close()


# ════════════════════════════════════════════════════════════════════
# 3. ORDER DB — Orders, OrderItems, Carts
# ════════════════════════════════════════════════════════════════════

def seed_orders():
    print("\n" + "=" * 60)
    print("3. ORDER DB — Seeding Orders, OrderItems, Carts")
    print("=" * 60)
    db = OrderSession()
    try:
        customer_ids = [USER_IDS[f"customer{i}"] for i in range(1, 11)]
        product_keys = list(PRODUCT_IDS.keys())
        statuses = list(OrderStatus)
        payment_methods = ["COD", "BANK_TRANSFER", "MOMO", "VNPAY", "CREDIT_CARD"]
        cities = ["Hồ Chí Minh", "Hà Nội", "Đà Nẵng", "Cần Thơ", "Hải Phòng", "Huế"]

        # Product price map (matching seed_products above)
        product_prices = {
            "prod1": 45000000, "prod2": 35000000, "prod3": 38000000,
            "prod4": 42000000, "prod5": 28000000, "prod6": 32000000,
            "prod7": 28000000, "prod8": 22000000, "prod9": 24000000,
            "prod10": 26000000, "prod11": 28000000, "prod12": 22000000,
            "prod13": 18000000, "prod14": 8500000, "prod15": 6800000,
            "prod16": 5500000, "prod17": 21000000, "prod18": 8000000,
            "prod19": 14000000, "prod20": 12000000, "prod21": 2500000,
            "prod22": 2800000, "prod23": 4500000, "prod24": 3200000,
            "prod25": 1800000,
        }
        product_names = {
            "prod1": "Laptop Dell XPS 15", "prod2": "MacBook Air M3",
            "prod3": "Lenovo ThinkPad X1 Carbon", "prod4": "ASUS ROG Strix G16",
            "prod5": "HP Envy x360", "prod6": "iPhone 15 Pro Max 256GB",
            "prod7": "Samsung Galaxy S24 Ultra", "prod8": "Xiaomi 14 Ultra",
            "prod9": "Google Pixel 8 Pro", "prod10": "OPPO Find X7 Ultra",
            "prod11": "iPad Pro 12.9 inch M2", "prod12": "Samsung Galaxy Tab S9+",
            "prod13": "iPad Air M2", "prod14": "Sony WH-1000XM5",
            "prod15": "AirPods Pro 2", "prod16": "Samsung Galaxy Buds3 Pro",
            "prod17": "Apple Watch Ultra 2", "prod18": "Samsung Galaxy Watch 6",
            "prod19": "Dell UltraSharp U2723QE", "prod20": "LG UltraGear 27GP850-B",
            "prod21": "Logitech MX Master 3S", "prod22": "Keychron K8 Pro",
            "prod23": "Samsung T7 Shield 2TB", "prod24": "WD My Passport 4TB",
            "prod25": "Anker 737 GaNPrime 120W",
        }

        random.seed(42)  # Reproducible data
        oi_counter = 0
        created_orders = 0

        for i in range(1, 31):
            oid = ORDER_IDS[f"order{i}"]
            existing = db.query(Order).filter(Order.id == oid).first()
            if existing:
                print(f"  [SKIP] ORD-{i:04d}")
                continue

            cust = random.choice(customer_ids)
            days_ago = random.randint(1, 120)
            order_status = random.choice(statuses)

            # Pick 1-3 products per order
            num_items = random.randint(1, 3)
            selected_prods = random.sample(product_keys, num_items)

            total = 0.0
            items = []
            for pk in selected_prods:
                oi_counter += 1
                qty = random.randint(1, 2)
                price = product_prices[pk]
                subtotal = price * qty
                total += subtotal
                items.append(OrderItem(
                    id=ORDER_ITEM_IDS[f"oi{oi_counter}"],
                    order_id=oid,
                    product_id=PRODUCT_IDS[pk],
                    product_name=product_names[pk],
                    product_sku=pk.upper(),
                    quantity=qty,
                    unit_price=price,
                    subtotal=subtotal,
                ))

            shipping_fee = 30000 if total < 5000000 else 0
            tax = round(total * 0.08, 0)

            order = Order(
                id=oid,
                order_number=f"ORD-2025-{i:04d}",
                customer_id=cust,
                status=order_status,
                total_amount=total + shipping_fee + tax,
                tax_amount=tax,
                shipping_fee=shipping_fee,
                discount_amount=0,
                shipping_address=f"Số {random.randint(1, 200)} Đường Nguyễn Huệ",
                shipping_city=random.choice(cities),
                shipping_phone=f"09{random.randint(10000000, 99999999)}",
                payment_method=random.choice(payment_methods),
                payment_status="PAID" if order_status in (OrderStatus.CONFIRMED, OrderStatus.SHIPPED, OrderStatus.DELIVERED) else "PENDING",
                created_at=ts(days_ago),
            )
            db.add(order)
            for item in items:
                db.add(item)
            created_orders += 1

        # ── Carts ──
        created_carts = 0
        ci_counter = 0
        for i in range(1, 6):
            cart_id = CART_IDS[f"cart{i}"]
            existing = db.query(Cart).filter(Cart.id == cart_id).first()
            if existing:
                continue
            cart = Cart(
                id=cart_id,
                user_id=USER_IDS[f"customer{i}"],
            )
            db.add(cart)
            # Add 1-2 items to each cart
            for j in range(random.randint(1, 2)):
                ci_counter += 1
                pk = random.choice(product_keys)
                db.add(CartItem(
                    id=CART_ITEM_IDS[f"ci{ci_counter}"],
                    cart_id=cart_id,
                    product_id=PRODUCT_IDS[pk],
                    quantity=random.randint(1, 2),
                ))
            created_carts += 1

        db.commit()
        print(f"  [OK] Created {created_orders} orders, {oi_counter} order items, {created_carts} carts")
    except Exception as e:
        db.rollback()
        print(f"  [ERROR] {e}")
        import traceback; traceback.print_exc()
    finally:
        db.close()


# ════════════════════════════════════════════════════════════════════
# 4. SUPPORT DB — Tickets, TicketMessages
# ════════════════════════════════════════════════════════════════════

def seed_tickets():
    print("\n" + "=" * 60)
    print("4. SUPPORT DB — Seeding Tickets & Messages")
    print("=" * 60)
    db = SupportSession()
    try:
        ticket_data = [
            ("Đơn hàng bị chậm giao",           TicketCategory.ORDER_ISSUE,        TicketPriority.HIGH,   TicketStatus.OPEN,        "customer1", -0.6, "NEGATIVE"),
            ("Hỏi về chính sách đổi trả",        TicketCategory.GENERAL_INQUIRY,    TicketPriority.MEDIUM, TicketStatus.RESOLVED,    "customer2",  0.2, "NEUTRAL"),
            ("Sản phẩm không đúng mô tả",        TicketCategory.COMPLAINT,          TicketPriority.HIGH,   TicketStatus.IN_PROGRESS, "customer3", -0.8, "NEGATIVE"),
            ("Laptop bị lỗi màn hình",           TicketCategory.TECHNICAL_SUPPORT,  TicketPriority.URGENT, TicketStatus.OPEN,        "customer1", -0.5, "NEGATIVE"),
            ("Muốn hoàn tiền đơn hàng",          TicketCategory.REFUND_REQUEST,     TicketPriority.HIGH,   TicketStatus.WAITING_CUSTOMER, "customer4", -0.3, "NEGATIVE"),
            ("Hỏi về bảo hành iPhone",           TicketCategory.PRODUCT_QUESTION,   TicketPriority.LOW,    TicketStatus.RESOLVED,    "customer5",  0.5, "POSITIVE"),
            ("Không nhận được mã thanh toán",     TicketCategory.TECHNICAL_SUPPORT,  TicketPriority.MEDIUM, TicketStatus.OPEN,        "customer6", -0.2, "NEUTRAL"),
            ("Cảm ơn đội ngũ hỗ trợ",            TicketCategory.GENERAL_INQUIRY,    TicketPriority.LOW,    TicketStatus.CLOSED,      "customer2",  0.9, "POSITIVE"),
            ("Sản phẩm thiếu phụ kiện",          TicketCategory.ORDER_ISSUE,        TicketPriority.MEDIUM, TicketStatus.IN_PROGRESS, "customer7", -0.4, "NEGATIVE"),
            ("Hỏi về chương trình khuyến mãi",   TicketCategory.GENERAL_INQUIRY,    TicketPriority.LOW,    TicketStatus.RESOLVED,    "customer8",  0.3, "NEUTRAL"),
            ("Giao hàng sai địa chỉ",            TicketCategory.ORDER_ISSUE,        TicketPriority.HIGH,   TicketStatus.OPEN,        "customer9", -0.7, "NEGATIVE"),
            ("Tư vấn chọn laptop lập trình",     TicketCategory.PRODUCT_QUESTION,   TicketPriority.LOW,    TicketStatus.RESOLVED,    "customer10", 0.4, "POSITIVE"),
            ("Yêu cầu xuất hóa đơn VAT",         TicketCategory.GENERAL_INQUIRY,    TicketPriority.MEDIUM, TicketStatus.WAITING_CUSTOMER, "customer3",  0.1, "NEUTRAL"),
            ("Tai nghe lỗi 1 bên",               TicketCategory.TECHNICAL_SUPPORT,  TicketPriority.MEDIUM, TicketStatus.OPEN,        "customer5", -0.5, "NEGATIVE"),
            ("Đánh giá 5 sao cho dịch vụ",       TicketCategory.GENERAL_INQUIRY,    TicketPriority.LOW,    TicketStatus.CLOSED,      "customer6",  0.95,"POSITIVE"),
            ("Pin điện thoại sụt nhanh",          TicketCategory.TECHNICAL_SUPPORT,  TicketPriority.MEDIUM, TicketStatus.IN_PROGRESS, "customer4", -0.3, "NEGATIVE"),
            ("Hỏi về gói trả góp 0%",            TicketCategory.GENERAL_INQUIRY,    TicketPriority.LOW,    TicketStatus.RESOLVED,    "customer7",  0.2, "NEUTRAL"),
            ("Đổi màu sản phẩm đã đặt",          TicketCategory.ORDER_ISSUE,        TicketPriority.MEDIUM, TicketStatus.OPEN,        "customer8", -0.1, "NEUTRAL"),
            ("Cập nhật thông tin giao hàng",      TicketCategory.ORDER_ISSUE,        TicketPriority.LOW,    TicketStatus.RESOLVED,    "customer9",  0.0, "NEUTRAL"),
            ("Máy tính bảng không bật được",      TicketCategory.TECHNICAL_SUPPORT,  TicketPriority.URGENT, TicketStatus.OPEN,        "customer10",-0.6, "NEGATIVE"),
        ]

        # Message templates per ticket
        msg_templates = [
            ("Chào bạn, tôi gặp vấn đề với {subject}. Mong được hỗ trợ sớm.", False, False),
            ("Chào bạn, cảm ơn bạn đã liên hệ. Chúng tôi đang kiểm tra và sẽ phản hồi sớm.", True, False),
        ]

        created_tickets = 0
        tm_counter = 0
        for i, (subject, cat, priority, st, cust_key, sentiment, label) in enumerate(ticket_data, 1):
            tid = TICKET_IDS[f"ticket{i}"]
            existing = db.query(Ticket).filter(Ticket.id == tid).first()
            if existing:
                print(f"  [SKIP] TK-{i:04d}")
                continue

            days_ago = random.randint(1, 60)
            ticket = Ticket(
                id=tid,
                ticket_number=f"TK-2025-{i:04d}",
                customer_id=USER_IDS[cust_key],
                assigned_to=USER_IDS[random.choice(["staff1", "staff2"])],
                subject=subject,
                category=cat,
                status=st,
                priority=priority,
                sentiment_score=sentiment,
                sentiment_label=label,
                channel="WEB",
                created_at=ts(days_ago),
                resolved_at=ts(days_ago - 1) if st in (TicketStatus.RESOLVED, TicketStatus.CLOSED) else None,
                closed_at=ts(days_ago - 1) if st == TicketStatus.CLOSED else None,
            )
            db.add(ticket)

            # Add 2 messages per ticket
            for msg_text, is_staff, is_ai in msg_templates:
                tm_counter += 1
                if tm_counter > 40:
                    break
                db.add(TicketMessage(
                    id=TICKET_MSG_IDS[f"tm{tm_counter}"],
                    ticket_id=tid,
                    sender_id=USER_IDS["staff1"] if is_staff else USER_IDS[cust_key],
                    is_staff=1 if is_staff else 0,
                    is_ai_generated=1 if is_ai else 0,
                    message=msg_text.format(subject=subject.lower()),
                    created_at=ts(days_ago, hours_ago=2 if is_staff else 0),
                ))
            created_tickets += 1

        db.commit()
        print(f"  [OK] Created {created_tickets} tickets, {tm_counter} messages")
    except Exception as e:
        db.rollback()
        print(f"  [ERROR] {e}")
        import traceback; traceback.print_exc()
    finally:
        db.close()


# ════════════════════════════════════════════════════════════════════
# 5. KNOWLEDGE DB — Conversations, KBArticles
# ════════════════════════════════════════════════════════════════════

def seed_knowledge():
    print("\n" + "=" * 60)
    print("5. KNOWLEDGE DB — Seeding Conversations & KB Articles")
    print("=" * 60)
    db = KnowledgeSession()
    try:
        # ── Conversations ──
        conv_scenarios = [
            ("customer1", "Tư vấn laptop cho lập trình", [
                ("user", "Cho mình hỏi laptop nào tốt cho lập trình Python và AI?"),
                ("assistant", "Dạ, em xin tư vấn một số dòng laptop phù hợp cho lập trình:\n1. MacBook Air M3 - 35 triệu: Chip M3 mạnh mẽ, pin lâu\n2. Dell XPS 15 - 45 triệu: Màn hình đẹp, hiệu năng cao\n3. Lenovo ThinkPad X1 Carbon - 38 triệu: Nhẹ, bàn phím tốt"),
                ("user", "MacBook Air M3 có chạy được Docker không?"),
                ("assistant", "Dạ, MacBook Air M3 chạy Docker rất tốt ạ. Chip M3 hỗ trợ ảo hóa phần cứng, RAM 16GB đủ để chạy nhiều container đồng thời."),
            ]),
            ("customer2", "Hỏi về chính sách bảo hành", [
                ("user", "Chính sách bảo hành của shop như thế nào?"),
                ("assistant", "Dạ, chính sách bảo hành của chúng tôi:\n- Bảo hành 12 tháng theo hãng\n- Đổi trả trong 7 ngày nếu lỗi từ nhà sản xuất\n- Hỗ trợ sửa chữa sau bảo hành với giá ưu đãi"),
            ]),
            ("customer3", "So sánh iPhone vs Samsung", [
                ("user", "iPhone 15 Pro Max với Samsung S24 Ultra cái nào tốt hơn?"),
                ("assistant", "Dạ, cả hai đều là flagship tuyệt vời. Em so sánh nhanh:\n- iPhone 15 Pro Max: Camera ổn định, hệ sinh thái Apple, chip A17 Pro\n- Samsung S24 Ultra: Camera 200MP, S Pen, Galaxy AI\nTùy vào nhu cầu sử dụng của anh/chị ạ."),
                ("user", "Mình muốn chụp ảnh đẹp, chọn cái nào?"),
                ("assistant", "Nếu ưu tiên chụp ảnh, em gợi ý Samsung S24 Ultra ạ. Camera 200MP cho độ chi tiết cao, AI xử lý ảnh thông minh, và chế độ Nightography chụp đêm rất tốt."),
            ]),
            ("customer4", "Đặt hàng tablet", [
                ("user", "Cho mình xem iPad Pro 12.9 inch"),
                ("assistant", "Dạ, iPad Pro 12.9 inch M2 hiện có giá 28,000,000đ. Máy trang bị chip M2, màn hình Liquid Retina XDR, còn 18 sản phẩm trong kho ạ."),
            ]),
            ("customer5", "Hỏi phụ kiện tai nghe", [
                ("user", "Tai nghe chống ồn nào tốt nhất hiện tại?"),
                ("assistant", "Dạ, top tai nghe chống ồn:\n1. Sony WH-1000XM5 (8.5 triệu) - Chống ồn tốt nhất\n2. AirPods Pro 2 (6.8 triệu) - Tốt nhất cho iPhone\n3. Samsung Galaxy Buds3 Pro (5.5 triệu) - Giá tốt nhất"),
                ("user", "Mình dùng iPhone, nên mua cái nào?"),
                ("assistant", "Nếu dùng iPhone, em khuyên AirPods Pro 2 ạ. Kết nối seamless với hệ sinh thái Apple, âm thanh Spatial Audio, và chống ồn thích ứng rất tốt."),
            ]),
            ("customer6", "Tra cứu đơn hàng", [
                ("user", "Tra cứu đơn hàng ORD-2025-0001"),
                ("assistant", "Dạ, đơn hàng ORD-2025-0001 hiện đang ở trạng thái PENDING. Đơn hàng sẽ được xử lý trong 24h tới ạ."),
            ]),
            ("customer7", "Tư vấn màn hình", [
                ("user", "Mình cần mua màn hình cho thiết kế đồ họa"),
                ("assistant", "Dạ, em gợi ý Dell UltraSharp U2723QE (14 triệu). Màn hình 4K 27 inch, độ phủ màu 98% DCI-P3, cổng USB-C 90W rất tiện cho laptop ạ."),
            ]),
            ("customer8", "Hỏi về thanh toán", [
                ("user", "Shop hỗ trợ những phương thức thanh toán nào?"),
                ("assistant", "Dạ, chúng tôi hỗ trợ:\n1. COD - Thanh toán khi nhận hàng\n2. Chuyển khoản ngân hàng (VietQR)\n3. Ví MoMo\n4. VNPay\n5. Thẻ tín dụng Visa/Mastercard"),
            ]),
            ("customer9", "Khiếu nại giao hàng", [
                ("user", "Đơn hàng giao sai địa chỉ rồi, làm sao giờ?"),
                ("assistant", "Dạ, em rất xin lỗi về sự bất tiện này. Em đã tạo ticket hỗ trợ TK-2025-0011 cho anh/chị. Đội ngũ giao hàng sẽ liên hệ lại trong 2 giờ tới để sắp xếp giao lại ạ."),
            ]),
            ("customer10", "Tư vấn gaming laptop", [
                ("user", "Laptop gaming nào chơi được Cyberpunk 2077?"),
                ("assistant", "Dạ, ASUS ROG Strix G16 (42 triệu) là lựa chọn tốt nhất ạ. RTX 4070 + AMD Ryzen 9, chơi Cyberpunk 2077 ở Ultra settings 60+ FPS ạ."),
                ("user", "Có khuyến mãi gì không?"),
                ("assistant", "Dạ, hiện tại ROG Strix G16 đang có ưu đãi tặng kèm chuột Logitech MX Master 3S (trị giá 2.5 triệu) khi mua trước ngày 28/02/2025 ạ."),
            ]),
        ]

        cm_counter = 0
        created_convs = 0
        for i, (cust_key, title, messages) in enumerate(conv_scenarios, 1):
            conv_id = CONV_IDS[f"conv{i}"]
            existing = db.query(Conversation).filter(Conversation.id == conv_id).first()
            if existing:
                print(f"  [SKIP] conv-{i}")
                continue

            conv = Conversation(
                id=conv_id,
                user_id=USER_IDS[cust_key],
                title=title,
                created_at=ts(random.randint(1, 30)),
            )
            db.add(conv)

            for role, content in messages:
                cm_counter += 1
                if cm_counter > 50:
                    break
                db.add(ConversationMessage(
                    id=CONV_MSG_IDS[f"cm{cm_counter}"],
                    conversation_id=conv_id,
                    role=role,
                    content=content,
                ))
            created_convs += 1

        # ── KB Articles ──
        kb_data = [
            ("Chính sách đổi trả hàng", "POLICY", "Khách hàng được đổi trả trong 7 ngày kể từ ngày nhận hàng. Sản phẩm phải còn nguyên seal, chưa qua sử dụng. Hoàn tiền trong 3-5 ngày làm việc."),
            ("Hướng dẫn thanh toán VietQR", "GUIDE", "Bước 1: Chọn sản phẩm. Bước 2: Nhấn Đặt hàng. Bước 3: Chọn Chuyển khoản ngân hàng. Bước 4: Quét mã QR bằng app ngân hàng."),
            ("Chính sách bảo hành", "POLICY", "Tất cả sản phẩm được bảo hành 12 tháng theo hãng. Phụ kiện bảo hành 6 tháng. Lỗi người dùng không thuộc phạm vi bảo hành."),
            ("FAQ - Giao hàng", "FAQ", "Q: Thời gian giao hàng? A: Nội thành 1-2 ngày, ngoại thành 3-5 ngày. Q: Phí ship? A: Miễn phí cho đơn trên 5 triệu."),
            ("Hướng dẫn chọn laptop", "GUIDE", "Dựa trên nhu cầu: Văn phòng → MacBook Air, Lập trình → Dell XPS / ThinkPad, Gaming → ROG Strix, Thiết kế → MacBook Pro."),
            ("Chính sách trả góp 0%", "POLICY", "Áp dụng cho đơn từ 3 triệu. Kỳ hạn 6-12 tháng. Thẻ tín dụng Visa/Mastercard. Không phụ phí."),
            ("FAQ - Tài khoản", "FAQ", "Q: Quên mật khẩu? A: Nhấn 'Quên mật khẩu' và nhập email. Q: Đổi email? A: Liên hệ hỗ trợ qua ticket."),
            ("Hướng dẫn sử dụng AI Chat", "GUIDE", "Bạn có thể hỏi AI về: sản phẩm, giá cả, chính sách, tra cứu đơn hàng, so sánh sản phẩm. Gõ câu hỏi và AI sẽ trả lời ngay."),
            ("Chương trình khách hàng VIP", "POLICY", "Tổng chi tiêu > 10 triệu → Hạng VIP. Ưu đãi: giảm 5% mọi đơn, giao hàng ưu tiên, hỗ trợ 24/7."),
            ("FAQ - Sản phẩm", "FAQ", "Q: Hàng chính hãng? A: 100% chính hãng, có tem bảo hành. Q: Giá có thay đổi? A: Giá có thể thay đổi theo chương trình khuyến mãi."),
        ]

        created_kb = 0
        for i, (title, cat, content) in enumerate(kb_data, 1):
            kb_id = KB_IDS[f"kb{i}"]
            existing = db.query(KBArticle).filter(KBArticle.id == kb_id).first()
            if existing:
                continue
            db.add(KBArticle(
                id=kb_id,
                title=title,
                category=cat,
                body=content,
                is_published=True,
                uploaded_by=USER_IDS["admin"],
            ))
            created_kb += 1

        db.commit()
        print(f"  [OK] Created {created_convs} conversations, {cm_counter} messages, {created_kb} KB articles")
    except Exception as e:
        db.rollback()
        print(f"  [ERROR] {e}")
        import traceback; traceback.print_exc()
    finally:
        db.close()


# ════════════════════════════════════════════════════════════════════
# 6. ANALYTICS DB — AuditLogs
# ════════════════════════════════════════════════════════════════════

def seed_audit_logs():
    print("\n" + "=" * 60)
    print("6. ANALYTICS DB — Seeding Audit Logs")
    print("=" * 60)
    db = AnalyticsSession()
    try:
        logs_data = [
            (USER_IDS["admin"],     "LOGIN",  "User",    USER_IDS["admin"],     "POST", "/auth/login",     "SUCCESS"),
            (USER_IDS["staff1"],    "LOGIN",  "User",    USER_IDS["staff1"],    "POST", "/auth/login",     "SUCCESS"),
            (USER_IDS["customer1"], "LOGIN",  "User",    USER_IDS["customer1"], "POST", "/auth/login",     "SUCCESS"),
            (USER_IDS["customer1"], "CREATE", "Order",   ORDER_IDS["order1"],   "POST", "/orders",         "SUCCESS"),
            (USER_IDS["customer2"], "CREATE", "Order",   ORDER_IDS["order2"],   "POST", "/orders",         "SUCCESS"),
            (USER_IDS["customer1"], "CREATE", "Ticket",  TICKET_IDS["ticket1"], "POST", "/tickets",        "SUCCESS"),
            (USER_IDS["customer3"], "CREATE", "Ticket",  TICKET_IDS["ticket3"], "POST", "/tickets",        "SUCCESS"),
            (USER_IDS["staff1"],    "UPDATE", "Ticket",  TICKET_IDS["ticket2"], "PUT",  "/tickets/2",      "SUCCESS"),
            (USER_IDS["admin"],     "CREATE", "Product", PRODUCT_IDS["prod1"],  "POST", "/products",       "SUCCESS"),
            (USER_IDS["admin"],     "UPDATE", "Product", PRODUCT_IDS["prod6"],  "PUT",  "/products/6",     "SUCCESS"),
            (USER_IDS["customer4"], "CREATE", "Order",   ORDER_IDS["order5"],   "POST", "/orders",         "SUCCESS"),
            (USER_IDS["customer5"], "READ",   "Product", PRODUCT_IDS["prod14"], "GET",  "/products/14",    "SUCCESS"),
            (None,                  "READ",   "System",  None,                  "GET",  "/health",         "SUCCESS"),
            (USER_IDS["customer2"], "LOGIN",  "User",    USER_IDS["customer2"], "POST", "/auth/login",     "FAILED"),
            (USER_IDS["customer6"], "CREATE", "Conversation", CONV_IDS["conv6"], "POST", "/rag/chat",      "SUCCESS"),
            (USER_IDS["admin"],     "DELETE", "Product", PRODUCT_IDS["prod25"], "DELETE","/products/25",   "SUCCESS"),
            (USER_IDS["staff2"],    "UPDATE", "Ticket",  TICKET_IDS["ticket4"], "PUT",  "/tickets/4",      "SUCCESS"),
            (USER_IDS["customer7"], "CREATE", "Cart",    CART_IDS["cart3"],      "POST", "/cart/add",       "SUCCESS"),
            (USER_IDS["customer8"], "READ",   "Order",   ORDER_IDS["order10"],  "GET",  "/orders/10",      "SUCCESS"),
            (USER_IDS["admin"],     "CREATE", "KBArticle", KB_IDS["kb1"],       "POST", "/kb-articles",    "SUCCESS"),
        ]

        created = 0
        for i, (user_id, action, res_type, res_id, method, endpoint, stat) in enumerate(logs_data, 1):
            aid = AUDIT_IDS[f"audit{i}"]
            existing = db.query(AuditLog).filter(AuditLog.id == aid).first()
            if existing:
                continue
            db.add(AuditLog(
                id=aid,
                user_id=user_id,
                action=action,
                resource_type=res_type,
                resource_id=res_id,
                method=method,
                endpoint=endpoint,
                ip_address=f"192.168.1.{random.randint(1, 254)}",
                status=stat,
                duration_ms=random.randint(10, 500),
                created_at=ts(random.randint(1, 30), hours_ago=random.randint(0, 23)),
            ))
            created += 1

        db.commit()
        print(f"  [OK] Created {created} audit logs")
    except Exception as e:
        db.rollback()
        print(f"  [ERROR] {e}")
        import traceback; traceback.print_exc()
    finally:
        db.close()


# ════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════

def create_tables():
    """Create tables on all engines that have models."""
    print("\n" + "=" * 60)
    print("CREATING TABLES (if not exist)")
    print("=" * 60)
    engine_names = {
        "identity": "Identity DB (Users)",
        "product": "Product DB",
        "order": "Order DB (Orders, Carts)",
        "support": "Support DB (Tickets)",
        "knowledge": "Knowledge DB (Conversations, KB)",
        "analytics": "Analytics DB (AuditLogs)",
    }
    for name, label in engine_names.items():
        eng = ENGINES.get(name)
        if eng:
            try:
                Base.metadata.create_all(bind=eng)
                print(f"  [OK] {label}")
            except Exception as e:
                print(f"  [WARN] {label}: {e}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Seed CRM-AI-Agent databases")
    parser.add_argument("--reset", action="store_true", help="Drop & recreate all tables before seeding")
    args = parser.parse_args()

    print("╔══════════════════════════════════════════════════════════╗")
    print("║   CRM-AI-Agent — Seed Data Script (7 Microservices)    ║")
    print("╚══════════════════════════════════════════════════════════╝")

    if args.reset:
        print("\n⚠️  RESET MODE — Dropping all tables first!")
        for name, eng in ENGINES.items():
            if eng:
                try:
                    Base.metadata.drop_all(bind=eng)
                    print(f"  [OK] Dropped tables on {name}")
                except Exception as e:
                    print(f"  [WARN] {name}: {e}")

    create_tables()
    seed_users()
    seed_products()
    seed_orders()
    seed_tickets()
    seed_knowledge()
    seed_audit_logs()

    print("\n" + "=" * 60)
    print("✅ SEED COMPLETE!")
    print("=" * 60)
    print("\nLogin credentials:")
    print("  Admin:    admin@crm-demo.com / admin123")
    print("  Staff:    staff1@crm-demo.com / staff123")
    print("  Customer: customer1@crm-demo.com / customer123")
    print(f"\nTotal seeded: 13 users, 25 products, 30 orders, 20 tickets,")
    print(f"  10 conversations, 10 KB articles, 20 audit logs, 5 carts")


if __name__ == "__main__":
    main()
