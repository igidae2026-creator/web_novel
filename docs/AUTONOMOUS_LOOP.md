# Autonomous Loop

This repository now includes a WSL-oriented Codex loop runner.

## Files

- `prompts/autonomous_webnovel_loop.txt`
- `scripts/autonomous_codex_loop.sh`
- `ops/autonomous_loop/`

## Purpose

Run a bounded autonomous improvement cycle without continuous user intervention.

Each cycle:
- runs repo-truth validation before changes
- invokes `codex` with the repository prompt
- stores the last Codex message and stdout logs
- runs repo-truth validation again
- records a ledger entry

## Usage

```bash
cd /home/meta_os/web_novel
scripts/bootstrap_wsl_env.sh
chmod +x scripts/autonomous_codex_loop.sh
MAX_CYCLES=3 scripts/autonomous_codex_loop.sh
```

## Outputs

- per-cycle logs: `ops/autonomous_loop/logs/<timestamp>/`
- iteration ledger: `ops/autonomous_loop/iteration_ledger.jsonl`

## Stop Model

This loop is intentionally bounded by `MAX_CYCLES`.

For long unattended runs, use a small cycle count first and inspect:
- `postflight_validator.json`
- `codex_last_message.txt`
- changed files

## Current Limitations

- the loop improves the repo, but it does not yet auto-rollback on semantic regression
- long unattended runs should still be started with a small `MAX_CYCLES` first
