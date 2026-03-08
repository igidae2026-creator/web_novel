import re
from typing import Tuple, Dict
from .cliffhanger_engine import validate_cliffhanger

def normalize_space(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())

def validate_viral(meta: Dict, cliffhanger_plan: Dict | None = None) -> Tuple[bool, str]:
    quote_line = normalize_space(meta.get("quote_line",""))
    comment_hook = normalize_space(meta.get("comment_hook",""))
    cliffhanger = normalize_space(meta.get("cliffhanger",""))
    if not quote_line or len(quote_line) < 8:
        return False, "quote_line missing/too short"
    if not comment_hook or len(comment_hook) < 8:
        return False, "comment_hook missing/too short"
    valid_cliff, message = validate_cliffhanger(meta, cliffhanger_plan)
    if not cliffhanger or not valid_cliff:
        return False, message
    return True, "ok"
