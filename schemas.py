from pydantic import BaseModel
from datetime import datetime
class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = 1
    
class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str = "buyer"


class UserLogin(BaseModel):
    email: str
    password: str


class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    price: float
    stock: int


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    stock: int | None = None
    
# -------------------------
# PROMOTION SCHEMAS
# -------------------------

class PromotionCreate(BaseModel):
    code: str
    discount_percent: float
    minimum_amount: float = 0
    expiry_date: datetime
    
class ApplyCoupon(BaseModel):
    code: str
    
class OrderCreate(BaseModel):
    pass

class PaymentCreate(BaseModel):
    payment_method: str = "online"
    
class PaymentStatusUpdate(BaseModel):
    status: str
    transaction_id: str | None = None