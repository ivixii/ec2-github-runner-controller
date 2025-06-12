#!/bin/bash

set -e

if [[ -z "$GH_REPO_URL" || -z "$GH_RUNNER_TOKEN" ]]; then
  echo "Missing GH_REPO_URL or GH_RUNNER_TOKEN"
  exit 1
fi

REPO_NAME=$(basename "$GH_REPO_URL")
REPO_OWNER=$(basename $(dirname "$GH_REPO_URL"))
RUNNER_NAME=$(hostname)-$RANDOM

cd /runner

# Clean up previous runner if exists
if [ -d ".runner" ]; then
  ./config.sh remove --unattended --token "$GH_RUNNER_TOKEN" || true
  rm -rf .runner
fi

./config.sh \
  --url "$GH_REPO_URL" \
  --token "$GH_RUNNER_TOKEN" \
  --name "$RUNNER_NAME" \
  --labels "$LABELS" \
  --work "/runner/_work" \
  --unattended

cleanup() {
  echo "Caught signal, removing runner..."
  ./config.sh remove --unattended --token "$GH_RUNNER_TOKEN"
  exit 0
}

trap cleanup SIGINT SIGTERM

./run.sh
