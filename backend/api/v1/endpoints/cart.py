"""
Shopping Cart endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database.session import get_db
from backend.models.cart import Cart, CartItem
from backend.models.product import Product
from backend.models.order import Order, OrderItem, OrderStatus
from backend.models.user import User
from backend.schemas.cart import (
    CartItemCreate, CartItemUpdate, CartItemResponse,
    CartResponse, CheckoutRequest
)
from backend.schemas.order import OrderResponse
from backend.utils.security import get_current_user
from datetime import datetime
import random
import string

router = APIRouter()


def get_or_create_cart(db: Session, user_id: int) -> Cart:
    """Get existing cart or create new one for user"""
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart


@router.get("/", response_model=CartResponse)
def get_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's cart
    """
    cart = get_or_create_cart(db, int(current_user.id))  # type: ignore
    return cart


@router.post("/items", response_model=CartItemResponse, status_code=status.HTTP_201_CREATED)
def add_to_cart(
    item_data: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add product to cart or update quantity if already exists
    """
    # Get product
    product = db.query(Product).filter(Product.id == item_data.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    if not bool(product.is_active):  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product is not available"
        )
    
    if int(product.stock_quantity) < item_data.quantity:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient stock. Available: {product.stock_quantity}"
        )
    
    # Get or create cart
    cart = get_or_create_cart(db, int(current_user.id))  # type: ignore
    
    # Check if item already in cart
    existing_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == item_data.product_id
    ).first()
    
    if existing_item:
        # Update quantity
        new_quantity = int(existing_item.quantity) + item_data.quantity  # type: ignore
        if int(product.stock_quantity) < new_quantity:  # type: ignore
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot add more. Stock available: {product.stock_quantity}"
            )
        existing_item.quantity = new_quantity  # type: ignore
        db.commit()
        db.refresh(existing_item)
        return existing_item
    else:
        # Create new cart item
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=product.id,
            product_name=product.name,
            product_sku=product.sku,
            unit_price=product.price,
            quantity=item_data.quantity
        )
        db.add(cart_item)
        db.commit()
        db.refresh(cart_item)
        return cart_item


@router.put("/items/{item_id}", response_model=CartItemResponse)
def update_cart_item(
    item_id: int,
    item_data: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update cart item quantity
    """
    cart = get_or_create_cart(db, int(current_user.id))  # type: ignore
    
    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.cart_id == cart.id
    ).first()
    
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )
    
    # Check stock
    product = db.query(Product).filter(Product.id == cart_item.product_id).first()
    if product and int(product.stock_quantity) < item_data.quantity:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient stock. Available: {product.stock_quantity}"
        )
    
    cart_item.quantity = item_data.quantity  # type: ignore
    db.commit()
    db.refresh(cart_item)
    return cart_item


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_cart(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Remove item from cart
    """
    cart = get_or_create_cart(db, int(current_user.id))  # type: ignore
    
    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.cart_id == cart.id
    ).first()
    
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )
    
    db.delete(cart_item)
    db.commit()
    return None


@router.delete("/clear", status_code=status.HTTP_204_NO_CONTENT)
def clear_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Clear all items from cart
    """
    cart = get_or_create_cart(db, int(current_user.id))  # type: ignore
    
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    db.commit()
    return None


@router.post("/checkout", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def checkout(
    checkout_data: CheckoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Checkout: Convert cart to order
    """
    cart = get_or_create_cart(db, int(current_user.id))  # type: ignore
    
    if not cart.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart is empty"
        )
    
    # Validate stock for all items
    for cart_item in cart.items:
        product = db.query(Product).filter(Product.id == cart_item.product_id).first()
        if not product or not bool(product.is_active):  # type: ignore
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product {cart_item.product_name} is no longer available"
            )
        if product.stock_quantity < cart_item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for {cart_item.product_name}"
            )
    
    # Generate order number
    timestamp = datetime.now().strftime("%Y%m%d")
    random_suffix = ''.join(random.choices(string.digits, k=6))
    order_number = f"ORD-{timestamp}-{random_suffix}"
    
    # Create order
    new_order = Order(
        order_number=order_number,
        customer_id=current_user.id,
        status=OrderStatus.PENDING,
        total_amount=cart.total_amount,
        shipping_address=checkout_data.shipping_address,
        shipping_city=checkout_data.shipping_city,
        shipping_phone=checkout_data.shipping_phone,
        payment_method=checkout_data.payment_method,
        customer_notes=checkout_data.customer_notes
    )
    
    db.add(new_order)
    db.flush()
    
    # Create order items and update stock
    for cart_item in cart.items:
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=cart_item.product_id,
            product_name=cart_item.product_name,
            product_sku=cart_item.product_sku,
            quantity=cart_item.quantity,
            unit_price=cart_item.unit_price,
            subtotal=cart_item.subtotal
        )
        db.add(order_item)
        
        # Decrease stock
        product = db.query(Product).filter(Product.id == cart_item.product_id).first()
        if product:
            product.stock_quantity -= cart_item.quantity
    
    # Clear cart after successful checkout
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    
    db.commit()
    db.refresh(new_order)
    
    return new_order
