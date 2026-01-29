"""
Import Products from JSON to MySQL Database
Chạy sau khi đã khởi tạo database
Usage: python scripts/import_products_to_mysql.py
"""
import json
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database connection settings
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3307"))  # Docker port
MYSQL_USER = os.getenv("MYSQL_USER", "crm_user")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "crm_admin_pass")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "crm_ai_db")

DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

# Path to products JSON
PRODUCTS_JSON = Path(__file__).parent / "cleaned_products.json"


def import_products():
    """Import products from JSON to MySQL"""
    print(f"Connecting to: {MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}")
    
    try:
        engine = create_engine(DATABASE_URL, echo=False)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Test connection
        result = session.execute(text("SELECT 1"))
        print("✅ Database connection successful!")
        
        # Load products JSON
        print(f"\nLoading products from: {PRODUCTS_JSON}")
        with open(PRODUCTS_JSON, 'r', encoding='utf-8') as f:
            products = json.load(f)
        
        print(f"Found {len(products)} products to import")
        
        # Prepare insert statement
        insert_sql = text("""
            INSERT INTO products (
                sku, name, price, original_price, discount_percent,
                description, image_url, category, brand,
                stock_quantity, is_active, in_stock, source_url
            ) VALUES (
                :sku, :name, :price, :original_price, :discount_percent,
                :description, :image_url, :category, :brand,
                :stock_quantity, :is_active, :in_stock, :source_url
            )
            ON DUPLICATE KEY UPDATE
                name = VALUES(name),
                price = VALUES(price),
                original_price = VALUES(original_price),
                discount_percent = VALUES(discount_percent),
                description = VALUES(description),
                category = VALUES(category),
                brand = VALUES(brand),
                updated_at = CURRENT_TIMESTAMP(6)
        """)
        
        # Batch insert
        batch_size = 100
        imported = 0
        errors = 0
        
        for i in range(0, len(products), batch_size):
            batch = products[i:i + batch_size]
            
            for product in batch:
                try:
                    params = {
                        'sku': product.get('sku', f"SKU-{i}"),
                        'name': product.get('name', 'Unknown')[:500],
                        'price': float(product.get('price', 0) or 0),
                        'original_price': float(product.get('original_price', 0) or 0) if product.get('original_price') else None,
                        'discount_percent': int(product.get('discount_percent', 0) or 0),
                        'description': product.get('description'),
                        'image_url': product.get('image_url'),
                        'category': product.get('category'),
                        'brand': product.get('brand'),
                        'stock_quantity': 100,
                        'is_active': 1,
                        'in_stock': 1 if product.get('in_stock', True) else 0,
                        'source_url': product.get('source_url')
                    }
                    session.execute(insert_sql, params)
                    imported += 1
                except Exception as e:
                    errors += 1
                    if errors <= 5:
                        print(f"  Error importing {product.get('sku')}: {e}")
            
            session.commit()
            print(f"  Imported {min(i + batch_size, len(products))}/{len(products)} products...")
        
        print(f"\n✅ Import completed!")
        print(f"   Imported: {imported} products")
        print(f"   Errors: {errors}")
        
        # Verify
        result = session.execute(text("SELECT COUNT(*) FROM products"))
        count = result.scalar()
        print(f"   Total products in database: {count}")
        
        session.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise


def check_database_status():
    """Check current database status"""
    try:
        engine = create_engine(DATABASE_URL, echo=False)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        print("\n📊 DATABASE STATUS:")
        print("=" * 50)
        
        tables = ['users', 'products', 'kb_articles', 'conversations', 'orders', 'tickets']
        for table in tables:
            try:
                result = session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print(f"  {table}: {count} records")
            except Exception as e:
                print(f"  {table}: ❌ Table not found")
        
        session.close()
        
    except Exception as e:
        print(f"❌ Cannot connect: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Import products to MySQL")
    parser.add_argument("--check", action="store_true", help="Check database status only")
    parser.add_argument("--host", default="localhost", help="MySQL host")
    parser.add_argument("--port", type=int, default=3307, help="MySQL port")
    args = parser.parse_args()
    
    if args.host:
        MYSQL_HOST = args.host
    if args.port:
        MYSQL_PORT = args.port
        DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    
    if args.check:
        check_database_status()
    else:
        import_products()
        check_database_status()
