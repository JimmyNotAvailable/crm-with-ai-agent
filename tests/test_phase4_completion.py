"""
Phase 4 Completion Tests
Verifies:
- 4.1: Audit middleware registered in main.py
- 4.2: Backend endpoint structure & AI module structure
- 4.3: Integration flow checks (models, schemas, services)
- 4.4: Legacy code documentation / deprecation markers
- 4.5: UI pagination & polish components
- 4.6: Docker configuration completeness
- 4.7: Documentation completeness
"""
import os
import re
import json
import importlib
import subprocess
import pytest

ROOT = os.path.dirname(os.path.dirname(__file__))
BACKEND = os.path.join(ROOT, "backend")
AI_MODULES = os.path.join(ROOT, "ai_modules")
FRONTEND_SRC = os.path.join(ROOT, "frontend", "src")


def read(rel_path):
    """Read file relative to project root."""
    full = os.path.join(ROOT, rel_path)
    assert os.path.exists(full), f"File not found: {full}"
    with open(full, encoding="utf-8") as f:
        return f.read()


# ==================================================================
# 4.1 — Audit Middleware Registration
# ==================================================================
class TestTask41_AuditMiddleware:
    """Verify audit logging middleware is registered and functional."""

    def test_audit_middleware_file_exists(self):
        assert os.path.exists(os.path.join(BACKEND, "middleware", "audit_logging.py"))

    def test_audit_middleware_registered_in_main(self):
        content = read("backend/main.py")
        assert "AuditLoggingMiddleware" in content
        assert "add_middleware" in content

    def test_audit_middleware_class_exists(self):
        content = read("backend/middleware/audit_logging.py")
        assert "class AuditLoggingMiddleware" in content
        assert "BaseHTTPMiddleware" in content

    def test_audit_log_model_exists(self):
        content = read("backend/models/audit_log.py")
        assert "class AuditLog" in content
        assert "audit_logs" in content

    def test_audit_log_model_uuid_pk(self):
        content = read("backend/models/audit_log.py")
        assert "String(36)" in content
        assert "uuid" in content.lower()

    def test_audit_endpoints_exist(self):
        content = read("backend/api/v1/endpoints/audit_logs.py")
        assert "router" in content

    def test_pii_masking_exists(self):
        assert os.path.exists(os.path.join(BACKEND, "utils", "pii_masking.py"))
        content = read("backend/utils/pii_masking.py")
        assert "PIIMasker" in content


# ==================================================================
# 4.2 — Backend Endpoint Structure
# ==================================================================
class TestTask42_BackendEndpoints:
    """Verify all 13 router groups exist and are registered."""

    EXPECTED_ENDPOINTS = [
        "auth.py",
        "products.py",
        "orders.py",
        "tickets.py",
        "ticket_deduplication.py",
        "cart.py",
        "rag.py",
        "kb_articles.py",
        "summarization.py",
        "analytics.py",
        "audit_logs.py",
        "personalization.py",
        "knowledge_sync.py",
    ]

    @pytest.mark.parametrize("endpoint_file", EXPECTED_ENDPOINTS)
    def test_endpoint_file_exists(self, endpoint_file):
        path = os.path.join(BACKEND, "api", "v1", "endpoints", endpoint_file)
        assert os.path.exists(path), f"Missing endpoint: {endpoint_file}"

    @pytest.mark.parametrize("endpoint_file", EXPECTED_ENDPOINTS)
    def test_endpoint_has_router(self, endpoint_file):
        content = read(f"backend/api/v1/endpoints/{endpoint_file}")
        assert "router" in content
        assert "APIRouter" in content

    EXPECTED_ROUTERS_IN_MAIN = [
        "auth.router",
        "products.router",
        "orders.router",
        "tickets.router",
        "ticket_deduplication.router",
        "cart.router",
        "rag.router",
        "kb_articles.router",
        "summarization.router",
        "analytics.router",
        "audit_logs.router",
        "personalization.router",
        "knowledge_sync.router",
    ]

    @pytest.mark.parametrize("router_ref", EXPECTED_ROUTERS_IN_MAIN)
    def test_router_registered_in_main(self, router_ref):
        content = read("backend/main.py")
        assert router_ref in content, f"Router {router_ref} not in main.py"


