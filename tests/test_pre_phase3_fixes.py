"""
Pre-Phase 3 Fixes Validation Test Suite
========================================
Validates all fixes applied before Phase 3:

FIX-1:  table_db_mapping — 4 Phase 2 tables added
FIX-2:  tickets.py cross-DB — identity_db for User queries
FIX-3:  audit middleware — AnalyticsSession instead of SessionLocal
FIX-4:  OperationsAgent multi-DB — order_db separation
FIX-5:  personalization multi-DB — BehaviorTrackingService refactored
OPT-1:  get_db → get_identity_db in auth, rag, analytics, personalization

Usage:
    pytest tests/test_pre_phase3_fixes.py -v
"""
import sys
import os
import ast
import inspect
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Force DEMO_MODE
os.environ["DEMO_MODE"] = "true"

import pytest


# ══════════════════════════════════════════════════════════════════
# FIX-1: table_db_mapping completeness
# ══════════════════════════════════════════════════════════════════

class TestFix1TableDbMapping:
    """FIX-1 — Verify 4 Phase 2 tables added to table_db_mapping"""

    def _get_mapping_source(self):
        """Read the table_db_mapping dict from session.py source"""
        return Path(ROOT_DIR / "backend/database/session.py").read_text(encoding="utf-8")

    def test_table_db_mapping_has_routing_rules(self):
        source = self._get_mapping_source()
        assert "'routing_rules': 'support'" in source

    def test_table_db_mapping_has_work_queues(self):
        source = self._get_mapping_source()
        assert "'work_queues': 'support'" in source

    def test_table_db_mapping_has_assignments(self):
        source = self._get_mapping_source()
        assert "'assignments': 'support'" in source

    def test_table_db_mapping_has_payment_transactions(self):
        source = self._get_mapping_source()
        assert "'payment_transactions': 'order'" in source

    def test_existing_tables_still_present(self):
        """Ensure pre-existing mappings weren't removed"""
        source = self._get_mapping_source()
        assert "'users': 'identity'" in source
        assert "'orders': 'order'" in source
        assert "'products': 'product'" in source
        assert "'tickets': 'support'" in source


# ══════════════════════════════════════════════════════════════════
# FIX-2: tickets.py cross-DB User query
# ══════════════════════════════════════════════════════════════════

class TestFix2TicketsCrossDB:
    """FIX-2 — tickets.py uses identity_db for User queries"""

    def test_tickets_imports_get_identity_db(self):
        """tickets.py imports get_identity_db"""
        source = Path(ROOT_DIR / "backend/api/v1/endpoints/tickets.py").read_text(encoding="utf-8")
        assert "get_identity_db" in source

    def test_create_ticket_has_identity_db_param(self):
        """create_ticket function has identity_db parameter"""
        from backend.api.v1.endpoints.tickets import create_ticket
        sig = inspect.signature(create_ticket)
        assert "identity_db" in sig.parameters, \
            f"create_ticket params: {list(sig.parameters.keys())}"

    def test_user_query_uses_identity_db(self):
        """Staff member query uses identity_db, not db (support session)"""
        source = Path(ROOT_DIR / "backend/api/v1/endpoints/tickets.py").read_text(encoding="utf-8")
        assert "identity_db.query(User)" in source
        # The old pattern used the support db variable 'db' for User queries
        # Make sure we don't have bare "= db.query(User)" (not "identity_db")
        import re
        bare_db_user_query = re.findall(r'(?<!identity_)db\.query\(User\)', source)
        assert len(bare_db_user_query) == 0, \
            f"Found bare db.query(User) not prefixed with identity_: {bare_db_user_query}"


# ══════════════════════════════════════════════════════════════════
# FIX-3: audit middleware uses AnalyticsSession
# ══════════════════════════════════════════════════════════════════

class TestFix3AuditMiddleware:
    """FIX-3 — audit_logging.py uses AnalyticsSession"""

    def test_imports_analytics_session(self):
        source = Path(ROOT_DIR / "backend/middleware/audit_logging.py").read_text(encoding="utf-8")
        assert "AnalyticsSession" in source

    def test_no_session_local_usage(self):
        """SessionLocal should not be used in audit middleware"""
        source = Path(ROOT_DIR / "backend/middleware/audit_logging.py").read_text(encoding="utf-8")
        assert "SessionLocal()" not in source

    def test_log_audit_uses_analytics(self):
        """The _log_audit method creates AnalyticsSession"""
        source = Path(ROOT_DIR / "backend/middleware/audit_logging.py").read_text(encoding="utf-8")
        assert "db = AnalyticsSession()" in source


