
import os
from engine.safe_io import safe_append_text
import datetime

LOG_FILE = "safety_events.log"

def log_event(project_dir: str, level: str, message: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {message}\n"
    path = os.path.join(project_dir, LOG_FILE)
    safe_append_text(path, line, safe_mode=True, project_dir_for_backup=project_dir)
