
import os
import shutil
from datetime import datetime

BACKUP_ROOT = "global_backups"

def _parse_ts(name: str):
    try:
        # YYYYMMDD_HHMMSS_tag
        base = name.split("_")[0]
        return datetime.strptime(base, "%Y%m%d")
    except Exception:
        return None

def enforce_retention(project_dir: str, keep_last: int = 20, keep_daily: int = 7, keep_weekly: int = 4):
    root = os.path.join(project_dir, BACKUP_ROOT)
    if not os.path.exists(root):
        return

    snapshots = sorted(os.listdir(root))
    if not snapshots:
        return

    # Keep last N snapshots always
    keep = set(snapshots[-keep_last:])

    # Daily retention
    daily_map = {}
    for s in snapshots:
        dt = _parse_ts(s)
        if not dt:
            continue
        key = dt.strftime("%Y-%m-%d")
        daily_map[key] = s

    daily_keep = list(daily_map.values())[-keep_daily:]
    keep.update(daily_keep)

    # Weekly retention (ISO week)
    weekly_map = {}
    for s in snapshots:
        dt = _parse_ts(s)
        if not dt:
            continue
        key = f"{dt.year}-W{dt.isocalendar()[1]}"
        weekly_map[key] = s

    weekly_keep = list(weekly_map.values())[-keep_weekly:]
    keep.update(weekly_keep)

    # Remove others
    for s in snapshots:
        if s not in keep:
            full = os.path.join(root, s)
            try:
                shutil.rmtree(full)
            except Exception:
                pass
