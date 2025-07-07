from zestapi import route, ORJSONResponse
from app.models import UserCreate, UserLogin, Token, Message
from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_user_from_token,
)
from app.database import users_db, user_id_counter, get_user_by_email
from datetime import datetime


@route("/auth/register", methods=["POST"])
async def register(request):
    """Register a new user"""
    try:
        # Parse request body
        body = await request.json()
        user_data = UserCreate(**body)

        # Check if user already exists
        if get_user_by_email(user_data.email):
            return ORJSONResponse(
                {"error": "User with this email already exists"}, status_code=400
            )

        # Create new user
        global user_id_counter
        hashed_password = hash_password(user_data.password)

        new_user = {
            "id": user_id_counter,
            "email": user_data.email,
            "full_name": user_data.full_name,
            "password": hashed_password,
            "role": "user",
            "created_at": datetime.utcnow(),
            "is_active": True,
        }

        users_db[user_id_counter] = new_user
        user_id_counter += 1

        # Create access token
        token_data = {"sub": str(new_user["id"]), "email": new_user["email"]}
        access_token = create_access_token(token_data)

        # Remove password from response
        user_response = {k: v for k, v in new_user.items() if k != "password"}

        return ORJSONResponse(
            {
                "access_token": access_token,
                "token_type": "bearer",
                "user": user_response,
            }
        )

    except ValueError as e:
        return ORJSONResponse({"error": str(e)}, status_code=400)
    except Exception as e:
        return ORJSONResponse({"error": "Internal server error"}, status_code=500)


@route("/auth/login", methods=["POST"])
async def login(request):
    """Login user"""
    try:
        # Parse request body
        body = await request.json()
        login_data = UserLogin(**body)

        # Find user
        user = get_user_by_email(login_data.email)
        if not user:
            return ORJSONResponse(
                {"error": "Invalid email or password"}, status_code=401
            )

        # Verify password
        if not verify_password(login_data.password, user["password"]):
            return ORJSONResponse(
                {"error": "Invalid email or password"}, status_code=401
            )

        # Check if user is active
        if not user.get("is_active", True):
            return ORJSONResponse({"error": "Account is disabled"}, status_code=401)

        # Create access token
        token_data = {"sub": str(user["id"]), "email": user["email"]}
        access_token = create_access_token(token_data)

        # Remove password from response
        user_response = {k: v for k, v in user.items() if k != "password"}

        return ORJSONResponse(
            {
                "access_token": access_token,
                "token_type": "bearer",
                "user": user_response,
            }
        )

    except ValueError as e:
        return ORJSONResponse({"error": str(e)}, status_code=400)
    except Exception as e:
        return ORJSONResponse({"error": "Internal server error"}, status_code=500)


@route("/auth/logout", methods=["POST"])
async def logout(request):
    """Logout user (client should remove token)"""
    return ORJSONResponse({"message": "Successfully logged out"})


# Helper function to get current user from request
async def get_current_user(request):
    """Extract user from Authorization header"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ")[1]
    return get_user_from_token(token, users_db)
