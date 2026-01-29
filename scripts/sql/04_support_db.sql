-- ============================================================================
-- DATABASE: crm_support_db
-- Mục đích: Quản lý Tickets, Conversations, Messages, Channels, Routing
-- Tables: 12
-- Port: 3313
-- ============================================================================

-- Đảm bảo sử dụng đúng database
USE crm_support_db;

-- Đặt character set
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- ============================================================================
-- BẢNG: channels
-- ============================================================================
CREATE TABLE IF NOT EXISTS channels (
    id          CHAR(36)    DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    code        VARCHAR(50) NOT NULL,
    type        ENUM('WEBCHAT', 'EMAIL', 'PHONE', 'FACEBOOK', 'ZALO', 'DISCORD', 'INSTAGRAM', 'OTHER') NOT NULL,
    name        VARCHAR(255) NOT NULL,
    config      JSON        NULL COMMENT 'Channel-specific configuration',
    is_active   TINYINT(1)  DEFAULT 1 NOT NULL,
    
    CONSTRAINT uq_channel_code UNIQUE (code)
) ENGINE=InnoDB;

-- ============================================================================
-- BẢNG: ticket_tags
-- ============================================================================
CREATE TABLE IF NOT EXISTS ticket_tags (
    id          CHAR(36)    DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    name        VARCHAR(128) NOT NULL,
    color       VARCHAR(7)  NULL COMMENT 'Hex color code',
    description TEXT        NULL,
    
    CONSTRAINT uq_tag_name UNIQUE (name)
) ENGINE=InnoDB;

-- ============================================================================
-- BẢNG: tickets
-- LƯU Ý: customer_id, assignee_id KHÔNG có FK
-- ============================================================================
CREATE TABLE IF NOT EXISTS tickets (
    id              CHAR(36)        DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    ticket_number   VARCHAR(50)     NOT NULL,
    
    -- Customer info (cross-service ref)
    customer_id     CHAR(36)        NOT NULL COMMENT 'Ref to Identity.users.id (no FK)',
    customer_email  VARCHAR(320)    NULL COMMENT 'Denormalized for quick access',
    customer_name   VARCHAR(255)    NULL,
    
    -- Ticket details
    channel_id      CHAR(36)        NULL,
    subject         VARCHAR(255)    NOT NULL,
    category        ENUM('GENERAL_INQUIRY', 'ORDER_ISSUE', 'PRODUCT_QUESTION', 'COMPLAINT', 'TECHNICAL_SUPPORT', 'REFUND_REQUEST', 'OTHER') DEFAULT 'GENERAL_INQUIRY' NOT NULL,
    
    -- Status & Priority
    status          ENUM('OPEN', 'IN_PROGRESS', 'WAITING_CUSTOMER', 'WAITING_INTERNAL', 'RESOLVED', 'CLOSED') DEFAULT 'OPEN' NOT NULL,
    priority        ENUM('LOW', 'MEDIUM', 'HIGH', 'URGENT') DEFAULT 'MEDIUM' NOT NULL,
    
    -- Assignment (cross-service ref)
    assignee_id     CHAR(36)        NULL COMMENT 'Ref to Identity.users.id (no FK)',
    assignee_name   VARCHAR(255)    NULL COMMENT 'Denormalized',
    
    -- Related entities (cross-service refs)
    order_id        CHAR(36)        NULL COMMENT 'Ref to Order.orders.id (no FK)',
    order_number    VARCHAR(50)     NULL COMMENT 'Denormalized',
    
    -- AI/Sentiment
    sentiment_score DECIMAL(4, 3)   NULL COMMENT '0.0-1.0',
    sentiment_label ENUM('NEGATIVE', 'NEUTRAL', 'POSITIVE', 'MIXED') NULL,
    ai_suggested    TINYINT(1)      DEFAULT 0 NOT NULL COMMENT 'AI auto-response suggested',
    
    -- Timestamps
    created_at      DATETIME(6)     DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    updated_at      DATETIME(6)     DEFAULT CURRENT_TIMESTAMP(6) NOT NULL ON UPDATE CURRENT_TIMESTAMP(6),
    first_response_at DATETIME(6)   NULL,
    resolved_at     DATETIME(6)     NULL,
    closed_at       DATETIME(6)     NULL,
    
    CONSTRAINT uq_ticket_number UNIQUE (ticket_number),
    CONSTRAINT fk_tk_channel FOREIGN KEY (channel_id) REFERENCES channels(id) ON DELETE SET NULL,
    INDEX idx_tk_customer (customer_id),
    INDEX idx_tk_status (status),
    INDEX idx_tk_priority (priority),
    INDEX idx_tk_assignee (assignee_id),
    INDEX idx_tk_created (created_at),
    INDEX idx_tk_cust_status (customer_id, status)
) ENGINE=InnoDB;

