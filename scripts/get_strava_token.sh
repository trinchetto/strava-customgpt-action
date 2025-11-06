#!/usr/bin/env bash

# Semi-automated helper to fetch Strava tokens.
# Prompts the user for inputs that require manual interaction.

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  echo "This script must be sourced so the environment variables persist."
  echo "Usage: source ${BASH_SOURCE[0]}"
  exit 1
fi

set -euo pipefail

DEFAULT_SCOPE="activity:read"
DEFAULT_REDIRECT_URI="http://localhost/exchange_token"

read -rp "Enter your Strava Client ID: " CLIENT_ID
read -rsp "Enter your Strava Client Secret: " CLIENT_SECRET
echo
read -rp "Redirect URI [${DEFAULT_REDIRECT_URI}]: " REDIRECT_URI
REDIRECT_URI=${REDIRECT_URI:-$DEFAULT_REDIRECT_URI}
read -rp "Requested scope [${DEFAULT_SCOPE}]: " SCOPE
SCOPE=${SCOPE:-$DEFAULT_SCOPE}

ENCODED_SCOPE=${SCOPE// /%20}
AUTH_URL="https://www.strava.com/oauth/authorize?client_id=${CLIENT_ID}&redirect_uri=${REDIRECT_URI}&response_type=code&scope=${ENCODED_SCOPE}"

echo
echo "Open this URL in your browser, authorize the application, and copy the 'code' parameter from the redirected URL:"
echo "${AUTH_URL}"
echo
read -rp "Paste the authorization code: " AUTH_CODE

echo
echo "Exchanging authorization code for refresh token..."
TOKEN_RESPONSE=$(curl -s -X POST https://www.strava.com/oauth/token \
  -d client_id="${CLIENT_ID}" \
  -d client_secret="${CLIENT_SECRET}" \
  -d code="${AUTH_CODE}" \
  -d grant_type=authorization_code)

extract_json_field() {
  local json="$1"
  local field="$2"
  if command -v jq >/dev/null 2>&1; then
    echo "${json}" | jq -r ".${field}"
  else
    python3 - "$field" <<'PY'
import json, sys
payload = json.loads(sys.stdin.read())
field = sys.argv[1]
print(payload.get(field, ""))
PY
  fi
}

REFRESH_TOKEN=$(extract_json_field "${TOKEN_RESPONSE}" "refresh_token")

if [[ -z "${REFRESH_TOKEN}" || "${REFRESH_TOKEN}" == "null" ]]; then
  echo "Failed to retrieve refresh token. Raw response:"
  echo "${TOKEN_RESPONSE}"
  return 1
fi

echo "Refresh token obtained."
echo
echo "Fetching a fresh short-lived access token using the refresh token..."
ACCESS_RESPONSE=$(curl -s -X POST https://www.strava.com/oauth/token \
  -d client_id="${CLIENT_ID}" \
  -d client_secret="${CLIENT_SECRET}" \
  -d grant_type=refresh_token \
  -d refresh_token="${REFRESH_TOKEN}")

ACCESS_TOKEN=$(extract_json_field "${ACCESS_RESPONSE}" "access_token")
EXPIRES_AT=$(extract_json_field "${ACCESS_RESPONSE}" "expires_at")

if [[ -z "${ACCESS_TOKEN}" || "${ACCESS_TOKEN}" == "null" ]]; then
  echo "Failed to retrieve access token. Raw response:"
  echo "${ACCESS_RESPONSE}"
  return 1
fi

export STRAVA_CLIENT_ID="${CLIENT_ID}"
export STRAVA_CLIENT_SECRET="${CLIENT_SECRET}"
export STRAVA_REFRESH_TOKEN="${REFRESH_TOKEN}"
export STRAVA_ACCESS_TOKEN="${ACCESS_TOKEN}"
if [[ -n "${EXPIRES_AT}" && "${EXPIRES_AT}" != "null" ]]; then
  export STRAVA_ACCESS_TOKEN_EXPIRES_AT="${EXPIRES_AT}"
fi

echo
echo "Success! Environment variables exported in current shell:"
echo "  STRAVA_CLIENT_ID"
echo "  STRAVA_CLIENT_SECRET"
echo "  STRAVA_REFRESH_TOKEN"
echo "  STRAVA_ACCESS_TOKEN"
if [[ -n "${EXPIRES_AT}" && "${EXPIRES_AT}" != "null" ]]; then
  echo "  STRAVA_ACCESS_TOKEN_EXPIRES_AT (UNIX timestamp)"
fi

echo
echo "When the access token expires, refresh it with:"
cat <<'EOF'
export STRAVA_ACCESS_TOKEN="$(curl -s -X POST https://www.strava.com/oauth/token \
  -d client_id=$STRAVA_CLIENT_ID \
  -d client_secret=$STRAVA_CLIENT_SECRET \
  -d grant_type=refresh_token \
  -d refresh_token=$STRAVA_REFRESH_TOKEN | jq -r '.access_token')"
EOF

return 0
