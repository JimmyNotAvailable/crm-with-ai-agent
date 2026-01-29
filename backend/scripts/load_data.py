"""
Data Loader Script
Load cleaned_products.json and cleaned_kb_articles.json into MySQL database

Usage:
    cd backend
    python -m scripts.load_data
"""
import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy.orm import Session
from backend.database.session import engine, SessionLocal, Base
from backend.models.product import Product
from backend.models.kb_article import KBArticle


def load_products(db: Session, file_path: str) -> int:
    """
    Load products from JSON file into database
    
    Args:
        db: Database session
        file_path: Path to cleaned_products.json
        
    Returns:
        Number of products loaded
    """
    print(f"Loading products from: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        products_data = json.load(f)
    
    count = 0
    for item in products_data:
        # Check if product already exists by SKU
        existing = db.query(Product).filter(Product.sku == item['sku']).first()
        if existing:
            # Update existing product
            existing.name = item['name']
            existing.price = item['price']
            existing.description = item.get('description', '')
            existing.category = item.get('category', 'General')
            existing.image_url = item.get('image_url')
            existing.stock_quantity = 100 if item.get('in_stock', True) else 0
            existing.is_active = item.get('in_stock', True)
            existing.tags = item.get('brand', '')
        else:
            # Create new product
            product = Product(
                sku=item['sku'],
                name=item['name'],
                price=item['price'],
                description=item.get('description', ''),
                category=item.get('category', 'General'),
                image_url=item.get('image_url'),
                stock_quantity=100 if item.get('in_stock', True) else 0,
                is_active=item.get('in_stock', True),
                is_featured=item.get('discount_percent', 0) >= 10,  # Featured if 10%+ discount
                tags=item.get('brand', ''),
                cost=item.get('original_price', item['price'])
            )
            db.add(product)
            count += 1
        
        # Commit every 100 items
        if count % 100 == 0:
            db.commit()
            print(f"  Loaded {count} products...")
    
    db.commit()
    print(f"Loaded {count} new products (updated existing)")
    return count


def load_kb_articles(db: Session, file_path: str) -> int:
    """
    Load KB articles from JSON file into database
    
    Args:
        db: Database session
        file_path: Path to cleaned_kb_articles.json
        
    Returns:
        Number of articles loaded
    """
    print(f"Loading KB articles from: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        articles_data = json.load(f)
    
    count = 0
    for item in articles_data:
        # Use code as unique identifier
        code = item.get('code', f"KB-{count:06d}")
        
        # Check if article already exists
        existing = db.query(KBArticle).filter(KBArticle.filename == code).first()
        if existing:
            # Update existing
            existing.title = item['title']
            existing.content = item.get('body_md', '')
            existing.category = item.get('_meta', {}).get('category', 'General')
            existing.source_url = item.get('_meta', {}).get('source_url', '')
            existing.is_active = item.get('is_public', True)
        else:
            # Create new KB article
            meta = item.get('_meta', {})
            article = KBArticle(
                title=item['title'],
                filename=code,
                file_path=f"/kb/{code}.md",
                file_type="md",
                content=item.get('body_md', ''),
                category=meta.get('category', 'General'),
                source_url=meta.get('source_url', ''),
                tags=meta.get('brand', ''),
                is_active=item.get('is_public', True),
                is_indexed=False,
                chunk_count=0
            )
            db.add(article)
            count += 1
        
        # Commit every 100 items
        if count % 100 == 0:
            db.commit()
            print(f"  Loaded {count} KB articles...")
    
    db.commit()
    print(f"Loaded {count} new KB articles (updated existing)")
    return count


def create_tables():
    """Create database tables if they don't exist"""
    print("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully!")
    except Exception as e:
        print(f"Warning: Could not create tables: {e}")
        print("Continuing with existing tables...")


def main():
    """Main function to load all data"""
    print("=" * 60)
    print("CRM-AI-Agent Data Loader")
    print("=" * 60)
    
    # Define file paths
    base_path = Path(__file__).parent.parent.parent
    products_file = base_path / "scripts" / "cleaned_products.json"
    kb_file = base_path / "scripts" / "cleaned_kb_articles.json"
    
    # Check files exist
    if not products_file.exists():
        print(f"ERROR: Products file not found: {products_file}")
        sys.exit(1)
    
    if not kb_file.exists():
        print(f"ERROR: KB articles file not found: {kb_file}")
        sys.exit(1)
    
    # Create tables
    create_tables()
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Load products
        print("\n--- Loading Products ---")
        products_count = load_products(db, str(products_file))
        
        # Load KB articles
        print("\n--- Loading KB Articles ---")
        kb_count = load_kb_articles(db, str(kb_file))
        
        # Summary
        print("\n" + "=" * 60)
        print("DATA LOADING COMPLETE")
        print("=" * 60)
        print(f"Products loaded/updated: {products_count}")
        print(f"KB Articles loaded/updated: {kb_count}")
        
        # Count totals in database
        total_products = db.query(Product).count()
        total_articles = db.query(KBArticle).count()
        print(f"\nTotal Products in DB: {total_products}")
        print(f"Total KB Articles in DB: {total_articles}")
        
    except Exception as e:
        print(f"\nERROR: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