-- ============================================================================
-- BẢNG: ticket_tag_links
-- ============================================================================
CREATE TABLE IF NOT EXISTS ticket_tag_links (
    ticket_id   CHAR(36) NOT NULL,
    tag_id      CHAR(36) NOT NULL,
    
    PRIMARY KEY (ticket_id, tag_id),
    CONSTRAINT fk_ttl_ticket FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE,
    CONSTRAINT fk_ttl_tag FOREIGN KEY (tag_id) REFERENCES ticket_tags(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================================
-- BẢNG: ticket_messages
-- ============================================================================
CREATE TABLE IF NOT EXISTS ticket_messages (
    id              CHAR(36)    DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    ticket_id       CHAR(36)    NOT NULL,
    
    -- Sender info (cross-service ref)
    sender_id       CHAR(36)    NULL COMMENT 'User ID (no FK)',
    sender_type     ENUM('CUSTOMER', 'STAFF', 'SYSTEM', 'AI') NOT NULL,
    sender_name     VARCHAR(255) NULL,
    
    -- Content
    message         TEXT        NOT NULL,
    is_internal     TINYINT(1)  DEFAULT 0 NOT NULL COMMENT 'Internal note, not visible to customer',
    is_ai_generated TINYINT(1)  DEFAULT 0 NOT NULL,
    
    -- Attachments
    attachments     JSON        NULL COMMENT '[{name, url, mime_type, size}]',
    
    created_at      DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    
    CONSTRAINT fk_tmsg_ticket FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE,
    INDEX idx_tmsg_created (created_at)
) ENGINE=InnoDB;

-- ============================================================================
-- BẢNG: conversations (Live chat sessions)
-- ============================================================================
CREATE TABLE IF NOT EXISTS conversations (
    id              CHAR(36)    DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    ticket_id       CHAR(36)    NULL COMMENT 'Optional link to ticket',
    channel_id      CHAR(36)    NULL,
    
    -- Participants (cross-service refs)
    customer_id     CHAR(36)    NULL COMMENT 'User ID (no FK)',
    agent_id        CHAR(36)    NULL COMMENT 'Staff user ID (no FK)',
    
    -- Status
    status          ENUM('ACTIVE', 'WAITING', 'ENDED') DEFAULT 'ACTIVE' NOT NULL,
    
    started_at      DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    ended_at        DATETIME(6) NULL,
    
    CONSTRAINT fk_conv_ticket FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE SET NULL,
    CONSTRAINT fk_conv_channel FOREIGN KEY (channel_id) REFERENCES channels(id) ON DELETE SET NULL,
    INDEX idx_conv_customer (customer_id),
    INDEX idx_conv_agent (agent_id),
    INDEX idx_conv_status (status)
) ENGINE=InnoDB;

-- ============================================================================
-- BẢNG: messages (Chat messages)
-- ============================================================================
CREATE TABLE IF NOT EXISTS messages (
    id              CHAR(36)    DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    conversation_id CHAR(36)    NOT NULL,
    
    -- Sender
    sender_id       CHAR(36)    NULL,
    sender_type     ENUM('CUSTOMER', 'AGENT', 'CHATBOT', 'SYSTEM') NOT NULL,
    
    -- Content
    content         TEXT        NOT NULL,
    content_type    ENUM('TEXT', 'IMAGE', 'FILE', 'CARD', 'QUICK_REPLY') DEFAULT 'TEXT' NOT NULL,
    metadata        JSON        NULL COMMENT 'Extra data for rich content',
    
    sent_at         DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    read_at         DATETIME(6) NULL,
    
    CONSTRAINT fk_msg_conv FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    INDEX idx_msg_sent (sent_at)
) ENGINE=InnoDB;

-- ============================================================================
-- BẢNG: attachments
-- ============================================================================
CREATE TABLE IF NOT EXISTS attachments (
    id          CHAR(36)    DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    message_id  CHAR(36)    NOT NULL,
    file_name   VARCHAR(255) NOT NULL,
    mime_type   VARCHAR(127) NOT NULL,
    url         TEXT        NOT NULL,
    size_bytes  BIGINT      NULL,
    
    CONSTRAINT fk_att_msg FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================================
-- BẢNG: routing_rules
-- ============================================================================
CREATE TABLE IF NOT EXISTS routing_rules (
    id          CHAR(36)    DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    code        VARCHAR(64) NOT NULL,
    name        VARCHAR(255) NOT NULL,
    priority    INT         DEFAULT 100 NOT NULL COMMENT 'Lower = higher priority',
    predicate   JSON        NOT NULL COMMENT 'Conditions to match',
    action      JSON        NOT NULL COMMENT 'Actions to take',
    is_active   TINYINT(1)  DEFAULT 1 NOT NULL,
    
    CONSTRAINT uq_rule_code UNIQUE (code),
    INDEX idx_rule_priority (priority)
) ENGINE=InnoDB;

-- ============================================================================
-- BẢNG: work_queues
-- ============================================================================
CREATE TABLE IF NOT EXISTS work_queues (
    id      CHAR(36)    DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    code    VARCHAR(64) NOT NULL,
    name    VARCHAR(255) NOT NULL,
    
    CONSTRAINT uq_queue_code UNIQUE (code)
) ENGINE=InnoDB;

-- ============================================================================
-- BẢNG: assignments
-- ============================================================================
CREATE TABLE IF NOT EXISTS assignments (
    id              CHAR(36)    DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    ticket_id       CHAR(36)    NOT NULL,
    queue_id        CHAR(36)    NULL,
    assignee_id     CHAR(36)    NULL COMMENT 'User ID (no FK)',
    assigned_by     CHAR(36)    NULL COMMENT 'User ID who assigned (no FK)',
    decided_by_rule CHAR(36)    NULL,
    assigned_at     DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    
    CONSTRAINT fk_asg_ticket FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE,
    CONSTRAINT fk_asg_queue FOREIGN KEY (queue_id) REFERENCES work_queues(id) ON DELETE SET NULL,
    CONSTRAINT fk_asg_rule FOREIGN KEY (decided_by_rule) REFERENCES routing_rules(id) ON DELETE SET NULL,
    INDEX idx_asg_assignee (assignee_id)
) ENGINE=InnoDB;

-- ============================================================================
-- SEED DATA: Default Channels
-- ============================================================================
INSERT INTO channels (id, code, type, name, is_active) VALUES
(UUID(), 'WEBCHAT', 'WEBCHAT', 'Website Chat', 1),
(UUID(), 'EMAIL', 'EMAIL', 'Email Support', 1),
(UUID(), 'PHONE', 'PHONE', 'Phone Support', 1),
(UUID(), 'FACEBOOK', 'FACEBOOK', 'Facebook Messenger', 1),
(UUID(), 'ZALO', 'ZALO', 'Zalo OA', 1);

-- ============================================================================
-- SEED DATA: Default Ticket Tags
-- ============================================================================
INSERT INTO ticket_tags (id, name, color, description) VALUES
(UUID(), 'urgent', '#FF0000', 'Cần xử lý gấp'),
(UUID(), 'vip-customer', '#FFD700', 'Khách hàng VIP'),
(UUID(), 'refund', '#FF6B6B', 'Yêu cầu hoàn tiền'),
(UUID(), 'technical', '#4ECDC4', 'Vấn đề kỹ thuật'),
(UUID(), 'complaint', '#FFA500', 'Khiếu nại'),
(UUID(), 'feedback', '#45B7D1', 'Góp ý');

-- ============================================================================
-- SEED DATA: Default Work Queues
-- ============================================================================
INSERT INTO work_queues (id, code, name) VALUES
(UUID(), 'GENERAL', 'General Support'),
(UUID(), 'SALES', 'Sales Support'),
(UUID(), 'TECHNICAL', 'Technical Support'),
(UUID(), 'VIP', 'VIP Customers'),
(UUID(), 'ESCALATION', 'Escalation Queue');

SELECT 'crm_support_db initialized successfully with 12 tables!' AS status;
