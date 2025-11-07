"""
Activity retrieval helpers built on top of stravalib.
"""

from __future__ import annotations

import os
from collections.abc import Iterable

from stravalib.client import Client
from stravalib.exc import AccessUnauthorized
from stravalib.model import Activity


def fetch_recent_activities(limit: int = 3) -> list[Activity]:
    """
    Fetch the most recent activities for the authenticated athlete.

    Args:
        limit: Maximum number of activities to retrieve.

    Returns:
        A list of stravalib activity objects.
    """
    access_token = os.getenv("STRAVA_ACCESS_TOKEN")
    if not access_token:
        raise RuntimeError(
            "STRAVA_ACCESS_TOKEN environment variable is required to authenticate."
        )

    client = Client()
    client.access_token = access_token

    try:
        activities: Iterable[Activity] = client.get_activities(limit=limit)
    except AccessUnauthorized as exc:
        raise RuntimeError(
            "Authentication with Strava failed; refresh the access token."
        ) from exc

    return list(activities)
