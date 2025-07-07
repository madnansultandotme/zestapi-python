from app.routing import route
from starlette.responses import JSONResponse


@route("/posts", methods=["GET"])
async def posts_index(request):
    return JSONResponse({"posts": "Hello from posts route!"})
