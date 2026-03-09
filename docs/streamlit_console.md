# Streamlit Production Console

`app.py` remains the legacy or test UI.

`console_app.py` is the primary operator console.

The console UI is now split into modular panel files under `ui/` while the root `console_app.py` remains the single entrypoint.

## UI Module Structure

```text
ui/
  console_app.py
  panels/
    dashboard.py
    project_setup.py
    generation_control.py
    track_portfolio.py
    release_scheduler.py
    quality_reliability.py
    outputs_viewer.py
    shared.py
```

## How It Works

The console does not embed core generation logic in Streamlit code.

- Streamlit writes runtime settings to `runtime_config.json`
- Streamlit requests actions through `outputs/policy_action.json`
- Engine control-plane code reads those files and runs the requested action
- Runtime status is reflected through `outputs/system_status.json`
- Episode outputs and metrics are read from `tracks/*/outputs/*` and `metrics.jsonl`
- Project switching updates project-specific paths inside `runtime_config.json`

## Main Sections

- Home dashboard
- Project Setup
- Generation Control
- Track / Portfolio
- Release Scheduler
- Quality / Reliability
- Outputs Review

The console is Korean-first by default and supports a Korean/English toggle.

It also supports:

- simple mode for daily operation
- advanced mode for full runtime tuning
- confirmation flow for high-impact actions
- runtime snapshots and stable restore
- operator override actions through the file-based control plane
- lightweight generated episode review

## One-Click Actions

- One-click Generate
- One-click Auto Loop
- One-click Release Plan
- One-click Reliability Check
- One-click Stop / Pause

## Running

```bash
streamlit run console_app.py
```

The legacy UI is still available:

```bash
streamlit run app.py
```
