def top_percent_from_rank(rank: int, chart_size: int) -> float:
    n = max(1, int(chart_size))
    r = max(1, int(rank))
    return (r / n) * 100.0

def band_from_top_percent(p: float) -> str:
    p = float(p)
    if p <= 1.0:
        return "Top 1%"
    if p <= 3.0:
        return "Top 1-3%"
    if p <= 5.0:
        return "Top 3-5%"
    if p <= 10.0:
        return "Top 5-10%"
    if p <= 20.0:
        return "Top 10-20%"
    return "Top 20%+"
