-- ============================================================================
-- DATABASE: crm_identity_db
-- Mục đích: Quản lý Users, Roles, Permissions, Profiles, GDPR
-- Tables: 12
-- Port: 3310
-- ============================================================================

-- Đảm bảo sử dụng đúng database
USE crm_identity_db;

-- Đặt character set
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- ============================================================================
-- BẢNG: roles
-- ============================================================================
CREATE TABLE IF NOT EXISTS roles (
    id          CHAR(36)    DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    code        VARCHAR(64) NOT NULL,
    name        VARCHAR(128) NOT NULL,
    description TEXT        NULL,
    is_system   TINYINT(1)  DEFAULT 0 NOT NULL COMMENT 'Built-in role',
    created_at  DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    updated_at  DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL ON UPDATE CURRENT_TIMESTAMP(6),
    
    CONSTRAINT uq_role_code UNIQUE (code)
) ENGINE=InnoDB;

-- ============================================================================
-- BẢNG: permissions
-- ============================================================================
CREATE TABLE IF NOT EXISTS permissions (
    id          CHAR(36)    DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    code        VARCHAR(128) NOT NULL,
    name        VARCHAR(255) NOT NULL,
    resource    VARCHAR(64) NOT NULL COMMENT 'e.g. orders, products, tickets',
    action      VARCHAR(64) NOT NULL COMMENT 'e.g. read, write, delete',
    description TEXT        NULL,
    
    CONSTRAINT uq_perm_code UNIQUE (code),
    INDEX idx_perm_resource (resource)
) ENGINE=InnoDB;

