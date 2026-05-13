#!/usr/bin/env bash
set -euo pipefail
source "$REPO_ROOT/scripts/linux/common/common.sh"


cmd_setup() {
    echo "==> Copying hooks to .git/hooks"
    cp "$REPO_ROOT/scripts/hooks/"* "$REPO_ROOT/.git/hooks/"
    echo "==> Setup complete"
}
