"""Compression Middleware - Gateway Offloading Pattern
Offloads response compression from individual services to the gateway level.
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import gzip
import io


class CompressionMiddleware(BaseHTTPMiddleware):
    """Middleware to compress responses using gzip when client accepts it."""
    
    def __init__(self, app, minimum_size: int = 500):
        super().__init__(app)
        self.minimum_size = minimum_size
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Check if client accepts gzip encoding
        accept_encoding = request.headers.get("accept-encoding", "")
        if "gzip" not in accept_encoding.lower():
            return response
        
        # Don't compress already compressed content
        if response.headers.get("content-encoding"):
            return response
        
        # Only compress responses larger than minimum_size
        content_length = response.headers.get("content-length")
        if content_length and int(content_length) < self.minimum_size:
            return response
        
        # Compress the response body
        body = b""
        async for chunk in response.body_iterator:
            body += chunk
        
        if len(body) < self.minimum_size:
            # Too small to compress, return original
            return Response(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
        
        # Compress using gzip
        gzip_buffer = io.BytesIO()
        with gzip.GzipFile(mode="wb", fileobj=gzip_buffer, compresslevel=6) as gzip_file:
            gzip_file.write(body)
        
        compressed_body = gzip_buffer.getvalue()
        
        # Update headers
        headers = dict(response.headers)
        headers["content-encoding"] = "gzip"
        headers["content-length"] = str(len(compressed_body))
        headers["vary"] = "Accept-Encoding"
        
        return Response(
            content=compressed_body,
            status_code=response.status_code,
            headers=headers,
            media_type=response.media_type
        )