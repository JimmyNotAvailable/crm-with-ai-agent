"""
Phase 1 Validation Test Suite
==============================
Comprehensive validation of all Phase 1 changes:
- UUID Migration (7 models)
- __init__.py exports (12 models)
- Pydantic schemas (6 files)
- DB routing (11 endpoints)
- Bug fixes (3 files)
- Seed data script

Usage:
    pytest tests/test_phase1_validation.py -v
    python tests/test_phase1_validation.py
"""
import sys
import ast
import inspect
from pathlib import Path
from datetime import datetime

# Add backend to path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from sqlalchemy.sql.sqltypes import String, Integer
import pytest


# ══════════════════════════════════════════════════════════════════
# FIXTURES
# ══════════════════════════════════════════════════════════════════

@pytest.fixture(scope="module")
def models():
    """Import all models"""
    from backend.models import (
        User, Product, Order, OrderItem,
        Ticket, TicketMessage,
        Conversation, ConversationMessage,
        Cart, CartItem,
        KBArticle, AuditLog
    )
    return {
        "User": User,
        "Product": Product,
        "Order": Order,
        "OrderItem": OrderItem,
        "Ticket": Ticket,
        "TicketMessage": TicketMessage,
        "Conversation": Conversation,
        "ConversationMessage": ConversationMessage,
        "Cart": Cart,
        "CartItem": CartItem,
        "KBArticle": KBArticle,
        "AuditLog": AuditLog,
    }


@pytest.fixture(scope="module")
def session_factories():
    """Import session factories"""
    from backend.database.session import (
        get_db, get_product_db, get_order_db, get_support_db,
        get_knowledge_db, get_analytics_db
    )
    return {
        "get_db": (get_db, "Identity DB (Users)"),
        "get_product_db": (get_product_db, "Product DB"),
        "get_order_db": (get_order_db, "Order DB (Orders, Carts)"),
        "get_support_db": (get_support_db, "Support DB (Tickets)"),
        "get_knowledge_db": (get_knowledge_db, "Knowledge DB (Conversations, KB)"),
        "get_analytics_db": (get_analytics_db, "Analytics DB (Audit Logs)"),
    }


@pytest.fixture(scope="module")
def schemas():
    """Import Pydantic schemas"""
    from backend.schemas.product import ProductResponse
    from backend.schemas.order import OrderResponse, OrderItemResponse
    from backend.schemas.ticket import TicketResponse, TicketMessageResponse
    from backend.schemas.conversation import ConversationResponse, ConversationMessageResponse
    from backend.schemas.cart import CartResponse, CartItemResponse
    from backend.schemas.kb_article import KBArticleResponse
    
    return {
        "ProductResponse": (ProductResponse, ["id"]),
        "OrderResponse": (OrderResponse, ["id", "customer_id"]),
        "OrderItemResponse": (OrderItemResponse, ["id", "product_id"]),
        "TicketResponse": (TicketResponse, ["id", "customer_id", "assigned_to", "order_id"]),
        "TicketMessageResponse": (TicketMessageResponse, ["id", "ticket_id", "sender_id"]),
        "ConversationResponse": (ConversationResponse, ["id", "user_id"]),
        "ConversationMessageResponse": (ConversationMessageResponse, ["id", "conversation_id"]),
        "CartResponse": (CartResponse, ["id", "user_id"]),
        "CartItemResponse": (CartItemResponse, ["id", "product_id"]),
        "KBArticleResponse": (KBArticleResponse, ["id"]),
    }


# ══════════════════════════════════════════════════════════════════
# TASK 1: UUID MIGRATION
# ══════════════════════════════════════════════════════════════════

