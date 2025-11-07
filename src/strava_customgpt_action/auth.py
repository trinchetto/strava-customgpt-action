"""
Authentication helpers built on top of stravalib's OAuth support.
"""

from __future__ import annotations

import os
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from getpass import getpass
from pathlib import Path

from dotenv import load_dotenv, set_key
from stravalib.client import Client

DEFAULT_SCOPE = ("activity:read",)
DEFAULT_REDIRECT_URI = "http://localhost/exchange_token"
EXPIRY_GRACE_SECONDS = 60
ENV_FILE = Path(
    os.environ.get("STRAVA_ENV_FILE", "~/.strava-customgpt-env")
).expanduser()
ENV_FILE.parent.mkdir(parents=True, exist_ok=True)

# Load any previously stored credentials once on import so downstream modules see them.
load_dotenv(dotenv_path=ENV_FILE, override=False)


@dataclass
class OAuthTokens:
    """
    Container for Strava OAuth tokens and metadata.
    """

    access_token: str
    refresh_token: str
    expires_at: datetime | None

    @classmethod
    def from_response(cls, payload: dict) -> OAuthTokens:
        expires_at = payload.get("expires_at")
        expires_dt = (
            datetime.fromtimestamp(int(expires_at), tz=UTC) if expires_at else None
        )
        return cls(
            access_token=payload["access_token"],
            refresh_token=payload.get("refresh_token") or "",
            expires_at=expires_dt,
        )


@dataclass
class OAuthConfig:
    client_id: str
    client_secret: str
    refresh_token: str | None
    access_token: str | None
    expires_at: datetime | None

    @classmethod
    def from_env(cls) -> OAuthConfig:
        return cls(
            client_id=_require_env("STRAVA_CLIENT_ID"),
            client_secret=_require_env("STRAVA_CLIENT_SECRET"),
            refresh_token=os.getenv("STRAVA_REFRESH_TOKEN"),
            access_token=os.getenv("STRAVA_ACCESS_TOKEN"),
            expires_at=_parse_timestamp(os.getenv("STRAVA_ACCESS_TOKEN_EXPIRES_AT")),
        )

    def needs_refresh(self, *, now: datetime | None = None) -> bool:
        if not self.expires_at:
            return self.access_token is None
        current = now or datetime.now(tz=UTC)
        return self.expires_at <= current + timedelta(seconds=EXPIRY_GRACE_SECONDS)


def get_authenticated_client() -> Client:
    """
    Return a stravalib Client configured with a valid (refreshed) access token.
    """

    config = OAuthConfig.from_env()
    client = Client()

    if config.access_token and not config.needs_refresh():
        client.access_token = config.access_token
        return client

    if not config.refresh_token:
        raise RuntimeError(
            "STRAVA_REFRESH_TOKEN is missing; run `poetry run strava-auth` first."
        )

    tokens = client.refresh_access_token(
        client_id=config.client_id,
        client_secret=config.client_secret,
        refresh_token=config.refresh_token,
    )
    bundle = OAuthTokens.from_response(tokens)
    client.access_token = bundle.access_token

    os.environ["STRAVA_ACCESS_TOKEN"] = bundle.access_token
    if bundle.expires_at:
        os.environ["STRAVA_ACCESS_TOKEN_EXPIRES_AT"] = str(
            int(bundle.expires_at.timestamp())
        )
    if bundle.refresh_token:
        os.environ["STRAVA_REFRESH_TOKEN"] = bundle.refresh_token

    return client


def run_authorization_cli() -> None:
    """
    Interactive helper replicating the old shell script, powered by stravalib.
    """

    print("=== Strava OAuth helper ===")
    client_id = input("Enter your Strava Client ID: ").strip()
    client_secret = getpass("Enter your Strava Client Secret: ").strip()
    redirect_uri = (
        input(f"Redirect URI [{DEFAULT_REDIRECT_URI}]: ").strip()
        or DEFAULT_REDIRECT_URI
    )
    scope_input = input(
        f"Requested scope (space separated) [{' '.join(DEFAULT_SCOPE)}]: "
    ).strip()
    scope: Sequence[str] = scope_input.split() if scope_input else DEFAULT_SCOPE

    client = Client()
    auth_url = client.authorization_url(
        client_id=client_id,
        redirect_uri=redirect_uri,
        scope=scope,
    )

    print("\nOpen this URL in your browser and authorize the application:\n")
    print(auth_url)
    print()
    auth_code = input("Paste the authorization code from the redirect URL: ").strip()

    token_response = client.exchange_code_for_token(
        client_id=client_id,
        client_secret=client_secret,
        code=auth_code,
    )

    bundle = OAuthTokens.from_response(token_response)
    _set_env_and_echo(client_id=client_id, client_secret=client_secret, bundle=bundle)


def _set_env_and_echo(
    *, client_id: str, client_secret: str, bundle: OAuthTokens
) -> None:
    env_updates: dict[str, str] = {
        "STRAVA_CLIENT_ID": client_id,
        "STRAVA_CLIENT_SECRET": client_secret,
        "STRAVA_REFRESH_TOKEN": bundle.refresh_token,
        "STRAVA_ACCESS_TOKEN": bundle.access_token,
    }
    if bundle.expires_at:
        env_updates["STRAVA_ACCESS_TOKEN_EXPIRES_AT"] = str(
            int(bundle.expires_at.timestamp())
        )

    for key, value in env_updates.items():
        os.environ[key] = value
        set_key(str(ENV_FILE), key, value)

    print("\nEnvironment variables set for this session:")
    for key, value in env_updates.items():
        print(f"  {key}={value}")


def _require_env(var_name: str) -> str:
    value = os.getenv(var_name)
    if not value:
        raise RuntimeError(f"Environment variable {var_name} is required.")
    return value


def _parse_timestamp(raw: str | None) -> datetime | None:
    if not raw:
        return None
    try:
        return datetime.fromtimestamp(int(raw), tz=UTC)
    except ValueError as exc:
        raise RuntimeError(
            "STRAVA_ACCESS_TOKEN_EXPIRES_AT must be a UNIX timestamp."
        ) from exc


def main() -> None:
    run_authorization_cli()
