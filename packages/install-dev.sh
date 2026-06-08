#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="${PY:-python3}"
PIP="${PIP:-$PY -m pip}"

echo "📦 Installing wup core..."
$PIP install -e "$ROOT"

PKGS=(
  uri2wup
  dsl2wup
  nlp2wup
  cli2wup
  mcp2wup
  rest2wup
)

for pkg in "${PKGS[@]}"; do
  echo "📦 Installing $pkg..."
  $PIP install -e "$ROOT/packages/$pkg[dev]"
done

echo "✅ Control layer packages installed."
