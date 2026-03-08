import os, json
from .safe_io import safe_write_text
from typing import Any

class StateStore:
    def __init__(self, path: str, safe_mode: bool = False, project_dir_for_backup: str | None = None):
        self.path = path
        self.safe_mode = bool(safe_mode)
        self.project_dir_for_backup = project_dir_for_backup
        self.data: dict[str, Any] = {}

    def load(self):
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        else:
            self.data = {}
        self.data.setdefault('phase', 'STABILIZE')
        self.data.setdefault('phase_cooldown', 0)

    def save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        txt = json.dumps(self.data, ensure_ascii=False, indent=2)
        safe_write_text(self.path, txt, safe_mode=self.safe_mode, project_dir_for_backup=self.project_dir_for_backup)

    def get(self, key: str, default=None):
        return self.data.get(key, default)

    def set(self, key: str, value):
        self.data[key] = value

    def reset(self):
        self.data = {}
        self.data.setdefault('phase', 'STABILIZE')
        self.data.setdefault('phase_cooldown', 0)
        self.save()
