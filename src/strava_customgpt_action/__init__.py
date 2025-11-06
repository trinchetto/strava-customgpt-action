"""
strava_customgpt_action package.

Provides helpers to authenticate with Strava via stravalib and fetch activities.
"""

from .activities import fetch_recent_activities

__all__ = ["fetch_recent_activities"]
