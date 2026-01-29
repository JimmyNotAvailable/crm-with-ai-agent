-- ============================================================================
-- DATABASE: crm_knowledge_db
-- Mục đích: Quản lý Knowledge Base, Documents, RAG content
-- Tables: 8
-- Port: 3314
-- ============================================================================

-- Đảm bảo sử dụng đúng database
USE crm_knowledge_db;

-- Đặt character set
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- ============================================================================
-- BẢNG: corpora
-- ============================================================================
CREATE TABLE IF NOT EXISTS corpora (
    id          CHAR(36)    NOT NULL PRIMARY KEY,
    code        VARCHAR(64) NOT NULL,
    name        VARCHAR(255) NOT NULL,
    description TEXT        NULL,
    is_active   TINYINT(1)  DEFAULT 1 NOT NULL,
    created_at  DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    
    CONSTRAINT uq_corpus_code UNIQUE (code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- BẢNG: documents
-- ============================================================================
CREATE TABLE IF NOT EXISTS documents (
    id          CHAR(36)    NOT NULL PRIMARY KEY,
    corpus_id   CHAR(36)    NOT NULL,
    
    -- File info
    file_name   VARCHAR(255) NOT NULL,
    file_type   VARCHAR(50) NULL COMMENT 'pdf, docx, md, txt',
    file_url    TEXT        NOT NULL,
    file_size   BIGINT      NULL,
    
    -- Processing status
    status      ENUM('PENDING', 'PROCESSING', 'INDEXED', 'FAILED') DEFAULT 'PENDING' NOT NULL,
    chunk_count INT         NULL,
    
    -- Metadata
    meta        JSON        NULL,
    
    uploaded_by CHAR(36)    NULL COMMENT 'User ID (no FK)',
    uploaded_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    indexed_at  DATETIME(6) NULL,
    error_msg   TEXT        NULL,
    
    CONSTRAINT fk_doc_corpus FOREIGN KEY (corpus_id) REFERENCES corpora(id) ON DELETE CASCADE,
    INDEX idx_doc_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- BẢNG: kb_tags
-- ============================================================================
CREATE TABLE IF NOT EXISTS kb_tags (
    id      CHAR(36)    NOT NULL PRIMARY KEY,
    name    VARCHAR(128) NOT NULL,
    color   VARCHAR(7)  NULL,
    
    CONSTRAINT uq_kbtag_name UNIQUE (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- BẢNG: kb_articles
-- ============================================================================
CREATE TABLE IF NOT EXISTS kb_articles (
    id          CHAR(36)    NOT NULL PRIMARY KEY,
    code        VARCHAR(64) NULL,
    slug        VARCHAR(255) NULL,
    
    -- Content
    title       VARCHAR(255) NOT NULL,
    summary     VARCHAR(500) NULL,
    body_md     MEDIUMTEXT  NOT NULL COMMENT 'Markdown content',
    body_html   MEDIUMTEXT  NULL COMMENT 'Rendered HTML',
    
    -- Categorization
    category    VARCHAR(100) NULL,
    
    -- Visibility
    is_public   TINYINT(1)  DEFAULT 1 NOT NULL,
    is_featured TINYINT(1)  DEFAULT 0 NOT NULL,
    
    -- Author (cross-service ref)
    created_by  CHAR(36)    NULL COMMENT 'User ID (no FK)',
    author_name VARCHAR(255) NULL COMMENT 'Denormalized',
    
    -- Stats
    view_count  INT         DEFAULT 0 NOT NULL,
    helpful_count INT       DEFAULT 0 NOT NULL,
    unhelpful_count INT     DEFAULT 0 NOT NULL,
    
    -- Timestamps
    created_at  DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    updated_at  DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) NOT NULL,
    published_at DATETIME(6) NULL,
    
    CONSTRAINT uq_kb_code UNIQUE (code),
    INDEX idx_kb_public (is_public),
    INDEX idx_kb_category (category),
    FULLTEXT INDEX ft_kb_search (title, summary, body_md)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- BẢNG: kb_article_tags
-- ============================================================================
CREATE TABLE IF NOT EXISTS kb_article_tags (
    article_id  CHAR(36) NOT NULL,
    tag_id      CHAR(36) NOT NULL,
    
    PRIMARY KEY (article_id, tag_id),
    CONSTRAINT fk_kbat_article FOREIGN KEY (article_id) REFERENCES kb_articles(id) ON DELETE CASCADE,
    CONSTRAINT fk_kbat_tag FOREIGN KEY (tag_id) REFERENCES kb_tags(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- BẢNG: kb_article_revisions
-- ============================================================================
CREATE TABLE IF NOT EXISTS kb_article_revisions (
    id          CHAR(36)    NOT NULL PRIMARY KEY,
    article_id  CHAR(36)    NOT NULL,
    version     INT         NOT NULL,
    title       VARCHAR(255) NOT NULL,
    body_md     MEDIUMTEXT  NOT NULL,
    edited_by   CHAR(36)    NULL COMMENT 'User ID (no FK)',
    edited_at   DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    change_note TEXT        NULL,
    
    CONSTRAINT uq_kb_rev UNIQUE (article_id, version),
    CONSTRAINT fk_kbr_article FOREIGN KEY (article_id) REFERENCES kb_articles(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- BẢNG: kb_feedback
-- ============================================================================
CREATE TABLE IF NOT EXISTS kb_feedback (
    id          CHAR(36)    NOT NULL PRIMARY KEY,
    article_id  CHAR(36)    NOT NULL,
    user_id     CHAR(36)    NULL COMMENT 'User ID (no FK)',
    helpful     TINYINT(1)  NULL,
    comment     TEXT        NULL,
    created_at  DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    
    CONSTRAINT fk_kbf_article FOREIGN KEY (article_id) REFERENCES kb_articles(id) ON DELETE CASCADE,
    INDEX idx_kbf_article (article_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- BẢNG: rag_health_snapshots
-- ============================================================================
CREATE TABLE IF NOT EXISTS rag_health_snapshots (
    id              CHAR(36)    NOT NULL PRIMARY KEY,
    corpus_id       CHAR(36)    NOT NULL,
    snapshot_at     DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
    total_docs      INT         DEFAULT 0 NOT NULL,
    indexed_docs    INT         DEFAULT 0 NOT NULL,
    stale_docs      INT         DEFAULT 0 NOT NULL,
    avg_latency_ms  INT         NULL,
    coverage_pct    DECIMAL(5, 2) NULL,
    status          ENUM('OK', 'WARN', 'ERROR') DEFAULT 'OK' NOT NULL,
    meta            JSON        NULL,
    
    CONSTRAINT fk_rhs_corpus FOREIGN KEY (corpus_id) REFERENCES corpora(id) ON DELETE CASCADE,
    INDEX idx_rhs_time (snapshot_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- SEED DATA: Default Corpora
-- ============================================================================
INSERT INTO corpora (id, code, name, description, is_active) VALUES
(UUID(), 'POLICIES', 'Chính sách & Điều khoản', 'Tập hợp các chính sách bảo hành, đổi trả, giao hàng', 1),
(UUID(), 'PRODUCTS', 'Thông tin sản phẩm', 'Mô tả chi tiết sản phẩm cho RAG', 1),
(UUID(), 'FAQ', 'Câu hỏi thường gặp', 'FAQ cho customer service chatbot', 1),
(UUID(), 'GUIDES', 'Hướng dẫn sử dụng', 'Hướng dẫn sử dụng sản phẩm', 1);

-- ============================================================================
-- SEED DATA: Default KB Tags
-- ============================================================================
INSERT INTO kb_tags (id, name, color) VALUES
(UUID(), 'warranty', '#4CAF50'),
(UUID(), 'return-policy', '#2196F3'),
(UUID(), 'shipping', '#FF9800'),
(UUID(), 'payment', '#9C27B0'),
(UUID(), 'faq', '#795548'),
(UUID(), 'guide', '#607D8B');

-- ============================================================================
-- SEED DATA: Default KB Articles
-- ============================================================================
INSERT INTO kb_articles (id, code, slug, title, summary, body_md, category, is_public, is_featured) VALUES
(UUID(), 'WARRANTY-POLICY', 'chinh-sach-bao-hanh', 'Chính sách bảo hành', 
'Thông tin chi tiết về chính sách bảo hành sản phẩm',
'# Chính sách bảo hành

## 1. Thời gian bảo hành
- Điện thoại: 12 tháng
- Laptop: 24 tháng
- Phụ kiện: 6 tháng

## 2. Điều kiện bảo hành
- Sản phẩm còn trong thời hạn bảo hành
- Tem bảo hành còn nguyên vẹn
- Lỗi do nhà sản xuất

## 3. Không bảo hành khi
- Sản phẩm bị rơi vỡ, vào nước
- Tự ý sửa chữa
- Hết hạn bảo hành

## 4. Quy trình bảo hành
1. Mang sản phẩm đến cửa hàng
2. Nhân viên kiểm tra và tiếp nhận
3. Thời gian xử lý: 7-14 ngày làm việc
4. Nhận sản phẩm sau khi sửa xong',
'Chính sách', 1, 1),

(UUID(), 'RETURN-POLICY', 'chinh-sach-doi-tra', 'Chính sách đổi trả', 
'Hướng dẫn đổi trả sản phẩm trong vòng 7 ngày',
'# Chính sách đổi trả

## 1. Điều kiện đổi trả
- Trong vòng 7 ngày kể từ ngày mua
- Sản phẩm còn nguyên seal/hộp
- Có hóa đơn mua hàng

## 2. Sản phẩm được đổi trả
- Sản phẩm lỗi từ nhà sản xuất
- Sản phẩm không đúng mô tả
- Khách hàng đổi ý (phí 10%)

## 3. Sản phẩm KHÔNG được đổi trả
- Đã qua sử dụng
- Sản phẩm khuyến mại
- Phụ kiện đã mở seal

## 4. Quy trình đổi trả
1. Liên hệ hotline: 1900 xxxx
2. Mang sản phẩm + hóa đơn đến cửa hàng
3. Nhân viên kiểm tra
4. Đổi sản phẩm mới hoặc hoàn tiền',
'Chính sách', 1, 1),

(UUID(), 'SHIPPING-POLICY', 'chinh-sach-giao-hang', 'Chính sách giao hàng',
'Thông tin về phí ship và thời gian giao hàng',
'# Chính sách giao hàng

## 1. Phí giao hàng
- Nội thành TP.HCM, Hà Nội: MIỄN PHÍ
- Các tỉnh thành khác: 30.000đ - 50.000đ
- Miễn phí ship đơn hàng từ 500.000đ

## 2. Thời gian giao hàng
- Nội thành: 2-4 giờ
- Ngoại thành: 1-2 ngày
- Tỉnh khác: 2-5 ngày

## 3. Đối tác vận chuyển
- GHN (Giao hàng nhanh)
- GHTK (Giao hàng tiết kiệm)
- Viettel Post

## 4. Lưu ý
- Kiểm tra hàng trước khi nhận
- Từ chối nhận nếu hàng bị hư hỏng
- Liên hệ hotline nếu giao trễ',
'Chính sách', 1, 0);

SELECT 'crm_knowledge_db initialized successfully with 8 tables!' AS status;
