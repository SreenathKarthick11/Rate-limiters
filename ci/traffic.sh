#!/usr/bin/env bash
set -e

mkdir -p ci/results

run_traffic () {
  local name=$1
  local url=$2

  echo "Running traffic for $name"

  > ci/results/${name}.txt

  for i in {1..100}; do
    curl -s -o /dev/null -w "%{http_code}\n" \
      http://localhost:8000${url} >> ci/results/${name}.txt
    sleep 0.1
  done
}

run_traffic token_bucket /token_bucket
sleep 2
run_traffic leaky_bucket /leaky_bucket
sleep 2
run_traffic fixed_window_counter /fixed_window_counter
sleep 2
run_traffic sliding_window_log /sliding_window_log
sleep 2
run_traffic sliding_window_counter /sliding_window_counter