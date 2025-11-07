# trinchetto-strava-customgpt-action
A CustomGPT Action that connects to Strava and fetches information to be used for training follow-up and planning.

## Getting a Strava access token

You need a short-lived Strava access token to authenticate the sample script.

```bash
chmod +x scripts/get_strava_token.sh  # first run only
source scripts/get_strava_token.sh
```

The script will:
- prompt for your `Client ID`/`Client Secret` (step 1),
- generate the authorization URL for you to open manually (step 2),
- exchange the returned code for a refresh token (step 3),
- fetch a fresh short-lived access token and print export commands (step 4).

The script exports the resulting environment variables directly into your current shell. You still need to approve the application in your browser and paste back the authorization code when prompted.

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
- `GET /activities?limit=5` returning the latest Strava activities (requires `STRAVA_ACCESS_TOKEN`)

## Development

- Install dependencies for development (including linters/type-checkers):
  ```bash
  poetry install --with dev
  ```
- Set up the pre-commit hooks locally:
  ```bash
  poetry run pre-commit install
  ```
- CI runs the same pre-commit configuration (Black, Ruff, Mypy) to keep formatting and checks consistent.
