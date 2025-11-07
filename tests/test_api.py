from __future__ import annotations

from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from strava_customgpt_action import api


def create_test_app():
    return TestClient(api.create_app())


def test_health_endpoint():
    client = create_test_app()
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_list_activities_success(monkeypatch):
    sample_activity = SimpleNamespace(
        id=101,
        name="Morning Ride",
        sport_type="Ride",
        distance=12345.0,
        moving_time=timedelta(minutes=42),
        elapsed_time=timedelta(minutes=45),
        start_date=datetime(2024, 5, 1, 6, 0, 0),
        external_id="abc123",
    )

    monkeypatch.setattr(
        api, "fetch_recent_activities", lambda limit: [sample_activity], raising=False
    )

    client = create_test_app()
    resp = client.get("/activities?limit=1")
    assert resp.status_code == 200
    body = resp.json()
    record = body["activities"][0]
    assert record["id"] == 101
    assert record["distance_m"] == pytest.approx(12345.0)
    assert record["moving_time_s"] == 42 * 60
    assert record["elapsed_time_s"] == 45 * 60


def test_list_activities_handles_runtime_error(monkeypatch):
    def _boom(limit: int):
        raise RuntimeError("token expired")

    monkeypatch.setattr(api, "fetch_recent_activities", _boom, raising=False)

    client = create_test_app()
    resp = client.get("/activities")
    assert resp.status_code == 500
    assert resp.json()["detail"] == "token expired"
