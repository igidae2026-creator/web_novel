from __future__ import annotations
import os, json, datetime
from typing import Dict, Any
from engine.safe_io import safe_append_text

def _ts() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log_event(out_dir: str, event_type: str, payload: Dict[str, Any], safe_mode: bool = True) -> None:
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "events.jsonl")
    rec = {"ts": _ts(), "type": event_type, "payload": payload}
    safe_append_text(path, json.dumps(rec, ensure_ascii=False) + "\n", safe_mode=safe_mode, project_dir_for_backup=out_dir)

def read_recent(out_dir: str, n: int = 50) -> list[dict]:
    path = os.path.join(out_dir, "events.jsonl")
    if not os.path.exists(path):
        return []
    rows=[]
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line=line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                continue
    return rows[-max(1,int(n)):]