# ==================================================================
# 4.2b — Backend Models Structure
# ==================================================================
class TestTask42b_BackendModels:
    """Verify all models exist with UUID primary keys."""

    MODELS = [
        ("models/user.py", "User", "users"),
        ("models/product.py", "Product", "products"),
        ("models/order.py", "Order", "orders"),
        ("models/ticket.py", "Ticket", "tickets"),
        ("models/conversation.py", "Conversation", "conversations"),
        ("models/cart.py", "Cart", "carts"),
        ("models/kb_article.py", "KBArticle", "kb_articles"),
        ("models/audit_log.py", "AuditLog", "audit_logs"),
    ]

    @pytest.mark.parametrize("path,class_name,table", MODELS)
    def test_model_exists(self, path, class_name, table):
        content = read(f"backend/{path}")
        assert f"class {class_name}" in content
        assert table in content

    def test_user_model_uuid(self):
        content = read("backend/models/user.py")
        assert "String(36)" in content

    def test_product_model_uuid(self):
        content = read("backend/models/product.py")
        assert "String(36)" in content

    def test_order_model_uuid(self):
        content = read("backend/models/order.py")
        assert "String(36)" in content

    def test_ticket_model_uuid(self):
        content = read("backend/models/ticket.py")
        assert "String(36)" in content


# ==================================================================
# 4.2c — AI Module Structure
# ==================================================================
class TestTask42c_AIModules:
    """Verify all AI modules are properly structured."""

    def test_core_config_exists(self):
        content = read("ai_modules/core/config.py")
        assert "AIConfig" in content
        assert "ai_config" in content

    def test_core_base_agent_exists(self):
        content = read("ai_modules/core/base_agent.py")
        assert "BaseAgent" in content
        assert "AgentResponse" in content
        assert "AgentType" in content

    def test_customer_service_agent_exists(self):
        content = read("ai_modules/agent_customer_service/agent.py")
        assert "CustomerServiceAgent" in content
        assert "BaseAgent" in content

    def test_operations_agent_exists(self):
        content = read("ai_modules/agent_operations/agent.py")
        assert "OperationsAgent" in content
        assert "BaseAgent" in content

    def test_operations_agent_has_sentiment(self):
        content = read("ai_modules/agent_operations/agent.py")
        assert "SentimentAnalyzer" in content
        assert "_handle_analyze_sentiment" in content

    def test_operations_agent_has_dedup(self):
        content = read("ai_modules/agent_operations/agent.py")
        assert "TicketDeduplicationService" in content
        assert "_handle_find_duplicates" in content

    def test_sentiment_analyzer_exists(self):
        content = read("ai_modules/sentiment/analyzer.py")
        assert "class SentimentAnalyzer" in content
        assert "analyze_text" in content
        assert "analyze_ticket" in content
        assert "SentimentLabel" in content

    def test_sentiment_analyzer_has_llm_support(self):
        content = read("ai_modules/sentiment/analyzer.py")
        assert "gemini" in content.lower()
        assert "openai" in content.lower()
        assert "rule_based" in content

    def test_rag_service_exists(self):
        content = read("ai_modules/agent_customer_service/rag/service.py")
        assert "RAGService" in content

    def test_rag_retriever_exists(self):
        content = read("ai_modules/agent_customer_service/rag/retriever.py")
        assert "PolicyRetriever" in content or "Retriever" in content

    def test_rag_indexer_exists(self):
        content = read("ai_modules/agent_customer_service/rag/indexer.py")
        assert "ChromaIndexer" in content or "Indexer" in content

    def test_recommender_exists(self):
        content = read("ai_modules/agent_customer_service/recommendation/recommender.py")
        assert "ProductRecommender" in content or "Recommender" in content

    def test_summarizer_exists(self):
        content = read("ai_modules/agent_customer_service/summarization/summarizer.py")
        assert "ConversationSummarizer" in content or "Summarizer" in content

    def test_order_workflow_exists(self):
        content = read("ai_modules/agent_customer_service/order_workflow/workflow_manager.py")
        assert "OrderWorkflowManager" in content

    def test_qr_generator_exists(self):
        content = read("ai_modules/agent_customer_service/order_workflow/qr_generator.py")
        assert "QRGenerator" in content

    def test_ticket_dedup_service_exists(self):
        content = read("ai_modules/ticket_deduplication.py")
        assert "TicketDeduplicationService" in content
        assert "find_similar_tickets" in content


