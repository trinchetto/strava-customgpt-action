"""
Activity retrieval helpers built on top of stravalib.
"""

from __future__ import annotations

from collections.abc import Iterable

from stravalib.exc import AccessUnauthorized
from stravalib.model import SummaryActivity

from .auth import get_authenticated_client


def fetch_recent_activities(limit: int = 3) -> list[SummaryActivity]:
    """
    Fetch the most recent activities for the authenticated athlete.

    Args:
        limit: Maximum number of activities to retrieve.

    Returns:
        A list of stravalib activity objects.
    """
    client = get_authenticated_client()

    try:
        activities: Iterable[SummaryActivity] = client.get_activities(limit=limit)
    except AccessUnauthorized as exc:
        raise RuntimeError(
            "Authentication with Strava failed; refresh the access token."
        ) from exc

    return list(activities)
