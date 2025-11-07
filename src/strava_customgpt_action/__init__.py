"""
strava_customgpt_action package.

Provides helpers to authenticate with Strava via stravalib and fetch activities.
"""

from .activities import fetch_recent_activities
from .api import create_app
from .auth import get_authenticated_client, run_authorization_cli

__all__ = [
    "fetch_recent_activities",
    "create_app",
    "get_authenticated_client",
    "run_authorization_cli",
]
