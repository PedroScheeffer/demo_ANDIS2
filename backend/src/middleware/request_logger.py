"""Request Logger Middleware - Gateway Offloading Pattern
Offloads request/response logging from individual services to the gateway level.
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import time
import logging
from datetime import datetime

# Configure logger
logger = logging.getLogger("gateway")
logger.setLevel(logging.INFO)

# Create console handler with formatting
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    """Middleware to log all incoming requests and outgoing responses."""
    
    async def dispatch(self, request: Request, call_next):
        # Start timing
        start_time = time.time()
        
        # Get request info
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path
        
        # Log request
        logger.info(
            f"→ {method} {path} | Client: {client_ip}"
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                f"← {method} {path} | Status: {response.status_code} | "
                f"Time: {process_time:.3f}s"
            )
            
            # Add custom headers
            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-Request-ID"] = self._get_request_id(request)
            
            return response
        
        except Exception as e:
            # Log error
            process_time = time.time() - start_time
            logger.error(
                f"✗ {method} {path} | Error: {str(e)} | "
                f"Time: {process_time:.3f}s"
            )
            raise
    
    def _get_request_id(self, request: Request) -> str:
        """Generate or retrieve request ID for tracing."""
        # Check if request ID already exists in headers
        request_id = request.headers.get("X-Request-ID")
        if request_id:
            return request_id
        
        # Generate new request ID
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
        return f"req-{timestamp}"