from zestapi import route, ORJSONResponse
from app.models import CartItemCreate, CartItemUpdate
from app.database import (
    get_product_by_id, get_user_cart, add_to_cart, 
    calculate_cart_total, cart_items_db
)
from app.routes.auth import get_current_user

@route("/cart", methods=["GET"])
async def get_cart(request):
    """Get user's shopping cart"""
    try:
        # Check authentication
        current_user = await get_current_user(request)
        if not current_user:
            return ORJSONResponse({"error": "Authentication required"}, status_code=401)
        
        user_id = current_user["id"]
        cart_items = get_user_cart(user_id)
        
        # Add product details to cart items
        enriched_items = []
        for item in cart_items:
            product = get_product_by_id(item["product_id"])
            if product:
                enriched_item = {
                    **item,
                    "product": product,
                    "total_price": product["price"] * item["quantity"]
                }
                enriched_items.append(enriched_item)
        
        # Calculate totals
        totals = calculate_cart_total(user_id)
        
        return ORJSONResponse({
            "items": enriched_items,
            "total_items": len(enriched_items),
            **totals
        })
        
    except Exception as e:
        return ORJSONResponse({"error": "Internal server error"}, status_code=500)

@route("/cart/items", methods=["POST"])
async def add_cart_item(request):
    """Add item to cart"""
    try:
        # Check authentication
        current_user = await get_current_user(request)
        if not current_user:
            return ORJSONResponse({"error": "Authentication required"}, status_code=401)
        
        # Parse request body
        body = await request.json()
        item_data = CartItemCreate(**body)
        
        # Validate product exists
        product = get_product_by_id(item_data.product_id)
        if not product:
            return ORJSONResponse({"error": "Product not found"}, status_code=404)
        
        # Check stock availability
        if product["stock_quantity"] < item_data.quantity:
            return ORJSONResponse({
                "error": f"Insufficient stock. Available: {product['stock_quantity']}"
            }, status_code=400)
        
        # Add to cart
        user_id = current_user["id"]
        cart_item = add_to_cart(user_id, item_data.product_id, item_data.quantity)
        
        # Return enriched cart item
        enriched_item = {
            **cart_item,
            "product": product,
            "total_price": product["price"] * cart_item["quantity"]
        }
        
        return ORJSONResponse(enriched_item, status_code=201)
        
    except ValueError as e:
        return ORJSONResponse({"error": str(e)}, status_code=400)
    except Exception as e:
        return ORJSONResponse({"error": "Internal server error"}, status_code=500)

@route("/cart/items/{item_id}", methods=["PUT"])
async def update_cart_item(request):
    """Update cart item quantity"""
    try:
        # Check authentication
        current_user = await get_current_user(request)
        if not current_user:
            return ORJSONResponse({"error": "Authentication required"}, status_code=401)
        
        # Get item ID
        item_id = int(request.path_params["item_id"])
        user_id = current_user["id"]
        
        # Find cart item
        cart_items = get_user_cart(user_id)
        cart_item = None
        for item in cart_items:
            if item["id"] == item_id:
                cart_item = item
                break
        
        if not cart_item:
            return ORJSONResponse({"error": "Cart item not found"}, status_code=404)
        
        # Parse request body
        body = await request.json()
        update_data = CartItemUpdate(**body)
        
        # Check stock availability
        product = get_product_by_id(cart_item["product_id"])
        if not product:
            return ORJSONResponse({"error": "Product not found"}, status_code=404)
        
        if product["stock_quantity"] < update_data.quantity:
            return ORJSONResponse({
                "error": f"Insufficient stock. Available: {product['stock_quantity']}"
            }, status_code=400)
        
        # Update quantity
        cart_item["quantity"] = update_data.quantity
        
        # Return enriched cart item
        enriched_item = {
            **cart_item,
            "product": product,
            "total_price": product["price"] * cart_item["quantity"]
        }
        
        return ORJSONResponse(enriched_item)
        
    except ValueError as e:
        return ORJSONResponse({"error": str(e)}, status_code=400)
    except Exception as e:
        return ORJSONResponse({"error": "Internal server error"}, status_code=500)

@route("/cart/items/{item_id}", methods=["DELETE"])
async def remove_cart_item(request):
    """Remove item from cart"""
    try:
        # Check authentication
        current_user = await get_current_user(request)
        if not current_user:
            return ORJSONResponse({"error": "Authentication required"}, status_code=401)
        
        # Get item ID
        item_id = int(request.path_params["item_id"])
        user_id = current_user["id"]
        
        # Find and remove cart item
        cart_items = get_user_cart(user_id)
        for i, item in enumerate(cart_items):
            if item["id"] == item_id:
                removed_item = cart_items.pop(i)
                return ORJSONResponse({"message": "Item removed from cart"})
        
        return ORJSONResponse({"error": "Cart item not found"}, status_code=404)
        
    except ValueError:
        return ORJSONResponse({"error": "Invalid item ID"}, status_code=400)
    except Exception as e:
        return ORJSONResponse({"error": "Internal server error"}, status_code=500)

@route("/cart", methods=["DELETE"])
async def clear_cart(request):
    """Clear entire cart"""
    try:
        # Check authentication
        current_user = await get_current_user(request)
        if not current_user:
            return ORJSONResponse({"error": "Authentication required"}, status_code=401)
        
        user_id = current_user["id"]
        cart_items_db[user_id] = []
        
        return ORJSONResponse({"message": "Cart cleared"})
        
    except Exception as e:
        return ORJSONResponse({"error": "Internal server error"}, status_code=500)
