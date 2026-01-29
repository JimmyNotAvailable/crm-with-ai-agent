"""
Audit Logging Middleware
Automatically log all API requests for security and compliance
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from sqlalchemy.orm import Session
from typing import Callable
import time
import json
from backend.models.audit_log import AuditLog
from backend.utils.pii_masking import PIIMasker
from backend.database.session import SessionLocal


class AuditLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to automatically log all API requests
    Records user actions, resource access, and data changes
    """
    
    # Endpoints to skip logging (too noisy)
    SKIP_ENDPOINTS = {
        "/", "/health", "/docs", "/redoc", "/openapi.json"
    }
    
    # Methods to log
    LOG_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log audit trail"""
        
        # Skip logging for certain endpoints
        if request.url.path in self.SKIP_ENDPOINTS:
            return await call_next(request)
        
        # Skip logging for GET requests (too noisy, read-only)
        # Only log state-changing operations
        if request.method not in self.LOG_METHODS:
            return await call_next(request)
        
        # Start timing
        start_time = time.time()
        
        # Extract user information from request
        user_info = self._extract_user_info(request)
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Log to database asynchronously
        try:
            self._log_audit(
                request=request,
                response=response,
                user_info=user_info,
                duration_ms=duration_ms
            )
        except Exception as e:
            # Don't fail the request if audit logging fails
            print(f"Audit logging error: {e}")
        
        return response
    
    def _extract_user_info(self, request: Request) -> dict:
        """Extract user information from request state"""
        user_info = {
            "user_id": None,
            "username": "anonymous",
            "role": "GUEST"
        }
        
        # Try to get user from request state (set by auth middleware)
        if hasattr(request.state, "user"):
            user = request.state.user
            user_info["user_id"] = getattr(user, "id", None)
            user_info["username"] = getattr(user, "username", "unknown")
            user_info["role"] = getattr(user, "role", "UNKNOWN")
        
        return user_info
    
    def _parse_resource_info(self, path: str, method: str) -> dict:
        """Parse resource type and action from request path"""
        parts = path.strip("/").split("/")
        
        # Default values
        resource_type = "UNKNOWN"
        resource_id = None
        action = method  # Fallback to HTTP method
        
        # Try to extract resource from path
        # Example: /api/v1/orders/123 -> resource_type=Order, resource_id=123
        if len(parts) >= 3:
            resource_type = parts[2].upper().rstrip("S")  # Remove plural 's'
        
        if len(parts) >= 4 and parts[3].isdigit():
            resource_id = parts[3]
        
        # Map HTTP methods to actions
        action_map = {
            "POST": "CREATE",
            "PUT": "UPDATE",
            "PATCH": "UPDATE",
            "DELETE": "DELETE",
            "GET": "READ"
        }
        action = action_map.get(method, method)
        
        # Special cases
        if "login" in path.lower():
            action = "LOGIN"
            resource_type = "AUTH"
        elif "logout" in path.lower():
            action = "LOGOUT"
            resource_type = "AUTH"
        elif "refund" in path.lower():
            action = "REFUND"
        elif "return" in path.lower():
            action = "RETURN"
        elif "merge" in path.lower():
            action = "MERGE"
        
        return {
            "resource_type": resource_type,
            "resource_id": resource_id,
            "action": action
        }
    
    def _log_audit(
        self,
        request: Request,
        response: Response,
        user_info: dict,
        duration_ms: int
    ):
        """Write audit log to database"""
        db = SessionLocal()
        
        try:
            # Parse resource information
            resource_info = self._parse_resource_info(
                request.url.path,
                request.method
            )
            
            # Determine status
            status = "SUCCESS" if response.status_code < 400 else "FAILED"
            error_message = None
            if status == "FAILED":
                error_message = f"HTTP {response.status_code}"
            
            # Create audit log entry
            audit_log = AuditLog(
                user_id=user_info["user_id"],
                username=user_info["username"],
                user_role=user_info["role"],
                action=resource_info["action"],
                resource_type=resource_info["resource_type"],
                resource_id=resource_info["resource_id"],
                method=request.method,
                endpoint=request.url.path,
                ip_address=self._get_client_ip(request),
                user_agent=request.headers.get("user-agent", "")[:500],
                status=status,
                error_message=error_message,
                duration_ms=duration_ms,
                # Note: old_values and new_values would require more complex
                # request/response body parsing and are left for future enhancement
                old_values=None,
                new_values=None
            )
            
            db.add(audit_log)
            db.commit()
        
        finally:
            db.close()
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request"""
        # Check X-Forwarded-For header (for proxy/load balancer)
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        # Fall back to direct client
        if request.client:
            return request.client.host
        
        return "unknown"
