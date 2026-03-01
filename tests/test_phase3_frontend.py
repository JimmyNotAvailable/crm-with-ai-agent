"""
Phase 3 Frontend Validation Tests
Verifies frontend architecture:
- Centralized API service layer
- Zustand state management
- Notification system
- All pages migrated (no hardcoded URLs, no alert/confirm)
- New pages created
- Role-based navigation
- Build success
"""
import os
import re
import subprocess
import pytest

FRONTEND_SRC = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "frontend", "src"
)

def read_file(rel_path):
    """Read a frontend source file."""
    full = os.path.join(FRONTEND_SRC, rel_path)
    assert os.path.exists(full), f"File not found: {rel_path}"
    with open(full, encoding="utf-8") as f:
        return f.read()


# ==================================================================
# 3.1 - API Service Layer
# ==================================================================
class TestTask31_APIService:
    """Verify centralized API service exists and has all required exports."""

    def test_api_file_exists(self):
        assert os.path.exists(os.path.join(FRONTEND_SRC, "services", "api.js"))

    def test_uses_axios_instance(self):
        content = read_file("services/api.js")
        assert "axios.create" in content

    def test_baseurl_uses_proxy(self):
        content = read_file("services/api.js")
        assert "baseURL" in content
        assert "/api" in content

    def test_request_interceptor_attaches_token(self):
        content = read_file("services/api.js")
        assert "interceptors.request" in content
        assert "Authorization" in content

    def test_response_interceptor_handles_401(self):
        content = read_file("services/api.js")
        assert "interceptors.response" in content
        assert "401" in content

    def test_exports_auth_api(self):
        content = read_file("services/api.js")
        assert "export const authAPI" in content

    def test_exports_products_api(self):
        content = read_file("services/api.js")
        assert "export const productsAPI" in content

    def test_exports_orders_api(self):
        content = read_file("services/api.js")
        assert "export const ordersAPI" in content

    def test_exports_cart_api(self):
        content = read_file("services/api.js")
        assert "export const cartAPI" in content

    def test_exports_tickets_api(self):
        content = read_file("services/api.js")
        assert "export const ticketsAPI" in content

    def test_exports_chat_api(self):
        content = read_file("services/api.js")
        assert "export const chatAPI" in content

    def test_exports_kb_api(self):
        content = read_file("services/api.js")
        assert "export const kbAPI" in content

    def test_exports_analytics_api(self):
        content = read_file("services/api.js")
        assert "export const analyticsAPI" in content

    def test_exports_users_api(self):
        content = read_file("services/api.js")
        assert "export const usersAPI" in content

    def test_no_hardcoded_localhost_outside_comment(self):
        content = read_file("services/api.js")
        lines = content.split("\n")
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("*") or stripped.startswith("//"):
                continue  # skip comments
            assert "localhost:8000" not in line, f"Hardcoded URL in api.js: {line}"


# ==================================================================
# 3.2 - Zustand Stores
# ==================================================================
class TestTask32_Stores:
    """Verify Zustand stores for auth and notifications."""

    def test_auth_store_exists(self):
        assert os.path.exists(os.path.join(FRONTEND_SRC, "stores", "authStore.js"))

    def test_auth_store_uses_zustand(self):
        content = read_file("stores/authStore.js")
        assert "zustand" in content or "create(" in content

    def test_auth_store_has_login(self):
        content = read_file("stores/authStore.js")
        assert "login" in content

    def test_auth_store_has_logout(self):
        content = read_file("stores/authStore.js")
        assert "logout" in content

    def test_auth_store_has_register(self):
        content = read_file("stores/authStore.js")
        assert "register" in content

    def test_notification_store_exists(self):
        assert os.path.exists(os.path.join(FRONTEND_SRC, "stores", "notificationStore.js"))

    def test_notification_store_has_success(self):
        content = read_file("stores/notificationStore.js")
        assert "success" in content

    def test_notification_store_has_error(self):
        content = read_file("stores/notificationStore.js")
        assert "error" in content


# ==================================================================
# 3.3 - Notification Toast Component
# ==================================================================
class TestTask33_NotificationToast:
    """Verify notification toast component."""

    def test_notification_toast_exists(self):
        assert os.path.exists(os.path.join(FRONTEND_SRC, "components", "NotificationToast.jsx"))

    def test_uses_notification_store(self):
        content = read_file("components/NotificationToast.jsx")
        assert "notificationStore" in content or "useNotificationStore" in content