# ==================================================================
# 4.2d — AI Sentiment Module Importable
# ==================================================================
class TestTask42d_SentimentImport:
    """Verify Sentiment module can be imported."""

    def test_sentiment_module_imports(self):
        """Test that sentiment module is importable"""
        from ai_modules.sentiment import SentimentAnalyzer, SentimentResult, SentimentLabel
        assert SentimentAnalyzer is not None
        assert SentimentResult is not None
        assert SentimentLabel is not None

    def test_sentiment_label_values(self):
        from ai_modules.sentiment import SentimentLabel
        assert SentimentLabel.POSITIVE.value == "POSITIVE"
        assert SentimentLabel.NEUTRAL.value == "NEUTRAL"
        assert SentimentLabel.NEGATIVE.value == "NEGATIVE"

    def test_sentiment_analyze_text(self):
        """Test rule-based sentiment on simple text"""
        from ai_modules.sentiment import SentimentAnalyzer
        analyzer = SentimentAnalyzer()
        
        # Positive
        result = analyzer.analyze_text("Sản phẩm rất tốt, tuyệt vời!")
        assert result.label.value == "POSITIVE"
        assert result.score > 0

        # Negative
        result = analyzer.analyze_text("Sản phẩm tệ, tôi thất vọng")
        assert result.label.value == "NEGATIVE"
        assert result.score < 0

    def test_sentiment_batch_analyze(self):
        from ai_modules.sentiment import SentimentAnalyzer
        analyzer = SentimentAnalyzer()
        results = analyzer.batch_analyze(["tốt quá", "xấu quá", "bình thường"])
        assert len(results) == 3

    def test_sentiment_empty_text(self):
        from ai_modules.sentiment import SentimentAnalyzer
        analyzer = SentimentAnalyzer()
        result = analyzer.analyze_text("")
        assert result.label.value == "NEUTRAL"

    def test_sentiment_result_to_dict(self):
        from ai_modules.sentiment import SentimentAnalyzer
        analyzer = SentimentAnalyzer()
        result = analyzer.analyze_text("Cảm ơn bạn rất nhiều!")
        d = result.to_dict()
        assert "score" in d
        assert "label" in d
        assert "confidence" in d
        assert "provider" in d


# ==================================================================
# 4.3 — Integration Flow Checks
# ==================================================================
class TestTask43_IntegrationFlow:
    """Verify end-to-end flow components exist."""

    def test_auth_endpoint_has_login(self):
        content = read("backend/api/v1/endpoints/auth.py")
        assert "login" in content.lower()

    def test_auth_endpoint_has_register(self):
        content = read("backend/api/v1/endpoints/auth.py")
        assert "register" in content.lower()

    def test_rag_endpoint_has_chat(self):
        content = read("backend/api/v1/endpoints/rag.py")
        assert "chat" in content.lower()

    def test_order_endpoint_has_cancel(self):
        content = read("backend/api/v1/endpoints/orders.py")
        assert "cancel" in content.lower()

    def test_ticket_endpoint_has_create(self):
        content = read("backend/api/v1/endpoints/tickets.py")
        assert "create" in content.lower() or "POST" in content

    def test_cart_endpoint_has_checkout(self):
        content = read("backend/api/v1/endpoints/cart.py")
        assert "checkout" in content.lower()

    def test_db_session_has_7_databases(self):
        content = read("backend/database/session.py")
        db_names = ["identity", "product", "order", "support", "knowledge", "analytics", "marketing"]
        for db_name in db_names:
            assert db_name in content.lower(), f"Missing {db_name} DB config"

    def test_db_session_has_health_check(self):
        content = read("backend/database/session.py")
        assert "check_database_health" in content

    def test_security_utils_exist(self):
        content = read("backend/utils/security.py")
        assert "verify" in content.lower() or "hash" in content.lower() or "password" in content.lower()

    def test_ticket_routing_service_exists(self):
        content = read("backend/services/ticket_routing.py")
        assert "routing" in content.lower() or "assign" in content.lower()

    def test_behavior_tracking_service_exists(self):
        content = read("backend/services/behavior_tracking.py")
        assert "Behavior" in content or "tracking" in content.lower()

    def test_knowledge_sync_service_exists(self):
        content = read("backend/services/knowledge_sync.py")
        assert "sync" in content.lower()


