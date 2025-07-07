from pydantic import BaseModel, field_validator
from typing import Optional, List, Union
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

class OrderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

# User Models
class UserBase(BaseModel):
    email: str
    full_name: str
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if '@' not in v or '.' not in v.split('@')[1]:
            raise ValueError('Invalid email format')
        return v.lower()

class UserCreate(UserBase):
    password: str
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v

class UserLogin(BaseModel):
    email: str
    password: str

class User(UserBase):
    id: int
    role: UserRole = UserRole.USER
    created_at: datetime
    is_active: bool = True

# Product Models
class Category(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category_id: int
    stock_quantity: int
    image_url: Optional[str] = None
    
    @field_validator('price')
    @classmethod
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Price must be greater than 0')
        return v
    
    @field_validator('stock_quantity')
    @classmethod
    def validate_stock(cls, v):
        if v < 0:
            raise ValueError('Stock quantity cannot be negative')
        return v

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category_id: Optional[int] = None
    stock_quantity: Optional[int] = None
    image_url: Optional[str] = None
    
    @field_validator('price')
    @classmethod
    def validate_price(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Price must be greater than 0')
        return v

class Product(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

# Cart Models
class CartItemBase(BaseModel):
    product_id: int
    quantity: int
    
    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be greater than 0')
        return v

class CartItemCreate(CartItemBase):
    pass

class CartItemUpdate(BaseModel):
    quantity: int
    
    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be greater than 0')
        return v

class CartItem(CartItemBase):
    id: int
    user_id: int
    product: Product
    total_price: float

class Cart(BaseModel):
    items: List[CartItem]
    total_amount: float
    tax_amount: float
    final_amount: float

# Order Models
class OrderItemBase(BaseModel):
    product_id: int
    quantity: int
    price: float  # Price at time of order

class OrderItem(OrderItemBase):
    id: int
    order_id: int
    product: Product
    total_price: float

class OrderBase(BaseModel):
    shipping_address: str
    
class OrderCreate(OrderBase):
    pass

class Order(OrderBase):
    id: int
    user_id: int
    status: OrderStatus
    items: List[OrderItem]
    total_amount: float
    tax_amount: float
    final_amount: float
    created_at: datetime
    updated_at: datetime

class OrderStatusUpdate(BaseModel):
    status: OrderStatus

# Response Models
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User

class Message(BaseModel):
    message: str

class ProductSearchFilters(BaseModel):
    category_id: Optional[int] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    search: Optional[str] = None
    in_stock_only: bool = False
