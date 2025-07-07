from datetime import datetime

from app.database import (
    categories_db,
    category_id_counter,
    get_category_by_id,
    get_product_by_id,
    product_id_counter,
    products_db,
    search_products,
)
from app.models import (
    CategoryCreate,
    ProductCreate,
    ProductSearchFilters,
    ProductUpdate,
)
from app.routes.auth import get_current_user
from zestapi import ORJSONResponse, route


@route("/products", methods=["GET"])
async def list_products(request):
    """List all products with optional filters"""
    try:
        # Parse query parameters
        query_params = dict(request.query_params)

        # Apply filters with proper type conversion
        category_id = None
        if query_params.get("category_id"):
            try:
                category_id = int(str(query_params.get("category_id")))
            except (ValueError, TypeError):
                category_id = None

        min_price = None
        if query_params.get("min_price"):
            try:
                min_price = float(str(query_params.get("min_price")))
            except (ValueError, TypeError):
                min_price = None

        max_price = None
        if query_params.get("max_price"):
            try:
                max_price = float(str(query_params.get("max_price")))
            except (ValueError, TypeError):
                max_price = None

        search = query_params.get("search")
        in_stock_only = query_params.get("in_stock_only", "").lower() == "true"

        products = search_products(
            category_id=category_id,
            min_price=min_price,
            max_price=max_price,
            search=search,
            in_stock_only=in_stock_only,
        )

        # Add category information to products
        for product in products:
            category = get_category_by_id(product["category_id"])
            product["category"] = category

        return ORJSONResponse(
            {
                "products": products,
                "total": len(products),
                "filters_applied": {
                    "category_id": category_id,
                    "min_price": min_price,
                    "max_price": max_price,
                    "search": search,
                    "in_stock_only": in_stock_only,
                },
            }
        )

    except Exception as e:
        return ORJSONResponse({"error": "Internal server error"}, status_code=500)


@route("/products/{product_id}", methods=["GET"])
async def get_product(request):
    """Get a specific product by ID"""
    try:
        product_id = int(request.path_params["product_id"])
        product = get_product_by_id(product_id)

        if not product:
            return ORJSONResponse({"error": "Product not found"}, status_code=404)

        # Add category information
        category = get_category_by_id(product["category_id"])
        product["category"] = category

        return ORJSONResponse(product)

    except ValueError:
        return ORJSONResponse({"error": "Invalid product ID"}, status_code=400)
    except Exception as e:
        return ORJSONResponse({"error": "Internal server error"}, status_code=500)


@route("/products", methods=["POST"])
async def create_product(request):
    """Create a new product (admin only)"""
    try:
        # Check authentication and admin role
        current_user = await get_current_user(request)
        if not current_user:
            return ORJSONResponse({"error": "Authentication required"}, status_code=401)

        if current_user.get("role") != "admin":
            return ORJSONResponse({"error": "Admin access required"}, status_code=403)

        # Parse request body
        body = await request.json()
        product_data = ProductCreate(**body)

        # Validate category exists
        if not get_category_by_id(product_data.category_id):
            return ORJSONResponse({"error": "Category not found"}, status_code=400)

        # Create new product
        global product_id_counter
        new_product = {
            "id": product_id_counter,
            "name": product_data.name,
            "description": product_data.description,
            "price": product_data.price,
            "category_id": product_data.category_id,
            "stock_quantity": product_data.stock_quantity,
            "image_url": product_data.image_url,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        products_db[product_id_counter] = new_product
        product_id_counter += 1

        # Add category information
        category = get_category_by_id(new_product["category_id"])
        new_product["category"] = category

        return ORJSONResponse(new_product, status_code=201)

    except ValueError as e:
        return ORJSONResponse({"error": str(e)}, status_code=400)
    except Exception as e:
        return ORJSONResponse({"error": "Internal server error"}, status_code=500)


@route("/products/{product_id}", methods=["PUT"])
async def update_product(request):
    """Update a product (admin only)"""
    try:
        # Check authentication and admin role
        current_user = await get_current_user(request)
        if not current_user:
            return ORJSONResponse({"error": "Authentication required"}, status_code=401)

        if current_user.get("role") != "admin":
            return ORJSONResponse({"error": "Admin access required"}, status_code=403)

        # Get product
        product_id = int(request.path_params["product_id"])
        product = get_product_by_id(product_id)

        if not product:
            return ORJSONResponse({"error": "Product not found"}, status_code=404)

        # Parse request body
        body = await request.json()
        update_data = ProductUpdate(**body)

        # Update product fields
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            if value is not None:
                if field == "category_id" and not get_category_by_id(value):
                    return ORJSONResponse(
                        {"error": "Category not found"}, status_code=400
                    )
                product[field] = value

        product["updated_at"] = datetime.utcnow()

        # Add category information
        category = get_category_by_id(product["category_id"])
        product["category"] = category

        return ORJSONResponse(product)

    except ValueError as e:
        return ORJSONResponse({"error": str(e)}, status_code=400)
    except Exception as e:
        return ORJSONResponse({"error": "Internal server error"}, status_code=500)


@route("/products/{product_id}", methods=["DELETE"])
async def delete_product(request):
    """Delete a product (admin only)"""
    try:
        # Check authentication and admin role
        current_user = await get_current_user(request)
        if not current_user:
            return ORJSONResponse({"error": "Authentication required"}, status_code=401)

        if current_user.get("role") != "admin":
            return ORJSONResponse({"error": "Admin access required"}, status_code=403)

        # Get product
        product_id = int(request.path_params["product_id"])

        if product_id not in products_db:
            return ORJSONResponse({"error": "Product not found"}, status_code=404)

        # Delete product
        del products_db[product_id]

        return ORJSONResponse({"message": "Product deleted successfully"})

    except ValueError:
        return ORJSONResponse({"error": "Invalid product ID"}, status_code=400)
    except Exception as e:
        return ORJSONResponse({"error": "Internal server error"}, status_code=500)


@route("/categories", methods=["GET"])
async def list_categories(request):
    """List all categories"""
    try:
        categories = list(categories_db.values())
        return ORJSONResponse({"categories": categories, "total": len(categories)})
    except Exception as e:
        return ORJSONResponse({"error": "Internal server error"}, status_code=500)


@route("/categories", methods=["POST"])
async def create_category(request):
    """Create a new category (admin only)"""
    try:
        # Check authentication and admin role
        current_user = await get_current_user(request)
        if not current_user:
            return ORJSONResponse({"error": "Authentication required"}, status_code=401)

        if current_user.get("role") != "admin":
            return ORJSONResponse({"error": "Admin access required"}, status_code=403)

        # Parse request body
        body = await request.json()
        category_data = CategoryCreate(**body)

        # Create new category
        global category_id_counter
        new_category = {
            "id": category_id_counter,
            "name": category_data.name,
            "description": category_data.description,
        }

        categories_db[category_id_counter] = new_category
        category_id_counter += 1

        return ORJSONResponse(new_category, status_code=201)

    except ValueError as e:
        return ORJSONResponse({"error": str(e)}, status_code=400)
    except Exception as e:
        return ORJSONResponse({"error": "Internal server error"}, status_code=500)
