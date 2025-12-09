"""
Customer Behavior Tracking Service
Track and analyze customer interactions for personalization
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from backend.models.user import User
from backend.models.order import Order
from backend.models.product import Product
from backend.models.ticket import Ticket
from backend.models.conversation import Conversation
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from collections import Counter


class BehaviorTrackingService:
    """Service for tracking and analyzing customer behavior"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_customer_profile(self, customer_id: int) -> Dict:
        """
        Get comprehensive customer behavior profile
        
        Returns:
            Dict with purchase history, preferences, engagement metrics
        """
        customer = self.db.query(User).filter(User.id == customer_id).first()
        if not customer:
            return {}
        
        # Purchase behavior
        purchase_stats = self._get_purchase_stats(customer_id)
        
        # Product preferences
        product_prefs = self._get_product_preferences(customer_id)
        
        # Support behavior
        support_stats = self._get_support_stats(customer_id)
        
        # Chat engagement
        chat_stats = self._get_chat_stats(customer_id)
        
        # Customer segment
        segment = self._classify_customer_segment(
            purchase_stats["total_spend"],
            purchase_stats["order_count"],
            support_stats["ticket_count"]
        )
        
        return {
            "customer_id": customer_id,
            "username": customer.username,
            "email": customer.email,
            "segment": segment,
            "purchase_behavior": purchase_stats,
            "product_preferences": product_prefs,
            "support_behavior": support_stats,
            "chat_engagement": chat_stats,
            "risk_level": self._calculate_risk_level(support_stats, purchase_stats),
            "engagement_score": self._calculate_engagement_score(
                purchase_stats, chat_stats, support_stats
            )
        }
    
    def _get_purchase_stats(self, customer_id: int) -> Dict:
        """Get customer purchase statistics"""
        orders = self.db.query(Order).filter(
            Order.customer_id == customer_id
        ).all()
        
        total_spend = sum(order.total_amount for order in orders)
        order_count = len(orders)
        
        # Recent activity
        recent_orders = [
            order for order in orders
            if order.created_at >= datetime.utcnow() - timedelta(days=90)
        ]
        recent_spend = sum(order.total_amount for order in recent_orders)
        
        # Average order value
        avg_order_value = total_spend / order_count if order_count > 0 else 0
        
        # Last purchase date
        last_purchase = None
        if orders:
            last_order = max(orders, key=lambda o: o.created_at)
            last_purchase = last_order.created_at
        
        return {
            "total_spend": total_spend,
            "order_count": order_count,
            "avg_order_value": avg_order_value,
            "recent_orders_90d": len(recent_orders),
            "recent_spend_90d": recent_spend,
            "last_purchase_date": last_purchase.isoformat() if last_purchase else None
        }
    
    def _get_product_preferences(self, customer_id: int) -> Dict:
        """Analyze product preferences from order history"""
        from backend.models.order import OrderItem
        
        # Get all order items
        orders = self.db.query(Order).filter(
            Order.customer_id == customer_id
        ).all()
        
        order_ids = [order.id for order in orders]
        
        if not order_ids:
            return {
                "favorite_categories": [],
                "frequent_products": [],
                "total_items_purchased": 0
            }
        
        # Get items
        items = self.db.query(OrderItem).filter(
            OrderItem.order_id.in_(order_ids)
        ).all()
        
        # Aggregate by product
        product_counter = Counter()
        for item in items:
            product_counter[item.product_id] += item.quantity
        
        # Get top products
        top_product_ids = [pid for pid, _ in product_counter.most_common(5)]
        top_products = self.db.query(Product).filter(
            Product.id.in_(top_product_ids)
        ).all()
        
        frequent_products = [
            {
                "product_id": p.id,
                "name": p.name,
                "category": p.category,
                "purchase_count": product_counter[p.id]
            }
            for p in top_products
        ]
        
        # Category preferences
        category_counter = Counter()
        for product in top_products:
            if product.category:
                category_counter[product.category] += product_counter[product.id]
        
        favorite_categories = [
            {"category": cat, "count": count}
            for cat, count in category_counter.most_common(3)
        ]
        
        return {
            "favorite_categories": favorite_categories,
            "frequent_products": frequent_products,
            "total_items_purchased": sum(item.quantity for item in items)
        }
    
    def _get_support_stats(self, customer_id: int) -> Dict:
        """Get customer support statistics"""
        tickets = self.db.query(Ticket).filter(
            Ticket.customer_id == customer_id
        ).all()
        
        ticket_count = len(tickets)
        open_tickets = len([t for t in tickets if t.status == "OPEN"])
        
        # Sentiment analysis
        negative_tickets = len([
            t for t in tickets
            if t.sentiment_score and t.sentiment_score < -0.3
        ])
        
        # Common categories
        category_counter = Counter(t.category for t in tickets if t.category)
        common_categories = [
            {"category": cat, "count": count}
            for cat, count in category_counter.most_common(3)
        ]
        
        return {
            "ticket_count": ticket_count,
            "open_tickets": open_tickets,
            "negative_sentiment_count": negative_tickets,
            "common_issue_categories": common_categories
        }
    
    def _get_chat_stats(self, customer_id: int) -> Dict:
        """Get chat engagement statistics"""
        conversations = self.db.query(Conversation).filter(
            Conversation.customer_id == customer_id
        ).all()
        
        total_conversations = len(conversations)
        total_messages = sum(c.message_count for c in conversations)
        
        # Recent activity
        recent_convos = [
            c for c in conversations
            if c.updated_at >= datetime.utcnow() - timedelta(days=30)
        ]
        
        return {
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "recent_conversations_30d": len(recent_convos),
            "avg_messages_per_conversation": (
                total_messages / total_conversations if total_conversations > 0 else 0
            )
        }
    
    def _classify_customer_segment(
        self,
        total_spend: float,
        order_count: int,
        ticket_count: int
    ) -> str:
        """Classify customer into segment"""
        if total_spend >= 10000000 and order_count >= 5:
            return "VIP"
        elif total_spend >= 5000000 or order_count >= 3:
            return "LOYAL"
        elif order_count >= 1:
            return "REGULAR"
        else:
            return "NEW"
    
    def _calculate_risk_level(self, support_stats: Dict, purchase_stats: Dict) -> str:
        """Calculate customer churn risk level"""
        # High risk if many negative tickets
        if support_stats["negative_sentiment_count"] >= 3:
            return "HIGH"
        
        # Medium risk if no recent purchases
        if purchase_stats["recent_orders_90d"] == 0 and purchase_stats["order_count"] > 0:
            return "MEDIUM"
        
        return "LOW"
    
    def _calculate_engagement_score(
        self,
        purchase_stats: Dict,
        chat_stats: Dict,
        support_stats: Dict
    ) -> float:
        """
        Calculate overall engagement score (0-100)
        Higher score = more engaged customer
        """
        score = 0.0
        
        # Purchase activity (40 points max)
        score += min(purchase_stats["order_count"] * 5, 40)
        
        # Chat engagement (30 points max)
        score += min(chat_stats["total_conversations"] * 3, 30)
        
        # Recent activity (30 points max)
        score += min(purchase_stats["recent_orders_90d"] * 10, 30)
        
        # Penalty for support issues
        score -= support_stats["negative_sentiment_count"] * 5
        
        return max(0, min(100, score))
    
    def get_product_recommendations(
        self,
        customer_id: int,
        limit: int = 5
    ) -> List[Dict]:
        """
        Generate personalized product recommendations
        
        Based on:
        - Purchase history (collaborative filtering)
        - Category preferences
        - Popular products
        """
        profile = self.get_customer_profile(customer_id)
        
        # Get favorite categories
        favorite_categories = [
            cat["category"]
            for cat in profile["product_preferences"]["favorite_categories"]
        ]
        
        # Get purchased product IDs to exclude
        purchased_ids = [
            p["product_id"]
            for p in profile["product_preferences"]["frequent_products"]
        ]
        
        # Query recommendations
        query = self.db.query(Product).filter(
            Product.is_active == True
        )
        
        # Prioritize favorite categories
        if favorite_categories:
            query = query.filter(Product.category.in_(favorite_categories))
        
        # Exclude already purchased
        if purchased_ids:
            query = query.filter(~Product.id.in_(purchased_ids))
        
        # Order by stock and random
        products = query.filter(Product.stock_quantity > 0).limit(limit * 2).all()
        
        # Score and rank
        recommendations = []
        for product in products[:limit]:
            score = 0.5  # Base score
            
            # Bonus for matching category
            if product.category in favorite_categories:
                score += 0.3
            
            recommendations.append({
                "product_id": product.id,
                "name": product.name,
                "category": product.category,
                "price": product.price,
                "recommendation_score": score,
                "reason": f"Based on your interest in {product.category}"
            })
        
        return recommendations
