from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from dependencies import (
    get_current_user,
    require_role,
    require_permission
)
from payment_gateway import client, RAZORPAY_KEY_ID
from database import Base, engine, get_db
import models
from fastapi.security import OAuth2PasswordRequestForm
from schemas import PaymentCreate, UserCreate, ProductCreate, ProductUpdate, CartItemCreate, PromotionCreate, ApplyCoupon, OrderCreate, PaymentStatusUpdate

from auth import (
    hash_password,
    verify_password,
    create_token
)


# Create database tables
Base.metadata.create_all(
    bind=engine
)


# Create FastAPI application
app = FastAPI()


# =========================
# HOME
# =========================

@app.get("/")
def home():

    return {
        "message": "E-commerce API is running"
    }


# =========================
# SIGNUP
# =========================

@app.post("/signup")
def signup(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    # Check if email already exists
    existing_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    # Create new user
    new_user = models.User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password),
        role="buyer"
    )

    # Add user to database
    db.add(new_user)

    # Save changes
    db.commit()

    # Get generated ID
    db.refresh(new_user)

    return {
        "message": "User created successfully",
        "user_id": new_user.id
    }


# =========================
# LOGIN
# =========================

@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    # Find user by email
    existing_user = db.query(models.User).filter(
        models.User.email == form_data.username
    ).first()

    # User doesn't exist
    if not existing_user:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Check password
    password_correct = verify_password(
        form_data.password,
        existing_user.password
    )

    if not password_correct:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Create JWT token
    token = create_token(
        existing_user.id,
        existing_user.role
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }
    
@app.get("/profile")
def profile(
    current_user = Depends(get_current_user)
):

    return {
        "message": "This is your profile",
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role
    }
    
@app.get("/buyer-area")
def buyer_area(
    current_user = Depends(
        require_role("buyer")
    )
):

    return {
        "message": "Welcome to the Buyer Area",
        "user": current_user.name,
        "role": current_user.role
    }
    
@app.get("/seller-area")
def seller_area(
    current_user = Depends(
        require_role("seller")
    )
):

    return {
        "message": "Welcome to the Seller Area",
        "user": current_user.name,
        "role": current_user.role
    }
    
@app.get("/admin-area")
def admin_area(
    current_user = Depends(
        require_role("admin")
    )
):

    return {
        "message": "Welcome to the Admin Area",
        "user": current_user.name,
        "role": current_user.role
    }
    
@app.put("/users/{user_id}/role")
def change_user_role(
    user_id: int,
    new_role: str,
    db: Session = Depends(get_db),
    current_user = Depends(
        require_role("admin")
    )
):

    # Find user
    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()

    # User not found
    if user is None:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Check valid role
    if new_role not in ["buyer", "seller", "admin"]:

        raise HTTPException(
            status_code=400,
            detail="Invalid role"
        )

    # Change role
    user.role = new_role

    # Save changes
    db.commit()

    # Refresh user
    db.refresh(user)

    return {
        "message": "Role updated successfully",
        "user_id": user.id,
        "new_role": user.role
    }
    
@app.get("/create-product-test")
def create_product_test(
    current_user = Depends(
        require_permission("CREATE_PRODUCT")
    )
):

    return {
        "message": "You can create products",
        "user": current_user.name,
        "role": current_user.role
    }
    
@app.post("/products")
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user = Depends(
        require_permission("CREATE_PRODUCT")
    )
):
    new_product = models.Product(
        name=product.name,
        description=product.description,
        price=product.price,
        stock=product.stock,
        seller_id=current_user.id
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return {
        "message": "Product created successfully",
        "product_id": new_product.id,
        "name": new_product.name,
        "price": new_product.price,
        "stock": new_product.stock,
        "seller_id": new_product.seller_id
    }
@app.get("/products")
def get_products(
    db: Session = Depends(get_db)
):
    products = db.query(models.Product).all()

    return products

@app.get("/products/{product_id}")
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.query(models.Product).filter(
        models.Product.id == product_id
    ).first()

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return product

@app.put("/products/{product_id}")
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(
        require_permission("UPDATE_PRODUCT")
    )
):
    product = db.query(models.Product).filter(
        models.Product.id == product_id
    ).first()

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    # Seller can update only their own product
    if (
        current_user.role == "seller"
        and product.seller_id != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="You can update only your own product"
        )

    if product_data.name is not None:
        product.name = product_data.name

    if product_data.description is not None:
        product.description = product_data.description

    if product_data.price is not None:
        product.price = product_data.price

    if product_data.stock is not None:
        product.stock = product_data.stock

    db.commit()
    db.refresh(product)

    return {
        "message": "Product updated successfully",
        "product_id": product.id,
        "name": product.name,
        "price": product.price,
        "stock": product.stock
    }
    
