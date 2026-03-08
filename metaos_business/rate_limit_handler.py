from __future__ import annotations
import time
from dataclasses import dataclass

@dataclass
class RateLimitState:
    last_call_ts: float = 0.0
    min_interval_sec: float = 0.2

class RateLimitHandler:
    def __init__(self, min_interval_sec: float = 0.2):
        self.state = RateLimitState(min_interval_sec=float(min_interval_sec))

    def wait(self):
        now = time.time()
        elapsed = now - self.state.last_call_ts
        if elapsed < self.state.min_interval_sec:
            time.sleep(self.state.min_interval_sec - elapsed)
        self.state.last_call_ts = time.time()