# ==================================================================
# 3.4 - Register Page
# ==================================================================
class TestTask34_RegisterPage:
    """Verify Register page exists and uses auth store."""

    def test_register_page_exists(self):
        assert os.path.exists(os.path.join(FRONTEND_SRC, "pages", "Register.jsx"))

    def test_uses_auth_store(self):
        content = read_file("pages/Register.jsx")
        assert "authStore" in content or "useAuthStore" in content

    def test_no_hardcoded_url(self):
        content = read_file("pages/Register.jsx")
        assert "localhost:8000" not in content


# ==================================================================
# 3.5 - Order History Page
# ==================================================================
class TestTask35_OrdersPage:
    """Verify Orders page uses API service."""

    def test_orders_page_exists(self):
        assert os.path.exists(os.path.join(FRONTEND_SRC, "pages", "Orders.jsx"))

    def test_uses_api_service(self):
        content = read_file("pages/Orders.jsx")
        assert "ordersAPI" in content

    def test_no_hardcoded_url(self):
        content = read_file("pages/Orders.jsx")
        assert "localhost:8000" not in content

    def test_no_alert_calls(self):
        content = read_file("pages/Orders.jsx")
        assert "alert(" not in content

    def test_no_confirm_calls(self):
        content = read_file("pages/Orders.jsx")
        assert re.search(r'\bconfirm\(', content) is None


# ==================================================================
# 3.6 - Product Detail Page
# ==================================================================
class TestTask36_ProductDetailPage:
    """Verify Product Detail page exists."""

    def test_product_detail_exists(self):
        assert os.path.exists(os.path.join(FRONTEND_SRC, "pages", "ProductDetail.jsx"))

    def test_uses_api_service(self):
        content = read_file("pages/ProductDetail.jsx")
        assert "productsAPI" in content

    def test_no_hardcoded_url(self):
        content = read_file("pages/ProductDetail.jsx")
        assert "localhost:8000" not in content


# ==================================================================
# 3.7 - Admin Panel
# ==================================================================
class TestTask37_AdminPanel:
    """Verify Admin Panel exists with tabs."""

    def test_admin_page_exists(self):
        assert os.path.exists(os.path.join(FRONTEND_SRC, "pages", "Admin.jsx"))

    def test_has_users_tab(self):
        content = read_file("pages/Admin.jsx")
        assert "UsersTab" in content or "users" in content.lower()

    def test_has_products_tab(self):
        content = read_file("pages/Admin.jsx")
        assert "ProductsTab" in content

    def test_has_orders_tab(self):
        content = read_file("pages/Admin.jsx")
        assert "OrdersTab" in content

    def test_has_tickets_tab(self):
        content = read_file("pages/Admin.jsx")
        assert "TicketsTab" in content

    def test_no_hardcoded_url(self):
        content = read_file("pages/Admin.jsx")
        assert "localhost:8000" not in content

    def test_no_alert_calls(self):
        content = read_file("pages/Admin.jsx")
        assert "alert(" not in content

    def test_no_confirm_calls(self):
        content = read_file("pages/Admin.jsx")
        assert re.search(r'\bconfirm\(', content) is None


# ==================================================================
# 3.8 - User Profile Page
# ==================================================================
class TestTask38_ProfilePage:
    """Verify Profile page exists."""

    def test_profile_page_exists(self):
        assert os.path.exists(os.path.join(FRONTEND_SRC, "pages", "Profile.jsx"))

    def test_uses_auth_store(self):
        content = read_file("pages/Profile.jsx")
        assert "authStore" in content or "useAuthStore" in content

    def test_no_hardcoded_url(self):
        content = read_file("pages/Profile.jsx")
        assert "localhost:8000" not in content


# ==================================================================
# 3.9 - App.jsx Routing
# ==================================================================
class TestTask39_AppRouting:
    """Verify App.jsx has all routes and uses auth store."""

    def test_uses_auth_store(self):
        content = read_file("App.jsx")
        assert "useAuthStore" in content

    def test_has_notification_toast(self):
        content = read_file("App.jsx")
        assert "NotificationToast" in content

    def test_has_register_route(self):
        content = read_file("App.jsx")
        assert "/register" in content

    def test_has_products_detail_route(self):
        content = read_file("App.jsx")
        assert "/products/:id" in content

    def test_has_orders_route(self):
        content = read_file("App.jsx")
        assert "/orders" in content

    def test_has_profile_route(self):
        content = read_file("App.jsx")
        assert "/profile" in content

    def test_has_admin_route(self):
        content = read_file("App.jsx")
        assert "/admin" in content


