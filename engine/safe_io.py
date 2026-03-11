from __future__ import annotations
import os, shutil, datetime
from typing import Optional

# Files that are allowed to overwrite in safe_mode, but must be snapshotted before overwrite.
ALLOW_OVERWRITE_WITH_BACKUP = {
    "state.json",
    "config.yaml",
    "rank_signals.csv",
    "metrics.jsonl",   # append is preferred; overwrite should be avoided
    "cost_summary.json",
    "final_threshold_eval.json",
    "queue_state.json",
    "job_queue.json",
    "supervisor_state.json",
    "admission_state.json",
    "promotion_state.json",
    "queue_history.json",
}

def _ts() -> str:
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

def versioned_path(path: str) -> str:
    root, ext = os.path.splitext(path)
    n = 2
    candidate = f"{root}_v{n}{ext}"
    while os.path.exists(candidate):
        n += 1
        candidate = f"{root}_v{n}{ext}"
    return candidate

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def backup_current_state(project_dir: str, tag: str = "pre_restore") -> Optional[str]:
    """Lightweight backup of current state/config/rank into project_dir/global_backups/<ts>_<tag>/"""
    if not project_dir or not os.path.isdir(project_dir):
        return None
    backup_root = os.path.join(project_dir, "global_backups")
    ensure_dir(backup_root)
    stamp = f"{_ts()}_{tag}"
    dest = os.path.join(backup_root, stamp)
    ensure_dir(dest)
    for fn in ("state.json", "config.yaml"):
        src = os.path.join(project_dir, fn)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(dest, fn))
    # rank signals usually live under ../data; caller can optionally pass those in separately
    return dest

def safe_write_text(path: str, text: str, safe_mode: bool, project_dir_for_backup: Optional[str] = None) -> str:
    """Write text to path. If safe_mode and path exists, block overwrite by writing to a versioned file,
    except for allowlist files which are backed up (if project_dir provided) then overwritten.
    Returns the actual path written.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    base = os.path.basename(path)

    if safe_mode and os.path.exists(path):
        if base == "config.yaml" and BLOCK_CONFIG_OVERWRITE and safe_mode:
            raise Exception("Config overwrite blocked in safe_mode.")
        if base in ALLOW_OVERWRITE_WITH_BACKUP:
            if project_dir_for_backup:
                backup_current_state(project_dir_for_backup, tag=f"pre_overwrite_{base}")
            # overwrite allowed for these critical files
        else:
            path = versioned_path(path)

    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path

def safe_copy_bytes(path: str, data: bytes, safe_mode: bool, project_dir_for_backup: Optional[str] = None) -> str:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    base = os.path.basename(path)
    if safe_mode and os.path.exists(path):
        if base == "config.yaml" and BLOCK_CONFIG_OVERWRITE and safe_mode:
            raise Exception("Config overwrite blocked in safe_mode.")
        if base in ALLOW_OVERWRITE_WITH_BACKUP:
            if project_dir_for_backup:
                backup_current_state(project_dir_for_backup, tag=f"pre_overwrite_{base}")
        else:
            path = versioned_path(path)
    with open(path, "wb") as f:
        f.write(data)
    return path


def safe_append_text(path: str, text: str, safe_mode: bool, project_dir_for_backup: Optional[str] = None) -> str:
    """Append text safely. In safe_mode, can snapshot once before append."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if safe_mode and os.path.exists(path) and project_dir_for_backup:
        backup_current_state(project_dir_for_backup, tag="pre_append")
    with open(path, "a", encoding="utf-8") as f:
        f.write(text)
    return path


# Hard block config overwrite in safe_mode unless explicitly backed up
BLOCK_CONFIG_OVERWRITE = True
