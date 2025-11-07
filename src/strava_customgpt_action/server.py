"""
Uvicorn server helpers for the Strava CustomGPT Action API.
"""

from __future__ import annotations

import os

import uvicorn

DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8000


def main() -> None:
    """
    Entrypoint for `poetry run strava-activities-api`.
    """

    host = os.getenv("API_HOST", DEFAULT_HOST)
    port = int(os.getenv("API_PORT", str(DEFAULT_PORT)))
    reload_enabled = os.getenv("API_RELOAD", "false").lower() in {"1", "true", "yes"}

    uvicorn.run(
        "strava_customgpt_action.api:app",
        host=host,
        port=port,
        reload=reload_enabled,
        factory=False,
    )
