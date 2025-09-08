"""
This module contains API endpoints for application health and readiness checks.

These endpoints are crucial for container orchestration systems like Kubernetes
to monitor the state of the API Gateway.
- The `/live` endpoint indicates if the service is running.
- The `/ready` endpoint checks if the service is ready to handle requests by
  verifying the health of its dependencies.
"""
from fastapi import APIRouter
import httpx

# The APIRouter instance for the health endpoints.
router = APIRouter()

@router.get("/live")
async def liveness():
    """
    Performs a liveness check on the API Gateway.

    This endpoint simply confirms that the service is running and
    responsive. It does not check any external dependencies.

    Returns:
        dict: A status message indicating the service is alive.
    """
    return {"status": "ok", "message": "Gateway is alive"}

@router.get("/ready")
async def readiness():
    """
    Performs a readiness check on the API Gateway and its dependencies.

    This endpoint is used to determine if the service is ready to accept
    traffic by checking if its key backend services are reachable. It returns
    the health status of each configured dependency.

    Returns:
        dict: A dictionary containing the overall status and a status
              for each backend service. Possible service statuses are:
              - "ok": The service is healthy.
              - "unhealthy": The service is running but returned an error status.
              - "unreachable": The service could not be reached.
    """
    # A dictionary of backend services to check.
    services = {
        "users": "http://localhost:5001/health",
        "orders": "http://localhost:5002/health"
    }
    status = {}
    
    # Use an asynchronous HTTP client to check each service.
    async with httpx.AsyncClient(timeout=2.0) as client:
        for name, url in services.items():
            try:
                # Make a GET request to the service's health endpoint.
                r = await client.get(url)
                # Check the status code to determine health.
                status[name] = "ok" if r.status_code == 200 else "unhealthy"
            except Exception:
                # If an exception occurs, the service is unreachable.
                status[name] = "unreachable"

    # Return the readiness status.
    return {"status": "ok", "services": status}
