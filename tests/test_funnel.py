from metaos_business.revenue_funnel import compute_funnel

def test_compute_funnel():
    f = compute_funnel({"exposures": "100", "clicks": "10", "purchases": "2", "repurchases": "1"})
    assert f.exposures == 100
    assert abs(f.ctr - 0.1) < 1e-9
    assert abs(f.cvr - 0.2) < 1e-9
    assert abs(f.repurchase_rate - 0.5) < 1e-9