class TestTask1_UUIDMigration:
    """Test that all models use String(36) UUID primary keys"""
    
    def test_all_models_have_uuid_pk(self, models):
        """All 12 models must have String(36) UUID primary keys"""
        results = []
        
        for name, model in models.items():
            pk_col = None
            for col in model.__table__.columns:
                if col.primary_key:
                    pk_col = col
                    break
            
            assert pk_col is not None, f"{name}: No primary key found"
            
            # Check if it's String(36)
            is_string = isinstance(pk_col.type, String)
            is_correct_length = is_string and pk_col.type.length == 36
            has_default = pk_col.default is not None or pk_col.server_default is not None
            
            assert is_correct_length, f"{name}: PK type is not String(36), got {pk_col.type}"
            assert has_default, f"{name}: PK has no default UUID generator"
            
            results.append(f"✅ {name:<20} | PK: {pk_col.name:<15} | String(36) | Default: ✓")
        
        print("\n" + "="*70)
        print("Task 1: UUID Migration Validation")
        print("="*70)
        for r in results:
            print(r)
        print("="*70)
    
    def test_cross_db_references_no_fk(self, models):
        """Cross-DB references should NOT have ForeignKey constraints"""
        cross_db_refs = [
            ("Order", "customer_id", "References User in Identity DB"),
            ("OrderItem", "product_id", "References Product in Product DB"),
            ("Ticket", "customer_id", "References User in Identity DB"),
            ("Ticket", "assigned_to", "References User in Identity DB"),
            ("Ticket", "order_id", "References Order in Order DB"),
            ("TicketMessage", "sender_id", "References User in Identity DB"),
            ("Conversation", "user_id", "References User in Identity DB"),
            ("Cart", "user_id", "References User in Identity DB"),
            ("CartItem", "product_id", "References Product in Product DB"),
            ("KBArticle", "uploaded_by", "References User in Identity DB"),
            ("AuditLog", "user_id", "References User in Identity DB"),
        ]
        
        results = []
        for model_name, col_name, desc in cross_db_refs:
            model = models[model_name]
            col = None
            for c in model.__table__.columns:
                if c.name == col_name:
                    col = c
                    break
            
            assert col is not None, f"{model_name}.{col_name} NOT FOUND"
            
            # Check it's String(36)
            is_string36 = isinstance(col.type, String) and col.type.length == 36
            assert is_string36, f"{model_name}.{col_name} is not String(36)"
            
            # Check no FK constraint
            has_fk = len(list(col.foreign_keys)) > 0
            assert not has_fk, f"{model_name}.{col_name} has FK constraint (cross-DB refs should not)"
            
            results.append(f"✅ {model_name:<20}.{col_name:<15} String(36), No FK")
        
        print("\nCross-DB References Validation:")
        for r in results:
            print(r)


# ══════════════════════════════════════════════════════════════════
# TASK 2: __init__.py EXPORTS
# ══════════════════════════════════════════════════════════════════

class TestTask2_Exports:
    """Test that all models are exported from __init__.py"""
    
    def test_all_models_exported(self):
        """All 12 models must be exported from backend.models"""
        import backend.models as models_module
        
        required_exports = [
            "User", "Product", "Order", "OrderItem",
            "Ticket", "TicketMessage",
            "Conversation", "ConversationMessage",
            "Cart", "CartItem",
            "KBArticle", "AuditLog"
        ]
        
        results = []
        for name in required_exports:
            assert hasattr(models_module, name), f"{name} NOT exported from backend.models"
            results.append(f"✅ {name} exported")
        
        print("\n" + "="*70)
        print("Task 2: __init__.py Exports Validation")
        print("="*70)
        for r in results:
            print(r)
        print("="*70)


# ══════════════════════════════════════════════════════════════════
# TASK 3: PYDANTIC SCHEMAS
# ══════════════════════════════════════════════════════════════════

class TestTask3_Schemas:
    """Test that all ID fields in schemas are str type"""
    
    def test_schema_id_fields_are_str(self, schemas):
        """All ID fields in Pydantic schemas must be str type"""
        results = []
        
        for schema_name, (schema_class, fields) in schemas.items():
            annotations = schema_class.__annotations__
            
            for field in fields:
                assert field in annotations, f"{schema_name}.{field} NOT FOUND"
                
                field_type = annotations[field]
                type_str = str(field_type)
                
                # Handle Optional[str] and str
                is_str_type = "str" in type_str or field_type == str
                assert is_str_type, f"{schema_name}.{field} is not str, got {type_str}"
                
                results.append(f"✅ {schema_name:<30}.{field:<20} : {type_str}")
        
        print("\n" + "="*70)
        print("Task 3: Pydantic Schema Type Validation")
        print("="*70)
        for r in results:
            print(r)
        print("="*70)


