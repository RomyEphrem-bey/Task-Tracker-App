# health.py — Route handler for the /health endpoint.
# Keeping routes in their own module makes the codebase easy to extend:
# each feature area gets its own file under app/api/routes/.

from datetime import datetime, timezone

from fastapi import APIRouter

from app.models import HealthResponse

# APIRouter lets us define routes here and register them in main.py
# with a shared prefix, keeping main.py clean.
router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Returns the service status and the current UTC timestamp.",
)
def get_health() -> HealthResponse:
    """Return the service health status and current UTC timestamp.

    Returns:
        HealthResponse: Object with `status` set to "ok" and `timestamp`
            set to the current UTC time in ISO 8601 format.

    Example:
        GET /health
        -> 200 OK
        {
            "status": "ok",
            "timestamp": "2025-05-16T10:30:00.123456+00:00"
        }
    """
    return HealthResponse(
        status="ok",
        # ISO 8601 timestamp in UTC, e.g. 2025-05-16T10:30:00.123456+00:00
        timestamp=datetime.now(tz=timezone.utc).isoformat(),
    )