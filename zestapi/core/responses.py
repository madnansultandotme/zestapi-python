import orjson
from starlette.responses import JSONResponse, HTMLResponse

class ORJSONResponse(JSONResponse):
    """High-performance JSON response using orjson for serialization"""
    media_type = "application/json"

    def render(self, content) -> bytes:
        return orjson.dumps(content)
