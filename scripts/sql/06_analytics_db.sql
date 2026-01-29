-- ============================================================================
-- DATABASE: crm_analytics_db
-- Mục đích: Analytics, KPIs, ML Models, RAG Queries, Sentiments
-- Tables: 11
-- Port: 3315
-- ============================================================================

-- Đảm bảo sử dụng đúng database
USE crm_analytics_db;

-- Đặt character set
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- ============================================================================
-- BẢNG: kpi_definitions
-- ============================================================================
CREATE TABLE IF NOT EXISTS kpi_definitions (
    id          CHAR(36)    DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    code        VARCHAR(64) NOT NULL,
    name        VARCHAR(255) NOT NULL,
    description TEXT        NULL,
    unit        VARCHAR(32) NULL COMMENT 'VND, %, count, etc',
    agg_fn      VARCHAR(32) NOT NULL COMMENT 'SUM, AVG, COUNT, etc',
    data_source VARCHAR(100) NULL COMMENT 'Table or API to query',
    query_template TEXT     NULL COMMENT 'SQL template for calculation',
    
    CONSTRAINT uq_kpi_code UNIQUE (code)
) ENGINE=InnoDB;

-- ============================================================================
-- BẢNG: kpi_samples
-- ============================================================================
CREATE TABLE IF NOT EXISTS kpi_samples (
    id          CHAR(36)    DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    kpi_id      CHAR(36)    NOT NULL,
    ts          DATETIME(6) NOT NULL COMMENT 'Timestamp of measurement',
    value       DECIMAL(18, 6) NOT NULL,
    dimension   JSON        NULL COMMENT 'Breakdown dimensions {region, product_id, etc}',
    
    CONSTRAINT uq_kpi_ts UNIQUE (kpi_id, ts),
    CONSTRAINT fk_kpis_kpi FOREIGN KEY (kpi_id) REFERENCES kpi_definitions(id) ON DELETE CASCADE,
    INDEX idx_kpis_ts (kpi_id, ts)
) ENGINE=InnoDB;

