from typing import Optional

from pydantic import BaseModel, field_validator

from zestapi import ORJSONResponse, route


# Pydantic models for validation
class UserCreate(BaseModel):
    name: str
    email: str
    age: int

    @field_validator("age")
    @classmethod
    def validate_age(cls, v):
        if v < 0 or v > 150:
            raise ValueError("Age must be between 0 and 150")
        return v

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        if "@" not in v:
            raise ValueError("Invalid email format")
        return v


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None

    @field_validator("age")
    @classmethod
    def validate_age(cls, v):
        if v is not None and (v < 0 or v > 150):
            raise ValueError("Age must be between 0 and 150")
        return v


# In-memory storage (use database in production)
users_db = {
    1: {"id": 1, "name": "Alice Smith", "email": "alice@example.com", "age": 28},
    2: {"id": 2, "name": "Bob Johnson", "email": "bob@example.com", "age": 35},
}
user_id_counter = 3


@route("/users", methods=["GET"])
async def list_users(request):
    """Get all users"""
    return ORJSONResponse({"users": list(users_db.values()), "total": len(users_db)})


@route("/users/{user_id}", methods=["GET"])
async def get_user(request):
    """Get user by ID"""
    user_id = int(request.path_params["user_id"])

    if user_id not in users_db:
        return ORJSONResponse({"error": "User not found"}, status_code=404)

    return ORJSONResponse({"user": users_db[user_id]})


@route("/users", methods=["POST"])
async def create_user(request):
    """Create new user"""
    global user_id_counter

    try:
        data = await request.json()
        user_data = UserCreate(**data)

        # Create new user
        new_user = {"id": user_id_counter, **user_data.model_dump()}
        users_db[user_id_counter] = new_user
        user_id_counter += 1

        return ORJSONResponse(
            {"user": new_user, "message": "User created successfully"}, status_code=201
        )

    except ValueError as e:
        return ORJSONResponse(
            {"error": "Validation error", "details": str(e)}, status_code=400
        )


@route("/users/{user_id}", methods=["PUT"])
async def update_user(request):
    """Update user"""
    user_id = int(request.path_params["user_id"])

    if user_id not in users_db:
        return ORJSONResponse({"error": "User not found"}, status_code=404)

    try:
        data = await request.json()
        user_update = UserUpdate(**data)

        # Update user
        current_user = users_db[user_id]
        update_data = user_update.model_dump(exclude_unset=True)
        current_user.update(update_data)

        return ORJSONResponse(
            {"user": current_user, "message": "User updated successfully"}
        )

    except ValueError as e:
        return ORJSONResponse(
            {"error": "Validation error", "details": str(e)}, status_code=400
        )


@route("/users/{user_id}", methods=["DELETE"])
async def delete_user(request):
    """Delete user"""
    user_id = int(request.path_params["user_id"])

    if user_id not in users_db:
        return ORJSONResponse({"error": "User not found"}, status_code=404)

    deleted_user = users_db.pop(user_id)

    return ORJSONResponse(
        {"message": "User deleted successfully", "user": deleted_user}
    )
