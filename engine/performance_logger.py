import time

def log_performance(state: dict):
    state["last_update_ts"] = time.time()
    return state