-- ============================================================================
-- BẢNG: alert_rules
-- ============================================================================
CREATE TABLE IF NOT EXISTS alert_rules (
    id              CHAR(36)    DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    kpi_id          CHAR(36)    NOT NULL,
    name            VARCHAR(255) NOT NULL,
    op              ENUM('>', '>=', '<', '<=', '=', '!=') NOT NULL,
    threshold       DECIMAL(18, 6) NOT NULL,
    window_minutes  INT         DEFAULT 15 NOT NULL,
    severity        ENUM('INFO', 'WARN', 'CRITICAL') NOT NULL,
    notify_channels JSON        NULL COMMENT '["email", "slack", "discord"]',
    is_active       TINYINT(1)  DEFAULT 1 NOT NULL,
    
    CONSTRAINT fk_ar_kpi FOREIGN KEY (kpi_id) REFERENCES kpi_definitions(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================================
-- BẢNG: alerts
-- ============================================================================
CREATE TABLE IF NOT EXISTS alerts (
    id          CHAR(36)    DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    rule_id     CHAR(36)    NOT NULL,
    fired_at    DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    kpi_value   DECIMAL(18, 6) NULL,
    context     JSON        NULL,
    acknowledged_at DATETIME(6) NULL,
    acknowledged_by CHAR(36) NULL COMMENT 'User ID (no FK)',
    
    CONSTRAINT fk_alert_rule FOREIGN KEY (rule_id) REFERENCES alert_rules(id) ON DELETE CASCADE,
    INDEX idx_alert_fired (fired_at)
) ENGINE=InnoDB;

-- ============================================================================
-- BẢNG: ml_models
-- ============================================================================
CREATE TABLE IF NOT EXISTS ml_models (
    id          CHAR(36)    DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    name        VARCHAR(128) NOT NULL,
    version     VARCHAR(64) NOT NULL,
    model_type  VARCHAR(100) NULL COMMENT 'sentiment, intent, recommendation, etc',
    description TEXT        NULL,
    metrics     JSON        NULL COMMENT 'accuracy, f1, etc',
    artifact_url TEXT       NULL COMMENT 'Path to model files',
    is_active   TINYINT(1)  DEFAULT 1 NOT NULL,
    created_at  DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    
    CONSTRAINT uq_model_name_ver UNIQUE (name, version)
) ENGINE=InnoDB;

-- ============================================================================
-- BẢNG: predictions
-- ============================================================================
CREATE TABLE IF NOT EXISTS predictions (
    id              CHAR(36)    DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    model_id        CHAR(36)    NOT NULL,
    entity_type     VARCHAR(64) NOT NULL COMMENT 'ticket, order, user, etc',
    entity_id       CHAR(36)    NOT NULL,
    label           VARCHAR(64) NOT NULL,
    score           DECIMAL(4, 3) NULL,
    confidence      DECIMAL(4, 3) NULL,
    input_data      JSON        NULL COMMENT 'Input features (for debugging)',
    created_at      DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    
    CONSTRAINT fk_pred_model FOREIGN KEY (model_id) REFERENCES ml_models(id) ON DELETE CASCADE,
    CONSTRAINT chk_pred_score CHECK (score >= 0 AND score <= 1),
    INDEX idx_pred_entity (entity_type, entity_id),
    INDEX idx_pred_created (created_at)
) ENGINE=InnoDB;

-- ============================================================================
-- BẢNG: rag_queries
-- ============================================================================
CREATE TABLE IF NOT EXISTS rag_queries (
    id              CHAR(36)    DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    user_id         CHAR(36)    NULL COMMENT 'User ID (no FK)',
    session_id      VARCHAR(255) NULL,
    question        MEDIUMTEXT  NOT NULL,
    response        MEDIUMTEXT  NULL,
    sources         JSON        NULL COMMENT 'Retrieved document chunks',
    latency_ms      INT         NULL,
    model_used      VARCHAR(100) NULL,
    tokens_used     INT         NULL,
    created_at      DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    
    INDEX idx_ragq_user (user_id),
    INDEX idx_ragq_created (created_at)
) ENGINE=InnoDB;

-- ============================================================================
-- BẢNG: rag_feedback
-- ============================================================================
CREATE TABLE IF NOT EXISTS rag_feedback (
    id          CHAR(36)    DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    query_id    CHAR(36)    NOT NULL,
    helpful     TINYINT(1)  NULL,
    rating      INT         NULL COMMENT '1-5 stars',
    comment     TEXT        NULL,
    created_at  DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    
    CONSTRAINT fk_ragfb_query FOREIGN KEY (query_id) REFERENCES rag_queries(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================================
-- BẢNG: interaction_events
-- ============================================================================
CREATE TABLE IF NOT EXISTS interaction_events (
    id          CHAR(36)    DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    user_id     CHAR(36)    NULL COMMENT 'User ID (no FK)',
    session_id  VARCHAR(255) NULL,
    event_type  VARCHAR(64) NOT NULL COMMENT 'page_view, click, chat_start, etc',
    entity_type VARCHAR(64) NULL COMMENT 'ticket, product, order',
    entity_id   CHAR(36)    NULL,
    raw_text    TEXT        NULL COMMENT 'User input text for NLP',
    metadata    JSON        NULL,
    created_at  DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    
    INDEX idx_ie_user (user_id),
    INDEX idx_ie_type (event_type),
    INDEX idx_ie_entity (entity_type, entity_id),
    INDEX idx_ie_created (created_at)
) ENGINE=InnoDB;

-- ============================================================================
-- BẢNG: sentiments
-- ============================================================================
CREATE TABLE IF NOT EXISTS sentiments (
    id              CHAR(36)    DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    event_id        CHAR(36)    NOT NULL,
    label           ENUM('NEGATIVE', 'NEUTRAL', 'POSITIVE', 'MIXED') NOT NULL,
    score           DECIMAL(4, 3) NULL,
    model_version   VARCHAR(64) NOT NULL,
    inferred_at     DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    
    CONSTRAINT uq_sent_event UNIQUE (event_id),
    CONSTRAINT fk_sent_event FOREIGN KEY (event_id) REFERENCES interaction_events(id) ON DELETE CASCADE,
    CONSTRAINT chk_sent_score CHECK (score >= 0 AND score <= 1)
) ENGINE=InnoDB;

-- ============================================================================
-- BẢNG: analytics_queue
-- ============================================================================
CREATE TABLE IF NOT EXISTS analytics_queue (
    id          CHAR(36)    DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    data_kind   VARCHAR(64) NOT NULL COMMENT 'order_created, ticket_resolved, etc',
    payload     JSON        NOT NULL,
    status      ENUM('PENDING', 'PROCESSING', 'SENT', 'ERROR') DEFAULT 'PENDING' NOT NULL,
    created_at  DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    processed_at DATETIME(6) NULL,
    error_msg   TEXT        NULL,
    
    INDEX idx_aq_status (status),
    INDEX idx_aq_created (created_at)
) ENGINE=InnoDB;

-- ============================================================================
-- SEED DATA: Default KPI Definitions
-- ============================================================================
INSERT INTO kpi_definitions (id, code, name, description, unit, agg_fn, data_source) VALUES
(UUID(), 'TOTAL_REVENUE', 'Tổng doanh thu', 'Tổng doanh thu từ đơn hàng hoàn thành', 'VND', 'SUM', 'orders'),
(UUID(), 'ORDER_COUNT', 'Số đơn hàng', 'Tổng số đơn hàng', 'count', 'COUNT', 'orders'),
(UUID(), 'AVG_ORDER_VALUE', 'Giá trị đơn TB', 'Giá trị đơn hàng trung bình', 'VND', 'AVG', 'orders'),
(UUID(), 'TICKET_RESPONSE_TIME', 'Thời gian phản hồi TB', 'Thời gian phản hồi ticket trung bình', 'minutes', 'AVG', 'tickets'),
(UUID(), 'TICKET_RESOLUTION_TIME', 'Thời gian xử lý TB', 'Thời gian xử lý ticket trung bình', 'hours', 'AVG', 'tickets'),
(UUID(), 'CUSTOMER_SATISFACTION', 'Độ hài lòng KH', 'Điểm CSAT trung bình', '%', 'AVG', 'rag_feedback'),
(UUID(), 'RAG_ACCURACY', 'Độ chính xác RAG', 'Tỷ lệ câu trả lời RAG được đánh giá helpful', '%', 'AVG', 'rag_feedback'),
(UUID(), 'ACTIVE_USERS', 'Người dùng hoạt động', 'Số người dùng hoạt động', 'count', 'COUNT', 'interaction_events');

-- ============================================================================
-- SEED DATA: Default ML Models
-- ============================================================================
INSERT INTO ml_models (id, name, version, model_type, description, is_active) VALUES
(UUID(), 'sentiment-vietnamese', 'v1.0', 'sentiment', 'Vietnamese sentiment analysis model', 1),
(UUID(), 'intent-classification', 'v1.0', 'intent', 'Customer intent classification', 1),
(UUID(), 'product-recommendation', 'v1.0', 'recommendation', 'Product recommendation model', 1),
(UUID(), 'ticket-deduplication', 'v1.0', 'similarity', 'Ticket similarity detection', 1);

SELECT 'crm_analytics_db initialized successfully with 11 tables!' AS status;
