# Environment Setup

Use WSL for this repository.

## One-shot bootstrap

```bash
cd /home/meta_os/web_novel
chmod +x scripts/bootstrap_wsl_env.sh
scripts/bootstrap_wsl_env.sh
```

## Manual equivalent

```bash
cd /home/meta_os/web_novel
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python verify_install.py
```

## After bootstrap

Run tests:

```bash
source .venv/bin/activate
pytest -q
```

Run app:

```bash
source .venv/bin/activate
streamlit run app.py
```

Run bounded autonomous loop:

```bash
source .venv/bin/activate
MAX_CYCLES=3 scripts/autonomous_codex_loop.sh
```
