from __future__ import annotations

from types import SimpleNamespace

import pytest
from stravalib.exc import AccessUnauthorized

from strava_customgpt_action import activities


def test_fetch_recent_activities_returns_list(monkeypatch):
    activities_stub = [
        SimpleNamespace(id=1, name="Ride"),
        SimpleNamespace(id=2, name="Run"),
    ]

    class FakeClient:
        def get_activities(self, limit: int):
            assert limit == 2
            return activities_stub[:limit]

    monkeypatch.setattr(
        activities, "get_authenticated_client", lambda: FakeClient(), raising=False
    )

    result = activities.fetch_recent_activities(limit=2)
    assert len(result) == 2
    assert result[0].name == "Ride"
    assert result[1].name == "Run"


def test_fetch_recent_activities_wraps_access_error(monkeypatch):
    class FakeClient:
        def get_activities(self, limit: int):
            raise AccessUnauthorized("bad token")

    monkeypatch.setattr(
        activities, "get_authenticated_client", lambda: FakeClient(), raising=False
    )

    with pytest.raises(RuntimeError, match="Authentication with Strava failed"):
        activities.fetch_recent_activities(limit=1)
