def get_phase(cfg: dict) -> str:
    p = str(cfg.get("phase", "STABILIZE")).strip().upper()
    return "BOOST" if p == "BOOST" else "STABILIZE"