# ══════════════════════════════════════════════════════════════════
# FIX-4: OperationsAgent multi-DB
# ══════════════════════════════════════════════════════════════════

class TestFix4OperationsAgentMultiDB:
    """FIX-4 — OperationsAgent accepts separate order_db"""

    def test_constructor_accepts_order_db(self):
        """__init__ has order_db parameter"""
        from ai_modules.agent_operations.agent import OperationsAgent
        sig = inspect.signature(OperationsAgent.__init__)
        assert "order_db" in sig.parameters

    def test_order_db_defaults_to_none(self):
        """order_db defaults to None for backward compatibility"""
        from ai_modules.agent_operations.agent import OperationsAgent
        sig = inspect.signature(OperationsAgent.__init__)
        order_db_param = sig.parameters["order_db"]
        assert order_db_param.default is None

    def test_order_db_attribute_set(self):
        """OperationsAgent stores self.order_db"""
        source = Path(ROOT_DIR / "ai_modules/agent_operations/agent.py").read_text(encoding="utf-8")
        assert "self.order_db" in source

    def test_order_queries_use_order_db(self):
        """Order queries use self.order_db, not self.db"""
        source = Path(ROOT_DIR / "ai_modules/agent_operations/agent.py").read_text(encoding="utf-8")
        assert "self.order_db.query(Order)" in source
        # Ensure self.db.query(Order) is gone
        assert "self.db.query(Order)" not in source

    def test_order_cancel_commits_order_db(self):
        """Order cancel commits to self.order_db"""
        source = Path(ROOT_DIR / "ai_modules/agent_operations/agent.py").read_text(encoding="utf-8")
        assert "self.order_db.commit()" in source

    def test_ticket_queries_still_use_self_db(self):
        """Ticket queries still use self.db (support_db)"""
        source = Path(ROOT_DIR / "ai_modules/agent_operations/agent.py").read_text(encoding="utf-8")
        assert "self.db.query(Ticket)" in source
        assert "self.db.add(new_ticket)" in source

    def test_backward_compat_single_db(self):
        """Can instantiate with only db param (backward compat)"""
        from unittest.mock import MagicMock
        from ai_modules.agent_operations.agent import OperationsAgent
        mock_db = MagicMock()
        agent = OperationsAgent(db=mock_db)
        # order_db should fall back to db
        assert agent.order_db is mock_db
        assert agent.db is mock_db

    def test_multi_db_separation(self):
        """When both dbs provided, they are stored separately"""
        from unittest.mock import MagicMock
        from ai_modules.agent_operations.agent import OperationsAgent
        mock_support_db = MagicMock()
        mock_order_db = MagicMock()
        agent = OperationsAgent(db=mock_support_db, order_db=mock_order_db)
        assert agent.db is mock_support_db
        assert agent.order_db is mock_order_db


# ══════════════════════════════════════════════════════════════════
# FIX-5: BehaviorTrackingService multi-DB
# ══════════════════════════════════════════════════════════════════