# ==================================================================
# 3.10 - Layout Role-based Navigation
# ==================================================================
class TestTask310_Layout:
    """Verify Layout has role-based navigation."""

    def test_uses_auth_store(self):
        content = read_file("components/Layout.jsx")
        assert "useAuthStore" in content or "authStore" in content

    def test_has_profile_link(self):
        content = read_file("components/Layout.jsx")
        assert "/profile" in content

    def test_has_admin_link(self):
        content = read_file("components/Layout.jsx")
        assert "/admin" in content


# ==================================================================
# 3.11 - Dashboard Charts
# ==================================================================
class TestTask311_DashboardCharts:
    """Verify Dashboard uses API service and has charts."""

    def test_uses_analytics_api(self):
        content = read_file("pages/Dashboard.jsx")
        assert "analyticsAPI" in content

    def test_no_hardcoded_url(self):
        content = read_file("pages/Dashboard.jsx")
        assert "localhost:8000" not in content

    def test_has_recharts(self):
        content = read_file("pages/Dashboard.jsx")
        assert "recharts" in content

    def test_has_pie_chart(self):
        content = read_file("pages/Dashboard.jsx")
        assert "PieChart" in content

    def test_has_bar_chart(self):
        content = read_file("pages/Dashboard.jsx")
        assert "BarChart" in content


# ==================================================================
# 3.12 - Login Page Migration
# ==================================================================
class TestTask312_LoginMigration:
    """Verify Login page uses auth store, not direct axios."""

    def test_uses_auth_store(self):
        content = read_file("pages/Login.jsx")
        assert "useAuthStore" in content

    def test_no_hardcoded_url(self):
        content = read_file("pages/Login.jsx")
        assert "localhost:8000" not in content

    def test_has_register_link(self):
        content = read_file("pages/Login.jsx")
        assert "/register" in content


# ==================================================================
# 3.13 - All Pages Migrated (no hardcoded URLs or alert/confirm)
# ==================================================================
class TestTask313_AllPagesMigrated:
    """Verify all page files have no hardcoded URLs or alert/confirm."""

    PAGES = [
        "pages/Products.jsx",
        "pages/Cart.jsx",
        "pages/Chat.jsx",
        "pages/Tickets.jsx",
        "pages/KnowledgeBase.jsx",
    ]

    @pytest.mark.parametrize("page", PAGES)
    def test_no_hardcoded_url(self, page):
        content = read_file(page)
        assert "localhost:8000" not in content, f"{page} has hardcoded URL"

    @pytest.mark.parametrize("page", PAGES)
    def test_no_alert_calls(self, page):
        content = read_file(page)
        assert "alert(" not in content, f"{page} has alert() call"

    @pytest.mark.parametrize("page", PAGES)
    def test_no_raw_axios_import(self, page):
        content = read_file(page)
        has_raw_axios = bool(re.search(r"import\s+axios\s+from\s+['\"]axios['\"]", content))
        assert not has_raw_axios, f"{page} imports raw axios instead of API service"

    @pytest.mark.parametrize("page", PAGES)
    def test_no_manual_token_handling(self, page):
        content = read_file(page)
        has_manual_token = "localStorage.getItem('token')" in content
        assert not has_manual_token, f"{page} manually reads token"

    def test_products_uses_api(self):
        content = read_file("pages/Products.jsx")
        assert "productsAPI" in content

    def test_products_has_link_to_detail(self):
        content = read_file("pages/Products.jsx")
        assert "Link" in content
        assert "/products/" in content

    def test_cart_uses_api(self):
        content = read_file("pages/Cart.jsx")
        assert "cartAPI" in content

    def test_chat_uses_api(self):
        content = read_file("pages/Chat.jsx")
        assert "chatAPI" in content

    def test_tickets_uses_api(self):
        content = read_file("pages/Tickets.jsx")
        assert "ticketsAPI" in content

    def test_kb_uses_api(self):
        content = read_file("pages/KnowledgeBase.jsx")
        assert "kbAPI" in content


# ==================================================================
# 3.14 - Frontend Build
# ==================================================================
class TestTask314_FrontendBuild:
    """Verify frontend builds without errors."""

    def test_vite_build_succeeds(self):
        frontend_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "frontend"
        )
        result = subprocess.run(
            ["npx", "vite", "build"],
            cwd=frontend_dir,
            capture_output=True,
            text=True,
            timeout=120,
            shell=True
        )
        # vite build outputs to stderr for CJS deprecation warning
        # check that "built in" appears in the combined output
        combined = result.stdout + result.stderr
        assert "built in" in combined, f"Build failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
