"""
REST API surface for exposing Strava activities.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, Protocol, SupportsFloat, runtime_checkable

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from .activities import fetch_recent_activities

if TYPE_CHECKING:
    from stravalib.model import SummaryActivity


class ActivityPayload(BaseModel):
    """
    Lightweight response model for Strava activities.
    """

    id: int
    name: str | None = None
    sport_type: str | None = None
    distance_m: float | None = None
    moving_time_s: int | None = None
    elapsed_time_s: int | None = None
    start_date: datetime | None = None
    external_id: str | None = None


class ActivitiesResponse(BaseModel):
    activities: list[ActivityPayload]


def create_app() -> FastAPI:
    """
    Build the FastAPI application with all routes and dependencies wired in.
    """

    app = FastAPI(title="Strava CustomGPT Action", version="0.1.0")

    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get(
        "/activities",
        response_model=ActivitiesResponse,
        tags=["activities"],
    )
    def list_activities(
        limit: int = Query(
            default=5,
            ge=1,
            le=50,
            description="Maximum number of recent activities to fetch from Strava.",
        ),
    ) -> ActivitiesResponse:
        try:
            activities = fetch_recent_activities(limit=limit)
        except RuntimeError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        payload = [
            ActivityPayload(**_serialize_activity(activity)) for activity in activities
        ]
        return ActivitiesResponse(activities=payload)

    return app


def _serialize_activity(activity: SummaryActivity) -> dict[str, Any]:
    """
    Convert a stravalib activity object into serializable primitives.
    """

    return {
        "id": getattr(activity, "id", 0),
        "name": getattr(activity, "name", None),
        "sport_type": getattr(activity, "sport_type", None),
        "distance_m": _distance_to_meters(getattr(activity, "distance", None)),
        "moving_time_s": _duration_to_seconds(getattr(activity, "moving_time", None)),
        "elapsed_time_s": _duration_to_seconds(getattr(activity, "elapsed_time", None)),
        "start_date": getattr(activity, "start_date", None),
        "external_id": getattr(activity, "external_id", None),
    }


@runtime_checkable
class _HasNumericValue(Protocol):
    num: float | int


DistanceLike = SupportsFloat | _HasNumericValue | float | int


def _distance_to_meters(distance_obj: DistanceLike | None) -> float | None:
    if distance_obj is None:
        return None
    if isinstance(distance_obj, _HasNumericValue):
        return float(distance_obj.num)
    try:
        return float(distance_obj)
    except (TypeError, ValueError):
        return None


@runtime_checkable
class _HasTotalSeconds(Protocol):
    def total_seconds(self) -> float: ...


DurationLike = timedelta | _HasTotalSeconds | int | float


def _duration_to_seconds(duration_obj: DurationLike | None) -> int | None:
    if duration_obj is None:
        return None
    if isinstance(duration_obj, timedelta):
        return int(duration_obj.total_seconds())
    if isinstance(duration_obj, _HasTotalSeconds):
        return int(duration_obj.total_seconds())
    try:
        return int(duration_obj)
    except (TypeError, ValueError):
        return None


app = create_app()
