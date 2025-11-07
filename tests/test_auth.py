from __future__ import annotations

import builtins
import os
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta

import pytest
from dotenv import dotenv_values


def _future_timestamp(hours: int = 1) -> int:
    return int((datetime.now(tz=UTC) + timedelta(hours=hours)).timestamp())


def test_get_authenticated_client_uses_cached_token(auth_module, monkeypatch):
    auth = auth_module
    expiry = _future_timestamp()
    monkeypatch.setenv("STRAVA_CLIENT_ID", "client-123")
    monkeypatch.setenv("STRAVA_CLIENT_SECRET", "secret-xyz")
    monkeypatch.setenv("STRAVA_REFRESH_TOKEN", "refresh-abc")
    monkeypatch.setenv("STRAVA_ACCESS_TOKEN", "cached-token")
    monkeypatch.setenv("STRAVA_ACCESS_TOKEN_EXPIRES_AT", str(expiry))

    class DummyClient:
        def __init__(self):
            self.access_token = None

        def refresh_access_token(self, *args, **kwargs):
            raise AssertionError("refresh_access_token should not be called")

    monkeypatch.setattr(auth, "Client", DummyClient)

    client = auth.get_authenticated_client()
    assert isinstance(client, DummyClient)
    assert client.access_token == "cached-token"


def test_get_authenticated_client_refreshes_and_persists(auth_module, monkeypatch):
    auth = auth_module
    new_expiry = _future_timestamp(2)
    monkeypatch.setenv("STRAVA_CLIENT_ID", "client-123")
    monkeypatch.setenv("STRAVA_CLIENT_SECRET", "secret-xyz")
    monkeypatch.setenv("STRAVA_REFRESH_TOKEN", "stale-refresh")
    monkeypatch.delenv("STRAVA_ACCESS_TOKEN", raising=False)
    monkeypatch.delenv("STRAVA_ACCESS_TOKEN_EXPIRES_AT", raising=False)

    class RefreshingClient:
        def __init__(self):
            self.access_token = None
            self.refresh_called_with = None

        def refresh_access_token(self, *, client_id, client_secret, refresh_token):
            self.refresh_called_with = (client_id, client_secret, refresh_token)
            return {
                "access_token": "new-token",
                "refresh_token": "fresh-refresh",
                "expires_at": new_expiry,
            }

    monkeypatch.setattr(auth, "Client", RefreshingClient)

    client = auth.get_authenticated_client()
    assert isinstance(client, RefreshingClient)
    assert client.access_token == "new-token"

    assert os.environ.get("STRAVA_ACCESS_TOKEN") == "new-token"
    assert os.environ.get("STRAVA_REFRESH_TOKEN") == "fresh-refresh"
    assert os.environ.get("STRAVA_ACCESS_TOKEN_EXPIRES_AT") == str(new_expiry)

    env_values = dotenv_values(dotenv_path=auth.ENV_FILE)
    assert env_values["STRAVA_ACCESS_TOKEN"] == "new-token"
    assert env_values["STRAVA_REFRESH_TOKEN"] == "fresh-refresh"


def test_get_authenticated_client_requires_refresh_token(auth_module, monkeypatch):
    auth = auth_module
    monkeypatch.setenv("STRAVA_CLIENT_ID", "client-123")
    monkeypatch.setenv("STRAVA_CLIENT_SECRET", "secret-xyz")
    monkeypatch.delenv("STRAVA_REFRESH_TOKEN", raising=False)
    monkeypatch.delenv("STRAVA_ACCESS_TOKEN", raising=False)

    class DummyClient:
        def __init__(self):
            self.access_token = None

    monkeypatch.setattr(auth, "Client", DummyClient)

    with pytest.raises(RuntimeError, match="STRAVA_REFRESH_TOKEN"):
        auth.get_authenticated_client()


def test_run_authorization_cli_sets_env_file(auth_module, monkeypatch, capsys):
    auth = auth_module
    future_expiry = _future_timestamp(4)

    responses: Iterator[str] = iter(
        ["client-123", "", "", "auth-code-789"]
    )  # client_id, redirect, scope, auth code

    def fake_input(prompt: str = "") -> str:
        return next(responses)

    monkeypatch.setattr(builtins, "input", fake_input)
    monkeypatch.setattr(auth, "getpass", lambda prompt="": "secret-xyz")

    class FakeClient:
        def __init__(self):
            self.access_token = None

        def authorization_url(self, *, client_id, redirect_uri, scope):
            assert client_id == "client-123"
            assert redirect_uri == auth.DEFAULT_REDIRECT_URI
            assert scope == auth.DEFAULT_SCOPE
            return "https://example.test/authorize"

        def exchange_code_for_token(self, *, client_id, client_secret, code):
            assert client_id == "client-123"
            assert client_secret == "secret-xyz"
            assert code == "auth-code-789"
            return {
                "access_token": "cli-token",
                "refresh_token": "cli-refresh",
                "expires_at": future_expiry,
            }

    monkeypatch.setattr(auth, "Client", FakeClient)

    auth.run_authorization_cli()

    env_values = dotenv_values(dotenv_path=auth.ENV_FILE)
    assert env_values["STRAVA_CLIENT_ID"] == "client-123"
    assert env_values["STRAVA_ACCESS_TOKEN"] == "cli-token"
    assert os.environ["STRAVA_ACCESS_TOKEN_EXPIRES_AT"] == str(future_expiry)

    std_output = capsys.readouterr().out
    assert "Environment variables set for this session" in std_output
