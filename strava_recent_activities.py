"""
Mock script demonstrating how to connect to the Strava API with stravalib
and fetch the last three activities for the authenticated athlete.
"""

from __future__ import annotations

import os
from typing import List

from stravalib.client import Client
from stravalib.exc import AccessUnauthorized


def fetch_recent_activities(limit: int = 3) -> List:
    """
    Fetch the most recent activities using the Strava API.

    Args:
        limit: Number of recent activities to retrieve.

    Returns:
        A list containing the most recent activities.
    """
    access_token = os.getenv("STRAVA_ACCESS_TOKEN")
    if not access_token:
        raise RuntimeError(
            "STRAVA_ACCESS_TOKEN environment variable is required to authenticate."
        )

    client = Client()
    client.access_token = access_token

    try:
        activities = client.get_activities(limit=limit)
    except AccessUnauthorized as exc:
        raise RuntimeError(
            "Authentication with Strava failed; refresh the access token."
        ) from exc

    return list(activities)


if __name__ == "__main__":
    recent = fetch_recent_activities(limit=3)
    for idx, activity in enumerate(recent, start=1):
        print(f"{idx}. {activity.name} — distance: {activity.distance}, moving time: {activity.moving_time}")