# ==================================================================
# 4.4 — Legacy Code Documentation
# ==================================================================
class TestTask44_LegacyCode:
    """Verify legacy modules have deprecation markers or docs."""

    def test_legacy_agent_tools_has_docstring(self):
        content = read("ai_modules/agents/agent_tools.py")
        assert "class AgentTools" in content
        # Should have some form of documentation
        assert '"""' in content

    def test_legacy_rag_pipeline_has_docstring(self):
        content = read("ai_modules/rag_pipeline/rag_pipeline.py")
        assert '"""' in content

    def test_legacy_summarization_has_docstring(self):
        content = read("ai_modules/summarization.py")
        assert '"""' in content

    def test_new_agents_exist_alongside_legacy(self):
        """Verify new agent implementations exist"""
        assert os.path.exists(os.path.join(AI_MODULES, "agent_customer_service", "agent.py"))
        assert os.path.exists(os.path.join(AI_MODULES, "agent_operations", "agent.py"))

    def test_nlq_stub_documented(self):
        """NLQ module is a stub - verify documented"""
        content = read("ai_modules/nlq/__init__.py")
        assert "Natural Language Query" in content or "NLQ" in content

    def test_vector_store_stub_documented(self):
        """Vector store module is a stub - ChromaDB used via RAG instead"""
        content = read("ai_modules/vector_store/__init__.py")
        assert "Vector" in content


# ==================================================================
# 4.5 — UI Polish
# ==================================================================
class TestTask45_UIPolish:
    """Verify UI polish: pagination, notifications, responsive."""

    def test_products_page_has_pagination(self):
        content = read("frontend/src/pages/Products.jsx")
        # Products should have search + pagination
        assert "search" in content.lower() or "filter" in content.lower()
        assert "Pagination" in content, "Products.jsx should use Pagination component"
        assert "currentPage" in content, "Products.jsx should track currentPage"

    def test_orders_page_has_pagination(self):
        content = read("frontend/src/pages/Orders.jsx")
        assert "Pagination" in content, "Orders.jsx should use Pagination component"
        assert "currentPage" in content, "Orders.jsx should track currentPage"

    def test_pagination_component_exists(self):
        content = read("frontend/src/components/Pagination.jsx")
        assert "totalPages" in content
        assert "onPageChange" in content
        assert "currentPage" in content

    def test_notification_toast_exists(self):
        content = read("frontend/src/components/NotificationToast.jsx")
        assert "notification" in content.lower()

    def test_no_alert_in_pages(self):
        """No alert() calls in any page"""
        pages_dir = os.path.join(FRONTEND_SRC, "pages")
        for fname in os.listdir(pages_dir):
            if fname.endswith(".jsx"):
                content = read(f"frontend/src/pages/{fname}")
                assert "alert(" not in content, f"alert() found in {fname}"

    def test_no_confirm_in_pages(self):
        """No confirm() calls in any page"""
        pages_dir = os.path.join(FRONTEND_SRC, "pages")
        for fname in os.listdir(pages_dir):
            if fname.endswith(".jsx"):
                content = read(f"frontend/src/pages/{fname}")
                # Only match standalone confirm(, not confirmDeleteId etc
                matches = re.findall(r'\bconfirm\s*\(', content)
                assert not matches, f"confirm() found in {fname}"

    def test_all_pages_use_api_service(self):
        """All pages should import from services/api"""
        pages_using_api = [
            "Products.jsx", "Cart.jsx", "Chat.jsx",
            "Tickets.jsx", "KnowledgeBase.jsx", "Dashboard.jsx",
            "Orders.jsx", "Admin.jsx", "ProductDetail.jsx",
        ]
        for page in pages_using_api:
            path = os.path.join(FRONTEND_SRC, "pages", page)
            if os.path.exists(path):
                content = read(f"frontend/src/pages/{page}")
                assert "from '../services/api'" in content or "from '../../services/api'" in content, \
                    f"{page} doesn't import API service"

    def test_tailwind_config_exists(self):
        assert os.path.exists(os.path.join(ROOT, "frontend", "tailwind.config.js"))

    def test_postcss_config_exists(self):
        assert os.path.exists(os.path.join(ROOT, "frontend", "postcss.config.js"))


