#!/usr/bin/env bash
set -e

URL="http://localhost:8000/limited"

> responses.txt

for i in {1..7}; do
  curl -s -o /dev/null -w "%{http_code}\n" "$URL" >> responses.txt
done

cat responses.txt
