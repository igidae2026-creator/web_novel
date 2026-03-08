import yaml
from .safe_io import safe_write_text
from copy import deepcopy

def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def save_config(path: str, cfg: dict, safe_mode: bool = False, project_dir_for_backup: str | None = None):
    txt = yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True)
    safe_write_text(path, txt, safe_mode=safe_mode, project_dir_for_backup=project_dir_for_backup)

def deep_merge(base: dict, override: dict) -> dict:
    out = deepcopy(base)
    def _merge(a, b):
        for k, v in b.items():
            if isinstance(v, dict) and isinstance(a.get(k), dict):
                _merge(a[k], v)
            else:
                a[k] = v
    _merge(out, override)
    return out
