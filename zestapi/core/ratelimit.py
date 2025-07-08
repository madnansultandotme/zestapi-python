import re
import time
from collections import defaultdict
from typing import Any, Dict, Tuple

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: Any, rate_limit: str = "100/minute") -> None:
        super().__init__(app)
        self.rate_limit = rate_limit
        self.requests: Dict[str, list] = defaultdict(list)
        self.limit, self.window = self._parse_rate_limit(rate_limit)

    def _parse_rate_limit(self, rate_limit: str) -> Tuple[int, int]:
        """Parse rate limit string like '100/minute' into
        (limit, window_seconds)"""
        match = re.match(r"(\d+)/(second|minute|hour|day)", rate_limit.lower())
        if not match:
            raise ValueError(f"Invalid rate limit format: {rate_limit}")

        limit = int(match.group(1))
        unit = match.group(2)

        window_seconds = {
            "second": 1,
            "minute": 60,
            "hour": 3600,
            "day": 86400,
        }[unit]

        return limit, window_seconds

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _is_rate_limited(self, client_ip: str) -> bool:
        """Check if client is rate limited"""
        current_time = time.time()

        # Clean old requests outside the window
        self.requests[client_ip] = [
            req_time
            for req_time in self.requests[client_ip]
            if current_time - req_time < self.window
        ]

        # Check if limit exceeded
        if len(self.requests[client_ip]) >= self.limit:
            return True

        # Add current request
        self.requests[client_ip].append(current_time)
        return False

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        client_ip = self._get_client_ip(request)

        if self._is_rate_limited(client_ip):
            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "code": 429,
                        "message": "Rate limit exceeded",
                        "type": "RateLimitExceeded",
                    }
                },
                headers={
                    "X-RateLimit-Limit": str(self.limit),
                    "X-RateLimit-Window": str(self.window),
                    "Retry-After": str(self.window),
                },
            )

        response = await call_next(request)

        # Add rate limit headers to response
        remaining = max(0, self.limit - len(self.requests[client_ip]))
        response.headers["X-RateLimit-Limit"] = str(self.limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Window"] = str(self.window)

        return response  # type: ignore
