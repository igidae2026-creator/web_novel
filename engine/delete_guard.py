
import os
from .safe_guard import block_destructive_action

def safe_delete(path: str, cfg: dict):
    block_destructive_action(cfg, f"delete:{path}")
