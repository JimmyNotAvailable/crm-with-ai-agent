-- =============================================================================
-- CRM-AI-Agent Database Initialization Script
-- Chạy sau khi Docker MySQL khởi động
-- =============================================================================

-- Sử dụng database chính
CREATE DATABASE IF NOT EXISTS crm_ai_db 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

USE crm_ai_db;

-- =============================================================================
-- USERS TABLE (Compatible with SQLAlchemy models - Integer ID)
-- =============================================================================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(320) NOT NULL UNIQUE,
    username VARCHAR(100) NULL,
    password_hash TEXT NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(50) NULL,
    avatar_url TEXT NULL,
    role ENUM('ADMIN', 'STAFF', 'CUSTOMER') DEFAULT 'CUSTOMER' NOT NULL,
    status ENUM('ACTIVE', 'LOCKED', 'PENDING') DEFAULT 'ACTIVE' NOT NULL,
    is_verified TINYINT(1) DEFAULT 0 NOT NULL,
    created_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    updated_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) NOT NULL,
    INDEX idx_users_email (email),
    INDEX idx_users_role (role),
    INDEX idx_users_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- PRODUCTS TABLE (Compatible with SQLAlchemy models - Integer ID)
-- =============================================================================
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sku VARCHAR(128) NOT NULL UNIQUE,
    name VARCHAR(500) NOT NULL,
    price DECIMAL(15, 2) NOT NULL CHECK (price >= 0),
    original_price DECIMAL(15, 2) NULL,
    discount_percent INT DEFAULT 0,
    description TEXT NULL,
    image_url TEXT NULL,
    category VARCHAR(255) NULL,
    brand VARCHAR(255) NULL,
    stock_quantity INT DEFAULT 100 NOT NULL,
    is_active TINYINT(1) DEFAULT 1 NOT NULL,
    in_stock TINYINT(1) DEFAULT 1 NOT NULL,
    source_url TEXT NULL,
    created_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    updated_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) NOT NULL,
    INDEX idx_products_category (category),
    INDEX idx_products_brand (brand),
    INDEX idx_products_price (price),
    INDEX idx_products_active (is_active),
    FULLTEXT INDEX ft_products_name (name),
    FULLTEXT INDEX ft_products_desc (description)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- CARTS TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS carts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    created_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    updated_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) NOT NULL,
    CONSTRAINT fk_carts_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE INDEX idx_carts_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- CART_ITEMS TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS cart_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cart_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT DEFAULT 1 NOT NULL CHECK (quantity > 0),
    added_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    CONSTRAINT fk_cartitems_cart FOREIGN KEY (cart_id) REFERENCES carts(id) ON DELETE CASCADE,
    CONSTRAINT fk_cartitems_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    UNIQUE INDEX idx_cartitems_cart_product (cart_id, product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- ORDERS TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_number VARCHAR(50) NOT NULL UNIQUE,
    customer_id INT NOT NULL,
    status ENUM('PENDING', 'CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'CANCELLED', 'REFUNDED') DEFAULT 'PENDING' NOT NULL,
    total_amount DECIMAL(15, 2) DEFAULT 0.00 NOT NULL,
    shipping_fee DECIMAL(12, 2) DEFAULT 0.00 NOT NULL,
    discount_amount DECIMAL(12, 2) DEFAULT 0.00 NOT NULL,
    shipping_address TEXT NULL,
    shipping_city VARCHAR(120) NULL,
    shipping_phone VARCHAR(50) NULL,
    payment_method ENUM('COD', 'BANK_TRANSFER', 'CREDIT_CARD', 'MOMO', 'ZALOPAY') DEFAULT 'COD' NOT NULL,
    payment_status ENUM('PENDING', 'PAID', 'FAILED', 'REFUNDED') DEFAULT 'PENDING' NOT NULL,
    customer_notes TEXT NULL,
    staff_notes TEXT NULL,
    created_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    updated_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) NOT NULL,
    CONSTRAINT fk_orders_customer FOREIGN KEY (customer_id) REFERENCES users(id),
    INDEX idx_orders_customer (customer_id),
    INDEX idx_orders_status (status),
    INDEX idx_orders_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- ORDER_ITEMS TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    product_name VARCHAR(500) NOT NULL,
    product_sku VARCHAR(128) NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(15, 2) NOT NULL CHECK (unit_price >= 0),
    subtotal DECIMAL(15, 2) NOT NULL,
    CONSTRAINT fk_orderitems_order FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    CONSTRAINT fk_orderitems_product FOREIGN KEY (product_id) REFERENCES products(id),
    INDEX idx_orderitems_order (order_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- CONVERSATIONS TABLE (Chat sessions)
-- =============================================================================
CREATE TABLE IF NOT EXISTS conversations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255) NULL,
    created_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    updated_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) NOT NULL,
    CONSTRAINT fk_conversations_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_conversations_user (user_id),
    INDEX idx_conversations_updated (updated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- CONVERSATION_MESSAGES TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS conversation_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    conversation_id INT NOT NULL,
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    metadata TEXT NULL,
    created_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    CONSTRAINT fk_messages_conversation FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    INDEX idx_messages_conversation (conversation_id),
    INDEX idx_messages_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- TICKETS TABLE (Support tickets)
-- =============================================================================
CREATE TABLE IF NOT EXISTS tickets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticket_number VARCHAR(50) NOT NULL UNIQUE,
    customer_id INT NOT NULL,
    assigned_to INT NULL,
    subject VARCHAR(500) NOT NULL,
    description TEXT NULL,
    status ENUM('OPEN', 'IN_PROGRESS', 'WAITING_CUSTOMER', 'RESOLVED', 'CLOSED') DEFAULT 'OPEN' NOT NULL,
    priority ENUM('LOW', 'MEDIUM', 'HIGH', 'URGENT') DEFAULT 'MEDIUM' NOT NULL,
    category VARCHAR(100) NULL,
    created_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    updated_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) NOT NULL,
    resolved_at DATETIME(6) NULL,
    CONSTRAINT fk_tickets_customer FOREIGN KEY (customer_id) REFERENCES users(id),
    CONSTRAINT fk_tickets_staff FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_tickets_customer (customer_id),
    INDEX idx_tickets_status (status),
    INDEX idx_tickets_priority (priority)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- KB_ARTICLES TABLE (Knowledge Base for RAG)
