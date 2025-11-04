"""Rate Limiter Middleware - Gateway Offloading Pattern
Offloads rate limiting from individual services to the gateway level.
Uses Redis for distributed rate limiting.
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from datetime import datetime, timedelta
from config.redis_client import get_redis_client
import time


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Middleware to implement rate limiting using sliding window algorithm."""
    
    def __init__(
        self, 
        app, 
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/api/health"]:
            return await call_next(request)
        
        # Get client identifier (IP or user ID if authenticated)
        client_id = self._get_client_identifier(request)
        
        # Check rate limits
        is_allowed, retry_after = await self._check_rate_limit(client_id)
        
        if not is_allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded. Please try again later.",
                    "retry_after": retry_after
                },
                headers={"Retry-After": str(retry_after)}
            )
        
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = await self._get_remaining_requests(client_id)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + 60)
        
        return response
    
    def _get_client_identifier(self, request: Request) -> str:
        """Get unique identifier for the client (IP or user ID)."""
        # Try to get user from request state (set by auth middleware)
        if hasattr(request.state, "user") and request.state.user:
            return f"user:{request.state.user.id}"
        
        # Fall back to IP address
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"
    
    async def _check_rate_limit(self, client_id: str) -> tuple[bool, int]:
        """Check if client has exceeded rate limits.
        
        Returns:
            tuple: (is_allowed, retry_after_seconds)
        """
        redis_client = get_redis_client()
        if not redis_client:
            # If Redis is unavailable, allow the request
            return True, 0
        
        current_time = int(time.time())
        minute_key = f"rate_limit:minute:{client_id}"
        hour_key = f"rate_limit:hour:{client_id}"
        
        try:
            # Check minute limit
            minute_count = redis_client.incr(minute_key)
            if minute_count == 1:
                redis_client.expire(minute_key, 60)
            
            if minute_count > self.requests_per_minute:
                ttl = redis_client.ttl(minute_key)
                return False, max(ttl, 1)
            
            # Check hour limit
            hour_count = redis_client.incr(hour_key)
            if hour_count == 1:
                redis_client.expire(hour_key, 3600)
            
            if hour_count > self.requests_per_hour:
                ttl = redis_client.ttl(hour_key)
                return False, max(ttl, 1)
            
            return True, 0
        
        except Exception as e:
            # If Redis fails, allow the request (fail open)
            print(f"Rate limiter error: {e}")
            return True, 0
    
    async def _get_remaining_requests(self, client_id: str) -> int:
        """Get remaining requests for the current minute."""
        redis_client = get_redis_client()
        if not redis_client:
            return self.requests_per_minute
        
        try:
            minute_key = f"rate_limit:minute:{client_id}"
            count = redis_client.get(minute_key)
            current_count = int(count) if count else 0
            return max(0, self.requests_per_minute - current_count)
        except Exception:
            return self.requests_per_minute