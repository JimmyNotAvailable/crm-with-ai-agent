"""
Analytics and KPI Dashboard Endpoints
Real-time KPI monitoring and anomaly detection
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime, timedelta
from backend.database.session import get_db
from backend.models.user import User
from backend.models.order import Order, OrderStatus
from backend.models.ticket import Ticket, TicketStatus
from backend.models.product import Product
from backend.models.conversation import Conversation
from backend.utils.security import require_role

router = APIRouter()


@router.get("/dashboard")
def get_dashboard_stats(
    days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("STAFF"))
):
    """
    Get comprehensive dashboard statistics
    """
    # Date range
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Orders statistics
    total_orders = db.query(Order).count()
    recent_orders = db.query(Order).filter(Order.created_at >= start_date).count()
    pending_orders = db.query(Order).filter(Order.status == OrderStatus.PENDING).count()
    
    total_revenue = db.query(func.sum(Order.total_amount)).filter(
        Order.created_at >= start_date
    ).scalar() or 0
    
    # Tickets statistics
    total_tickets = db.query(Ticket).count()
    open_tickets = db.query(Ticket).filter(Ticket.status == TicketStatus.OPEN).count()
    in_progress_tickets = db.query(Ticket).filter(Ticket.status == TicketStatus.IN_PROGRESS).count()
    
    negative_tickets = db.query(Ticket).filter(
        Ticket.sentiment_label == "NEGATIVE",
        Ticket.created_at >= start_date
    ).count()
    
    # Products statistics
    total_products = db.query(Product).filter(Product.is_active == True).count()
    low_stock_products = db.query(Product).filter(
        Product.is_active == True,
        Product.stock_quantity <= Product.low_stock_threshold
    ).count()
    
    # Customer statistics
    total_customers = db.query(User).filter(User.role == "CUSTOMER").count()
    new_customers = db.query(User).filter(
        User.role == "CUSTOMER",
        User.created_at >= start_date
    ).count()
    
    # Conversations
    total_conversations = db.query(Conversation).filter(
        Conversation.created_at >= start_date
    ).count()
    
    # Calculate KPIs
    average_order_value = float(total_revenue) / recent_orders if recent_orders > 0 else 0
    ticket_resolution_rate = 0  # TODO: Calculate based on resolved tickets
    
    return {
        "period_days": days,
        "orders": {
            "total": total_orders,
            "recent": recent_orders,
            "pending": pending_orders,
            "total_revenue": float(total_revenue),
            "average_order_value": round(average_order_value, 2)
        },
        "tickets": {
            "total": total_tickets,
            "open": open_tickets,
            "in_progress": in_progress_tickets,
            "negative_sentiment": negative_tickets
        },
        "products": {
            "total_active": total_products,
            "low_stock": low_stock_products
        },
        "customers": {
            "total": total_customers,
            "new": new_customers
        },
        "engagement": {
            "conversations": total_conversations
        }
    }


@router.get("/kpi/overview")
def get_kpi_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("STAFF"))
):
    """
    Get key performance indicators overview
    """
    # Calculate KPIs for last 30 days
    last_30_days = datetime.utcnow() - timedelta(days=30)
    last_7_days = datetime.utcnow() - timedelta(days=7)
    
    # Revenue KPI
    revenue_30d = db.query(func.sum(Order.total_amount)).filter(
        Order.created_at >= last_30_days
    ).scalar() or 0
    
    revenue_7d = db.query(func.sum(Order.total_amount)).filter(
        Order.created_at >= last_7_days
    ).scalar() or 0
    
    # Orders KPI
    orders_30d = db.query(Order).filter(Order.created_at >= last_30_days).count()
    orders_7d = db.query(Order).filter(Order.created_at >= last_7_days).count()
    
    # Support KPI - Average response time (mock)
    avg_response_time_hours = 2.5  # TODO: Calculate from ticket messages
    
    # Customer satisfaction (mock)
    csat_score = 4.2  # TODO: Calculate from feedback
    
    # Ticket backlog
    ticket_backlog = db.query(Ticket).filter(
        Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS])
    ).count()
    
    return {
        "revenue": {
            "last_30_days": float(revenue_30d),
            "last_7_days": float(revenue_7d),
            "trend": "UP" if float(revenue_7d) > float(revenue_30d) / 4 else "DOWN"
        },
        "orders": {
            "last_30_days": orders_30d,
            "last_7_days": orders_7d,
            "avg_per_day": round(orders_30d / 30, 2)
        },
        "support": {
            "avg_response_time_hours": avg_response_time_hours,
            "ticket_backlog": ticket_backlog,
            "sla_compliance": 95.5  # Mock
        },
        "customer_satisfaction": {
            "csat_score": csat_score,
            "nps": 42  # Mock Net Promoter Score
        }
    }


@router.get("/anomalies/detect")
def detect_anomalies(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("STAFF"))
):
    """
    Detect anomalies in system metrics
    Returns alerts for unusual patterns
    """
    anomalies = []
    
    # Check for unusual spike in negative tickets (last 24h)
    last_24h = datetime.utcnow() - timedelta(hours=24)
    negative_tickets_24h = db.query(Ticket).filter(
        Ticket.sentiment_label == "NEGATIVE",
        Ticket.created_at >= last_24h
    ).count()
    
    if negative_tickets_24h > 5:  # Threshold
        anomalies.append({
            "type": "HIGH_NEGATIVE_SENTIMENT",
            "severity": "HIGH",
            "message": f"Phát hiện {negative_tickets_24h} ticket cảm xúc tiêu cực trong 24h qua",
            "recommendation": "Kiểm tra nguyên nhân và xử lý ưu tiên"
        })
    
    # Check for low stock products
    low_stock_count = db.query(Product).filter(
        Product.is_active == True,
        Product.stock_quantity <= Product.low_stock_threshold
    ).count()
    
    if low_stock_count > 10:
        anomalies.append({
            "type": "LOW_STOCK_ALERT",
            "severity": "MEDIUM",
            "message": f"{low_stock_count} sản phẩm sắp hết hàng",
            "recommendation": "Nhập hàng bổ sung"
        })
    
    # Check for order backlog
    pending_orders = db.query(Order).filter(
        Order.status == OrderStatus.PENDING,
        Order.created_at < datetime.utcnow() - timedelta(days=2)
    ).count()
    
    if pending_orders > 5:
        anomalies.append({
            "type": "ORDER_BACKLOG",
            "severity": "HIGH",
            "message": f"{pending_orders} đơn hàng chưa xử lý quá 2 ngày",
            "recommendation": "Xử lý đơn hàng tồn đọng"
        })
    
    # Check for support ticket overflow
    open_tickets = db.query(Ticket).filter(
        Ticket.status == TicketStatus.OPEN
    ).count()
    
    if open_tickets > 20:
        anomalies.append({
            "type": "TICKET_OVERFLOW",
            "severity": "MEDIUM",
            "message": f"{open_tickets} ticket đang chờ xử lý",
            "recommendation": "Phân công thêm nhân viên hỗ trợ"
        })
    
    return {
        "timestamp": datetime.utcnow(),
        "total_anomalies": len(anomalies),
        "anomalies": anomalies,
        "system_health": "WARNING" if len(anomalies) > 2 else "HEALTHY" if len(anomalies) == 0 else "ATTENTION"
    }


@router.get("/trends/orders")
def get_order_trends(
    days: int = Query(30, ge=7, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("STAFF"))
):
    """
    Get order trends over time
    Returns daily order counts and revenue
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get orders grouped by date
    # This is a simplified version - in production use proper SQL grouping
    orders = db.query(Order).filter(Order.created_at >= start_date).all()
    
    # Group by date
    daily_data = {}
    for order in orders:
        date_key = order.created_at.date().isoformat()  # type: ignore
        if date_key not in daily_data:
            daily_data[date_key] = {"count": 0, "revenue": 0}
        
        daily_data[date_key]["count"] += 1
        daily_data[date_key]["revenue"] += float(order.total_amount) if order.total_amount else 0  # type: ignore
    
    # Convert to list
    trend_data = [
        {
            "date": date,
            "order_count": data["count"],
            "revenue": round(data["revenue"], 2)
        }
        for date, data in sorted(daily_data.items())
    ]
    
    return {
        "period_days": days,
        "data_points": len(trend_data),
        "trends": trend_data
    }


@router.get("/performance/staff")
def get_staff_performance(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN"))
):
    """
    Get staff performance metrics (Admin only)
    """
    # Get all staff
    staff_members = db.query(User).filter(User.role == "STAFF").all()
    
    performance = []
    for staff in staff_members:
        # Get assigned tickets
        assigned_tickets = db.query(Ticket).filter(Ticket.assigned_to == staff.id).count()
        resolved_tickets = db.query(Ticket).filter(
            Ticket.assigned_to == staff.id,
            Ticket.status == TicketStatus.RESOLVED
        ).count()
        
        performance.append({
            "staff_id": staff.id,
            "staff_name": staff.full_name,
            "tickets_assigned": assigned_tickets,
            "tickets_resolved": resolved_tickets,
            "resolution_rate": round((resolved_tickets / assigned_tickets * 100), 2) if assigned_tickets > 0 else 0
        })
    
    return {
        "total_staff": len(performance),
        "performance": sorted(performance, key=lambda x: x["resolution_rate"], reverse=True)
    }
