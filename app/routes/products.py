from app.routing import route
from starlette.responses import JSONResponse


@route("/products", methods=["GET"])
async def products_index(request):
    return JSONResponse({"products": "Hello from products route!"})
