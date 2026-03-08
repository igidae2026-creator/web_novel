def pivot_strategy(state: dict):
    fitness = state.get("fitness",0.5)
    if fitness < 0.4:
        state["pivot"] = "hard_reset_arc"
    elif fitness > 0.9:
        state["pivot"] = "expand_universe"
    return state
