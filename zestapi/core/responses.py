from typing import Any

import orjson
from starlette.responses import JSONResponse


class ORJSONResponse(JSONResponse):
    """High-performance JSON response using orjson for serialization"""

    media_type = "application/json"

    def render(self, content: Any) -> bytes:
        return orjson.dumps(content)
