from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if SRC.exists():
    sys.path.insert(0, str(SRC))


@pytest.fixture
def auth_module(tmp_path, monkeypatch):
    """
    Provide a fresh copy of the auth module that stores state in a temp .env file.
    """

    env_file = tmp_path / ".auth-env"
    monkeypatch.setenv("STRAVA_ENV_FILE", str(env_file))
    # Ensure we import a clean module so ENV_FILE picks up the new path.
    sys.modules.pop("strava_customgpt_action.auth", None)
    auth = importlib.import_module("strava_customgpt_action.auth")
    yield auth
    # Remove module so subsequent tests can reconfigure environment if needed.
    sys.modules.pop("strava_customgpt_action.auth", None)
