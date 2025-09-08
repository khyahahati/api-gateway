from fastapi import APIRouter
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
import time

router = APIRouter()

# Prometheus metrics
REQUEST_COUNT = Counter(
   "gateway_requests_total",
   "Total number of requests handled by the gateway",
   ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
   "gateway_request_latency_seconds",
   "Latency of requests handled by the gateway",
   ["endpoint"]
)

def setup_metrics(app):
   """
   Set up Prometheus metrics middleware to track request counts and latency.
   
   Args:
       app: FastAPI application instance
   """
   @app.middleware("http")
   async def metrics_middleware(request, call_next):
       start_time = time.time()
       response = await call_next(request)
       process_time = time.time() - start_time

       endpoint = request.url.path
       REQUEST_COUNT.labels(request.method, endpoint, response.status_code).inc()
       REQUEST_LATENCY.labels(endpoint).observe(process_time)

       return response

@router.get("/health")
async def health_check():
   """Health check endpoint to verify gateway status."""
   return {"status": "ok", "message": "API Gateway is healthy"}

@router.get("/metrics")
async def metrics():
   """Prometheus metrics endpoint for scraping monitoring data."""
   return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)