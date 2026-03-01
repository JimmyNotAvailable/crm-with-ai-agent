"""
AI Personalization Endpoints
Provide personalized experiences based on customer behavior
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict
from pydantic import BaseModel
from backend.database.session import get_identity_db, get_order_db, get_product_db, get_support_db, get_knowledge_db
from backend.models.user import User
from backend.utils.security import get_current_user
from backend.services.behavior_tracking import BehaviorTrackingService

router = APIRouter()


class CustomerProfileResponse(BaseModel):
    """Response schema for customer profile"""
    customer_id: str
    username: str
    email: str
    segment: str
    purchase_behavior: Dict
    product_preferences: Dict
    support_behavior: Dict
    chat_engagement: Dict
    risk_level: str
    engagement_score: float


class ProductRecommendationResponse(BaseModel):
    """Response schema for product recommendation"""
    product_id: str
    name: str
    category: str
    price: float
    recommendation_score: float
    reason: str


class PersonalizedMessageResponse(BaseModel):
    """Response schema for personalized message"""
    greeting: str
    message: str
    recommendations: List[str]
    special_offers: List[str]


@router.get("/profile", response_model=CustomerProfileResponse)
def get_my_profile(
    identity_db: Session = Depends(get_identity_db),
    order_db: Session = Depends(get_order_db),
    product_db: Session = Depends(get_product_db),
    support_db: Session = Depends(get_support_db),
    knowledge_db: Session = Depends(get_knowledge_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get personalized customer profile
    Includes behavior analysis and segment classification
    """
    tracking_service = BehaviorTrackingService(
        identity_db=identity_db,
        order_db=order_db,
        product_db=product_db,
        support_db=support_db,
        knowledge_db=knowledge_db
    )
    profile = tracking_service.get_customer_profile(current_user.id)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    return CustomerProfileResponse(**profile)


@router.get("/recommendations", response_model=List[ProductRecommendationResponse])
def get_personalized_recommendations(
    limit: int = 5,
    identity_db: Session = Depends(get_identity_db),
    order_db: Session = Depends(get_order_db),
    product_db: Session = Depends(get_product_db),
    support_db: Session = Depends(get_support_db),
    knowledge_db: Session = Depends(get_knowledge_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get personalized product recommendations
    Based on purchase history and preferences
    """
    tracking_service = BehaviorTrackingService(
        identity_db=identity_db,
        order_db=order_db,
        product_db=product_db,
        support_db=support_db,
        knowledge_db=knowledge_db
    )
    recommendations = tracking_service.get_product_recommendations(
        customer_id=current_user.id,
        limit=limit
    )
    
    return [ProductRecommendationResponse(**rec) for rec in recommendations]


@router.get("/greeting", response_model=PersonalizedMessageResponse)
def get_personalized_greeting(
    identity_db: Session = Depends(get_identity_db),
    order_db: Session = Depends(get_order_db),
    product_db: Session = Depends(get_product_db),
    support_db: Session = Depends(get_support_db),
    knowledge_db: Session = Depends(get_knowledge_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get personalized greeting message
    Customized based on customer segment and behavior
    """
    tracking_service = BehaviorTrackingService(
        identity_db=identity_db,
        order_db=order_db,
        product_db=product_db,
        support_db=support_db,
        knowledge_db=knowledge_db
    )
    profile = tracking_service.get_customer_profile(current_user.id)
    
    # Generate personalized greeting
    segment = profile.get("segment", "NEW")
    engagement_score = profile.get("engagement_score", 0)
    
    # Customize greeting based on segment
    greetings = {
        "VIP": f"Chào quý khách VIP {current_user.username}! 🌟",
        "LOYAL": f"Xin chào khách hàng thân thiết {current_user.username}! 👋",
        "REGULAR": f"Chào {current_user.username}! 😊",
        "NEW": f"Chào mừng {current_user.username} đến với chúng tôi! 🎉"
    }
    
    greeting = greetings.get(segment, f"Xin chào {current_user.username}!")
    
    # Generate personalized message
    messages = []
    
    if segment == "VIP":
        messages.append("Cảm ơn bạn đã là khách hàng VIP của chúng tôi!")
        messages.append("Bạn được hưởng ưu đãi đặc biệt và hỗ trợ ưu tiên.")
    elif segment == "LOYAL":
        messages.append("Cảm ơn sự ủng hộ lâu dài của bạn!")
        messages.append("Chúng tôi có nhiều ưu đãi dành riêng cho bạn.")
    elif segment == "NEW":
        messages.append("Chào mừng bạn lần đầu đến với chúng tôi!")
        messages.append("Hãy khám phá các sản phẩm và dịch vụ tuyệt vời của chúng tôi.")
    
    message = " ".join(messages)
    
    # Get product recommendations
    recommendations_list = tracking_service.get_product_recommendations(
        customer_id=current_user.id,
        limit=3
    )
    
    recommendation_messages = [
        f"🔥 {rec['name']} - {rec['reason']}"
        for rec in recommendations_list
    ]
    
    # Special offers based on segment
    special_offers = []
    
    if segment == "VIP":
        special_offers.append("🎁 Giảm 20% cho đơn hàng tiếp theo")
        special_offers.append("🚚 Miễn phí vận chuyển toàn quốc")
        special_offers.append("⭐ Tích điểm gấp đôi")
    elif segment == "LOYAL":
        special_offers.append("🎁 Giảm 15% cho đơn hàng tiếp theo")
        special_offers.append("🚚 Miễn phí vận chuyển đơn > 500k")
    elif segment == "NEW":
        special_offers.append("🎁 Giảm 10% cho đơn hàng đầu tiên")
        special_offers.append("🎉 Quà tặng chào mừng")
    
    # Risk warning for staff (not shown to customer)
    risk_level = profile.get("risk_level", "LOW")
    if risk_level == "HIGH":
        # Internal note: customer at high risk of churn
        pass
    
    return PersonalizedMessageResponse(
        greeting=greeting,
        message=message,
        recommendations=recommendation_messages,
        special_offers=special_offers
    )


@router.get("/profile/{customer_id}", response_model=CustomerProfileResponse)
def get_customer_profile_admin(
    customer_id: str,
    identity_db: Session = Depends(get_identity_db),
    order_db: Session = Depends(get_order_db),
    product_db: Session = Depends(get_product_db),
    support_db: Session = Depends(get_support_db),
    knowledge_db: Session = Depends(get_knowledge_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get customer profile (Staff/Admin only)
    For customer service and analysis
    """
    # Check permissions
    if current_user.role.value not in ["STAFF", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    tracking_service = BehaviorTrackingService(
        identity_db=identity_db,
        order_db=order_db,
        product_db=product_db,
        support_db=support_db,
        knowledge_db=knowledge_db
    )
    profile = tracking_service.get_customer_profile(customer_id)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    return CustomerProfileResponse(**profile)
