import re
from typing import Tuple, Dict

def normalize_space(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())

def validate_viral(meta: Dict) -> Tuple[bool, str]:
    quote_line = normalize_space(meta.get("quote_line",""))
    comment_hook = normalize_space(meta.get("comment_hook",""))
    cliffhanger = normalize_space(meta.get("cliffhanger",""))
    if not quote_line or len(quote_line) < 8:
        return False, "quote_line missing/too short"
    if not comment_hook or len(comment_hook) < 8:
        return False, "comment_hook missing/too short"
    if not cliffhanger or len(cliffhanger) < 8:
        return False, "cliffhanger missing/too short"
    return True, "ok"