@app.delete("/products/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(
        require_permission("DELETE_PRODUCT")
    )
):
    product = db.query(models.Product).filter(
        models.Product.id == product_id
    ).first()

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    # Seller can delete only their own product
    if (
        current_user.role == "seller"
        and product.seller_id != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="You can delete only your own product"
        )

    db.delete(product)
    db.commit()

    return {
        "message": "Product deleted successfully"
    }
    
@app.get("/my-products")
def get_my_products(
    db: Session = Depends(get_db),
    current_user = Depends(
        require_permission("VIEW_PRODUCT")
    )
):
    products = db.query(models.Product).filter(
        models.Product.seller_id == current_user.id
    ).all()

    return products

@app.post("/cart/add")
def add_to_cart(
    item: CartItemCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Find product
    product = db.query(models.Product).filter(
        models.Product.id == item.product_id
    ).first()

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    # Check quantity
    if item.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than 0"
        )

    # Check stock
    if item.quantity > product.stock:
        raise HTTPException(
            status_code=400,
            detail="Not enough stock available"
        )

    # Find user's cart
    cart = db.query(models.Cart).filter(
        models.Cart.user_id == current_user.id
    ).first()

    # Create cart if it doesn't exist
    if cart is None:
        cart = models.Cart(
            user_id=current_user.id
        )

        db.add(cart)
        db.commit()
        db.refresh(cart)

    # Check whether product already exists in cart
    cart_item = db.query(models.CartItem).filter(
        models.CartItem.cart_id == cart.id,
        models.CartItem.product_id == item.product_id
    ).first()

    if cart_item:
        new_quantity = cart_item.quantity + item.quantity

        if new_quantity > product.stock:
            raise HTTPException(
                status_code=400,
                detail="Not enough stock available"
            )

        cart_item.quantity = new_quantity

    else:
        cart_item = models.CartItem(
            cart_id=cart.id,
            product_id=item.product_id,
            quantity=item.quantity
        )

        db.add(cart_item)

    db.commit()
    db.refresh(cart_item)

    return {
        "message": "Product added to cart",
        "product_id": product.id,
        "quantity": cart_item.quantity
    }
    
@app.get("/cart")
def get_cart(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    cart = db.query(models.Cart).filter(
        models.Cart.user_id == current_user.id
    ).first()

    if cart is None:
        return {
            "message": "Cart is empty",
            "items": [],
            "total": 0
        }

    items = []

    total = 0

    for item in cart.items:
        item_total = item.product.price * item.quantity

        items.append({
            "product_id": item.product.id,
            "product_name": item.product.name,
            "price": item.product.price,
            "quantity": item.quantity,
            "item_total": item_total
        })

        total += item_total

    return {
        "cart_id": cart.id,
        "items": items,
        "total": total
    }
    
@app.put("/cart/{product_id}")
def update_cart_item(
    product_id: int,
    quantity: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    cart = db.query(models.Cart).filter(
        models.Cart.user_id == current_user.id
    ).first()

    if cart is None:
        raise HTTPException(
            status_code=404,
            detail="Cart not found"
        )

    cart_item = db.query(models.CartItem).filter(
        models.CartItem.cart_id == cart.id,
        models.CartItem.product_id == product_id
    ).first()

    if cart_item is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found in cart"
        )

    product = db.query(models.Product).filter(
        models.Product.id == product_id
    ).first()

    if quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than 0"
        )

    if quantity > product.stock:
        raise HTTPException(
            status_code=400,
            detail="Not enough stock available"
        )

    cart_item.quantity = quantity

    db.commit()
    db.refresh(cart_item)

    return {
        "message": "Cart quantity updated",
        "product_id": product_id,
        "quantity": cart_item.quantity
    }
    
@app.delete("/cart/{product_id}")
def remove_from_cart(
    product_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    cart = db.query(models.Cart).filter(
        models.Cart.user_id == current_user.id
    ).first()

    if cart is None:
        raise HTTPException(
            status_code=404,
            detail="Cart not found"
        )

    cart_item = db.query(models.CartItem).filter(
        models.CartItem.cart_id == cart.id,
        models.CartItem.product_id == product_id
    ).first()

    if cart_item is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found in cart"
        )

    db.delete(cart_item)
    db.commit()

    return {
        "message": "Product removed from cart"
    }
    
