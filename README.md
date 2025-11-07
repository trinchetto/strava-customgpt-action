# trinchetto-strava-customgpt-action
A CustomGPT Action that connects to Strava and fetches information to be used for training follow-up and planning.

## Getting a Strava access token

Run the built-in helper (powered by `stravalib`) to walk through the OAuth flow:

```bash
poetry run strava-auth
```

The CLI will:
- prompt for your `Client ID`/`Client Secret`,
- generate the authorization URL for you to open manually,
- exchange the returned authorization code for refresh + access tokens,
- persist the `STRAVA_CLIENT_ID`, `STRAVA_CLIENT_SECRET`, `STRAVA_REFRESH_TOKEN`, `STRAVA_ACCESS_TOKEN`, and `STRAVA_ACCESS_TOKEN_EXPIRES_AT` values into `~/.strava-customgpt-env` (or a custom file via `STRAVA_ENV_FILE`) and load them into the running process, echoing the final values so you can double-check.

Every time the package starts up, it automatically loads the `.env` file so both the CLI and the REST API can reuse the saved credentials. Access tokens refresh themselves using the stored refresh token; you only need to rerun `strava-auth` if you rotate credentials or scopes.

## Run a sample script
Once the `STRAVA_ACCESS_TOKEN` environment variable is set, run the packaged CLI:

```bash
poetry run strava-recent-activities
```

Alternatively, you can call the compatibility script directly:

```bash
python strava_recent_activities.py
```

## Expose a REST API

The FastAPI surface lets you query Strava data from CustomGPT (or any HTTP client).

```bash
poetry run strava-activities-api
# or without Poetry:
python strava_recent_activities.py
```

Environment variables:
- `API_HOST` (default `0.0.0.0`)
- `API_PORT` (default `8000`)
- `API_RELOAD` (set to `true`/`1` for hot reload during development)

The server exposes:
- `GET /health` for readiness checks
- `GET /activities?limit=5` returning the latest Strava activities (requires Strava OAuth credentials)

## Development

- Install dependencies for development (including linters/type-checkers):
  ```bash
  poetry install --with dev
  ```
- Run the automated test suite:
  ```bash
  poetry run pytest
  ```
- Set up the pre-commit hooks locally:
  ```bash
  poetry run pre-commit install
  ```
- CI runs the same pre-commit configuration (Black, Ruff, Mypy) to keep formatting and checks consistent.
