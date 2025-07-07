from starlette.responses import JSONResponse
from starlette.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import logging
import traceback
import time
import uuid
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Comprehensive error handling middleware for production use
    """
    
    def __init__(self, app, debug: bool = False):
        super().__init__(app)
        self.debug = debug
        
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()
        request_id = str(uuid.uuid4())[:8]
        
        try:
            # Add request ID to request state
            request.state.request_id = request_id
            
            response = await call_next(request)
            
            # Add performance headers
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = f"{process_time:.4f}"
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except HTTPException as exc:
            # Handle HTTP exceptions (4xx, 5xx)
            error_response = self._create_error_response(
                status_code=exc.status_code,
                message=exc.detail,
                error_type="HTTPException",
                request_id=request_id,
                request=request
            )
            logger.warning(f"HTTP Exception {exc.status_code}: {exc.detail} (Request: {request_id})")
            return error_response
            
        except ValueError as exc:
            # Handle validation errors (400)
            error_response = self._create_error_response(
                status_code=400,
                message=str(exc),
                error_type="ValidationError",
                request_id=request_id,
                request=request
            )
            logger.warning(f"Validation Error: {exc} (Request: {request_id})")
            return error_response
            
        except PermissionError as exc:
            # Handle permission errors (403)
            error_response = self._create_error_response(
                status_code=403,
                message="Access forbidden",
                error_type="PermissionError",
                request_id=request_id,
                request=request
            )
            logger.warning(f"Permission Error: {exc} (Request: {request_id})")
            return error_response
            
        except FileNotFoundError as exc:
            # Handle file not found errors (404)
            error_response = self._create_error_response(
                status_code=404,
                message="Resource not found",
                error_type="NotFoundError",
                request_id=request_id,
                request=request
            )
            logger.warning(f"Not Found Error: {exc} (Request: {request_id})")
            return error_response
            
        except Exception as exc:
            # Handle all other exceptions (500)
            error_response = self._create_error_response(
                status_code=500,
                message="Internal server error",
                error_type="InternalServerError",
                request_id=request_id,
                request=request,
                exception=exc
            )
            
            # Log the full exception with traceback
            logger.error(
                f"Unhandled exception in request {request_id}: {exc}",
                exc_info=True,
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "url": str(request.url),
                    "user_agent": request.headers.get("user-agent"),
                    "client_ip": request.client.host if request.client else None,
                }
            )
            return error_response
            
    def _create_error_response(
        self,
        status_code: int,
        message: str,
        error_type: str,
        request_id: str,
        request: Request,
        exception: Optional[Exception] = None
    ) -> JSONResponse:
        """Create a standardized error response"""
        
        error_data: Dict[str, Any] = {
            "error": {
                "code": status_code,
                "message": message,
                "type": error_type,
                "request_id": request_id,
                "timestamp": time.time(),
            }
        }
        
        # Add debug information if in debug mode
        if self.debug and exception:
            error_data["error"]["debug"] = {
                "exception": str(exception),
                "traceback": traceback.format_exc(),
                "path": str(request.url.path),
                "method": request.method,
            }
            
        # Add helpful hints for common errors
        if status_code == 400:
            error_data["error"]["hint"] = "Check your request parameters and data format"
        elif status_code == 401:
            error_data["error"]["hint"] = "Authentication required or invalid credentials"
        elif status_code == 403:
            error_data["error"]["hint"] = "You don't have permission to access this resource"
        elif status_code == 404:
            error_data["error"]["hint"] = "The requested resource was not found"
        elif status_code == 429:
            error_data["error"]["hint"] = "Too many requests, please try again later"
        elif status_code >= 500:
            error_data["error"]["hint"] = "Server error, please try again or contact support"
            
        return JSONResponse(
            status_code=status_code,
            content=error_data,
            headers={
                "X-Request-ID": request_id,
                "Content-Type": "application/json"
            }
        )

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Enhanced request logging middleware
    """
    
    def __init__(self, app, log_body: bool = False, max_body_size: int = 1024):
        super().__init__(app)
        self.log_body = log_body
        self.max_body_size = max_body_size
        
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()
        
        # Get request ID from state (set by ErrorHandlingMiddleware)
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        # Log request details
        log_data = {
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "user_agent": request.headers.get("user-agent"),
            "client_ip": request.client.host if request.client else None,
            "content_length": request.headers.get("content-length"),
        }
        
        # Optionally log request body (be careful with sensitive data)
        if self.log_body and request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if len(body) <= self.max_body_size:
                    log_data["body_preview"] = body.decode("utf-8")[:self.max_body_size]
                else:
                    log_data["body_size"] = len(body)
            except Exception:
                log_data["body"] = "Could not read body"
        
        logger.info(f"Request started", extra=log_data)
        
        try:
            response = await call_next(request)
        except Exception as e:
            # Log the exception before re-raising
            logger.error(f"Request failed: {e}", extra=log_data, exc_info=True)
            raise
        
        # Log response details
        process_time = time.time() - start_time
        response_log_data = {
            **log_data,
            "status_code": response.status_code,
            "process_time": f"{process_time:.4f}s",
            "response_size": response.headers.get("content-length"),
        }
        
        if response.status_code >= 400:
            logger.warning(f"Request completed with error", extra=response_log_data)
        else:
            logger.info(f"Request completed successfully", extra=response_log_data)
        
        return response