@app.delete("/cart")
def clear_cart(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    cart = db.query(models.Cart).filter(
        models.Cart.user_id == current_user.id
    ).first()

    if cart is None:
        raise HTTPException(
            status_code=404,
            detail="Cart not found"
        )

    for item in cart.items:
        db.delete(item)

    db.commit()

    return {
        "message": "Cart cleared successfully"
    }
@app.post("/promotions")
def create_promotion(
    promotion: PromotionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(
        require_permission("MANAGE_PROMOTIONS")
    )
):
    existing_promotion = db.query(
        models.Promotion
    ).filter(
        models.Promotion.code == promotion.code.upper()
    ).first()

    if existing_promotion:
        raise HTTPException(
            status_code=400,
            detail="Promotion code already exists"
        )

    if promotion.discount_percent <= 0:
        raise HTTPException(
            status_code=400,
            detail="Discount must be greater than 0"
        )

    if promotion.discount_percent > 100:
        raise HTTPException(
            status_code=400,
            detail="Discount cannot be greater than 100%"
        )

    new_promotion = models.Promotion(
        code=promotion.code.upper(),
        discount_percent=promotion.discount_percent,
        minimum_amount=promotion.minimum_amount,
        expiry_date=promotion.expiry_date,
        active=True
    )

    db.add(new_promotion)
    db.commit()
    db.refresh(new_promotion)

    return {
        "message": "Promotion created successfully",
        "id": new_promotion.id,
        "code": new_promotion.code,
        "discount_percent": new_promotion.discount_percent,
        "minimum_amount": new_promotion.minimum_amount,
        "expiry_date": new_promotion.expiry_date,
        "active": new_promotion.active
    }
@app.get("/promotions")
def get_promotions(
    db: Session = Depends(get_db),
    current_user = Depends(
        require_role("admin")
    )
):
    promotions = db.query(
        models.Promotion
    ).all()

    return promotions
@app.post("/cart/apply-coupon")
def apply_coupon(
    coupon_data: ApplyCoupon,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Find user's cart
    cart = db.query(models.Cart).filter(
        models.Cart.user_id == current_user.id
    ).first()

    if cart is None:
        raise HTTPException(
            status_code=404,
            detail="Cart not found"
        )

    # Calculate cart total
    total = 0

    for item in cart.items:
        total += item.product.price * item.quantity

    if total <= 0:
        raise HTTPException(
            status_code=400,
            detail="Cart is empty"
        )

    # Find coupon
    promotion = db.query(
        models.Promotion
    ).filter(
        models.Promotion.code == coupon_data.code.upper()
    ).first()

    if promotion is None:
        raise HTTPException(
            status_code=404,
            detail="Invalid coupon code"
        )

    # Check active status
    if not promotion.active:
        raise HTTPException(
            status_code=400,
            detail="Coupon is not active"
        )

    # Check expiry
    if promotion.expiry_date < datetime.now():
        raise HTTPException(
            status_code=400,
            detail="Coupon has expired"
        )

    # Check minimum amount
    if total < promotion.minimum_amount:
        raise HTTPException(
            status_code=400,
            detail=f"Minimum cart amount is {promotion.minimum_amount}"
        )

    # Calculate discount
    discount_amount = (
        total * promotion.discount_percent
    ) / 100

    final_amount = total - discount_amount

    return {
        "message": "Coupon applied successfully",
        "coupon": promotion.code,
        "cart_total": total,
        "discount_percent": promotion.discount_percent,
        "discount_amount": discount_amount,
        "final_amount": final_amount
    }
    
@app.post("/orders")
def create_order(
    db: Session = Depends(get_db),
    current_user = Depends(
        require_permission("CREATE_ORDER")
    )
):
    # Find user's cart
    cart = db.query(models.Cart).filter(
        models.Cart.user_id == current_user.id
    ).first()

    if cart is None or len(cart.items) == 0:
        raise HTTPException(
            status_code=400,
            detail="Cart is empty"
        )

    total = 0

    # Check stock and calculate total
    for item in cart.items:

        if item.quantity > item.product.stock:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for {item.product.name}"
            )

        total += (
            item.product.price *
            item.quantity
        )

    # Create order
    new_order = models.Order(
        user_id=current_user.id,
        total_amount=total,
        discount_amount=0,
        final_amount=total,
        status="pending"
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    # Create order items
    for item in cart.items:

        order_item = models.OrderItem(
            order_id=new_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.product.price
        )

        db.add(order_item)

        # Reduce stock
        item.product.stock -= item.quantity

    # Remove cart items
    for item in cart.items:
        db.delete(item)

    db.commit()

    return {
        "message": "Order created successfully",
        "order_id": new_order.id,
        "total_amount": total,
        "status": new_order.status
    }
@app.get("/orders")
def get_my_orders(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    orders = db.query(models.Order).filter(
        models.Order.user_id == current_user.id
    ).all()

    return orders
@app.put("/orders/{order_id}/status")
def update_order_status(
    order_id: int,
    new_status: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Find order
    order = db.query(models.Order).filter(
        models.Order.id == order_id
    ).first()

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    # Buyer cannot change order status
    if current_user.role == "buyer":
        raise HTTPException(
            status_code=403,
            detail="Buyer cannot change order status"
        )

    # Allowed statuses
    allowed_statuses = [
        "pending",
        "confirmed",
        "shipped",
        "delivered",
        "cancelled"
    ]

    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid order status"
        )

    # Seller ownership check
    if current_user.role == "seller":

        seller_has_product = False

        for item in order.items:

            if item.product.seller_id == current_user.id:
                seller_has_product = True
                break

        if not seller_has_product:
            raise HTTPException(
                status_code=403,
                detail="You cannot manage this order"
            )

    # Delivered order cannot be changed
    if order.status == "delivered":
        raise HTTPException(
            status_code=400,
            detail="Delivered order cannot be changed"
        )

    # Cancelled order cannot be changed
    if order.status == "cancelled":
        raise HTTPException(
            status_code=400,
            detail="Cancelled order cannot be changed"
        )

    # Update status
    order.status = new_status

    db.commit()
    db.refresh(order)

    return {
        "message": "Order status updated successfully",
        "order_id": order.id,
        "status": order.status
    }
    
@app.post("/payments/{order_id}")
def create_payment(
    order_id: int,
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Find order
    order = db.query(models.Order).filter(
        models.Order.id == order_id
    ).first()

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    # Check order ownership
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You cannot make payment for this order"
        )

    # Check whether payment already exists
    existing_payment = db.query(
        models.Payment
    ).filter(
        models.Payment.order_id == order_id
    ).first()

    if existing_payment:
        raise HTTPException(
            status_code=400,
            detail="Payment already exists for this order"
        )

    # Create payment
    payment = models.Payment(
        order_id=order.id,
        amount=order.final_amount,
        status="pending",
        payment_method=payment_data.payment_method
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return {
        "message": "Payment created",
        "payment_id": payment.id,
        "order_id": order.id,
        "amount": payment.amount,
        "status": payment.status,
        "payment_method": payment.payment_method
    }
    
@app.put("/payments/{payment_id}/status")
def update_payment_status(
    payment_id: int,
    payment_data: PaymentStatusUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Find payment
    payment = db.query(models.Payment).filter(
        models.Payment.id == payment_id
    ).first()

    if payment is None:
        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )

    # Find related order
    order = db.query(models.Order).filter(
        models.Order.id == payment.order_id
    ).first()

    # Only order owner can update payment
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You cannot update this payment"
        )

    # Allowed statuses
    allowed_statuses = [
        "success",
        "failed"
    ]

    if payment_data.status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid payment status"
        )

    # Payment cannot be changed after final status
    if payment.status in ["success", "failed"]:
        raise HTTPException(
            status_code=400,
            detail="Payment has already been processed"
        )

    payment.status = payment_data.status

    if payment_data.transaction_id:
        payment.transaction_id = payment_data.transaction_id

    # If payment succeeds, confirm order
    if payment_data.status == "success":
        order.status = "confirmed"

    # If payment fails, keep order pending
    if payment_data.status == "failed":
        order.status = "pending"

    db.commit()
    db.refresh(payment)

    return {
        "message": "Payment status updated",
        "payment_id": payment.id,
        "order_id": payment.order_id,
        "amount": payment.amount,
        "status": payment.status,
        "transaction_id": payment.transaction_id,
        "order_status": order.status
    }
@app.post("/payments/{order_id}/razorpay")
def create_razorpay_payment(
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Find order
    order = db.query(models.Order).filter(
        models.Order.id == order_id
    ).first()

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    # Check order ownership
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You cannot pay for this order"
        )

    # Check existing payment
    existing_payment = db.query(
        models.Payment
    ).filter(
        models.Payment.order_id == order_id
    ).first()

    if existing_payment:
        raise HTTPException(
            status_code=400,
            detail="Payment already exists"
        )

    # Razorpay amount is in paise
    amount_in_paise = int(
        order.final_amount * 100
    )

    razorpay_order = client.order.create({
        "amount": amount_in_paise,
        "currency": "INR",
        "receipt": f"order_{order.id}"
    })

    # Save payment in our database
    payment = models.Payment(
        order_id=order.id,
        amount=order.final_amount,
        status="pending",
        payment_method="razorpay",
        razorpay_order_id=razorpay_order["id"]
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return {
        "message": "Razorpay order created",
        "payment_id": payment.id,
        "razorpay_order_id": razorpay_order["id"],
        "razorpay_key_id": RAZORPAY_KEY_ID,
        "amount": amount_in_paise,
        "currency": "INR"
    }