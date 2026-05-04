#!/usr/bin/env bash
set -euo pipefail

export PATH="$HOME/.local/bin:$PATH"
export PLAYWRIGHT_BROWSERS_PATH="${PLAYWRIGHT_BROWSERS_PATH:-$HOME/Library/Caches/ms-playwright}"

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required but was not found on PATH." >&2
  exit 1
fi

args=("$@")

if [[ -n "${NOTEBOOKLM_STORAGE_PATH:-}" ]]; then
  exec uvx --python 3.13 --with playwright --from notebooklm-py notebooklm --storage "$NOTEBOOKLM_STORAGE_PATH" "${args[@]}"
fi

exec uvx --python 3.13 --with playwright --from notebooklm-py notebooklm "${args[@]}"
