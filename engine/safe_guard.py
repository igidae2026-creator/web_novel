
from __future__ import annotations
import os

from .safe_logger import log_event

class UnsafeOperationError(Exception):
    pass

def require_safe_mode(cfg: dict):
    if not bool(cfg.get("safe_mode", False)):
        log_event('.', 'ERROR', 'Restore blocked: safe_mode disabled')
        raise UnsafeOperationError("Operation blocked: safe_mode must be enabled.")

def block_destructive_action(cfg: dict, action_name: str):
    if bool(cfg.get("safe_mode", False)):
        log_event('.', 'WARN', f"Blocked destructive action: {action_name}")
        raise UnsafeOperationError(f"Destructive action '{action_name}' blocked in safe_mode.")
