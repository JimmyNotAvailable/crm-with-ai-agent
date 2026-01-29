-- ============================================================================
-- DATABASE: crm_marketing_db
-- Mục đích: Marketing Automation, Campaigns, Journeys, Segments
-- Tables: 12
-- Port: 3316
-- ============================================================================

-- Đảm bảo sử dụng đúng database
USE crm_marketing_db;

-- Đặt character set
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- ============================================================================
-- BẢNG: audience_segments
-- ============================================================================
CREATE TABLE IF NOT EXISTS audience_segments (
    id          CHAR(36)    DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    code        VARCHAR(64) NOT NULL,
    name        VARCHAR(255) NOT NULL,
    description TEXT        NULL,
    filter_criteria JSON    NULL COMMENT 'Dynamic filter conditions',
    is_dynamic  TINYINT(1)  DEFAULT 1 NOT NULL COMMENT 'Auto-update membership',
    member_count INT        DEFAULT 0 NOT NULL,
    created_at  DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    updated_at  DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL ON UPDATE CURRENT_TIMESTAMP(6),
    
    CONSTRAINT uq_seg_code UNIQUE (code)
) ENGINE=InnoDB;

-- ============================================================================
-- BẢNG: segment_memberships
-- ============================================================================
CREATE TABLE IF NOT EXISTS segment_memberships (
    id          CHAR(36)    DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    segment_id  CHAR(36)    NOT NULL,
    user_id     CHAR(36)    NOT NULL COMMENT 'User ID (no FK)',
    source      ENUM('AUTOMATIC', 'MANUAL', 'IMPORT') DEFAULT 'AUTOMATIC' NOT NULL,
    is_active   TINYINT(1)  DEFAULT 1 NOT NULL,
    joined_at   DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    left_at     DATETIME(6) NULL,
    
    CONSTRAINT uq_segm_user UNIQUE (segment_id, user_id),
    CONSTRAINT fk_segm_segment FOREIGN KEY (segment_id) REFERENCES audience_segments(id) ON DELETE CASCADE,
    INDEX idx_segm_user (user_id)
) ENGINE=InnoDB;

-- ============================================================================
-- BẢNG: customer_tags
-- ============================================================================
CREATE TABLE IF NOT EXISTS customer_tags (
    id          CHAR(36)    DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    code        VARCHAR(64) NOT NULL,
    name        VARCHAR(255) NOT NULL,
    color       VARCHAR(7)  NULL,
    description TEXT        NULL,
    created_at  DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    created_by  CHAR(36)    NULL COMMENT 'User ID (no FK)',
    
    CONSTRAINT uq_ctag_code UNIQUE (code)
) ENGINE=InnoDB;

-- ============================================================================
-- BẢNG: customer_tag_links
-- ============================================================================
CREATE TABLE IF NOT EXISTS customer_tag_links (
    customer_id CHAR(36)    NOT NULL COMMENT 'User ID (no FK)',
    tag_id      CHAR(36)    NOT NULL,
    created_at  DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    created_by  CHAR(36)    NULL COMMENT 'User ID (no FK)',
    
    PRIMARY KEY (customer_id, tag_id),
    CONSTRAINT fk_ctl_tag FOREIGN KEY (tag_id) REFERENCES customer_tags(id) ON DELETE CASCADE,
    INDEX idx_ctl_customer (customer_id)
) ENGINE=InnoDB;

-- ============================================================================
-- BẢNG: journeys
-- ============================================================================
CREATE TABLE IF NOT EXISTS journeys (
    id          CHAR(36)    DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    name        VARCHAR(255) NOT NULL,
    description TEXT        NULL,
    status      ENUM('DRAFT', 'ACTIVE', 'PAUSED', 'STOPPED', 'ARCHIVED') DEFAULT 'DRAFT' NOT NULL,
    trigger_type VARCHAR(50) NULL COMMENT 'signup, purchase, abandoned_cart, manual',
    trigger_config JSON     NULL,
    created_by  CHAR(36)    NULL COMMENT 'User ID (no FK)',
    created_at  DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    updated_at  DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL ON UPDATE CURRENT_TIMESTAMP(6),
    
    INDEX idx_journey_status (status)
) ENGINE=InnoDB;

