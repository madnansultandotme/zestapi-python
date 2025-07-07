from datetime import datetime
from typing import Dict, List, Optional, Any
from app.models import Product, Category, User, CartItem, Order, OrderItem, UserRole, OrderStatus

# In-memory databases (replace with real database in production)
users_db: Dict[int, Dict[str, Any]] = {}
products_db: Dict[int, Dict[str, Any]] = {}
categories_db: Dict[int, Dict[str, Any]] = {}
cart_items_db: Dict[int, List[Dict[str, Any]]] = {}  # user_id -> cart_items
orders_db: Dict[int, Dict[str, Any]] = {}

# Counters for IDs
user_id_counter = 1
product_id_counter = 1
category_id_counter = 1
order_id_counter = 1
cart_item_id_counter = 1
order_item_id_counter = 1

# Initialize sample data
def init_sample_data():
    global user_id_counter, product_id_counter, category_id_counter
    
    # Sample categories
    categories = [
        {"id": 1, "name": "Electronics", "description": "Electronic devices and gadgets"},
        {"id": 2, "name": "Clothing", "description": "Fashion and apparel"},
        {"id": 3, "name": "Books", "description": "Books and literature"},
        {"id": 4, "name": "Home & Garden", "description": "Home improvement and gardening"},
    ]
    
    for category in categories:
        categories_db[category["id"]] = category
    category_id_counter = 5
    
    # Sample products
    products = [
        {
            "id": 1,
            "name": "Smartphone Pro",
            "description": "Latest smartphone with advanced features",
            "price": 699.99,
            "category_id": 1,
            "stock_quantity": 50,
            "image_url": "https://example.com/images/smartphone.jpg",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": 2,
            "name": "Wireless Headphones",
            "description": "High-quality wireless headphones with noise cancellation",
            "price": 199.99,
            "category_id": 1,
            "stock_quantity": 100,
            "image_url": "https://example.com/images/headphones.jpg",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": 3,
            "name": "Cotton T-Shirt",
            "description": "Comfortable 100% cotton t-shirt",
            "price": 29.99,
            "category_id": 2,
            "stock_quantity": 200,
            "image_url": "https://example.com/images/tshirt.jpg",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": 4,
            "name": "Python Programming Book",
            "description": "Learn Python programming from scratch",
            "price": 49.99,
            "category_id": 3,
            "stock_quantity": 75,
            "image_url": "https://example.com/images/python-book.jpg",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": 5,
            "name": "Garden Tool Set",
            "description": "Complete set of essential garden tools",
            "price": 89.99,
            "category_id": 4,
            "stock_quantity": 30,
            "image_url": "https://example.com/images/garden-tools.jpg",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    for product in products:
        products_db[product["id"]] = product
    product_id_counter = 6
    
    # Sample users
    from app.auth import hash_password
    users = [
        {
            "id": 1,
            "email": "admin@example.com",
            "full_name": "Admin User",
            "password": hash_password("admin123"),
            "role": UserRole.ADMIN,
            "created_at": datetime.utcnow(),
            "is_active": True
        },
        {
            "id": 2,
            "email": "user@example.com",
            "full_name": "Regular User",
            "password": hash_password("user123"),
            "role": UserRole.USER,
            "created_at": datetime.utcnow(),
            "is_active": True
        }
    ]
    
    for user in users:
        users_db[user["id"]] = user
    user_id_counter = 3

# Helper functions
def get_product_by_id(product_id: int) -> Optional[Dict[str, Any]]:
    return products_db.get(product_id)

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    for user in users_db.values():
        if user["email"] == email:
            return user
    return None

def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    return users_db.get(user_id)

def get_category_by_id(category_id: int) -> Optional[Dict[str, Any]]:
    return categories_db.get(category_id)

def get_user_cart(user_id: int) -> List[Dict[str, Any]]:
    return cart_items_db.get(user_id, [])

def add_to_cart(user_id: int, product_id: int, quantity: int) -> Dict[str, Any]:
    global cart_item_id_counter
    
    if user_id not in cart_items_db:
        cart_items_db[user_id] = []
    
    # Check if item already in cart
    for item in cart_items_db[user_id]:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            return item
    
    # Add new item
    cart_item = {
        "id": cart_item_id_counter,
        "user_id": user_id,
        "product_id": product_id,
        "quantity": quantity
    }
    cart_items_db[user_id].append(cart_item)
    cart_item_id_counter += 1
    return cart_item

def calculate_cart_total(user_id: int) -> Dict[str, float]:
    cart_items = get_user_cart(user_id)
    total_amount = 0.0
    
    for item in cart_items:
        product = get_product_by_id(item["product_id"])
        if product:
            total_amount += product["price"] * item["quantity"]
    
    tax_rate = 0.08  # 8% tax
    tax_amount = total_amount * tax_rate
    final_amount = total_amount + tax_amount
    
    return {
        "total_amount": round(total_amount, 2),
        "tax_amount": round(tax_amount, 2),
        "final_amount": round(final_amount, 2)
    }

def create_order_from_cart(user_id: int, shipping_address: str) -> Dict[str, Any]:
    global order_id_counter, order_item_id_counter
    
    cart_items = get_user_cart(user_id)
    if not cart_items:
        raise ValueError("Cart is empty")
    
    # Calculate totals
    totals = calculate_cart_total(user_id)
    
    # Create order
    order = {
        "id": order_id_counter,
        "user_id": user_id,
        "status": OrderStatus.PENDING,
        "shipping_address": shipping_address,
        "total_amount": totals["total_amount"],
        "tax_amount": totals["tax_amount"],
        "final_amount": totals["final_amount"],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "items": []
    }
    
    # Create order items and update inventory
    for cart_item in cart_items:
        product = get_product_by_id(cart_item["product_id"])
        if not product:
            continue
            
        if product["stock_quantity"] < cart_item["quantity"]:
            raise ValueError(f"Insufficient stock for product {product['name']}")
        
        order_item = {
            "id": order_item_id_counter,
            "order_id": order_id_counter,
            "product_id": cart_item["product_id"],
            "quantity": cart_item["quantity"],
            "price": product["price"],
            "total_price": product["price"] * cart_item["quantity"]
        }
        order["items"].append(order_item)
        order_item_id_counter += 1
        
        # Update inventory
        product["stock_quantity"] -= cart_item["quantity"]
    
    orders_db[order_id_counter] = order
    order_id_counter += 1
    
    # Clear cart
    cart_items_db[user_id] = []
    
    return order

def get_user_orders(user_id: int) -> List[Dict[str, Any]]:
    return [order for order in orders_db.values() if order["user_id"] == user_id]

def search_products(
    category_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    search: Optional[str] = None,
    in_stock_only: bool = False
) -> List[Dict[str, Any]]:
    results = []
    
    for product in products_db.values():
        # Category filter
        if category_id and product["category_id"] != category_id:
            continue
            
        # Price filters
        if min_price and product["price"] < min_price:
            continue
        if max_price and product["price"] > max_price:
            continue
            
        # Stock filter
        if in_stock_only and product["stock_quantity"] <= 0:
            continue
            
        # Search filter
        if search:
            search_lower = search.lower()
            if (search_lower not in product["name"].lower() and 
                search_lower not in (product.get("description", "")).lower()):
                continue
        
        results.append(product)
    
    return results
