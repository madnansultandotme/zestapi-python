from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr, field_validator

from zestapi import ORJSONResponse, create_access_token, route


# User models
class UserSignup(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        if not v.isalnum():
            raise ValueError("Username must be alphanumeric")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class UserLogin(BaseModel):
    username: str
    password: str


class UserProfile(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    created_at: datetime


# Global storage (use database in production)
users_db = {}
active_tokens = set()


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def create_jwt_token(user_data: dict) -> str:
    """Create JWT token for user"""
    payload = {
        "sub": user_data["username"],
        "email": user_data["email"],
        "exp": datetime.utcnow() + timedelta(hours=24),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(
        payload, "auth-example-super-secret-key-change-in-production", algorithm="HS256"
    )


def verify_jwt_token(token: str) -> Optional[dict]:
    """Verify and decode JWT token"""
    try:
        if token not in active_tokens:
            return None
        payload = jwt.decode(
            token,
            "auth-example-super-secret-key-change-in-production",
            algorithms=["HS256"],
        )
        return payload
    except JWTError:
        return None


@route("/auth/signup", methods=["POST"])
async def signup(request):
    """User registration endpoint"""
    try:
        data = await request.json()
        user_data = UserSignup(**data)

        # Check if user already exists
        if user_data.username in users_db:
            return ORJSONResponse({"error": "Username already exists"}, status_code=400)

        # Check if email already exists
        for user in users_db.values():
            if user["email"] == user_data.email:
                return ORJSONResponse(
                    {"error": "Email already registered"}, status_code=400
                )

        # Hash password and create user
        hashed_password = hash_password(user_data.password)
        new_user = {
            "username": user_data.username,
            "email": user_data.email,
            "full_name": user_data.full_name,
            "password_hash": hashed_password,
            "created_at": datetime.utcnow(),
        }
        users_db[user_data.username] = new_user

        # Create JWT token
        token = create_jwt_token(new_user)
        active_tokens.add(token)

        return ORJSONResponse(
            {
                "message": "User created successfully",
                "user": {
                    "username": user_data.username,
                    "email": user_data.email,
                    "full_name": user_data.full_name,
                },
                "access_token": token,
                "token_type": "bearer",
            },
            status_code=201,
        )

    except ValueError as e:
        return ORJSONResponse(
            {"error": "Validation error", "details": str(e)}, status_code=400
        )


@route("/auth/login", methods=["POST"])
async def login(request):
    """User login endpoint"""
    try:
        data = await request.json()
        login_data = UserLogin(**data)

        # Check if user exists
        if login_data.username not in users_db:
            return ORJSONResponse({"error": "Invalid credentials"}, status_code=401)

        user = users_db[login_data.username]

        # Verify password
        if not verify_password(login_data.password, user["password_hash"]):
            return ORJSONResponse({"error": "Invalid credentials"}, status_code=401)

        # Create JWT token
        token = create_jwt_token(user)
        active_tokens.add(token)

        return ORJSONResponse(
            {
                "message": "Login successful",
                "user": {
                    "username": user["username"],
                    "email": user["email"],
                    "full_name": user["full_name"],
                },
                "access_token": token,
                "token_type": "bearer",
            }
        )

    except ValueError as e:
        return ORJSONResponse(
            {"error": "Validation error", "details": str(e)}, status_code=400
        )


@route("/auth/logout", methods=["POST"])
async def logout(request):
    """User logout endpoint"""
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return ORJSONResponse({"error": "No token provided"}, status_code=401)

    token = auth_header.split(" ")[1]
    active_tokens.discard(token)

    return ORJSONResponse({"message": "Logged out successfully"})


@route("/profile", methods=["GET"])
async def get_profile(request):
    """Get user profile (protected route)"""
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return ORJSONResponse({"error": "Authentication required"}, status_code=401)

    token = auth_header.split(" ")[1]
    payload = verify_jwt_token(token)

    if not payload:
        return ORJSONResponse({"error": "Invalid or expired token"}, status_code=401)

    username = payload["sub"]
    if username not in users_db:
        return ORJSONResponse({"error": "User not found"}, status_code=404)

    user = users_db[username]
    return ORJSONResponse(
        {
            "profile": {
                "username": user["username"],
                "email": user["email"],
                "full_name": user["full_name"],
                "created_at": user["created_at"].isoformat(),
            }
        }
    )


@route("/protected", methods=["GET"])
async def protected_route(request):
    """Example protected route"""
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return ORJSONResponse({"error": "Authentication required"}, status_code=401)

    token = auth_header.split(" ")[1]
    payload = verify_jwt_token(token)

    if not payload:
        return ORJSONResponse({"error": "Invalid or expired token"}, status_code=401)

    return ORJSONResponse(
        {
            "message": "Access granted to protected resource",
            "user": payload["sub"],
            "timestamp": datetime.utcnow().isoformat(),
        }
    )