-- ============================================================================
-- BẢNG: role_permissions
-- ============================================================================
CREATE TABLE IF NOT EXISTS role_permissions (
    role_id       CHAR(36) NOT NULL,
    permission_id CHAR(36) NOT NULL,
    
    PRIMARY KEY (role_id, permission_id),
    CONSTRAINT fk_rp_role FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    CONSTRAINT fk_rp_perm FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================================
-- BẢNG: users
-- ============================================================================
CREATE TABLE IF NOT EXISTS users (
    id              CHAR(36)        DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    email           VARCHAR(320)    NOT NULL,
    password_hash   VARCHAR(255)    NOT NULL,
    phone           VARCHAR(50)     NULL,
    full_name       VARCHAR(255)    NULL,
    avatar_url      TEXT            NULL,
    user_type       ENUM('CUSTOMER', 'STAFF', 'ADMIN', 'SYSTEM') DEFAULT 'CUSTOMER' NOT NULL,
    status          ENUM('ACTIVE', 'INACTIVE', 'SUSPENDED', 'DELETED') DEFAULT 'ACTIVE' NOT NULL,
    email_verified  TINYINT(1)      DEFAULT 0 NOT NULL,
    phone_verified  TINYINT(1)      DEFAULT 0 NOT NULL,
    locale          VARCHAR(10)     DEFAULT 'vi_VN' NOT NULL,
    timezone        VARCHAR(64)     DEFAULT 'Asia/Ho_Chi_Minh' NOT NULL,
    last_login_at   DATETIME(6)     NULL,
    last_login_ip   VARCHAR(45)     NULL,
    failed_login_attempts INT       DEFAULT 0 NOT NULL,
    locked_until    DATETIME(6)     NULL,
    password_changed_at DATETIME(6) NULL,
    created_at      DATETIME(6)     DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    updated_at      DATETIME(6)     DEFAULT CURRENT_TIMESTAMP(6) NOT NULL ON UPDATE CURRENT_TIMESTAMP(6),
    
    CONSTRAINT uq_user_email UNIQUE (email),
    INDEX idx_user_type (user_type),
    INDEX idx_user_status (status),
    INDEX idx_user_phone (phone)
) ENGINE=InnoDB;

-- ============================================================================
-- BẢNG: user_roles
-- ============================================================================
CREATE TABLE IF NOT EXISTS user_roles (
    user_id  CHAR(36) NOT NULL,
    role_id  CHAR(36) NOT NULL,
    
    PRIMARY KEY (user_id, role_id),
    CONSTRAINT fk_ur_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_ur_role FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================================
-- BẢNG: addresses
-- ============================================================================
CREATE TABLE IF NOT EXISTS addresses (
    id          CHAR(36)    DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    user_id     CHAR(36)    NOT NULL,
    type        ENUM('SHIPPING', 'BILLING', 'BOTH') DEFAULT 'BOTH' NOT NULL,
    is_default  TINYINT(1)  DEFAULT 0 NOT NULL,
    full_name   VARCHAR(255) NOT NULL,
    phone       VARCHAR(50) NULL,
    line1       VARCHAR(255) NOT NULL,
    line2       VARCHAR(255) NULL,
    ward        VARCHAR(120) NULL,
    district    VARCHAR(120) NULL,
    city        VARCHAR(120) NOT NULL,
    province    VARCHAR(120) NULL,
    postal_code VARCHAR(30) NULL,
    country     VARCHAR(2)  DEFAULT 'VN' NOT NULL,
    created_at  DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    updated_at  DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL ON UPDATE CURRENT_TIMESTAMP(6),
    
    CONSTRAINT fk_addr_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_addr_user (user_id)
) ENGINE=InnoDB;

-- ============================================================================
-- BẢNG: customer_profiles
-- ============================================================================
CREATE TABLE IF NOT EXISTS customer_profiles (
    id                  CHAR(36)    DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    user_id             CHAR(36)    NOT NULL,
    date_of_birth       DATE        NULL,
    gender              ENUM('MALE', 'FEMALE', 'OTHER', 'UNDISCLOSED') NULL,
    vip_tier            ENUM('STANDARD', 'SILVER', 'GOLD', 'PLATINUM') DEFAULT 'STANDARD' NOT NULL,
    loyalty_points      INT         DEFAULT 0 NOT NULL,
    total_spent         DECIMAL(14, 2) DEFAULT 0.00 NOT NULL,
    total_orders        INT         DEFAULT 0 NOT NULL,
    first_order_at      DATETIME(6) NULL,
    last_order_at       DATETIME(6) NULL,
    preferred_channel   VARCHAR(50) NULL,
    marketing_consent   TINYINT(1)  DEFAULT 0 NOT NULL,
    
    CONSTRAINT uq_cp_user UNIQUE (user_id),
    CONSTRAINT fk_cp_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================================
-- BẢNG: staff_profiles
-- ============================================================================
CREATE TABLE IF NOT EXISTS staff_profiles (
    id              CHAR(36)    DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    user_id         CHAR(36)    NOT NULL,
    employee_code   VARCHAR(50) NULL,
    department      VARCHAR(100) NULL,
    position        VARCHAR(100) NULL,
    manager_id      CHAR(36)    NULL COMMENT 'Direct manager user_id',
    hire_date       DATE        NULL,
    skills          JSON        NULL COMMENT '["sales", "support", "tech"]',
    max_concurrent_chats INT    DEFAULT 5 NOT NULL,
    
    CONSTRAINT uq_sp_user UNIQUE (user_id),
    CONSTRAINT fk_sp_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================================
-- BẢNG: consents (GDPR consent tracking)
-- ============================================================================
CREATE TABLE IF NOT EXISTS consents (
    id              CHAR(36)    DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    user_id         CHAR(36)    NOT NULL,
    consent_type    VARCHAR(64) NOT NULL COMMENT 'marketing, analytics, third_party',
    granted         TINYINT(1)  NOT NULL,
    granted_at      DATETIME(6) NOT NULL,
    revoked_at      DATETIME(6) NULL,
    ip_address      VARCHAR(45) NULL,
    source          VARCHAR(100) NULL COMMENT 'registration, settings, etc',
    
    CONSTRAINT fk_consent_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_consent_user (user_id),
    INDEX idx_consent_type (consent_type)
) ENGINE=InnoDB;

-- ============================================================================
-- BẢNG: audit_logs
-- ============================================================================
CREATE TABLE IF NOT EXISTS audit_logs (
    id          CHAR(36)    DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    user_id     CHAR(36)    NULL,
    action      VARCHAR(64) NOT NULL COMMENT 'login, logout, update_profile, etc',
    entity_type VARCHAR(64) NULL COMMENT 'user, order, ticket',
    entity_id   CHAR(36)    NULL,
    old_values  JSON        NULL,
    new_values  JSON        NULL,
    ip_address  VARCHAR(45) NULL,
    user_agent  TEXT        NULL,
    created_at  DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    
    INDEX idx_audit_user (user_id),
    INDEX idx_audit_action (action),
    INDEX idx_audit_entity (entity_type, entity_id),
    INDEX idx_audit_created (created_at)
) ENGINE=InnoDB;

-- ============================================================================
-- BẢNG: erasure_requests (GDPR Right to be forgotten)
-- ============================================================================
CREATE TABLE IF NOT EXISTS erasure_requests (
    id          CHAR(36)    DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    user_id     CHAR(36)    NOT NULL,
    status      ENUM('PENDING', 'PROCESSING', 'COMPLETED', 'REJECTED') DEFAULT 'PENDING' NOT NULL,
    reason      TEXT        NULL,
    requested_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    processed_at DATETIME(6) NULL,
    processed_by CHAR(36)   NULL,
    note        TEXT        NULL,
    
    CONSTRAINT fk_er_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_er_status (status)
) ENGINE=InnoDB;

-- ============================================================================
-- BẢNG: pii_access_logs (Track who accessed PII)
-- ============================================================================
CREATE TABLE IF NOT EXISTS pii_access_logs (
    id              CHAR(36)    DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    accessor_id     CHAR(36)    NOT NULL COMMENT 'User who accessed',
    target_user_id  CHAR(36)    NOT NULL COMMENT 'User whose data was accessed',
    field_accessed  VARCHAR(64) NOT NULL COMMENT 'email, phone, address, etc',
    purpose         VARCHAR(255) NULL,
    accessed_at     DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    
    INDEX idx_pii_accessor (accessor_id),
    INDEX idx_pii_target (target_user_id),
    INDEX idx_pii_accessed (accessed_at)
) ENGINE=InnoDB;

-- ============================================================================
-- BẢNG: data_retention_policies
-- ============================================================================
CREATE TABLE IF NOT EXISTS data_retention_policies (
    id              CHAR(36)    DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    entity_type     VARCHAR(64) NOT NULL COMMENT 'user, order, ticket, etc',
    retention_days  INT         NOT NULL,
    action          ENUM('DELETE', 'ANONYMIZE', 'ARCHIVE') NOT NULL,
    is_active       TINYINT(1)  DEFAULT 1 NOT NULL,
    last_run_at     DATETIME(6) NULL,
    
    CONSTRAINT uq_drp_entity UNIQUE (entity_type)
) ENGINE=InnoDB;

-- ============================================================================
-- SEED DATA: Default Roles
-- ============================================================================
INSERT INTO roles (id, code, name, description, is_system) VALUES
(UUID(), 'ADMIN', 'Administrator', 'Full system access', 1),
(UUID(), 'STAFF', 'Staff', 'Customer support staff', 1),
(UUID(), 'CUSTOMER', 'Customer', 'Regular customer', 1),
(UUID(), 'MANAGER', 'Manager', 'Team manager with elevated permissions', 1);

-- ============================================================================
-- SEED DATA: Default Permissions
-- ============================================================================
INSERT INTO permissions (id, code, name, resource, action) VALUES
-- User permissions
(UUID(), 'users.read', 'View Users', 'users', 'read'),
(UUID(), 'users.write', 'Create/Edit Users', 'users', 'write'),
(UUID(), 'users.delete', 'Delete Users', 'users', 'delete'),
-- Product permissions
(UUID(), 'products.read', 'View Products', 'products', 'read'),
(UUID(), 'products.write', 'Create/Edit Products', 'products', 'write'),
(UUID(), 'products.delete', 'Delete Products', 'products', 'delete'),
-- Order permissions
(UUID(), 'orders.read', 'View Orders', 'orders', 'read'),
(UUID(), 'orders.write', 'Create/Edit Orders', 'orders', 'write'),
(UUID(), 'orders.delete', 'Delete Orders', 'orders', 'delete'),
-- Ticket permissions
(UUID(), 'tickets.read', 'View Tickets', 'tickets', 'read'),
(UUID(), 'tickets.write', 'Create/Edit Tickets', 'tickets', 'write'),
(UUID(), 'tickets.assign', 'Assign Tickets', 'tickets', 'assign'),
-- KB permissions
(UUID(), 'kb.read', 'View Knowledge Base', 'kb', 'read'),
(UUID(), 'kb.write', 'Create/Edit KB Articles', 'kb', 'write'),
-- Analytics permissions
(UUID(), 'analytics.read', 'View Analytics', 'analytics', 'read'),
(UUID(), 'analytics.export', 'Export Analytics Data', 'analytics', 'export');

-- ============================================================================
-- SEED DATA: Data Retention Policies
-- ============================================================================
INSERT INTO data_retention_policies (id, entity_type, retention_days, action, is_active) VALUES
(UUID(), 'audit_logs', 365, 'DELETE', 1),
(UUID(), 'pii_access_logs', 180, 'DELETE', 1),
(UUID(), 'deleted_users', 30, 'DELETE', 1);

SELECT 'crm_identity_db initialized successfully with 12 tables!' AS status;