# ══════════════════════════════════════════════════════════════════
# TASK 4: DB ROUTING
# ══════════════════════════════════════════════════════════════════

class TestTask4_DBRouting:
    """Test that all session factories work correctly"""
    
    def test_session_factories_work(self, session_factories):
        """All 6 session factories must return valid Session objects"""
        results = []
        
        for name, (factory, desc) in session_factories.items():
            # Test that the generator works
            session_gen = factory()
            session = next(session_gen)
            
            assert session is not None, f"{name} returns None"
            
            results.append(f"✅ {name:<25} → {desc}")
            session.close()
        
        print("\n" + "="*70)
        print("Task 4: DB Routing - Session Factory Validation")
        print("="*70)
        for r in results:
            print(r)
        print("="*70)


# ══════════════════════════════════════════════════════════════════
# TASK 5: BUG FIXES
# ══════════════════════════════════════════════════════════════════

class TestTask5_BugFixes:
    """Test that all bug fixes are applied correctly"""
    
    def test_db_helper_signatures(self):
        """db_helper methods must use str for user_id parameters"""
        from backend.utils.db_helper import AgentDatabaseHelper
        
        helper = AgentDatabaseHelper()
        methods_to_check = [
            ("get_user_by_id", "user_id"),
            ("get_user_orders", "user_id"),
            ("get_user_tickets", "user_id"),
            ("get_conversations", "user_id"),
            ("log_agent_action", "user_id"),
        ]
        
        results = []
        for method_name, param_name in methods_to_check:
            method = getattr(helper, method_name)
            sig = inspect.signature(method)
            param = sig.parameters.get(param_name)
            
            assert param is not None, f"{method_name}.{param_name} NOT FOUND"
            assert param.annotation == str, f"{method_name}.{param_name} is not str, got {param.annotation}"
            
            results.append(f"✅ {method_name:<25} {param_name}: str")
        
        print("\n" + "="*70)
        print("Task 5: Bug Fixes - db_helper.py")
        print("="*70)
        for r in results:
            print(r)
    
    def test_behavior_tracking_signatures(self):
        """BehaviorTrackingService methods must use str for customer_id"""
        from backend.services.behavior_tracking import BehaviorTrackingService
        
        bt_methods = [
            "get_customer_profile",
            "_get_purchase_stats",
            "_get_product_preferences",
            "_get_support_stats",
            "_get_chat_stats",
            "get_product_recommendations",
        ]
        
        results = []
        for method_name in bt_methods:
            method = getattr(BehaviorTrackingService, method_name)
            sig = inspect.signature(method)
            param = sig.parameters.get("customer_id")
            
            assert param is not None, f"{method_name}.customer_id NOT FOUND"
            assert param.annotation == str, f"{method_name}.customer_id is not str, got {param.annotation}"
            
            results.append(f"✅ {method_name:<30} customer_id: str")
        
        print("\nTask 5: Bug Fixes - behavior_tracking.py")
        print("="*70)
        for r in results:
            print(r)
    
    def test_config_no_duplicate_demo_mode(self):
        """config.py must have only one DEMO_MODE declaration"""
        config_file = ROOT_DIR / "backend" / "core" / "config.py"
        config_content = config_file.read_text(encoding="utf-8")
        demo_mode_count = config_content.count("DEMO_MODE: bool")
        
        assert demo_mode_count == 1, f"DEMO_MODE declared {demo_mode_count} times (expected 1)"
        
        print("\nTask 5: Bug Fixes - config.py")
        print("="*70)
        print(f"✅ DEMO_MODE declared exactly once")


# ══════════════════════════════════════════════════════════════════
# TASK 6: SEED DATA SCRIPT
# ══════════════════════════════════════════════════════════════════