-- ============================================================================
-- BẢNG: journey_nodes
-- ============================================================================
CREATE TABLE IF NOT EXISTS journey_nodes (
    id          CHAR(36)    DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    journey_id  CHAR(36)    NOT NULL,
    type        ENUM('ENTRY', 'FILTER', 'WAIT', 'ACTION_EMAIL', 'ACTION_SMS', 'ACTION_PUSH', 'ACTION_TAG', 'ACTION_WEBHOOK', 'EXIT') NOT NULL,
    name        VARCHAR(255) NULL,
    config      JSON        NOT NULL,
    position_x  INT         NULL COMMENT 'Canvas X position',
    position_y  INT         NULL COMMENT 'Canvas Y position',
    
    CONSTRAINT fk_jn_journey FOREIGN KEY (journey_id) REFERENCES journeys(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================================
-- BẢNG: journey_edges
-- ============================================================================
CREATE TABLE IF NOT EXISTS journey_edges (
    id          CHAR(36)    DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    journey_id  CHAR(36)    NOT NULL,
    from_node   CHAR(36)    NOT NULL,
    to_node     CHAR(36)    NOT NULL,
    condition   JSON        NULL COMMENT 'Branch condition',
    
    CONSTRAINT fk_je_journey FOREIGN KEY (journey_id) REFERENCES journeys(id) ON DELETE CASCADE,
    CONSTRAINT fk_je_from FOREIGN KEY (from_node) REFERENCES journey_nodes(id) ON DELETE CASCADE,
    CONSTRAINT fk_je_to FOREIGN KEY (to_node) REFERENCES journey_nodes(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================================
-- BẢNG: journey_enrollments
-- ============================================================================
CREATE TABLE IF NOT EXISTS journey_enrollments (
    id          CHAR(36)    DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    journey_id  CHAR(36)    NOT NULL,
    user_id     CHAR(36)    NOT NULL COMMENT 'User ID (no FK)',
    current_node CHAR(36)   NULL,
    status      ENUM('RUNNING', 'WAITING', 'COMPLETED', 'EXITED', 'ERROR') DEFAULT 'RUNNING' NOT NULL,
    enrolled_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    completed_at DATETIME(6) NULL,
    context     JSON        NULL COMMENT 'Runtime context/variables',
    
    CONSTRAINT uq_je_user UNIQUE (journey_id, user_id),
    CONSTRAINT fk_jenroll_journey FOREIGN KEY (journey_id) REFERENCES journeys(id) ON DELETE CASCADE,
    INDEX idx_jenroll_user (user_id),
    INDEX idx_jenroll_status (status)
) ENGINE=InnoDB;

-- ============================================================================
-- BẢNG: campaign_messages
-- ============================================================================
CREATE TABLE IF NOT EXISTS campaign_messages (
    id          CHAR(36)    DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    journey_id  CHAR(36)    NULL,
    name        VARCHAR(255) NOT NULL,
    channel     ENUM('EMAIL', 'SMS', 'PUSH', 'WEBCHAT', 'FACEBOOK', 'ZALO') DEFAULT 'EMAIL' NOT NULL,
    subject     VARCHAR(255) NULL COMMENT 'For email',
    body_html   MEDIUMTEXT  NULL COMMENT 'For email',
    body_text   TEXT        NULL COMMENT 'For SMS/text',
    template_vars JSON      NULL COMMENT 'Available merge variables',
    created_at  DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    
    CONSTRAINT fk_cm_journey FOREIGN KEY (journey_id) REFERENCES journeys(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ============================================================================
-- BẢNG: campaign_sends
-- ============================================================================
CREATE TABLE IF NOT EXISTS campaign_sends (
    id          CHAR(36)    DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    message_id  CHAR(36)    NOT NULL,
    to_user_id  CHAR(36)    NOT NULL COMMENT 'User ID (no FK)',
    to_email    VARCHAR(320) NULL COMMENT 'Denormalized',
    to_phone    VARCHAR(50) NULL,
    
    status      ENUM('QUEUED', 'SENDING', 'SENT', 'DELIVERED', 'OPENED', 'CLICKED', 'BOUNCED', 'FAILED') DEFAULT 'QUEUED' NOT NULL,
    
    scheduled_at DATETIME(6) NULL,
    sent_at     DATETIME(6) NULL,
    delivered_at DATETIME(6) NULL,
    opened_at   DATETIME(6) NULL,
    clicked_at  DATETIME(6) NULL,
    
    provider    VARCHAR(50) NULL COMMENT 'SendGrid, Twilio, etc',
    provider_ref VARCHAR(255) NULL,
    error_msg   TEXT        NULL,
    
    CONSTRAINT fk_cs_msg FOREIGN KEY (message_id) REFERENCES campaign_messages(id) ON DELETE CASCADE,
    INDEX idx_cs_user (to_user_id),
    INDEX idx_cs_status (status),
    INDEX idx_cs_scheduled (scheduled_at)
) ENGINE=InnoDB;

-- ============================================================================
-- BẢNG: webhooks
-- ============================================================================
CREATE TABLE IF NOT EXISTS webhooks (
    id          CHAR(36)    DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    name        VARCHAR(255) NOT NULL,
    target_url  TEXT        NOT NULL,
    secret      VARCHAR(255) NULL COMMENT 'For signature verification',
    events      JSON        NOT NULL COMMENT 'Events to trigger webhook',
    is_active   TINYINT(1)  DEFAULT 1 NOT NULL,
    created_at  DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL
) ENGINE=InnoDB;

-- ============================================================================
-- BẢNG: webhook_events
-- ============================================================================
CREATE TABLE IF NOT EXISTS webhook_events (
    id          CHAR(36)    DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    webhook_id  CHAR(36)    NOT NULL,
    topic       VARCHAR(128) NOT NULL,
    payload     JSON        NOT NULL,
    status      ENUM('PENDING', 'SENT', 'FAILED') DEFAULT 'PENDING' NOT NULL,
    attempts    INT         DEFAULT 0 NOT NULL,
    last_attempt DATETIME(6) NULL,
    delivered_at DATETIME(6) NULL,
    error_msg   TEXT        NULL,
    
    CONSTRAINT fk_whe_webhook FOREIGN KEY (webhook_id) REFERENCES webhooks(id) ON DELETE CASCADE,
    INDEX idx_whe_status (status)
) ENGINE=InnoDB;

-- ============================================================================
-- SEED DATA: Default Audience Segments
-- ============================================================================
INSERT INTO audience_segments (id, code, name, description, filter_criteria, is_dynamic, member_count) VALUES
(UUID(), 'VIP_CUSTOMERS', 'Khách hàng VIP', 'Khách hàng có tổng chi tiêu > 10 triệu', '{"total_spent": {"$gte": 10000000}}', 1, 0),
(UUID(), 'NEW_CUSTOMERS', 'Khách hàng mới', 'Đăng ký trong 30 ngày gần đây', '{"created_at": {"$gte": "NOW() - INTERVAL 30 DAY"}}', 1, 0),
(UUID(), 'INACTIVE_30D', 'Không hoạt động 30 ngày', 'Không mua hàng trong 30 ngày', '{"last_order_at": {"$lt": "NOW() - INTERVAL 30 DAY"}}', 1, 0),
(UUID(), 'CART_ABANDONERS', 'Bỏ giỏ hàng', 'Có giỏ hàng nhưng chưa checkout', '{"has_abandoned_cart": true}', 1, 0),
(UUID(), 'HIGH_VALUE', 'Giá trị cao', 'AOV > 2 triệu', '{"avg_order_value": {"$gte": 2000000}}', 1, 0);

-- ============================================================================
-- SEED DATA: Default Customer Tags
-- ============================================================================
INSERT INTO customer_tags (id, code, name, color, description) VALUES
(UUID(), 'VIP', 'VIP', '#FFD700', 'Khách hàng VIP'),
(UUID(), 'LOYAL', 'Loyal Customer', '#4CAF50', 'Khách hàng trung thành'),
(UUID(), 'AT_RISK', 'At Risk', '#FF5722', 'Có nguy cơ rời bỏ'),
(UUID(), 'NEW', 'New Customer', '#2196F3', 'Khách hàng mới'),
(UUID(), 'CHURNED', 'Churned', '#9E9E9E', 'Đã rời bỏ'),
(UUID(), 'HIGH_SPENDER', 'High Spender', '#E91E63', 'Chi tiêu cao');

-- ============================================================================
-- SEED DATA: Sample Journey
-- ============================================================================
INSERT INTO journeys (id, name, description, status, trigger_type, trigger_config) VALUES
(UUID(), 'Welcome Journey', 'Chào mừng khách hàng mới', 'DRAFT', 'signup', '{"delay_minutes": 0}');

SELECT 'crm_marketing_db initialized successfully with 12 tables!' AS status;
