-- Sample Data for CRM-AI-Agent
-- Insert test users and products

USE crm_demo;

-- Insert sample users (using bcrypt hashed passwords)
-- Admin user (password: admin123)
INSERT IGNORE INTO users (id, email, password_hash, full_name, phone, status)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'admin@crm.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeGDa7xXkMZF.kF8u',
    'System Administrator',
    '+84901234567',
    'ACTIVE'
);

-- Customer 1 (password: password123)
INSERT IGNORE INTO users (id, email, password_hash, full_name, phone, status)
VALUES (
    '00000000-0000-0000-0000-000000000002',
    'customer1@gmail.com',
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',
    'Nguyễn Văn A',
    '+84912345678',
    'ACTIVE'
);

-- Customer 2 (password: password123)
INSERT IGNORE INTO users (id, email, password_hash, full_name, phone, status)
VALUES (
    '00000000-0000-0000-0000-000000000003',
    'customer2@gmail.com',
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',
    'Trần Thị B',
    '+84923456789',
    'ACTIVE'
);

-- Staff/Agent (password: staff123)
INSERT IGNORE INTO users (id, email, password_hash, full_name, phone, status)
VALUES (
    '00000000-0000-0000-0000-000000000004',
    'agent@crm.com',
    '$2b$12$k4P9gDw8R5vNx7BQJHk.4eqJxK8mZWNfYvRjZ3LKf2XqYn8LfZ.mG',
    'Lê Văn C',
    '+84934567890',
    'ACTIVE'
);

-- Insert customer profiles
INSERT IGNORE INTO customer_profiles (user_id, loyalty_point, dob, gender)
VALUES 
    ('00000000-0000-0000-0000-000000000002', 100, '1990-05-15', 'M'),
    ('00000000-0000-0000-0000-000000000003', 250, '1995-08-20', 'F');

-- Insert staff profile
INSERT IGNORE INTO staff_profiles (user_id, employee_code, position, hired_at)
VALUES 
    ('00000000-0000-0000-0000-000000000004', 'EMP001', 'Customer Support Agent', '2024-01-01');

-- Insert categories
INSERT IGNORE INTO categories (id, code, name, description)
VALUES 
    ('10000000-0000-0000-0000-000000000001', 'ELECTRONICS', 'Điện tử', 'Thiết bị điện tử'),
    ('10000000-0000-0000-0000-000000000002', 'ACCESSORIES', 'Phụ kiện', 'Phụ kiện công nghệ'),
    ('10000000-0000-0000-0000-000000000003', 'COMPUTERS', 'Máy tính', 'Máy tính và laptop');

-- Insert sample products
INSERT IGNORE INTO products (id, sku, name, price, description, image_url, category_id)
VALUES 
    (
        '20000000-0000-0000-0000-000000000001',
        'LP-HP-001',
        'Laptop HP Pavilion 15',
        25000000.00,
        'Laptop gaming cao cấp với CPU Intel Core i7, RAM 16GB, SSD 512GB',
        'https://example.com/hp-pavilion.jpg',
        '10000000-0000-0000-0000-000000000003'
    ),
    (
        '20000000-0000-0000-0000-000000000002',
        'IP-15-PM',
        'iPhone 15 Pro Max 256GB',
        35000000.00,
        'Điện thoại thông minh flagship của Apple với chip A17 Pro',
        'https://example.com/iphone-15.jpg',
        '10000000-0000-0000-0000-000000000001'
    ),
    (
        '20000000-0000-0000-0000-000000000003',
        'SS-S24',
        'Samsung Galaxy S24 Ultra',
        28000000.00,
        'Smartphone Android cao cấp với camera 200MP, S Pen tích hợp',
        'https://example.com/samsung-s24.jpg',
        '10000000-0000-0000-0000-000000000001'
    ),
    (
        '20000000-0000-0000-0000-000000000004',
        'MB-M3-PRO',
        'MacBook Pro M3 14 inch',
        45000000.00,
        'Laptop chuyên nghiệp cho developers với chip M3, RAM 16GB',
        'https://example.com/macbook-m3.jpg',
        '10000000-0000-0000-0000-000000000003'
    ),
    (
        '20000000-0000-0000-0000-000000000005',
        'AP-PRO2',
        'AirPods Pro 2nd Generation',
        6500000.00,
        'Tai nghe không dây chống ồn chủ động với chip H2',
        'https://example.com/airpods-pro2.jpg',
        '10000000-0000-0000-0000-000000000002'
    ),
    (
        '20000000-0000-0000-0000-000000000006',
        'DELL-XPS15',
        'Dell XPS 15 9530',
        42000000.00,
        'Laptop cao cấp với màn hình OLED 3.5K, Intel Core i9',
        'https://example.com/dell-xps15.jpg',
        '10000000-0000-0000-0000-000000000003'
    ),
    (
        '20000000-0000-0000-0000-000000000007',
        'WATCH-S9',
        'Apple Watch Series 9',
        11000000.00,
        'Smartwatch với chip S9, Always-On Retina display',
        'https://example.com/watch-s9.jpg',
        '10000000-0000-0000-0000-000000000002'
    ),
    (
        '20000000-0000-0000-0000-000000000008',
        'IPAD-AIR',
        'iPad Air M2 11 inch',
        16000000.00,
        'Máy tính bảng với chip M2, hỗ trợ Apple Pencil Pro',
        'https://example.com/ipad-air.jpg',
        '10000000-0000-0000-0000-000000000001'
    );

-- Insert sample channels
INSERT IGNORE INTO channels (id, type, name)
VALUES 
    ('30000000-0000-0000-0000-000000000001', 'WEBCHAT', 'Website Live Chat'),
    ('30000000-0000-0000-0000-000000000002', 'EMAIL', 'Email Support'),
    ('30000000-0000-0000-0000-000000000003', 'PHONE', 'Hotline 1900-xxxx');

-- Insert sample corpus for RAG
INSERT IGNORE INTO corpora (id, name, description)
VALUES 
    ('40000000-0000-0000-0000-000000000001', 'Product Knowledge Base', 'Tài liệu về sản phẩm và chính sách');

-- Success message
SELECT 'Sample data inserted successfully!' AS Status;
SELECT COUNT(*) AS user_count FROM users;
SELECT COUNT(*) AS product_count FROM products;
SELECT COUNT(*) AS category_count FROM categories;
