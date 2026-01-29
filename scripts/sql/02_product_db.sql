-- ============================================================================
-- DATABASE: crm_product_db
-- Mục đích: Quản lý Products, Categories, Inventory, Warehouses
-- Tables: 5 + 1 View
-- Port: 3311
-- ============================================================================

-- Đảm bảo sử dụng đúng database
USE crm_product_db;

-- Đặt character set
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- ============================================================================
-- BẢNG: categories
-- ============================================================================
CREATE TABLE IF NOT EXISTS categories (
    id          CHAR(36)    DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    code        VARCHAR(64) NOT NULL,
    name        VARCHAR(255) NOT NULL,
    slug        VARCHAR(255) NULL,
    description TEXT        NULL,
    parent_id   CHAR(36)    NULL,
    image_url   TEXT        NULL,
    is_active   TINYINT(1)  DEFAULT 1 NOT NULL,
    sort_order  INT         DEFAULT 0 NOT NULL,
    created_at  DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    updated_at  DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL ON UPDATE CURRENT_TIMESTAMP(6),
    
    CONSTRAINT uq_cat_code UNIQUE (code),
    CONSTRAINT fk_cat_parent FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL,
    INDEX idx_cat_parent (parent_id),
    INDEX idx_cat_active (is_active)
) ENGINE=InnoDB;

-- ============================================================================
-- BẢNG: products
-- ============================================================================
CREATE TABLE IF NOT EXISTS products (
    id              CHAR(36)        DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    sku             VARCHAR(128)    NOT NULL,
    name            VARCHAR(255)    NOT NULL,
    slug            VARCHAR(255)    NULL,
    description     TEXT            NULL,
    short_description VARCHAR(500)  NULL,
    
    -- Pricing
    base_price      DECIMAL(14, 2)  NOT NULL DEFAULT 0.00,
    sale_price      DECIMAL(14, 2)  NULL,
    cost_price      DECIMAL(14, 2)  NULL COMMENT 'For margin calculation',
    currency        VARCHAR(3)      DEFAULT 'VND' NOT NULL,
    
    -- Categorization
    category_id     CHAR(36)        NULL,
    brand           VARCHAR(128)    NULL,
    
    -- Physical attributes
    weight_kg       DECIMAL(10, 3)  NULL,
    length_cm       DECIMAL(10, 2)  NULL,
    width_cm        DECIMAL(10, 2)  NULL,
    height_cm       DECIMAL(10, 2)  NULL,
    
    -- Images
    main_image_url  TEXT            NULL,
    images          JSON            NULL COMMENT '["url1", "url2", ...]',
    
    -- Status
    status          ENUM('ACTIVE', 'INACTIVE', 'DRAFT', 'ARCHIVED') DEFAULT 'ACTIVE' NOT NULL,
    is_featured     TINYINT(1)      DEFAULT 0 NOT NULL,
    
    -- SEO
    meta_title      VARCHAR(255)    NULL,
    meta_description VARCHAR(500)   NULL,
    
    -- Attributes
    attributes      JSON            NULL COMMENT '{"color": ["red", "blue"], "size": ["S", "M"]}',
    specifications  JSON            NULL COMMENT '{"RAM": "8GB", "CPU": "i7"}',
    tags            JSON            NULL COMMENT '["sale", "new", "bestseller"]',
    
    -- Stats (denormalized for performance)
    view_count      INT             DEFAULT 0 NOT NULL,
    sold_count      INT             DEFAULT 0 NOT NULL,
    avg_rating      DECIMAL(3, 2)   DEFAULT 0.00 NOT NULL,
    review_count    INT             DEFAULT 0 NOT NULL,
    
    -- Timestamps
    created_at      DATETIME(6)     DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    updated_at      DATETIME(6)     DEFAULT CURRENT_TIMESTAMP(6) NOT NULL ON UPDATE CURRENT_TIMESTAMP(6),
    published_at    DATETIME(6)     NULL,
    
    CONSTRAINT uq_prod_sku UNIQUE (sku),
    CONSTRAINT fk_prod_cat FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
    CONSTRAINT chk_prod_price CHECK (base_price >= 0),
    CONSTRAINT chk_prod_sale CHECK (sale_price IS NULL OR sale_price >= 0),
    INDEX idx_prod_status (status),
    INDEX idx_prod_cat (category_id),
    INDEX idx_prod_brand (brand),
    INDEX idx_prod_price (base_price),
    INDEX idx_prod_featured (is_featured),
    FULLTEXT INDEX ft_prod_search (name, description, brand)
) ENGINE=InnoDB;

-- ============================================================================
-- BẢNG: warehouses
-- ============================================================================
CREATE TABLE IF NOT EXISTS warehouses (
    id          CHAR(36)    DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    code        VARCHAR(50) NOT NULL,
    name        VARCHAR(255) NOT NULL,
    address     TEXT        NULL,
    city        VARCHAR(120) NULL,
    province    VARCHAR(120) NULL,
    is_active   TINYINT(1)  DEFAULT 1 NOT NULL,
    priority    INT         DEFAULT 0 NOT NULL COMMENT 'For fulfillment selection',
    
    CONSTRAINT uq_wh_code UNIQUE (code)
) ENGINE=InnoDB;