-- =============================================================================
CREATE TABLE IF NOT EXISTS kb_articles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(255) NULL,
    tags TEXT NULL,
    status ENUM('DRAFT', 'PUBLISHED', 'ARCHIVED') DEFAULT 'PUBLISHED' NOT NULL,
    view_count INT DEFAULT 0 NOT NULL,
    helpful_count INT DEFAULT 0 NOT NULL,
    created_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    updated_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) NOT NULL,
    INDEX idx_kbarticles_category (category),
    INDEX idx_kbarticles_status (status),
    FULLTEXT INDEX ft_kbarticles_title (title),
    FULLTEXT INDEX ft_kbarticles_content (content)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- AUDIT_LOGS TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100) NULL,
    entity_id VARCHAR(100) NULL,
    old_values TEXT NULL,
    new_values TEXT NULL,
    ip_address VARCHAR(45) NULL,
    user_agent TEXT NULL,
    created_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    CONSTRAINT fk_auditlogs_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_auditlogs_user (user_id),
    INDEX idx_auditlogs_action (action),
    INDEX idx_auditlogs_entity (entity_type, entity_id),
    INDEX idx_auditlogs_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- SEED DATA: Demo Users (passwords are bcrypt hashed)
-- =============================================================================
-- admin@crm-demo.com / admin123
-- staff@crm-demo.com / staff123
-- customer@crm-demo.com / customer123

