#!/usr/bin/env bash
set -euo pipefail

BASE=${E2E_BASE:-http://localhost:5000}

login() {
  local user=$1 pass=$2
  curl -s "$BASE/auth/login" -H 'Content-Type: application/json' \
    -d "{\"username\":\"$user\",\"password\":\"$pass\"}" | jq -r .access_token
}

ADMIN_TOK=$(login admin dwang1237)
EMP_TOK=$(login slave admin)

echo "Admin token: ${ADMIN_TOK:0:12}..."
echo "Employee token: ${EMP_TOK:0:12}..."

echo "== Sets (admin) =="
curl -s "$BASE/admin/sets" -H "Authorization: Bearer $ADMIN_TOK" | jq .

echo "== Stats (admin) =="
curl -s "$BASE/stats/sets?hours=72" -H "Authorization: Bearer $ADMIN_TOK" | jq .

echo "== Recent bets (admin) =="
curl -s "$BASE/bets/recent?hours=72" -H "Authorization: Bearer $ADMIN_TOK" | jq .

echo "== Upload (employee) =="
curl -s -X POST "$BASE/bets/upload" \
  -H "Authorization: Bearer $EMP_TOK" \
  -F set_id=1 \
  -F bookmaker_name=Sportsbet \
  -F stake_manual=25.00 \
  -F image=@tests/samples/sportsbet_sample.png | jq .