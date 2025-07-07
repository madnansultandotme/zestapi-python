from starlette.responses import JSONResponse
from app.routing import route


class ExamplePlugin:
    def __init__(self, app):
        self.app = app

    def register(self):
        @self.app.route("/plugin-test", methods=["GET"])
        async def plugin_test_route(request):
            return JSONResponse({"message": "Hello from example plugin!"})

        print("ExamplePlugin registered.")