INSERT INTO users (email, username, password_hash, full_name, phone, role, status, is_verified) VALUES
    ('admin@crm-demo.com', 'admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeGDa7xXkMZF.kF8u', 'System Admin', '0901234567', 'ADMIN', 'ACTIVE', 1),
    ('staff@crm-demo.com', 'staff', '$2b$12$k4P9gDw8R5vNx7BQJHk.4eqJxK8mZWNfYvRjZ3LKf2XqYn8LfZ.mG', 'Staff Member', '0912345678', 'STAFF', 'ACTIVE', 1),
    ('customer@crm-demo.com', 'customer', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Demo Customer', '0923456789', 'CUSTOMER', 'ACTIVE', 1)
ON DUPLICATE KEY UPDATE updated_at = CURRENT_TIMESTAMP(6);

-- =============================================================================
-- SEED DATA: Knowledge Base Articles (Policies)
-- =============================================================================
INSERT INTO kb_articles (title, content, category, tags, status) VALUES
    ('Chính sách đổi trả hàng', 'Khách hàng có thể đổi trả sản phẩm trong vòng 7 ngày kể từ ngày nhận hàng. Điều kiện: Sản phẩm còn nguyên tem mác, chưa qua sử dụng, có đầy đủ phụ kiện và hóa đơn mua hàng. Không áp dụng đổi trả với các sản phẩm giảm giá trên 50%.', 'Chính sách', 'đổi trả,hoàn tiền,bảo hành', 'PUBLISHED'),
    ('Chính sách bảo hành sản phẩm', 'Tất cả laptop được bảo hành chính hãng từ 12-24 tháng tùy sản phẩm. Linh kiện thay thế được bảo hành 6 tháng. Địa điểm bảo hành: Tất cả chi nhánh trên toàn quốc hoặc gửi qua đường bưu điện.', 'Bảo hành', 'bảo hành,sửa chữa,hỗ trợ kỹ thuật', 'PUBLISHED'),
    ('Phương thức thanh toán', 'Chúng tôi chấp nhận các hình thức thanh toán: COD (thanh toán khi nhận hàng), chuyển khoản ngân hàng, thẻ tín dụng/ghi nợ Visa/Mastercard, ví điện tử MoMo/ZaloPay. Trả góp 0% lãi suất qua các đối tác tài chính.', 'Thanh toán', 'thanh toán,trả góp,COD', 'PUBLISHED'),
    ('Chính sách giao hàng', 'Miễn phí giao hàng cho đơn từ 500.000đ trong nội thành. Giao hàng nhanh 2h tại TP.HCM và Hà Nội. Giao hàng tiêu chuẩn 2-5 ngày cho các tỉnh thành khác. Có thể theo dõi đơn hàng qua mã vận đơn.', 'Vận chuyển', 'giao hàng,vận chuyển,ship', 'PUBLISHED'),
    ('Hướng dẫn chọn laptop gaming', 'Khi chọn laptop gaming cần lưu ý: CPU mạnh (Intel i5/i7 hoặc AMD Ryzen 5/7), Card đồ họa rời (NVIDIA RTX 3050 trở lên), RAM tối thiểu 16GB, SSD NVMe 512GB trở lên, màn hình 144Hz. Các thương hiệu uy tín: ASUS ROG, MSI, Acer Nitro, Lenovo Legion.', 'Hướng dẫn', 'laptop gaming,tư vấn,mua laptop', 'PUBLISHED'),
    ('Hướng dẫn chọn laptop văn phòng', 'Laptop văn phòng cần: CPU Intel i5/AMD Ryzen 5, RAM 8-16GB, SSD 256-512GB, màn hình IPS Full HD, pin trên 8 tiếng, nhẹ dưới 1.5kg. Các dòng phù hợp: HP Pavilion, Dell Inspiron, ASUS VivoBook, Lenovo ThinkPad.', 'Hướng dẫn', 'laptop văn phòng,tư vấn,mua laptop', 'PUBLISHED')
ON DUPLICATE KEY UPDATE updated_at = CURRENT_TIMESTAMP(6);

SELECT 'Database initialized successfully!' as status;
SELECT COUNT(*) as user_count FROM users;
SELECT COUNT(*) as kb_count FROM kb_articles;
