#!/usr/bin/env bash
# Checks run by CI on Linux, macOS and Windows (and locally, with no hardware).
# Requires: uv.
set -euo pipefail
cd "$(dirname "$0")/.."

uv sync --locked
uv run pytest -q
echo "ci-check: PASS"
