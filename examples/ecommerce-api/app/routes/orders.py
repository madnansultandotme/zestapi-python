from zestapi import route, ORJSONResponse
from app.models import OrderCreate, OrderStatusUpdate
from app.database import (
    create_order_from_cart,
    get_user_orders,
    orders_db,
    get_product_by_id,
)
from app.routes.auth import get_current_user


@route("/orders", methods=["GET"])
async def get_orders(request):
    """Get user's order history"""
    try:
        # Check authentication
        current_user = await get_current_user(request)
        if not current_user:
            return ORJSONResponse({"error": "Authentication required"}, status_code=401)

        user_id = current_user["id"]
        orders = get_user_orders(user_id)

        # Add product details to order items
        enriched_orders = []
        for order in orders:
            enriched_items = []
            for item in order["items"]:
                product = get_product_by_id(item["product_id"])
                if product:
                    enriched_item = {**item, "product": product}
                    enriched_items.append(enriched_item)

            enriched_order = {**order, "items": enriched_items}
            enriched_orders.append(enriched_order)

        return ORJSONResponse(
            {"orders": enriched_orders, "total": len(enriched_orders)}
        )

    except Exception as e:
        return ORJSONResponse({"error": "Internal server error"}, status_code=500)


@route("/orders/{order_id}", methods=["GET"])
async def get_order(request):
    """Get specific order details"""
    try:
        # Check authentication
        current_user = await get_current_user(request)
        if not current_user:
            return ORJSONResponse({"error": "Authentication required"}, status_code=401)

        # Get order ID
        order_id = int(request.path_params["order_id"])

        # Find order
        order = orders_db.get(order_id)
        if not order:
            return ORJSONResponse({"error": "Order not found"}, status_code=404)

        # Check if user owns the order or is admin
        user_id = current_user["id"]
        if order["user_id"] != user_id and current_user.get("role") != "admin":
            return ORJSONResponse({"error": "Access denied"}, status_code=403)

        # Add product details to order items
        enriched_items = []
        for item in order["items"]:
            product = get_product_by_id(item["product_id"])
            if product:
                enriched_item = {**item, "product": product}
                enriched_items.append(enriched_item)

        enriched_order = {**order, "items": enriched_items}

        return ORJSONResponse(enriched_order)

    except ValueError:
        return ORJSONResponse({"error": "Invalid order ID"}, status_code=400)
    except Exception as e:
        return ORJSONResponse({"error": "Internal server error"}, status_code=500)


@route("/orders", methods=["POST"])
async def create_order(request):
    """Create order from cart"""
    try:
        # Check authentication
        current_user = await get_current_user(request)
        if not current_user:
            return ORJSONResponse({"error": "Authentication required"}, status_code=401)

        # Parse request body
        body = await request.json()
        order_data = OrderCreate(**body)

        user_id = current_user["id"]

        try:
            # Create order from cart
            order = create_order_from_cart(user_id, order_data.shipping_address)

            # Add product details to order items
            enriched_items = []
            for item in order["items"]:
                product = get_product_by_id(item["product_id"])
                if product:
                    enriched_item = {**item, "product": product}
                    enriched_items.append(enriched_item)

            enriched_order = {**order, "items": enriched_items}

            return ORJSONResponse(enriched_order, status_code=201)

        except ValueError as e:
            return ORJSONResponse({"error": str(e)}, status_code=400)

    except ValueError as e:
        return ORJSONResponse({"error": str(e)}, status_code=400)
    except Exception as e:
        return ORJSONResponse({"error": "Internal server error"}, status_code=500)


@route("/orders/{order_id}/status", methods=["PUT"])
async def update_order_status(request):
    """Update order status (admin only)"""
    try:
        # Check authentication and admin role
        current_user = await get_current_user(request)
        if not current_user:
            return ORJSONResponse({"error": "Authentication required"}, status_code=401)

        if current_user.get("role") != "admin":
            return ORJSONResponse({"error": "Admin access required"}, status_code=403)

        # Get order ID
        order_id = int(request.path_params["order_id"])

        # Find order
        order = orders_db.get(order_id)
        if not order:
            return ORJSONResponse({"error": "Order not found"}, status_code=404)

        # Parse request body
        body = await request.json()
        status_data = OrderStatusUpdate(**body)

        # Update order status
        from datetime import datetime

        order["status"] = status_data.status
        order["updated_at"] = datetime.utcnow()

        # Add product details to order items
        enriched_items = []
        for item in order["items"]:
            product = get_product_by_id(item["product_id"])
            if product:
                enriched_item = {**item, "product": product}
                enriched_items.append(enriched_item)

        enriched_order = {**order, "items": enriched_items}

        return ORJSONResponse(enriched_order)

    except ValueError as e:
        return ORJSONResponse({"error": str(e)}, status_code=400)
    except Exception as e:
        return ORJSONResponse({"error": "Internal server error"}, status_code=500)
