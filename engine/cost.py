import os, json
from datetime import datetime
from .safe_io import safe_write_text

class CostTracker:
    def __init__(self, cfg: dict, out_dir: str):
        self.cfg = cfg
        self.out_dir = out_dir
        self.input_tokens = 0
        self.output_tokens = 0

    def add_usage(self, resp):
        usage = getattr(resp, "usage", None)
        if usage is None:
            return
        self.input_tokens += int(getattr(usage, "input_tokens", 0) or 0)
        self.output_tokens += int(getattr(usage, "output_tokens", 0) or 0)

    def prices(self):
        prices = self.cfg["model"]["prices_per_1m"]
        mode = self.cfg["model"].get("mode", "batch").lower()
        mul = 4.0 if mode == "priority" else 1.0
        return {
            "input": float(prices["input"]) * mul,
            "output": float(prices["output"]) * mul,
            "cached_input": float(prices.get("cached_input", 0.0)) * mul
        }

    def cost_usd(self):
        p = self.prices()
        return (self.input_tokens / 1_000_000) * p["input"] + (self.output_tokens / 1_000_000) * p["output"]

    def snapshot(self):
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.input_tokens + self.output_tokens,
            "cost_usd": round(self.cost_usd(), 6)
        }

    def enforce_token_ceiling(self):
        ceiling = int(self.cfg["limits"]["token_ceiling_total"])
        total = self.input_tokens + self.output_tokens
        if total > ceiling:
            raise RuntimeError(f"Token ceiling exceeded: {total} > {ceiling}")

    def write_summary(self):
        path = os.path.join(self.out_dir, "cost_summary.json")
        data = {"ts": datetime.now().isoformat(timespec="seconds"), **self.snapshot(), "pricing": self.prices()}
        os.makedirs(os.path.dirname(path), exist_ok=True)
        safe_write_text(path, json.dumps(data, ensure_ascii=False, indent=2), safe_mode=bool(self.cfg.get('safe_mode', False)), project_dir_for_backup=self.out_dir)
