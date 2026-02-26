"""
Prometheus metrics endpoint.
"""

import time
from fastapi import APIRouter, Response

router = APIRouter(tags=["Metrics"])

# In-memory metrics counters (use prometheus_client in production)
_metrics = {
    "http_requests_total": 0,
    "http_request_duration_seconds": 0.0,
    "active_websocket_connections": 0,
    "llm_requests_total": 0,
    "llm_tokens_total": 0,
    "errors_total": 0,
}


def increment_metric(name: str, value: float = 1.0):
    """Increment a metric counter."""
    if name in _metrics:
        _metrics[name] += value


@router.get("/metrics")
async def prometheus_metrics():
    """Expose metrics in Prometheus text format."""
    lines = []
    for name, value in _metrics.items():
        metric_type = "counter" if "total" in name else "gauge"
        lines.append(f"# TYPE jarvis_{name} {metric_type}")
        lines.append(f"jarvis_{name} {value}")

    return Response(
        content="\n".join(lines) + "\n",
        media_type="text/plain; charset=utf-8",
    )
