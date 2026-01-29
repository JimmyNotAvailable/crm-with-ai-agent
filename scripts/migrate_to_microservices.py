"""
============================================================================
Migrate Data to Microservices Databases
============================================================================
Script này import dữ liệu từ JSON files vào các databases microservices:
- Products → crm_product_db (port 3311)
- Users → crm_identity_db (port 3310)
- KB Articles → crm_knowledge_db (port 3314)
============================================================================
"""

import json
import uuid
from datetime import datetime
import mysql.connector
from pathlib import Path
import hashlib

# ============================================================================
# Configuration
# ============================================================================
DB_CONFIGS = {
    "identity": {
        "host": "localhost",
        "port": 3310,
        "user": "identity_user",
        "password": "identity_pass",
        "database": "crm_identity_db"
    },
    "product": {
        "host": "localhost",
        "port": 3311,
        "user": "product_user",
        "password": "product_pass",
        "database": "crm_product_db"
    },
    "knowledge": {
        "host": "localhost",
        "port": 3314,
        "user": "knowledge_user",
        "password": "knowledge_pass",
        "database": "crm_knowledge_db"
    }
}

# Base path
BASE_PATH = Path(__file__).parent

# ============================================================================
# Helper Functions
# ============================================================================
def get_connection(db_name: str):
    """Get MySQL connection for specific database"""
    config = DB_CONFIGS[db_name]
    return mysql.connector.connect(**config)

def generate_uuid():
    """Generate UUID string"""
    return str(uuid.uuid4())

def hash_password(password: str) -> str:
    """Simple password hash for demo"""
    return hashlib.sha256(password.encode()).hexdigest()

# ============================================================================
# Import Users to Identity DB
# ============================================================================
def import_users():
    """Import default users to crm_identity_db"""
    print("\n📥 Importing Users to crm_identity_db...")
    
    users = [
        {
            "email": "admin@crm.local",
            "password": "admin123",
            "full_name": "Admin User",
            "phone": "0901234567",
            "user_type": "ADMIN"
        },
        {
            "email": "staff@crm.local",
            "password": "staff123",
            "full_name": "Staff User",
            "phone": "0901234568",
            "user_type": "STAFF"
        },
        {
            "email": "customer@crm.local",
            "password": "customer123",
            "full_name": "Customer User",
            "phone": "0901234569",
            "user_type": "CUSTOMER"
        }
    ]
    
    conn = get_connection("identity")
    cursor = conn.cursor()
    
    try:
        for user in users:
            user_id = generate_uuid()
            cursor.execute("""
                INSERT INTO users (id, email, password_hash, full_name, phone, user_type, status, email_verified)
                VALUES (%s, %s, %s, %s, %s, %s, 'ACTIVE', 1)
                ON DUPLICATE KEY UPDATE full_name = VALUES(full_name)
            """, (
                user_id,
                user["email"],
                hash_password(user["password"]),
                user["full_name"],
                user["phone"],
                user["user_type"]
            ))
            
            # Create customer profile if CUSTOMER
            if user["user_type"] == "CUSTOMER":
                cursor.execute("""
                    INSERT INTO customer_profiles (id, user_id, vip_tier, loyalty_points)
                    VALUES (%s, %s, 'STANDARD', 0)
                    ON DUPLICATE KEY UPDATE vip_tier = VALUES(vip_tier)
                """, (generate_uuid(), user_id))
        
        conn.commit()
        print(f"   ✅ Imported {len(users)} users")
        
    except Exception as e:
        conn.rollback()
        print(f"   ❌ Error: {e}")
    finally:
        cursor.close()
        conn.close()

