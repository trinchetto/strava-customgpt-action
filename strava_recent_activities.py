"""
Compatibility wrapper to run the package CLI without Poetry.
"""

from __future__ import annotations

from strava_customgpt_action.cli import main

if __name__ == "__main__":
    main()
