-- Full Database Schema for CRM-AI-Agent
-- Auto-run when MySQL container starts

USE crm_demo;

SET FOREIGN_KEY_CHECKS=0;

-- ===== USERS & AUTH =====
CREATE TABLE IF NOT EXISTS users (
    id CHAR(36) DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    email VARCHAR(320) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(50) NULL,
    status ENUM('ACTIVE', 'LOCKED', 'PENDING') DEFAULT 'ACTIVE' NOT NULL,
    created_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    updated_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL ON UPDATE CURRENT_TIMESTAMP(6),
    INDEX idx_users_statuss (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS customer_profiles (
    user_id CHAR(36) NOT NULL PRIMARY KEY,
    registered_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    loyalty_point INT DEFAULT 0 NOT NULL,
    dob DATE NULL,
    gender ENUM('M', 'F', 'O') NULL,
    CONSTRAINT fk_cust_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS staff_profiles (
    user_id CHAR(36) NOT NULL PRIMARY KEY,
    employee_code VARCHAR(128) NOT NULL UNIQUE,
    position VARCHAR(128) NOT NULL,
    hired_at DATE DEFAULT (CURDATE()) NOT NULL,
    CONSTRAINT fk_staff_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ===== CATEGORIES =====
CREATE TABLE IF NOT EXISTS categories (
    id CHAR(36) DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    code VARCHAR(64) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    description TEXT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ===== PRODUCTS =====
CREATE TABLE IF NOT EXISTS products (
    id CHAR(36) DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    sku VARCHAR(128) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(12, 2) NOT NULL CHECK (price >= 0),
    description TEXT NULL,
    image_url TEXT NULL,
    category_id CHAR(36) NULL,
    created_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    updated_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL ON UPDATE CURRENT_TIMESTAMP(6),
    CONSTRAINT fk_prod_cat FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ===== ADDRESSES =====
CREATE TABLE IF NOT EXISTS addresses (
    id CHAR(36) DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    label VARCHAR(100) NULL,
    line1 VARCHAR(255) NOT NULL,
    line2 VARCHAR(255) NULL,
    city VARCHAR(120) NOT NULL,
    state VARCHAR(120) NULL,
    postal VARCHAR(30) NULL,
    country VARCHAR(2) DEFAULT 'VN' NOT NULL,
    is_default TINYINT(1) DEFAULT 0 NOT NULL,
    created_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    updated_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL ON UPDATE CURRENT_TIMESTAMP(6),
    CONSTRAINT fk_addr_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ===== ORDERS =====
CREATE TABLE IF NOT EXISTS orders (
    id CHAR(36) DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    customer_id CHAR(36) NOT NULL,
    shipping_address CHAR(36) NULL,
    created_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    status ENUM('PENDING', 'CONFIRMED', 'FULFILLING', 'SHIPPED', 'COMPLETED', 'CANCELLED') DEFAULT 'PENDING' NOT NULL,
    subtotal_amount DECIMAL(12, 2) DEFAULT 0.00 NOT NULL,
    shipping_fee DECIMAL(12, 2) DEFAULT 0.00 NOT NULL,
    discount_amount DECIMAL(12, 2) DEFAULT 0.00 NOT NULL,
    total_amount DECIMAL(12, 2) DEFAULT 0.00 NOT NULL,
    payment_method ENUM('CASH', 'BANK_TRANSFER', 'CREDIT_CARD', 'EWALLET') NOT NULL,
    note TEXT NULL,
    CONSTRAINT fk_orders_customer FOREIGN KEY (customer_id) REFERENCES users(id),
    CONSTRAINT fk_orders_address FOREIGN KEY (shipping_address) REFERENCES addresses(id) ON DELETE SET NULL,
    INDEX idx_orders_cust_status (customer_id, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS order_items (
    id CHAR(36) DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    order_id CHAR(36) NOT NULL,
    product_id CHAR(36) NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(12, 2) NOT NULL CHECK (unit_price >= 0),
    line_total DECIMAL(12, 2) AS (quantity * unit_price) STORED,
    CONSTRAINT fk_oi_order FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    CONSTRAINT fk_oi_product FOREIGN KEY (product_id) REFERENCES products(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ===== CHANNELS =====
CREATE TABLE IF NOT EXISTS channels (
    id CHAR(36) DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    type ENUM('WEBCHAT', 'EMAIL', 'PHONE', 'FACEBOOK', 'ZALO', 'DISCORD', 'OTHER') NOT NULL,
    external_id VARCHAR(255) NULL,
    name VARCHAR(255) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ===== TICKETS =====
CREATE TABLE IF NOT EXISTS tickets (
    id CHAR(36) DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    customer_id CHAR(36) NOT NULL,
    channel_id CHAR(36) NULL,
    subject VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    status ENUM('NEW', 'IN_PROGRESS', 'RESOLVED', 'CLOSED') DEFAULT 'NEW' NOT NULL,
    priority ENUM('LOW', 'MEDIUM', 'HIGH', 'URGENT') DEFAULT 'MEDIUM' NOT NULL,
    assignee_id CHAR(36) NULL,
    CONSTRAINT fk_tk_customer FOREIGN KEY (customer_id) REFERENCES users(id),
    CONSTRAINT fk_tk_channel FOREIGN KEY (channel_id) REFERENCES channels(id) ON DELETE SET NULL,
    CONSTRAINT fk_tk_agent FOREIGN KEY (assignee_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_tickets_cust_status (customer_id, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ===== CONVERSATIONS =====
CREATE TABLE IF NOT EXISTS conversations (
    id CHAR(36) DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    ticket_id CHAR(36) NULL,
    started_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    ended_at DATETIME(6) NULL,
    CONSTRAINT fk_conv_ticket FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS messages (
    id CHAR(36) DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    conversation_id CHAR(36) NULL,
    sender_id CHAR(36) NULL,
    kind ENUM('CHATBOT', 'AGENT', 'CUSTOMER') NOT NULL,
    content TEXT NOT NULL,
    sent_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    channel_id CHAR(36) NULL,
    CONSTRAINT fk_msg_conv FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    CONSTRAINT fk_msg_sender FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT fk_msg_channel FOREIGN KEY (channel_id) REFERENCES channels(id) ON DELETE SET NULL,
    INDEX idx_messages_conv_time (conversation_id, sent_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ===== KNOWLEDGE BASE =====
CREATE TABLE IF NOT EXISTS kb_tags (
    id CHAR(36) DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    name VARCHAR(128) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS kb_articles (
    id CHAR(36) DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    code VARCHAR(64) NULL UNIQUE,
    title VARCHAR(255) NOT NULL,
    body_md MEDIUMTEXT NOT NULL,
    created_by CHAR(36) NULL,
    created_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    updated_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL ON UPDATE CURRENT_TIMESTAMP(6),
    is_public TINYINT(1) DEFAULT 1 NOT NULL,
    CONSTRAINT fk_kb_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ===== RAG SYSTEM =====
CREATE TABLE IF NOT EXISTS corpora (
    id CHAR(36) DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS documents (
    id CHAR(36) DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    corpus_id CHAR(36) NOT NULL,
    uri TEXT NOT NULL,
    meta JSON NULL,
    indexed_at DATETIME(6) NULL,
    CONSTRAINT fk_doc_corpus FOREIGN KEY (corpus_id) REFERENCES corpora(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS rag_queries (
    id CHAR(36) DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    user_id CHAR(36) NULL,
    question MEDIUMTEXT NOT NULL,
    response MEDIUMTEXT NULL,
    created_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    CONSTRAINT fk_ragq_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS=1;

-- Success message
SELECT 'Database schema created successfully!' AS Status;
