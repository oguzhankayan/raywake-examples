#!/usr/bin/env bash
# Quote, generate and poll one Raywake generation with curl and jq.
# Step 1 is free. Steps 2 and 3 run only with --generate.
#
#   export RAYWAKE_API_KEY=...
#   ./quickstart.sh             # price only
#   ./quickstart.sh --generate  # spend the quote and wait for the result
set -euo pipefail

BASE="${RAYWAKE_API_BASE:-https://api.raywake.com}"
AUTH="Authorization: Bearer ${RAYWAKE_API_KEY:?Set RAYWAKE_API_KEY}"
PAYLOAD='{"model":"kling/v4/text-to-video","input":{"prompt":"A perfume bottle on a stone table. Slow camera push in, soft window light, one continuous shot.","duration":5,"resolution":"720p","aspect_ratio":"16:9"}}'

# 1. Price the exact input (quotes are valid for up to 10 minutes)
QUOTE=$(curl -sS --fail-with-body "$BASE/v1/quotes" -H "$AUTH" -H "Content-Type: application/json" -d "$PAYLOAD")
echo "$QUOTE" | jq '{quote_id, price_usd, expires_at}'
[ "${1:-}" = "--generate" ] || { echo "Run again with --generate to start this generation."; exit 0; }

# 2. Start the generation with the quote_id from step 1
BODY=$(echo "$PAYLOAD" | jq --arg q "$(echo "$QUOTE" | jq -r .quote_id)" '. + {quote_id: $q}')
JOB=$(curl -sS --fail-with-body "$BASE/v1/generate" -H "$AUTH" -H "Content-Type: application/json" \
  -H "Idempotency-Key: $(uuidgen)" -d "$BODY")
JOB_ID=$(echo "$JOB" | jq -r .job_id)

# 3. Poll until the status is terminal
while :; do
  JOB=$(curl -sS --fail-with-body "$BASE/v1/jobs/$JOB_ID" -H "$AUTH")
  STATUS=$(echo "$JOB" | jq -r .status)
  echo "status: $STATUS"
  case "$STATUS" in succeeded|failed|needs_review|submission_unknown|needs_reconciliation) break ;; esac
  sleep 3
done
echo "$JOB" | jq -r '.outputs[]? | "\(.type) \(.url)"'
