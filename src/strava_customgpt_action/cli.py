"""
Command-line helpers for strava-customgpt-action.
"""

from __future__ import annotations

from .activities import fetch_recent_activities


def main() -> None:
    """
    Simple CLI entry point that prints the latest Strava activities.
    """
    recent = fetch_recent_activities(limit=5)
    for idx, activity in enumerate(recent, start=1):
        print(
            f"{idx}. {activity.name} — distance: {activity.distance}, "
            f"moving time: {activity.moving_time}"
        )


if __name__ == "__main__":
    main()
