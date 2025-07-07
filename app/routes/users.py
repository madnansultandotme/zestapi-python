from app.routing import route
from starlette.responses import JSONResponse


@route("/users", methods=["GET"])
async def list_users(request):
    return JSONResponse({"users": ["Alice", "Bob"]})


@route("/users/{user_id}", methods=["GET"])
async def get_user(request):
    user_id = request.path_params["user_id"]
    return JSONResponse({"user_id": user_id, "name": f"User {user_id}"})