# ==================================================================
# 4.6 — Docker Configuration
# ==================================================================
class TestTask46_DockerConfig:
    """Verify Docker Compose configuration is complete."""

    def test_docker_compose_exists(self):
        assert os.path.exists(os.path.join(ROOT, "docker-compose.yml"))

    def test_docker_compose_has_7_databases(self):
        content = read("docker-compose.yml")
        dbs = [
            "mysql-identity", "mysql-product", "mysql-order",
            "mysql-support", "mysql-knowledge", "mysql-analytics",
            "mysql-marketing"
        ]
        for db_name in dbs:
            assert db_name in content, f"Missing {db_name} in docker-compose.yml"

    def test_docker_compose_has_backend(self):
        content = read("docker-compose.yml")
        assert "backend:" in content

    def test_docker_compose_has_frontend(self):
        content = read("docker-compose.yml")
        assert "frontend:" in content

    def test_docker_compose_has_ports(self):
        content = read("docker-compose.yml")
        ports = ["3310:3306", "3311:3306", "3312:3306", "3313:3306",
                 "3314:3306", "3315:3306", "3316:3306", "8000:8000"]
        for port in ports:
            assert port in content, f"Missing port mapping {port}"

    def test_docker_compose_has_healthchecks(self):
        content = read("docker-compose.yml")
        assert content.count("healthcheck:") >= 7  # At least 7 DB healthchecks

    def test_docker_compose_has_volumes(self):
        content = read("docker-compose.yml")
        volumes = ["identity_data", "product_data", "order_data",
                    "support_data", "knowledge_data", "analytics_data",
                    "marketing_data"]
        for vol in volumes:
            assert vol in content, f"Missing volume {vol}"

    def test_docker_compose_has_network(self):
        content = read("docker-compose.yml")
        assert "crm-network" in content

    def test_docker_compose_has_sql_init_scripts(self):
        content = read("docker-compose.yml")
        sql_files = [
            "01_identity_db.sql", "02_product_db.sql", "03_order_db.sql",
            "04_support_db.sql", "05_knowledge_db.sql", "06_analytics_db.sql",
            "07_marketing_db.sql"
        ]
        for sql_file in sql_files:
            assert sql_file in content, f"Missing SQL init: {sql_file}"

    def test_backend_dockerfile_exists(self):
        assert os.path.exists(os.path.join(ROOT, "docker", "Dockerfile.backend"))

    def test_frontend_dockerfile_exists(self):
        assert os.path.exists(os.path.join(ROOT, "docker", "Dockerfile.frontend"))

    def test_nginx_config_exists(self):
        assert os.path.exists(os.path.join(ROOT, "docker", "nginx.conf"))


# ==================================================================
# 4.7 — Documentation
# ==================================================================
class TestTask47_Documentation:
    """Verify documentation files exist and are up to date."""

    REQUIRED_DOCS = [
        "docs/PROJECT_STRUCTURE.md",
        "docs/TECH_STACK_SUMMARY.md",
        "docs/QUICKSTART.md",
        "docs/BAO_CAO_TONG_QUAN_TIEN_DO_DU_AN.md",
    ]

    @pytest.mark.parametrize("doc_path", REQUIRED_DOCS)
    def test_doc_exists(self, doc_path):
        assert os.path.exists(os.path.join(ROOT, doc_path)), f"Missing: {doc_path}"

    def test_readme_exists(self):
        assert os.path.exists(os.path.join(ROOT, "README.md"))

    def test_readme_has_content(self):
        content = read("README.md")
        assert len(content) > 100

    def test_requirements_txt_exists(self):
        assert os.path.exists(os.path.join(ROOT, "requirements.txt"))


# ==================================================================
# 4.8 — Frontend Build Verification
# ==================================================================
class TestTask48_FrontendBuild:
    """Verify frontend builds successfully."""

    def test_vite_build_succeeds(self):
        frontend_dir = os.path.join(ROOT, "frontend")
        result = subprocess.run(
            ["npx", "vite", "build"],
            cwd=frontend_dir,
            capture_output=True,
            text=True,
            timeout=120,
            shell=True
        )
        combined = result.stdout + result.stderr
        assert "built in" in combined, f"Build failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
