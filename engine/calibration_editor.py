
from __future__ import annotations
import yaml, difflib

def preview_diff(existing: dict, new: dict) -> str:
    before = yaml.safe_dump(existing, allow_unicode=True).splitlines()
    after = yaml.safe_dump(new, allow_unicode=True).splitlines()
    return "\n".join(difflib.unified_diff(before, after, fromfile="existing", tofile="new", lineterm=""))
