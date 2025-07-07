from zestapi import ZestAPI, ORJSONResponse

# Create ZestAPI instance
app_instance = ZestAPI()

# In-memory storage for demo
users_db = {}
user_id_counter = 1

# Manual route registration (alternative to file-based discovery)
async def root(request):
    return ORJSONResponse({
        "message": "Welcome to ZestAPI Basic Example",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "users": "/users",
            "health": "/health"
        }
    })

async def health_check(request):
    return ORJSONResponse({
        "status": "healthy",
        "service": "zestapi-basic-example"
    })

# Add routes manually
app_instance.add_route("/", root)
app_instance.add_route("/health", health_check)

# Get ASGI app for deployment
app = app_instance.app

if __name__ == "__main__":
    print("[*] Starting ZestAPI Basic Example...")
    print("[*] API available at: http://localhost:8000")
    print("[*] Health check: http://localhost:8000/health")
    print("[*] Users API: http://localhost:8000/users")
    app_instance.run()
