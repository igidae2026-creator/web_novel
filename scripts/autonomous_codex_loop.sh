#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-/home/meta_os/web_novel}"
MAX_CYCLES="${MAX_CYCLES:-5}"
PROMPT_FILE="${PROMPT_FILE:-$ROOT/prompts/autonomous_webnovel_loop.txt}"
STATE_DIR="${STATE_DIR:-$ROOT/ops/autonomous_loop}"
LOG_DIR="$STATE_DIR/logs"
LEDGER="$STATE_DIR/iteration_ledger.jsonl"

mkdir -p "$LOG_DIR"

cd "$ROOT"

if [[ ! -f "$PROMPT_FILE" ]]; then
  echo "missing prompt file: $PROMPT_FILE" >&2
  exit 1
fi

if ! command -v codex >/dev/null 2>&1; then
  echo "codex CLI not found" >&2
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not found" >&2
  exit 1
fi

for ((cycle=1; cycle<=MAX_CYCLES; cycle++)); do
  ts="$(date +%Y%m%d_%H%M%S)"
  run_dir="$LOG_DIR/$ts"
  mkdir -p "$run_dir"

  python3 - <<'PY' > "$run_dir/preflight_validator.json"
from engine.integrated_validator import run_all
import json
print(json.dumps(run_all("."), ensure_ascii=False, indent=2))
PY

  codex exec -C "$ROOT" --skip-git-repo-check --output-last-message "$run_dir/codex_last_message.txt" - < "$PROMPT_FILE" > "$run_dir/codex_stdout.txt"

  python3 - <<'PY' > "$run_dir/postflight_validator.json"
from engine.integrated_validator import run_all
import json
print(json.dumps(run_all("."), ensure_ascii=False, indent=2))
PY

  python3 - <<PY >> "$LEDGER"
import json
entry = {
    "timestamp": "$ts",
    "cycle": $cycle,
    "prompt_file": "$PROMPT_FILE",
    "run_dir": "$run_dir",
}
print(json.dumps(entry, ensure_ascii=False))
PY

  echo "cycle $cycle complete: $run_dir"
done
