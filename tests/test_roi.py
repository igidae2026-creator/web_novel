from metaos_business.roi_optimizer import compute_roi, select_best_campaign

def test_roi():
    r = compute_roi(100, 150)
    assert abs(r.roi - 0.5) < 1e-9

def test_best_campaign():
    best = select_best_campaign([
        {"campaign":"a","spend":100,"revenue":110},
        {"campaign":"b","spend":100,"revenue":200},
    ])
    assert best["campaign"] == "b"
