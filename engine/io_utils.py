import os, json, re
from .safe_io import safe_write_text, safe_append_text

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def safe_filename(name: str) -> str:
    name = name.strip()
    name = re.sub(r"[^a-zA-Z0-9._-]+", "_", name)
    return name[:120] if len(name) > 120 else name

def write_text(path: str, text: str, safe_mode: bool = False, project_dir_for_backup: str | None = None) -> str:
    return safe_write_text(path, text, safe_mode=safe_mode, project_dir_for_backup=project_dir_for_backup)

def append_jsonl(path: str, obj: dict, safe_mode: bool = False, project_dir_for_backup: str | None = None) -> str:
    line = json.dumps(obj, ensure_ascii=False) + "\n"
    return safe_append_text(path, line, safe_mode=safe_mode, project_dir_for_backup=project_dir_for_backup)

def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
