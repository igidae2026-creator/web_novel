def governance_check(state: dict):
    if state.get("fitness",0) < 0.4:
        state["governance_alert"] = "LOW_FITNESS"
    return state
