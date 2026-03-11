#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-/home/meta_os/web_novel}"
VENV_DIR="${VENV_DIR:-$ROOT/.venv}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

cd "$ROOT"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "python interpreter not found: $PYTHON_BIN" >&2
  exit 1
fi

"$PYTHON_BIN" -m venv "$VENV_DIR"
# shellcheck disable=SC1090
source "$VENV_DIR/bin/activate"

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python verify_install.py

cat <<'EOF'

Environment bootstrap complete.

Next steps:
  source .venv/bin/activate
  pytest -q
  streamlit run app.py
  MAX_CYCLES=3 scripts/autonomous_codex_loop.sh
EOF
