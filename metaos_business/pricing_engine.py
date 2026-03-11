from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class PricingScenario:
    episode_price: float
    bundle_size: int
    bundle_discount: float  # 0~1
    purchasers: int
    avg_bundles_per_user: float

    def expected_revenue(self) -> float:
        ep_price = max(0.0, float(self.episode_price))
        bs = max(1, int(self.bundle_size))
        disc = min(0.95, max(0.0, float(self.bundle_discount)))
        # Effective price per bundle
        bundle_price = ep_price * bs * (1.0 - disc)
        return float(self.purchasers) * max(0.0, float(self.avg_bundles_per_user)) * bundle_price

def simulate_pricing_grid(
    base_purchasers: int,
    episode_prices: List[float],
    bundle_sizes: List[int],
    bundle_discounts: List[float],
    avg_bundles_per_user: float = 1.0,
) -> List[Dict]:
    out = []
    for p in episode_prices:
        for bs in bundle_sizes:
            for d in bundle_discounts:
                sc = PricingScenario(
                    episode_price=p,
                    bundle_size=bs,
                    bundle_discount=d,
                    purchasers=base_purchasers,
                    avg_bundles_per_user=avg_bundles_per_user,
                )
                out.append({
                    "episode_price": p,
                    "bundle_size": bs,
                    "bundle_discount": d,
                    "expected_revenue": sc.expected_revenue(),
                })
    out.sort(key=lambda x: x["expected_revenue"], reverse=True)
    return out
