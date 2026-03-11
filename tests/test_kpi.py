from metaos_business.revenue_funnel import FunnelMetrics
from metaos_business.kpi_engine import compute_kpi, cohort_retention

def test_kpi_basic():
    f = FunnelMetrics(exposures=1000, clicks=100, purchases=10, repurchases=2)
    k = compute_kpi(f, total_revenue=1000.0, paying_users=10, retention_d7=0.2)
    assert abs(k.ctr - 0.1) < 1e-9
    assert abs(k.cvr - 0.1) < 1e-9
    assert k.arppu == 100.0
    assert k.ltv > 0

def test_cohort_retention():
    rows = [
        {"day": 0, "active_users": 100},
        {"day": 1, "active_users": 50},
        {"day": 7, "active_users": 20},
    ]
    curve = cohort_retention(rows)
    assert abs(curve[0] - 1.0) < 1e-9
    assert abs(curve[1] - 0.5) < 1e-9