# ============================================================================
# Import Products to Product DB
# ============================================================================
def import_products():
    """Import products from JSON to crm_product_db"""
    print("\n📥 Importing Products to crm_product_db...")
    
    # Load products JSON - try multiple paths
    json_path = BASE_PATH / "crawled_products.json"
    if not json_path.exists():
        json_path = BASE_PATH / "cleaned_products.json"
    if not json_path.exists():
        print(f"   ⚠️ File not found: {json_path}")
        return
    
    with open(json_path, "r", encoding="utf-8") as f:
        products = json.load(f)
    
    conn = get_connection("product")
    cursor = conn.cursor()
    
    # Get or create default category
    cursor.execute("SELECT id FROM categories WHERE code = 'DIEN_THOAI' LIMIT 1")
    result = cursor.fetchone()
    default_category_id = result[0] if result else None
    
    imported = 0
    skipped = 0
    
    try:
        for product in products:
            try:
                product_id = generate_uuid()
                
                # Extract data
                name = product.get("name", "")[:255]
                if not name:
                    skipped += 1
                    continue
                
                # Generate SKU from name
                sku = f"SKU-{hash(name) % 1000000:06d}"
                
                # Parse price
                price_str = product.get("price", "0")
                if isinstance(price_str, str):
                    price_str = price_str.replace(".", "").replace(",", "").replace("đ", "").replace(" ", "")
                try:
                    base_price = float(price_str) if price_str else 0
                except:
                    base_price = 0
                
                # Parse old price as sale indicator
                old_price_str = product.get("old_price", "")
                sale_price = None
                if old_price_str:
                    if isinstance(old_price_str, str):
                        old_price_str = old_price_str.replace(".", "").replace(",", "").replace("đ", "").replace(" ", "")
                    try:
                        old_price = float(old_price_str) if old_price_str else 0
                        if old_price > base_price:
                            sale_price = base_price
                            base_price = old_price
                    except:
                        pass
                
                description = product.get("description", "")
                image_url = product.get("image_url", "")
                detail_url = product.get("detail_url", "")
                
                # Build specifications JSON
                specs = {}
                for key in ["ram", "storage", "screen", "cpu", "battery", "camera"]:
                    if key in product and product[key]:
                        specs[key] = product[key]
                
                # Insert product
                cursor.execute("""
                    INSERT INTO products (
                        id, sku, name, description, base_price, sale_price,
                        category_id, main_image_url, specifications, status
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, 'ACTIVE'
                    )
                """, (
                    product_id,
                    sku,
                    name,
                    description[:65535] if description else None,
                    base_price,
                    sale_price,
                    default_category_id,
                    image_url,
                    json.dumps(specs, ensure_ascii=False) if specs else None
                ))
                
                # Add inventory for default warehouse
                cursor.execute("SELECT id FROM warehouses LIMIT 1")
                wh_result = cursor.fetchone()
                if wh_result:
                    cursor.execute("""
                        INSERT INTO inventory (warehouse_id, product_id, quantity, reserved, reorder_level)
                        VALUES (%s, %s, 100, 0, 10)
                    """, (wh_result[0], product_id))
                
                imported += 1
                
            except Exception as e:
                skipped += 1
                if imported < 5:  # Only show first few errors
                    print(f"   ⚠️ Skip product: {e}")
        
        conn.commit()
        print(f"   ✅ Imported {imported} products, skipped {skipped}")
        
    except Exception as e:
        conn.rollback()
        print(f"   ❌ Error: {e}")
    finally:
        cursor.close()
        conn.close()

# ============================================================================
# Import KB Articles to Knowledge DB
# ============================================================================
def import_kb_articles():
    """Import KB articles from JSON to crm_knowledge_db"""
    print("\n📥 Importing KB Articles to crm_knowledge_db...")
    
    # Load KB articles JSON
    json_path = BASE_PATH / "cleaned_kb_articles.json"
    if not json_path.exists():
        print(f"   ⚠️ File not found: {json_path}, using default articles")
        # Default articles already seeded in SQL
        return
    
    with open(json_path, "r", encoding="utf-8") as f:
        articles = json.load(f)
    
    conn = get_connection("knowledge")
    cursor = conn.cursor()
    
    imported = 0
    
    try:
        for article in articles:
            article_id = generate_uuid()
            
            title = article.get("title", "")[:255]
            if not title:
                continue
            
            body_md = article.get("content", article.get("body_md", ""))
            category = article.get("category", "General")
            
            cursor.execute("""
                INSERT INTO kb_articles (id, title, body_md, category, is_public)
                VALUES (%s, %s, %s, %s, 1)
            """, (
                article_id,
                title,
                body_md,
                category
            ))
            
            imported += 1
        
        conn.commit()
        print(f"   ✅ Imported {imported} KB articles")
        
    except Exception as e:
        conn.rollback()
        print(f"   ❌ Error: {e}")
    finally:
        cursor.close()
        conn.close()

# ============================================================================
# Verify Data
# ============================================================================
def verify_data():
    """Verify imported data in all databases"""
    print("\n📊 Verifying imported data...")
    
    verifications = [
        ("identity", "users", "SELECT COUNT(*) FROM users"),
        ("identity", "customer_profiles", "SELECT COUNT(*) FROM customer_profiles"),
        ("product", "products", "SELECT COUNT(*) FROM products"),
        ("product", "inventory", "SELECT COUNT(*) FROM inventory"),
        ("knowledge", "kb_articles", "SELECT COUNT(*) FROM kb_articles"),
    ]
    
    for db_name, table, query in verifications:
        try:
            conn = get_connection(db_name)
            cursor = conn.cursor()
            cursor.execute(query)
            count = cursor.fetchone()[0]
            print(f"   {db_name}.{table}: {count} records")
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"   ❌ {db_name}.{table}: {e}")

# ============================================================================
# Main
# ============================================================================
def main():
    print("=" * 60)
    print("🚀 MICROSERVICES DATA MIGRATION")
    print("=" * 60)
    
    # Import data
    import_users()
    import_products()
    import_kb_articles()
    
    # Verify
    verify_data()
    
    print("\n" + "=" * 60)
    print("✅ MIGRATION COMPLETED!")
    print("=" * 60)
    print("""
📌 Connection Info:
   - Identity DB: localhost:3310 (identity_user/identity_pass)
   - Product DB:  localhost:3311 (product_user/product_pass)
   - Order DB:    localhost:3312 (order_user/order_pass)
   - Support DB:  localhost:3313 (support_user/support_pass)
   - Knowledge DB: localhost:3314 (knowledge_user/knowledge_pass)
   - Analytics DB: localhost:3315 (analytics_user/analytics_pass)
   - Marketing DB: localhost:3316 (marketing_user/marketing_pass)
   - Adminer:     http://localhost:8081
""")

if __name__ == "__main__":
    main()