-- ============================================================================
-- BẢNG: inventory
-- ============================================================================
CREATE TABLE IF NOT EXISTS inventory (
    warehouse_id    CHAR(36)    NOT NULL,
    product_id      CHAR(36)    NOT NULL,
    quantity        INT         DEFAULT 0 NOT NULL,
    reserved        INT         DEFAULT 0 NOT NULL COMMENT 'Reserved for pending orders',
    reorder_level   INT         DEFAULT 10 NOT NULL COMMENT 'Alert when below this level',
    updated_at      DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL ON UPDATE CURRENT_TIMESTAMP(6),
    
    PRIMARY KEY (warehouse_id, product_id),
    CONSTRAINT fk_inv_wh FOREIGN KEY (warehouse_id) REFERENCES warehouses(id) ON DELETE CASCADE,
    CONSTRAINT fk_inv_prod FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    CONSTRAINT chk_inv_qty CHECK (quantity >= 0),
    CONSTRAINT chk_inv_res CHECK (reserved >= 0),
    INDEX idx_inv_low_stock (quantity, reorder_level)
) ENGINE=InnoDB;

-- ============================================================================
-- BẢNG: inventory_movements
-- ============================================================================
CREATE TABLE IF NOT EXISTS inventory_movements (
    id              CHAR(36)    DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    warehouse_id    CHAR(36)    NOT NULL,
    product_id      CHAR(36)    NOT NULL,
    movement_type   ENUM('IN', 'OUT', 'ADJUSTMENT', 'RESERVE', 'RELEASE') NOT NULL,
    quantity        INT         NOT NULL COMMENT 'Positive for IN, negative for OUT',
    reference_type  VARCHAR(50) NULL COMMENT 'e.g. ORDER, RETURN, MANUAL',
    reference_id    CHAR(36)    NULL COMMENT 'Order ID, Return ID, etc (cross-service ref)',
    note            TEXT        NULL,
    performed_by    CHAR(36)    NULL COMMENT 'User ID (cross-service ref, no FK)',
    created_at      DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    
    CONSTRAINT fk_invmov_wh FOREIGN KEY (warehouse_id) REFERENCES warehouses(id) ON DELETE CASCADE,
    CONSTRAINT fk_invmov_prod FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    INDEX idx_invmov_ref (reference_type, reference_id),
    INDEX idx_invmov_created (created_at)
) ENGINE=InnoDB;

-- ============================================================================
-- VIEW: v_product_stock
-- ============================================================================
CREATE OR REPLACE VIEW v_product_stock AS
SELECT 
    p.id AS product_id,
    p.sku,
    p.name,
    COALESCE(SUM(i.quantity), 0) AS total_quantity,
    COALESCE(SUM(i.reserved), 0) AS total_reserved,
    COALESCE(SUM(i.quantity) - SUM(i.reserved), 0) AS available
FROM products p
LEFT JOIN inventory i ON p.id = i.product_id
GROUP BY p.id, p.sku, p.name;

-- ============================================================================
-- SEED DATA: Default Categories
-- ============================================================================
INSERT INTO categories (id, code, name, slug, description, sort_order) VALUES
(UUID(), 'DIEN_THOAI', 'Điện thoại', 'dien-thoai', 'Điện thoại thông minh các loại', 1),
(UUID(), 'LAPTOP', 'Laptop', 'laptop', 'Máy tính xách tay', 2),
(UUID(), 'TABLET', 'Tablet', 'tablet', 'Máy tính bảng', 3),
(UUID(), 'PHU_KIEN', 'Phụ kiện', 'phu-kien', 'Phụ kiện điện thoại, laptop', 4),
(UUID(), 'DONG_HO', 'Đồng hồ thông minh', 'dong-ho', 'Smartwatch các loại', 5),
(UUID(), 'AM_THANH', 'Âm thanh', 'am-thanh', 'Tai nghe, loa bluetooth', 6);

-- ============================================================================
-- SEED DATA: Default Warehouse
-- ============================================================================
INSERT INTO warehouses (id, code, name, address, city, province, is_active, priority) VALUES
(UUID(), 'WH-HCM-01', 'Kho Hồ Chí Minh 01', '123 Nguyễn Văn Linh, Q7', 'Hồ Chí Minh', 'Hồ Chí Minh', 1, 1),
(UUID(), 'WH-HN-01', 'Kho Hà Nội 01', '456 Cầu Giấy', 'Hà Nội', 'Hà Nội', 1, 2),
(UUID(), 'WH-DN-01', 'Kho Đà Nẵng 01', '789 Nguyễn Văn Linh', 'Đà Nẵng', 'Đà Nẵng', 1, 3);

SELECT 'crm_product_db initialized successfully with 5 tables + 1 view!' AS status;
