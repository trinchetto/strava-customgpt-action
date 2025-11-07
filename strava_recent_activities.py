"""
Compatibility wrapper to launch the REST API without Poetry.
"""

from __future__ import annotations

from strava_customgpt_action.server import main

if __name__ == "__main__":
    main()
