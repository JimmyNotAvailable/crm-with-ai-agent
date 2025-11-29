from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from backend.database.session import get_db
from backend.models.order import Order, OrderItem, OrderStatus
from backend.models.product import Product
from backend.models.user import User
from backend.schemas.order import OrderCreate, OrderUpdate, OrderResponse
from backend.utils.security import get_current_user, require_role
import random
import string

router = APIRouter()


def generate_order_number() -> str:
    """Generate unique order number"""
    timestamp = datetime.now().strftime("%Y%m%d")
    random_suffix = ''.join(random.choices(string.digits, k=6))
    return f"ORD-{timestamp}-{random_suffix}"


@router.get("/", response_model=List[OrderResponse])
def list_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    status: Optional[OrderStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List orders
    Customers see only their orders, Staff/Admin see all
    """
    query = db.query(Order)
    
    # Filter by customer for non-staff users
    if current_user.role.value == "CUSTOMER":
        query = query.filter(Order.customer_id == current_user.id)
    
    if status:
        query = query.filter(Order.status == status)
    
    orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    return orders


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get order by ID
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Check permissions
    if current_user.role.value == "CUSTOMER" and getattr(order, 'customer_id', None) != current_user.id:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this order"
        )
    
    return order


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create new order
    """
    if not order_data.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must have at least one item"
        )
    
    # Calculate order totals
    total_amount = 0
    order_items = []
    
    for item_data in order_data.items:
        product = db.query(Product).filter(Product.id == item_data.product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {item_data.product_id} not found"
            )
        
        if not getattr(product, 'is_active', True):  # type: ignore
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product {product.name} is not available"
            )
        if getattr(product, 'stock_quantity', 0) < item_data.quantity:  # type: ignore
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for {product.name}"
            )
        
        subtotal = product.price * item_data.quantity
        total_amount += subtotal
        
        order_items.append({
            "product_id": product.id,
            "product_name": product.name,
            "product_sku": product.sku,
            "quantity": item_data.quantity,
            "unit_price": product.price,
            "subtotal": subtotal
        })
    
    # Create order
    new_order = Order(
        order_number=generate_order_number(),
        customer_id=current_user.id,
        status=OrderStatus.PENDING,
        total_amount=total_amount,
        shipping_address=order_data.shipping_address,
        shipping_city=order_data.shipping_city,
        shipping_phone=order_data.shipping_phone,
        payment_method=order_data.payment_method,
        customer_notes=order_data.customer_notes
    )
    
    db.add(new_order)
    db.flush()
    
    # Create order items
    for item_data in order_items:
        order_item = OrderItem(order_id=new_order.id, **item_data)
        db.add(order_item)
        
        # Decrease stock
        product = db.query(Product).filter(Product.id == item_data["product_id"]).first()
        if product:
            product.stock_quantity -= item_data["quantity"]
    
    db.commit()
    db.refresh(new_order)
    
    return new_order


@router.put("/{order_id}", response_model=OrderResponse)
def update_order(
    order_id: int,
    order_data: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("STAFF"))
):
    """
    Update order status (Staff/Admin only)
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Update fields
    if order_data.status:
        order.status = order_data.status  # type: ignore
        
        # Update timestamps based on status
        if order_data.status == OrderStatus.CONFIRMED:
            order.confirmed_at = datetime.utcnow()  # type: ignore
        elif order_data.status == OrderStatus.SHIPPED:
            order.shipped_at = datetime.utcnow()  # type: ignore
        elif order_data.status == OrderStatus.DELIVERED:
            order.delivered_at = datetime.utcnow()  # type: ignore
    
    if order_data.admin_notes:
        order.admin_notes = order_data.admin_notes  # type: ignore
    
    db.commit()
    db.refresh(order)
    
    return order


@router.delete("/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cancel order (if eligible)
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Check permissions
    if current_user.role.value == "CUSTOMER" and order.customer_id != current_user.id:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel this order"
        )
    
    # Check if can cancel
    if not order.can_cancel:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel order in {order.status} status"
        )
    
    # Restore stock
    for item in order.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            product.stock_quantity += item.quantity  # type: ignore
    
    order.status = OrderStatus.CANCELLED  # type: ignore
    db.commit()
    db.refresh(order)
    
    return order
