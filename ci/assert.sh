#!/usr/bin/env bash
set -e

OK=$(grep -c "^200$" responses.txt || true)
TOO_MANY=$(grep -c "^429$" responses.txt || true)

echo "200 responses: $OK"
echo "429 responses: $TOO_MANY"

if [ "$OK" -ne 5 ]; then
  echo "❌ Expected exactly 5 successful requests"
  exit 1
fi

if [ "$TOO_MANY" -lt 1 ]; then
  echo "❌ Rate limiting did not trigger"
  exit 1
fi

echo "✅ Token bucket behavior verified"
