#!/usr/bin/env sh
set -eu

API_URL="${API_URL:-http://localhost:8000}"
WEB_URL="${WEB_URL:-http://localhost:3000}"

printf 'Checking API health...\n'
curl --fail --silent --show-error "$API_URL/health"
printf '\nAPI is healthy.\n'

printf 'Checking web app...\n'
curl --fail --silent --show-error --output /dev/null "$WEB_URL"
printf 'Web app is reachable.\n'

printf 'Creating a sample saved search...\n'
curl --fail --silent --show-error \
  -H 'Content-Type: application/json' \
  -d '{
    "name":"Local San Diego vehicle search",
    "category":"vehicles",
    "keywords":["Toyota"],
    "exclude_keywords":["salvage"],
    "min_price":5000,
    "max_price":20000,
    "notify_threshold":80,
    "locations":[{
      "country_code":"US",
      "state_code":"CA",
      "city":"San Diego",
      "latitude":32.7157,
      "longitude":-117.1611,
      "radius_miles":50
    }]
  }' \
  "$API_URL/api/v1/searches"
printf '\nSmoke test passed.\n'
