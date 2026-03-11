
import os, shutil, datetime

def backup_file(path: str):
    if not os.path.exists(path):
        return
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(os.path.dirname(path), "backups")
    os.makedirs(backup_dir, exist_ok=True)
    fname = os.path.basename(path)
    new_path = os.path.join(backup_dir, f"{ts}_{fname}")
    shutil.copy2(path, new_path)
