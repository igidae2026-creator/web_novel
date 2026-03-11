import json
from typing import Tuple, Any

def parse_json_strict(text: str) -> Tuple[bool, Any]:
    s = (text or "").strip()
    try:
        return True, json.loads(s)
    except Exception:
        # attempt to salvage: find first {...} block
        start = s.find("{")
        end = s.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return True, json.loads(s[start:end+1])
            except Exception:
                pass
    return False, s
