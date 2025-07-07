from zestapi import ZestAPI, Settings, ORJSONResponse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Settings with strong JWT secret for auth
settings = Settings()
settings.jwt_secret = "auth-example-super-secret-key-change-in-production"
settings.debug = True

# Create ZestAPI instance
app_instance = ZestAPI(settings=settings)

# In-memory user storage (use database in production)
users_db = {}
active_tokens = set()  # Track active tokens


async def root(request):
    return ORJSONResponse(
        {
            "message": "ZestAPI Authentication Example",
            "version": "1.0.0",
            "endpoints": {
                "signup": "POST /auth/signup",
                "login": "POST /auth/login",
                "profile": "GET /profile (requires auth)",
                "protected": "GET /protected (requires auth)",
            },
            "docs": "See README.md for usage examples",
        }
    )


async def health_check(request):
    return ORJSONResponse(
        {
            "status": "healthy",
            "service": "zestapi-auth-example",
            "users_count": len(users_db),
        }
    )


# Add routes
app_instance.add_route("/", root)
app_instance.add_route("/health", health_check)

# Get ASGI app for deployment
app = app_instance.app

if __name__ == "__main__":
    print("[*] Starting ZestAPI Authentication Example...")
    print("[*] API available at: http://localhost:8000")
    print("[*] Health check: http://localhost:8000/health")
    print("[*] Auth endpoints: /auth/signup, /auth/login")
    print("[*] Protected: /profile, /protected")
    app_instance.run()
