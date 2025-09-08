"""
This module provides API endpoints for exposing application metrics in a format
that can be scraped by monitoring systems like Prometheus.

It includes:
- A `/metrics` endpoint that provides raw metrics data.
- A `/summary` endpoint for a human-readable, high-level overview.
"""
from fastapi import APIRouter
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

# The APIRouter instance for the metrics endpoints.
router = APIRouter()

@router.get("/")
async def metrics():
    """
    Exposes Prometheus metrics.

    This endpoint generates and returns the latest state of all registered
    Prometheus metrics. It is designed to be scraped by a Prometheus server.

    Returns:
        starlette.responses.Response: A response object with the metrics data
        and the appropriate media type.
    """
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@router.get("/summary")
async def summary():
    """
    Provides a simple, human-readable summary of key metrics.

    This endpoint is useful for quick checks when a full-fledged monitoring
    system is not available. It does not provide real-time, detailed data,
    but rather a high-level overview.

    Returns:
        dict: A dictionary with a summary of available metrics.
    """
    # Simple JSON summary (useful if Prometheus/Grafana not available)
    return {
        "total_requests": "exposed via Prometheus",
        "avg_latency": "exposed via Prometheus",
        "note": "Use /metrics for detailed metrics"
    }
