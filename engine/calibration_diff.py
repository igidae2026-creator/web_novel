
from __future__ import annotations
import yaml, difflib

def diff_text(before: str, after: str) -> str:
    b=before.splitlines()
    a=after.splitlines()
    return "\n".join(difflib.unified_diff(b,a,fromfile="before",tofile="after",lineterm=""))