class TestFix5BehaviorTrackingMultiDB:
    """FIX-5 — BehaviorTrackingService + personalization use multi-DB"""

    def test_constructor_accepts_multi_db(self):
        """BehaviorTrackingService accepts 5 DB sessions"""
        from backend.services.behavior_tracking import BehaviorTrackingService
        sig = inspect.signature(BehaviorTrackingService.__init__)
        params = list(sig.parameters.keys())
        assert "identity_db" in params
        assert "order_db" in params
        assert "product_db" in params
        assert "support_db" in params
        assert "knowledge_db" in params

    def test_all_optional_except_identity(self):
        """Only identity_db is required, others default to None"""
        from backend.services.behavior_tracking import BehaviorTrackingService
        sig = inspect.signature(BehaviorTrackingService.__init__)
        for name in ["order_db", "product_db", "support_db", "knowledge_db"]:
            assert sig.parameters[name].default is None

    def test_backward_compat_single_db(self):
        """Single identity_db should work (others fallback)"""
        from unittest.mock import MagicMock
        from backend.services.behavior_tracking import BehaviorTrackingService
        mock_db = MagicMock()
        service = BehaviorTrackingService(identity_db=mock_db)
        assert service.identity_db is mock_db
        assert service.order_db is mock_db
        assert service.product_db is mock_db
        assert service.support_db is mock_db
        assert service.knowledge_db is mock_db

    def test_multi_db_separation(self):
        """Each DB session is stored separately when provided"""
        from unittest.mock import MagicMock
        from backend.services.behavior_tracking import BehaviorTrackingService
        dbs = {k: MagicMock() for k in ["identity_db", "order_db", "product_db", "support_db", "knowledge_db"]}
        service = BehaviorTrackingService(**dbs)
        assert service.identity_db is dbs["identity_db"]
        assert service.order_db is dbs["order_db"]
        assert service.product_db is dbs["product_db"]
        assert service.support_db is dbs["support_db"]
        assert service.knowledge_db is dbs["knowledge_db"]

    def test_queries_route_to_correct_db(self):
        """Verify source code routes queries to correct sessions"""
        source = Path(ROOT_DIR / "backend/services/behavior_tracking.py").read_text(encoding="utf-8")
        assert "self.identity_db.query(User)" in source
        assert "self.order_db.query(Order)" in source
        assert "self.order_db.query(OrderItem)" in source
        assert "self.product_db.query(Product)" in source
        assert "self.support_db.query(Ticket)" in source
        assert "self.knowledge_db.query(Conversation)" in source

    def test_personalization_imports_multi_db(self):
        """personalization.py imports all 5 DB getters"""
        source = Path(ROOT_DIR / "backend/api/v1/endpoints/personalization.py").read_text(encoding="utf-8")
        for getter in ["get_identity_db", "get_order_db", "get_product_db", "get_support_db", "get_knowledge_db"]:
            assert getter in source, f"Missing {getter} import in personalization.py"

    def test_personalization_no_get_db(self):
        """personalization.py should not import or use get_db"""
        source = Path(ROOT_DIR / "backend/api/v1/endpoints/personalization.py").read_text(encoding="utf-8")
        # get_db should NOT appear (it was replaced)
        assert "import get_db" not in source
        assert "Depends(get_db)" not in source


# ══════════════════════════════════════════════════════════════════
# OPT-1: get_db → get_identity_db cleanup
# ══════════════════════════════════════════════════════════════════

class TestOpt1GetDbCleanup:
    """OPT-1 — All API endpoints use get_identity_db instead of get_db"""

    def test_auth_no_get_db(self):
        source = Path(ROOT_DIR / "backend/api/v1/endpoints/auth.py").read_text(encoding="utf-8")
        assert "get_identity_db" in source
        assert "Depends(get_db)" not in source

    def test_auth_register_uses_identity_db(self):
        from backend.api.v1.endpoints.auth import register
        sig = inspect.signature(register)
        assert "db" in sig.parameters

    def test_auth_login_uses_identity_db(self):
        from backend.api.v1.endpoints.auth import login
        sig = inspect.signature(login)
        assert "db" in sig.parameters

    def test_rag_no_get_db(self):
        source = Path(ROOT_DIR / "backend/api/v1/endpoints/rag.py").read_text(encoding="utf-8")
        assert "get_identity_db" in source
        assert "import get_db" not in source.replace("get_identity_db", "")

    def test_analytics_no_get_db(self):
        source = Path(ROOT_DIR / "backend/api/v1/endpoints/analytics.py").read_text(encoding="utf-8")
        assert "get_identity_db" in source
        assert "Depends(get_db)" not in source

    def test_analytics_uses_identity_db(self):
        """All analytics endpoints use get_identity_db"""
        source = Path(ROOT_DIR / "backend/api/v1/endpoints/analytics.py").read_text(encoding="utf-8")
        assert source.count("Depends(get_identity_db)") == 4, \
            f"Expected 4 Depends(get_identity_db), found {source.count('Depends(get_identity_db)')}"


# ══════════════════════════════════════════════════════════════════
# CROSS-CUTTING: No remaining get_db in API endpoints
# ══════════════════════════════════════════════════════════════════

class TestNoRemainingGetDb:
    """Ensure no API endpoint still imports bare get_db"""

    @pytest.mark.parametrize("endpoint_file", [
        "auth.py",
        "analytics.py",
        "personalization.py",
    ])
    def test_no_depends_get_db(self, endpoint_file):
        source = Path(ROOT_DIR / f"backend/api/v1/endpoints/{endpoint_file}").read_text(encoding="utf-8")
        assert "Depends(get_db)" not in source, \
            f"{endpoint_file} still uses Depends(get_db)"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
