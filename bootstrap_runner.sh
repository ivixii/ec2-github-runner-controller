#!/bin/bash
set -e

RUNNER_BASE="/opt/github-runner"
RUNNER_BIN="$RUNNER_BASE/bin"
RUNNER_DATA="$RUNNER_BASE/data"

sudo mkdir -p "$RUNNER_BIN" "$RUNNER_DATA"
sudo chown "$(whoami)" "$RUNNER_BASE" -R

echo "Downloading runner binaries to $RUNNER_BIN"

LATEST_VERSION=$(curl -s https://api.github.com/repos/actions/runner/releases/latest | jq -r '.tag_name')
TARBALL="actions-runner-linux-x64-$LATEST_VERSION.tar.gz"
DOWNLOAD_URL="https://github.com/actions/runner/releases/download/$LATEST_VERSION/$TARBALL"

curl -L -o "$TARBALL" "$DOWNLOAD_URL"
tar xzf "$TARBALL" -C "$RUNNER_BIN"
rm "$TARBALL"

echo "Runner binaries ready in $RUNNER_BIN"