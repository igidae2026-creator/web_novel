import random

def simulate_rank_distribution(current_top_percent: float, volatility: float = 0.1, runs: int = 100):
    results = []
    for _ in range(runs):
        noise = random.uniform(-volatility, volatility)
        simulated = max(0.1, current_top_percent + noise)
        results.append(simulated)
    results.sort()
    return {
        "p10": results[int(0.1*runs)],
        "p50": results[int(0.5*runs)],
        "p90": results[int(0.9*runs)]
    }
