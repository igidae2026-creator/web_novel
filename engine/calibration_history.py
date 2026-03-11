from __future__ import annotations
import os, shutil, datetime

HISTORY_DIR = "config/models/calibration_edits"

def snapshot(path: str):
    if not os.path.exists(path):
        return None
    os.makedirs(HISTORY_DIR, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = os.path.join(HISTORY_DIR, f"{ts}.yaml")
    shutil.copy2(path, dest)
    return dest

def last_saved():
    if not os.path.exists(HISTORY_DIR):
        return None
    files = sorted(os.listdir(HISTORY_DIR))
    return files[-1] if files else None


def list_edits():
    if not os.path.exists(HISTORY_DIR):
        return []
    return sorted(os.listdir(HISTORY_DIR))

def restore_edit(filename: str, target_path: str):
    src = os.path.join(HISTORY_DIR, filename)
    if not os.path.exists(src):
        return False
    shutil.copy2(src, target_path)
    return True
