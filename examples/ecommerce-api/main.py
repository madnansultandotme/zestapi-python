from zestapi import ZestAPI, ORJSONResponse
from app.database import init_sample_data

# Create ZestAPI instance
app_instance = ZestAPI()

# Initialize sample data
init_sample_data()


# Root endpoint
async def root(request):
    return ORJSONResponse(
        {
            "message": "Welcome to ZestAPI E-commerce API",
            "version": "1.0.0",
            "docs": "/docs",
            "endpoints": {
                "auth": {
                    "register": "POST /auth/register",
                    "login": "POST /auth/login",
                    "logout": "POST /auth/logout",
                },
                "products": {
                    "list": "GET /products",
                    "get": "GET /products/{id}",
                    "create": "POST /products (admin)",
                    "update": "PUT /products/{id} (admin)",
                    "delete": "DELETE /products/{id} (admin)",
                },
                "categories": {
                    "list": "GET /categories",
                    "create": "POST /categories (admin)",
                },
                "cart": {
                    "get": "GET /cart",
                    "add_item": "POST /cart/items",
                    "update_item": "PUT /cart/items/{id}",
                    "remove_item": "DELETE /cart/items/{id}",
                    "clear": "DELETE /cart",
                },
                "orders": {
                    "list": "GET /orders",
                    "get": "GET /orders/{id}",
                    "create": "POST /orders",
                    "update_status": "PUT /orders/{id}/status (admin)",
                },
            },
            "sample_users": {
                "admin": {
                    "email": "admin@example.com",
                    "password": "admin123",
                    "role": "admin",
                },
                "user": {
                    "email": "user@example.com",
                    "password": "user123",
                    "role": "user",
                },
            },
        }
    )


async def health_check(request):
    return ORJSONResponse({"status": "healthy", "service": "zestapi-ecommerce-api"})


# Add manual routes
app_instance.add_route("/", root)
app_instance.add_route("/health", health_check)

if __name__ == "__main__":
    print("[*] Starting ZestAPI E-commerce API...")
    print("[*] API available at: http://localhost:8000")
    print("[*] Health check: http://localhost:8000/health")
    print("[*] Sample users: admin@example.com/admin123, user@example.com/user123")
    app_instance.run()
