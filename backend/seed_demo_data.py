"""
Script to seed demo data for CRM-AI-Agent
Tạo user admin demo và các sản phẩm mẫu
"""
import sys
import uuid
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from backend.database.session import SessionLocal, engine, Base
from backend.models.user import User, UserType, UserStatus
from backend.models.product import Product
from backend.utils.security import get_password_hash
from sqlalchemy.exc import IntegrityError

def create_tables():
    """Create all tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("[OK] Tables created successfully!")

def seed_users(db):
    """Seed demo users"""
    print("\nSeeding demo users...")
    
    users_data = [
        {
            "email": "admin@crm-demo.com",
            "password": "admin123",
            "full_name": "Admin Demo",
            "user_type": UserType.ADMIN,
            "phone": "0901234567"
        },
        {
            "email": "staff@crm-demo.com",
            "password": "staff123",
            "full_name": "Nhân Viên Demo",
            "user_type": UserType.STAFF,
            "phone": "0901234568"
        },
        {
            "email": "customer@crm-demo.com",
            "password": "customer123",
            "full_name": "Khách Hàng Demo",
            "user_type": UserType.CUSTOMER,
            "phone": "0901234569"
        }
    ]
    
    created_count = 0
    for user_data in users_data:
        try:
            existing_user = db.query(User).filter(User.email == user_data["email"]).first()
            if existing_user:
                print(f"[SKIP] User {user_data['email']} already exists")
                continue
            
            user = User(
                id=str(uuid.uuid4()),  # Generate UUID for primary key
                email=user_data["email"],
                password_hash=get_password_hash(user_data["password"]),
                full_name=user_data["full_name"],
                user_type=user_data["user_type"],
                status=UserStatus.ACTIVE,
                phone=user_data.get("phone"),
                email_verified=True
            )
            db.add(user)
            db.commit()
            print(f"[OK] Created user: {user_data['email']} (password: {user_data['password']})")
            created_count += 1
        except IntegrityError:
            db.rollback()
            print(f"[SKIP] User {user_data['email']} already exists")
    
    print(f"[OK] Created {created_count} new users")

def seed_products(db):
    """Seed demo products"""
    print("\nSeeding demo products...")
    
    products_data = [
        {
            "name": "Laptop Dell XPS 15",
            "sku": "DELL-XPS15-2024",
            "description": "Laptop cao cấp cho dân văn phòng và thiết kế",
            "price": 45000000,
            "stock_quantity": 15,
            "category": "Laptop"
        },
        {
            "name": "iPhone 15 Pro Max",
            "sku": "IPHONE-15PM-256",
            "description": "Điện thoại iPhone mới nhất với chip A17 Pro",
            "price": 32000000,
            "stock_quantity": 25,
            "category": "Smartphone"
        },
        {
            "name": "Samsung Galaxy S24 Ultra",
            "sku": "SAMSUNG-S24U-512",
            "description": "Flagship Android với S Pen và camera 200MP",
            "price": 28000000,
            "stock_quantity": 30,
            "category": "Smartphone"
        },
        {
            "name": "MacBook Air M3",
            "sku": "MBA-M3-2024",
            "description": "Laptop mỏng nhẹ với chip M3 mạnh mẽ",
            "price": 35000000,
            "stock_quantity": 20,
            "category": "Laptop"
        },
        {
            "name": "iPad Pro 12.9 inch",
            "sku": "IPAD-PRO-129-M2",
            "description": "Máy tính bảng chuyên nghiệp cho sáng tạo",
            "price": 28000000,
            "stock_quantity": 18,
            "category": "Tablet"
        },
        {
            "name": "Sony WH-1000XM5",
            "sku": "SONY-WH1000XM5",
            "description": "Tai nghe chống ồn cao cấp",
            "price": 8500000,
            "stock_quantity": 40,
            "category": "Audio"
        },
        {
            "name": "Logitech MX Master 3S",
            "sku": "LOGI-MXM3S",
            "description": "Chuột không dây cao cấp cho dân văn phòng",
            "price": 2200000,
            "stock_quantity": 50,
            "category": "Accessories"
        },
        {
            "name": "Dell UltraSharp 27 4K",
            "sku": "DELL-U2723DE",
            "description": "Màn hình 4K chuyên nghiệp 27 inch",
            "price": 15000000,
            "stock_quantity": 12,
            "category": "Monitor"
        },
        {
            "name": "Apple Watch Series 9",
            "sku": "WATCH-S9-45MM",
            "description": "Đồng hồ thông minh với chip S9",
            "price": 11000000,
            "stock_quantity": 35,
            "category": "Wearable"
        },
        {
            "name": "Samsung 980 PRO 2TB",
            "sku": "SSD-980PRO-2TB",
            "description": "SSD NVMe tốc độ cao 2TB",
            "price": 5500000,
            "stock_quantity": 45,
            "category": "Storage"
        }
    ]
    
    created_count = 0
    for product_data in products_data:
        try:
            existing_product = db.query(Product).filter(Product.sku == product_data["sku"]).first()
            if existing_product:
                print(f"[SKIP] Product {product_data['sku']} already exists")
                continue
            
            product = Product(**product_data)
            db.add(product)
            db.commit()
            print(f"[OK] Created product: {product_data['name']} ({product_data['sku']})")
            created_count += 1
        except IntegrityError:
            db.rollback()
            print(f"[SKIP] Product {product_data['sku']} already exists")
    
    print(f"[OK] Created {created_count} new products")

def main():
    """Main seeding function"""
    print("Starting CRM Demo Data Seeding...\n")
    
    # Create tables first
    create_tables()
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Seed data
        seed_users(db)
        seed_products(db)
        
        print("\n[OK] Demo data seeding completed successfully!")
        print("\nLogin credentials:")
        print("   Admin:    admin@crm-demo.com / admin123")
        print("   Staff:    staff@crm-demo.com / staff123")
        print("   Customer: customer@crm-demo.com / customer123")
        
    except Exception as e:
        print(f"\n[ERROR] Error during seeding: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
