-- ============================================================================
-- DATABASE: crm_order_db
-- Mục đích: Quản lý Orders, Payments, Shipments, Returns, Carts
-- Tables: 6
-- Port: 3312
-- ============================================================================

-- Đảm bảo sử dụng đúng database
USE crm_order_db;

-- Đặt character set
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- ============================================================================
-- BẢNG: orders
-- LƯU Ý: customer_id KHÔNG có FK vì users ở Identity DB
-- ============================================================================
CREATE TABLE IF NOT EXISTS orders (
    id                  CHAR(36)        DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    order_number        VARCHAR(50)     NOT NULL,
    
    -- Customer info (denormalized snapshot, cross-service ref)
    customer_id         CHAR(36)        NOT NULL COMMENT 'Ref to Identity.users.id (no FK)',
    customer_email      VARCHAR(320)    NOT NULL COMMENT 'Snapshot at order time',
    customer_name       VARCHAR(255)    NOT NULL COMMENT 'Snapshot at order time',
    customer_phone      VARCHAR(50)     NULL,
    
    -- Shipping address (denormalized snapshot)
    shipping_name       VARCHAR(255)    NULL,
    shipping_phone      VARCHAR(50)     NULL,
    shipping_line1      VARCHAR(255)    NULL,
    shipping_line2      VARCHAR(255)    NULL,
    shipping_ward       VARCHAR(120)    NULL,
    shipping_district   VARCHAR(120)    NULL,
    shipping_city       VARCHAR(120)    NULL,
    shipping_province   VARCHAR(120)    NULL,
    shipping_postal     VARCHAR(30)     NULL,
    shipping_country    VARCHAR(2)      DEFAULT 'VN',
    
    -- Order status
    status              ENUM('PENDING', 'CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'COMPLETED', 'CANCELLED', 'REFUNDED') DEFAULT 'PENDING' NOT NULL,
    
    -- Amounts
    subtotal            DECIMAL(14, 2)  DEFAULT 0.00 NOT NULL,
    shipping_fee        DECIMAL(12, 2)  DEFAULT 0.00 NOT NULL,
    tax_amount          DECIMAL(12, 2)  DEFAULT 0.00 NOT NULL,
    discount_amount     DECIMAL(12, 2)  DEFAULT 0.00 NOT NULL,
    total_amount        DECIMAL(14, 2)  DEFAULT 0.00 NOT NULL,
    currency            VARCHAR(3)      DEFAULT 'VND' NOT NULL,
    
    -- Payment
    payment_method      ENUM('COD', 'BANK_TRANSFER', 'CREDIT_CARD', 'EWALLET', 'MOMO', 'VNPAY', 'ZALOPAY') NULL,
    payment_status      ENUM('PENDING', 'PAID', 'PARTIALLY_PAID', 'REFUNDED', 'FAILED') DEFAULT 'PENDING' NOT NULL,
    
    -- Metadata
    coupon_code         VARCHAR(50)     NULL,
    note                TEXT            NULL,
    internal_note       TEXT            NULL COMMENT 'Staff notes',
    source              VARCHAR(50)     NULL COMMENT 'WEB, APP, PHONE, etc',
    
    -- Timestamps
    ordered_at          DATETIME(6)     DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    confirmed_at        DATETIME(6)     NULL,
    shipped_at          DATETIME(6)     NULL,
    delivered_at        DATETIME(6)     NULL,
    completed_at        DATETIME(6)     NULL,
    cancelled_at        DATETIME(6)     NULL,
    created_at          DATETIME(6)     DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    updated_at          DATETIME(6)     DEFAULT CURRENT_TIMESTAMP(6) NOT NULL ON UPDATE CURRENT_TIMESTAMP(6),
    
    CONSTRAINT uq_order_number UNIQUE (order_number),
    INDEX idx_order_customer (customer_id),
    INDEX idx_order_status (status),
    INDEX idx_order_payment (payment_status),
    INDEX idx_order_date (ordered_at),
    INDEX idx_order_cust_status (customer_id, status)
) ENGINE=InnoDB;

-- ============================================================================
-- BẢNG: order_items
-- LƯU Ý: product_id KHÔNG có FK vì products ở Product DB
-- ============================================================================
CREATE TABLE IF NOT EXISTS order_items (
    id              CHAR(36)        DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    order_id        CHAR(36)        NOT NULL,
    
    -- Product info (denormalized snapshot, cross-service ref)
    product_id      CHAR(36)        NOT NULL COMMENT 'Ref to Product.products.id (no FK)',
    product_sku     VARCHAR(128)    NOT NULL COMMENT 'Snapshot at order time',
    product_name    VARCHAR(255)    NOT NULL COMMENT 'Snapshot at order time',
    product_image   TEXT            NULL,
    
    -- Pricing
    unit_price      DECIMAL(12, 2)  NOT NULL COMMENT 'Price at order time',
    quantity        INT             NOT NULL,
    discount        DECIMAL(12, 2)  DEFAULT 0.00 NOT NULL,
    line_total      DECIMAL(14, 2)  AS (quantity * unit_price - discount) STORED,
    
    -- Attributes
    attributes      JSON            NULL COMMENT 'Selected options {color, size, etc}',
    
    CONSTRAINT fk_oi_order FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    CONSTRAINT chk_oi_qty CHECK (quantity > 0),
    CONSTRAINT chk_oi_price CHECK (unit_price >= 0),
    INDEX idx_oi_product (product_id)
) ENGINE=InnoDB;

-- ============================================================================
-- TRIGGER: Cập nhật subtotal và total khi order_items thay đổi
-- ============================================================================
DELIMITER //

CREATE TRIGGER trg_order_items_after_insert
AFTER INSERT ON order_items
FOR EACH ROW
BEGIN
    UPDATE orders 
    SET subtotal = (SELECT COALESCE(SUM(line_total), 0) FROM order_items WHERE order_id = NEW.order_id),
        total_amount = subtotal + shipping_fee + tax_amount - discount_amount
    WHERE id = NEW.order_id;
END//

CREATE TRIGGER trg_order_items_after_update
AFTER UPDATE ON order_items
FOR EACH ROW
BEGIN
    UPDATE orders 
    SET subtotal = (SELECT COALESCE(SUM(line_total), 0) FROM order_items WHERE order_id = NEW.order_id),
        total_amount = subtotal + shipping_fee + tax_amount - discount_amount
    WHERE id = NEW.order_id;
END//

CREATE TRIGGER trg_order_items_after_delete
AFTER DELETE ON order_items
FOR EACH ROW
BEGIN
    UPDATE orders 
    SET subtotal = (SELECT COALESCE(SUM(line_total), 0) FROM order_items WHERE order_id = OLD.order_id),
        total_amount = subtotal + shipping_fee + tax_amount - discount_amount
    WHERE id = OLD.order_id;
END//

DELIMITER ;

-- ============================================================================
-- BẢNG: payments
-- ============================================================================
CREATE TABLE IF NOT EXISTS payments (
    id              CHAR(36)        DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    order_id        CHAR(36)        NOT NULL,
    
    -- Payment details
    method          ENUM('COD', 'BANK_TRANSFER', 'CREDIT_CARD', 'EWALLET', 'MOMO', 'VNPAY', 'ZALOPAY') NOT NULL,
    status          ENUM('PENDING', 'PROCESSING', 'SUCCESS', 'FAILED', 'CANCELLED', 'REFUNDED') DEFAULT 'PENDING' NOT NULL,
    amount          DECIMAL(14, 2)  NOT NULL,
    currency        VARCHAR(3)      DEFAULT 'VND' NOT NULL,
    
    -- Gateway info
    gateway         VARCHAR(50)     NULL COMMENT 'Payment gateway name',
    gateway_txn_id  VARCHAR(255)    NULL COMMENT 'Transaction ID from gateway',
    gateway_response JSON           NULL COMMENT 'Raw response from gateway',
    
    -- Timestamps
    paid_at         DATETIME(6)     NULL,
    refunded_at     DATETIME(6)     NULL,
    created_at      DATETIME(6)     DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    
    CONSTRAINT fk_pay_order FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    CONSTRAINT chk_pay_amount CHECK (amount >= 0),
    INDEX idx_pay_status (status),
    INDEX idx_pay_gateway (gateway_txn_id)
) ENGINE=InnoDB;

-- ============================================================================
-- BẢNG: shipments
-- ============================================================================
CREATE TABLE IF NOT EXISTS shipments (
    id              CHAR(36)        DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    order_id        CHAR(36)        NOT NULL,
    
    -- Carrier info
    carrier         VARCHAR(100)    NULL COMMENT 'GHN, GHTK, ViettelPost, etc',
    tracking_number VARCHAR(255)    NULL,
    tracking_url    TEXT            NULL,
    
    -- Status
    status          ENUM('PENDING', 'PICKED_UP', 'IN_TRANSIT', 'OUT_FOR_DELIVERY', 'DELIVERED', 'FAILED', 'RETURNED') DEFAULT 'PENDING' NOT NULL,
    
    -- Shipping details
    weight          DECIMAL(10, 3)  NULL COMMENT 'Actual weight in kg',
    shipping_cost   DECIMAL(12, 2)  NULL,
    estimated_delivery DATE         NULL,
    
    -- Timestamps
    picked_at       DATETIME(6)     NULL,
    shipped_at      DATETIME(6)     NULL,
    delivered_at    DATETIME(6)     NULL,
    created_at      DATETIME(6)     DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    updated_at      DATETIME(6)     DEFAULT CURRENT_TIMESTAMP(6) NOT NULL ON UPDATE CURRENT_TIMESTAMP(6),
    
    CONSTRAINT fk_ship_order FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    INDEX idx_ship_tracking (tracking_number),
    INDEX idx_ship_status (status)
) ENGINE=InnoDB;

-- ============================================================================
-- BẢNG: returns
-- ============================================================================
CREATE TABLE IF NOT EXISTS returns (
    id              CHAR(36)        DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    order_id        CHAR(36)        NOT NULL,
    
    -- Return details
    reason          ENUM('DEFECTIVE', 'WRONG_ITEM', 'NOT_AS_DESCRIBED', 'CHANGED_MIND', 'OTHER') NOT NULL,
    reason_detail   TEXT            NULL,
    status          ENUM('REQUESTED', 'APPROVED', 'REJECTED', 'RECEIVED', 'REFUNDED', 'CLOSED') DEFAULT 'REQUESTED' NOT NULL,
    
    -- Items to return
    items           JSON            NOT NULL COMMENT '[{order_item_id, quantity, reason}]',
    
    -- Refund info
    refund_amount   DECIMAL(14, 2)  NULL,
    refund_method   VARCHAR(50)     NULL,
    
    -- Timestamps
    requested_at    DATETIME(6)     DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    approved_at     DATETIME(6)     NULL,
    received_at     DATETIME(6)     NULL,
    refunded_at     DATETIME(6)     NULL,
    closed_at       DATETIME(6)     NULL,
    
    -- Staff handling
    handled_by      CHAR(36)        NULL COMMENT 'Staff user ID (cross-service ref)',
    note            TEXT            NULL,
    
    CONSTRAINT fk_ret_order FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    INDEX idx_ret_status (status)
) ENGINE=InnoDB;

-- ============================================================================
-- BẢNG: carts
-- ============================================================================
CREATE TABLE IF NOT EXISTS carts (
    id              CHAR(36)        DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    customer_id     CHAR(36)        NOT NULL COMMENT 'Ref to Identity.users.id (no FK)',
    session_id      VARCHAR(255)    NULL COMMENT 'For anonymous carts',
    items           JSON            NOT NULL DEFAULT ('[]') COMMENT '[{product_id, quantity, attributes}]',
    coupon_code     VARCHAR(50)     NULL,
    created_at      DATETIME(6)     DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    updated_at      DATETIME(6)     DEFAULT CURRENT_TIMESTAMP(6) NOT NULL ON UPDATE CURRENT_TIMESTAMP(6),
    expires_at      DATETIME(6)     NULL,
    
    INDEX idx_cart_customer (customer_id),
    INDEX idx_cart_session (session_id)
) ENGINE=InnoDB;

SELECT 'crm_order_db initialized successfully with 6 tables!' AS status;
