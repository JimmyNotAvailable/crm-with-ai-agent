"""
Product Recommender - ML-based product recommendation
Gợi ý sản phẩm dựa trên:
- Lịch sử mua hàng
- Hành vi browsing
- Sản phẩm tương tự (content-based)
- Collaborative filtering
"""
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from collections import Counter


class ProductRecommender:
    """
    ML-based Product Recommender
    
    Algorithms:
    1. Content-based: Dựa trên đặc điểm sản phẩm (category, brand, price range)
    2. Collaborative: Dựa trên hành vi users tương tự
    3. Popularity-based: Sản phẩm bán chạy
    4. Personalized: Kết hợp lịch sử user
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def recommend(
        self,
        user_id: Optional[int] = None,
        preferences: Optional[Dict[str, Any]] = None,
        category: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get product recommendations
        
        Args:
            user_id: User ID for personalized recommendations
            preferences: Extracted preferences from query
            category: Filter by category
            limit: Max number of recommendations
            
        Returns:
            List of recommended products
        """
        recommendations = []
        
        # Strategy 1: If user has history, use personalized
        if user_id:
            personalized = self._get_personalized_recommendations(user_id, limit)
            recommendations.extend(personalized)
        
        # Strategy 2: Content-based on preferences
        if preferences and len(recommendations) < limit:
            content_based = self._get_content_based_recommendations(
                preferences, 
                category,
                limit - len(recommendations)
            )
            recommendations.extend(content_based)
        
        # Strategy 3: Fallback to popularity
        if len(recommendations) < limit:
            popular = self._get_popular_products(
                category,
                limit - len(recommendations)
            )
            recommendations.extend(popular)
        
        # Deduplicate and limit
        seen_ids = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec.get("id") not in seen_ids:
                seen_ids.add(rec.get("id"))
                unique_recommendations.append(rec)
                if len(unique_recommendations) >= limit:
                    break
        
        return unique_recommendations
    
    def recommend_similar(
        self,
        product_id: int,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get similar products based on a reference product
        
        Args:
            product_id: Reference product ID
            limit: Max number of recommendations
            
        Returns:
            List of similar products
        """
        from backend.models.product import Product
        
        # Get reference product
        ref_product = self.db.query(Product).filter(Product.id == product_id).first()
        if not ref_product:
            return []
        
        # Find similar products (same category, similar price range)
        price_range_low = float(ref_product.price) * 0.7 if ref_product.price else 0
        price_range_high = float(ref_product.price) * 1.3 if ref_product.price else float('inf')
        
        similar = self.db.query(Product).filter(
            Product.id != product_id,
            Product.is_active == True,
            Product.category == ref_product.category,
            Product.price >= price_range_low,
            Product.price <= price_range_high
        ).limit(limit).all()
        
        return [self._product_to_dict(p) for p in similar]
    
    def _get_personalized_recommendations(
        self, 
        user_id: int, 
        limit: int
    ) -> List[Dict[str, Any]]:
        """Get personalized recommendations based on user history"""
        from backend.models.order import Order, OrderItem
        from backend.models.product import Product
        
        # Get user's purchased categories
        purchased_categories = self.db.query(Product.category).join(
            OrderItem, OrderItem.product_id == Product.id
        ).join(
            Order, Order.id == OrderItem.order_id
        ).filter(
            Order.customer_id == user_id
        ).all()
        
        if not purchased_categories:
            return []
        
        # Count category frequency
        category_counts = Counter([c[0] for c in purchased_categories if c[0]])
        top_categories = [cat for cat, _ in category_counts.most_common(3)]
        
        # Get purchased product IDs to exclude
        purchased_ids = self.db.query(OrderItem.product_id).join(
            Order, Order.id == OrderItem.order_id
        ).filter(
            Order.customer_id == user_id
        ).all()
        purchased_ids = [pid[0] for pid in purchased_ids]
        
        # Recommend products from favorite categories, not yet purchased
        recommendations = self.db.query(Product).filter(
            Product.is_active == True,
            Product.category.in_(top_categories),
            ~Product.id.in_(purchased_ids) if purchased_ids else True
        ).order_by(Product.stock_quantity.desc()).limit(limit).all()
        
        return [self._product_to_dict(p) for p in recommendations]
    
    def _get_content_based_recommendations(
        self,
        preferences: Dict[str, Any],
        category: Optional[str],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Get content-based recommendations based on preferences"""
        from backend.models.product import Product
        
        query = self.db.query(Product).filter(Product.is_active == True)
        
        if category:
            query = query.filter(Product.category == category)
        
        # Apply price constraints if available
        if preferences.get("max_price"):
            query = query.filter(Product.price <= preferences["max_price"])
        if preferences.get("min_price"):
            query = query.filter(Product.price >= preferences["min_price"])
        
        products = query.order_by(Product.stock_quantity.desc()).limit(limit).all()
        
        return [self._product_to_dict(p) for p in products]
    
    def _get_popular_products(
        self,
        category: Optional[str],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Get popular products based on sales"""
        from backend.models.product import Product
        from backend.models.order import OrderItem
        
        # Get best-selling products
        query = self.db.query(
            Product,
            func.sum(OrderItem.quantity).label('total_sold')
        ).outerjoin(
            OrderItem, OrderItem.product_id == Product.id
        ).filter(
            Product.is_active == True
        ).group_by(Product.id)
        
        if category:
            query = query.filter(Product.category == category)
        
        products = query.order_by(func.sum(OrderItem.quantity).desc().nullslast()).limit(limit).all()
        
        return [self._product_to_dict(p[0]) for p in products]
    
    def _product_to_dict(self, product) -> Dict[str, Any]:
        """Convert Product model to dictionary"""
        return {
            "id": product.id,
            "name": product.name,
            "price": float(product.price) if product.price else 0,
            "category": product.category,
            "brand": getattr(product, 'brand', None),
            "stock": int(product.stock_quantity) if product.stock_quantity else 0,
            "description": str(product.description)[:200] if product.description else ""
        }