class TestTask6_SeedData:
    """Test that seed data script is valid and complete"""
    
    def test_seed_script_exists_and_valid(self):
        """seed_data.py must exist and have valid syntax"""
        seed_script = ROOT_DIR / "scripts" / "seed_data.py"
        
        assert seed_script.exists(), "seed_data.py NOT FOUND"
        
        with open(seed_script, "r", encoding="utf-8") as f:
            code = f.read()
        
        # Parse and validate syntax
        tree = ast.parse(code)
        
        print("\n" + "="*70)
        print("Task 6: Seed Data Script Validation")
        print("="*70)
        print(f"✅ File exists: scripts/seed_data.py")
        print("✅ Syntax valid")
    
    def test_seed_script_has_required_functions(self):
        """seed_data.py must have all 6 seeding functions"""
        seed_script = ROOT_DIR / "scripts" / "seed_data.py"
        
        with open(seed_script, "r", encoding="utf-8") as f:
            code = f.read()
        
        tree = ast.parse(code)
        functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        
        required_functions = [
            "seed_users", "seed_products", "seed_orders",
            "seed_tickets", "seed_knowledge", "seed_audit_logs"
        ]
        
        results = []
        for func in required_functions:
            assert func in functions, f"{func} NOT FOUND in seed_data.py"
            results.append(f"✅ {func}")
        
        print("\nKey seeding functions:")
        for r in results:
            print(f"  {r}")
    
    def test_seed_script_has_uuid_dicts(self):
        """seed_data.py must have UUID dictionaries for all entities"""
        seed_script = ROOT_DIR / "scripts" / "seed_data.py"
        
        with open(seed_script, "r", encoding="utf-8") as f:
            code = f.read()
        
        uuid_dicts = ["USER_IDS", "PRODUCT_IDS", "ORDER_IDS", "TICKET_IDS", "CONV_IDS", "KB_IDS", "AUDIT_IDS"]
        
        results = []
        for dict_name in uuid_dicts:
            assert dict_name in code, f"{dict_name} NOT FOUND in seed_data.py"
            results.append(f"✅ {dict_name} defined")
        
        print("\nUUID Dictionaries:")
        for r in results:
            print(f"  {r}")
        
        # File stats
        file_size = seed_script.stat().st_size
        print(f"\n📏 File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        print(f"📝 Lines of code: {len(code.splitlines())}")
        print("="*70)


# ══════════════════════════════════════════════════════════════════
# STANDALONE RUNNER
# ══════════════════════════════════════════════════════════════════

def run_standalone():
    """Run all tests without pytest"""
    print("\n" + "╔" + "═"*68 + "╗")
    print("║" + " "*15 + "PHASE 1 VALIDATION TEST SUITE" + " "*24 + "║")
    print("╚" + "═"*68 + "╝")
    print(f"\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Project: CRM-AI-Agent")
    print(f"Phase: Phase 1 - Foundation\n")
    
    # Import fixtures data
    from backend.models import (
        User, Product, Order, OrderItem,
        Ticket, TicketMessage,
        Conversation, ConversationMessage,
        Cart, CartItem,
        KBArticle, AuditLog
    )
    
    models_dict = {
        "User": User, "Product": Product, "Order": Order, "OrderItem": OrderItem,
        "Ticket": Ticket, "TicketMessage": TicketMessage,
        "Conversation": Conversation, "ConversationMessage": ConversationMessage,
        "Cart": Cart, "CartItem": CartItem,
        "KBArticle": KBArticle, "AuditLog": AuditLog,
    }
    
    from backend.database.session import (
        get_db, get_product_db, get_order_db, get_support_db,
        get_knowledge_db, get_analytics_db
    )
    
    session_factories_dict = {
        "get_db": (get_db, "Identity DB (Users)"),
        "get_product_db": (get_product_db, "Product DB"),
        "get_order_db": (get_order_db, "Order DB (Orders, Carts)"),
        "get_support_db": (get_support_db, "Support DB (Tickets)"),
        "get_knowledge_db": (get_knowledge_db, "Knowledge DB (Conversations, KB)"),
        "get_analytics_db": (get_analytics_db, "Analytics DB (Audit Logs)"),
    }
    
    from backend.schemas.product import ProductResponse
    from backend.schemas.order import OrderResponse, OrderItemResponse
    from backend.schemas.ticket import TicketResponse, TicketMessageResponse
    from backend.schemas.conversation import ConversationResponse, ConversationMessageResponse
    from backend.schemas.cart import CartResponse, CartItemResponse
    from backend.schemas.kb_article import KBArticleResponse
    
    schemas_dict = {
        "ProductResponse": (ProductResponse, ["id"]),
        "OrderResponse": (OrderResponse, ["id", "customer_id"]),
        "OrderItemResponse": (OrderItemResponse, ["id", "product_id"]),
        "TicketResponse": (TicketResponse, ["id", "customer_id", "assigned_to", "order_id"]),
        "TicketMessageResponse": (TicketMessageResponse, ["id", "ticket_id", "sender_id"]),
        "ConversationResponse": (ConversationResponse, ["id", "user_id"]),
        "ConversationMessageResponse": (ConversationMessageResponse, ["id", "conversation_id"]),
        "CartResponse": (CartResponse, ["id", "user_id"]),
        "CartItemResponse": (CartItemResponse, ["id", "product_id"]),
        "KBArticleResponse": (KBArticleResponse, ["id"]),
    }
    
    # Run tests
    test_results = []
    
    try:
        # Task 1
        t1 = TestTask1_UUIDMigration()
        t1.test_all_models_have_uuid_pk(models_dict)
        t1.test_cross_db_references_no_fk(models_dict)
        test_results.append(("Task 1: UUID Migration", "PASSED"))
    except AssertionError as e:
        test_results.append(("Task 1: UUID Migration", f"FAILED: {e}"))
    
    try:
        # Task 2
        t2 = TestTask2_Exports()
        t2.test_all_models_exported()
        test_results.append(("Task 2: __init__.py Exports", "PASSED"))
    except AssertionError as e:
        test_results.append(("Task 2: __init__.py Exports", f"FAILED: {e}"))
    
    try:
        # Task 3
        t3 = TestTask3_Schemas()
        t3.test_schema_id_fields_are_str(schemas_dict)
        test_results.append(("Task 3: Pydantic Schemas", "PASSED"))
    except AssertionError as e:
        test_results.append(("Task 3: Pydantic Schemas", f"FAILED: {e}"))
    
    try:
        # Task 4
        t4 = TestTask4_DBRouting()
        t4.test_session_factories_work(session_factories_dict)
        test_results.append(("Task 4: DB Routing", "PASSED"))
    except AssertionError as e:
        test_results.append(("Task 4: DB Routing", f"FAILED: {e}"))
    
    try:
        # Task 5
        t5 = TestTask5_BugFixes()
        t5.test_db_helper_signatures()
        t5.test_behavior_tracking_signatures()
        t5.test_config_no_duplicate_demo_mode()
        test_results.append(("Task 5: Bug Fixes", "PASSED"))
    except AssertionError as e:
        test_results.append(("Task 5: Bug Fixes", f"FAILED: {e}"))
    
    try:
        # Task 6
        t6 = TestTask6_SeedData()
        t6.test_seed_script_exists_and_valid()
        t6.test_seed_script_has_required_functions()
        t6.test_seed_script_has_uuid_dicts()
        test_results.append(("Task 6: Seed Data Script", "PASSED"))
    except AssertionError as e:
        test_results.append(("Task 6: Seed Data Script", f"FAILED: {e}"))
    
    # Summary
    print("\n\n" + "╔" + "═"*68 + "╗")
    print("║" + " "*23 + "TEST SUMMARY" + " "*33 + "║")
    print("╚" + "═"*68 + "╝\n")
    
    passed = sum(1 for _, status in test_results if status == "PASSED")
    failed = len(test_results) - passed
    
    for task, status in test_results:
        icon = "✅" if status == "PASSED" else "❌"
        print(f"{icon} {task:<40} {status}")
    
    print("\n" + "="*70)
    print(f"Total: {len(test_results)} tasks | Passed: {passed} | Failed: {failed}")
    print("="*70)
    
    if failed == 0:
        print("\n🎉 ALL PHASE 1 TASKS VALIDATED SUCCESSFULLY!")
        print("\n📝 Next Steps:")
        print("  1. Run seed script: python scripts/seed_data.py --reset")
        print("  2. Test API endpoints with new UUID data")
        print("  3. Proceed to Phase 2: AI Modules Enhancement\n")
        return 0
    else:
        print("\n❌ Some tests failed. Please review the errors above.\n")
        return 1


if __name__ == "__main__":
    # Run standalone if executed directly
    sys.exit(run_standalone())
