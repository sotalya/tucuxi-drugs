#!/usr/bin/env bash
set -euo pipefail

: "${REPO_ROOT:?REPO_ROOT must be set by entrypoint}"

: "${CONFIG:=debug}"
: "${COVERAGE_MODE:=0}"
: "${BUILD_ROOT:=$REPO_ROOT/build}"
: "${PYTHON_BIN:=python3}"

SCRIPT_DIR="$REPO_ROOT/scripts/linux/"

die() {
  local msg="$1"; local code="${2:-1}"
  echo "==> ERROR: $msg" >&2
  exit "$code"
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "missing command '$1' (install it and retry)"
}

portable_nproc() {
  if command -v nproc >/dev/null 2>&1; then
    nproc
  elif sysctl -n hw.ncpu >/dev/null 2>&1; then
    sysctl -n hw.ncpu
  else
    echo 1
  fi
}

usage() {
  cat <<'EOF'
Usage:
  ./scripts/linux/run <command>

Commands:

  py-env          Print activation command for .venv
  py-deps         Install python deps into .venv
  setup           Copy git hooks to .git/hooks

  help
EOF
}

