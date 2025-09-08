import time
import os
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from src.core.logging import LoggerMixin

# Rate limiting configuration
RATE_LIMIT = int(os.getenv("RATE_LIMIT", "5"))
TIME_WINDOW = int(os.getenv("TIME_WINDOW", "60"))

# In-memory storage for request counts
requests_store = {}

class RateLimitMiddleware(BaseHTTPMiddleware, LoggerMixin):
   """
   Rate limiting middleware using sliding window algorithm.
   
   Tracks requests per client IP and enforces configurable rate limits.
   Uses in-memory storage - suitable for single instance deployments.
   """
   
   async def dispatch(self, request: Request, call_next):
       """
       Process incoming request and apply rate limiting.
       
       Args:
           request: Incoming HTTP request
           call_next: Next middleware in chain
           
       Returns:
           HTTP response or 429 if rate limit exceeded
       """
       client_ip = self.get_client_ip(request)
       request_id = getattr(request.state, "request_id", "unknown")
       now = time.time()

       # Get or create record for this client
       record = requests_store.get(client_ip, {"count": 0, "time": now})

       # Reset counter if time window has passed
       if now - record["time"] > TIME_WINDOW:
           record = {"count": 0, "time": now}
           self.log_info(
               "Rate limit window reset",
               request_id=request_id,
               client_ip=client_ip
           )

       # Increment request count
       record["count"] += 1
       requests_store[client_ip] = record

       # Log rate limit status
       self.log_info(
           "Rate limit check",
           request_id=request_id,
           client_ip=client_ip,
           current_count=record["count"],
           limit=RATE_LIMIT,
           path=request.url.path
       )

       # Check if limit exceeded
       if record["count"] > RATE_LIMIT:
           remaining_time = int(TIME_WINDOW - (now - record["time"]))
           
           self.log_warning(
               "Rate limit exceeded",
               request_id=request_id,
               client_ip=client_ip,
               current_count=record["count"],
               limit=RATE_LIMIT,
               reset_in=remaining_time,
               path=request.url.path
           )
           
           return JSONResponse(
               status_code=429,
               content={
                   "detail": f"Rate limit exceeded. Try again in {remaining_time}s."
               }
           )

       return await call_next(request)
   
   def get_client_ip(self, request: Request) -> str:
       """
       Extract client IP address from request headers.
       
       Checks proxy headers (X-Forwarded-For, X-Real-IP) before falling
       back to direct client IP. Useful for deployments behind load balancers.
       
       Args:
           request: HTTP request object
           
       Returns:
           Client IP address as string
       """
       forwarded_for = request.headers.get("X-Forwarded-For")
       if forwarded_for:
           return forwarded_for.split(",")[0].strip()
       
       real_ip = request.headers.get("X-Real-IP")
       if real_ip:
           return real_ip
       
       return request.client.host or "unknown"