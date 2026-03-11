import os, shutil, json, hashlib, datetime
from typing import List, Optional, Dict, Any
from .safe_io import backup_current_state
from .safe_guard import require_safe_mode
from .backup_retention import enforce_retention

BACKUP_ROOT = "global_backups"

def _ts() -> str:
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

def _hash_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(8192)
            if not b:
                break
            h.update(b)
    return h.hexdigest()

def snapshot_project(project_dir: str, extra_paths: Optional[List[str]] = None, tag: str = "snapshot") -> Optional[str]:
    """Create a full snapshot of project_dir into project_dir/global_backups/<ts>_<tag>/.
    Also copies extra_paths (if exist) under _external/ preserving filenames.
    Returns timestamp folder name.
    """
    if not project_dir or not os.path.exists(project_dir):
        return None

    stamp = f"{_ts()}_{tag}"
    backup_root = os.path.join(project_dir, BACKUP_ROOT)
    backup_dir = os.path.join(backup_root, stamp)
    os.makedirs(backup_dir, exist_ok=True)

    manifest: Dict[str, Any] = {"timestamp": stamp, "files": [], "external": []}

    # Copy internal project files
    for root, _, files in os.walk(project_dir):
        if BACKUP_ROOT in root:
            continue
        for fn in files:
            src = os.path.join(root, fn)
            rel = os.path.relpath(src, project_dir)
            dst = os.path.join(backup_dir, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            manifest["files"].append({"path": rel, "hash": _hash_file(src)})

    # Copy external paths (rank_signals etc)
    if extra_paths:
        ext_dir = os.path.join(backup_dir, "_external")
        os.makedirs(ext_dir, exist_ok=True)
        for p in extra_paths:
            if not p:
                continue
            p = os.path.normpath(p)
            if os.path.exists(p) and os.path.isfile(p):
                dst = os.path.join(ext_dir, os.path.basename(p))
                shutil.copy2(p, dst)
                manifest["external"].append({"path": p, "copied_as": os.path.basename(p), "hash": _hash_file(p)})

    with open(os.path.join(backup_dir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    enforce_retention(project_dir)
    return stamp

def _verify_snapshot(project_dir: str, backup_dir: str) -> bool:
    manifest_path = os.path.join(backup_dir, "manifest.json")
    if not os.path.exists(manifest_path):
        return False
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # Verify internal files
    for item in manifest.get("files", []):
        rel = item.get("path")
        expected = item.get("hash")
        if not rel or not expected:
            continue
        cur = os.path.join(project_dir, rel)
        if not os.path.exists(cur):
            return False
        if _hash_file(cur) != expected:
            return False
    # external not verified here (they may live outside project_dir)
    return True

def restore_snapshot(project_dir: str, timestamp: str, extra_restore_targets: Optional[List[str]] = None, cfg: Optional[dict] = None) -> bool:
    if cfg is not None:
        require_safe_mode(cfg)

    """Restore snapshot. Before restore, take a full pre_restore snapshot.
    After restore, verify hashes; if fail, rollback to pre_restore snapshot.
    If snapshot has _external files and extra_restore_targets provided, copy back by basename match.
    """
    if not project_dir:
        return False

    backup_root = os.path.join(project_dir, BACKUP_ROOT)
    backup_dir = os.path.join(backup_root, timestamp)
    if not os.path.exists(backup_dir):
        return False

    # Pre-restore safety snapshots
    backup_current_state(project_dir, tag="pre_restore")
    pre = snapshot_project(project_dir, extra_paths=None, tag="pre_restore_full")  # rollback point

    # Restore internal files
    for root, _, files in os.walk(backup_dir):
        if os.path.basename(root) == "_external":
            continue
        for fn in files:
            if fn == "manifest.json":
                continue
            src = os.path.join(root, fn)
            rel = os.path.relpath(src, backup_dir)
            dst = os.path.join(project_dir, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)

    # Restore external if requested
    ext_dir = os.path.join(backup_dir, "_external")
    if os.path.isdir(ext_dir) and extra_restore_targets:
        for t in extra_restore_targets:
            if not t:
                continue
            base = os.path.basename(t)
            src = os.path.join(ext_dir, base)
            if os.path.exists(src):
                os.makedirs(os.path.dirname(t), exist_ok=True)
                shutil.copy2(src, t)

    # Verify, else rollback
    ok = _verify_snapshot(project_dir, backup_dir)
    if ok:
        return True

    # rollback
    if pre:
        pre_dir = os.path.join(backup_root, pre)
        if os.path.exists(pre_dir):
            for root2, _, files2 in os.walk(pre_dir):
                if os.path.basename(root2) == "_external":
                    continue
                for fn2 in files2:
                    if fn2 == "manifest.json":
                        continue
                    src2 = os.path.join(root2, fn2)
                    rel2 = os.path.relpath(src2, pre_dir)
                    dst2 = os.path.join(project_dir, rel2)
                    os.makedirs(os.path.dirname(dst2), exist_ok=True)
                    shutil.copy2(src2, dst2)
    return False
