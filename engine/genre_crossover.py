from engine.strategy import GENRE_SUBENGINES

def crossover_engine(bucket: str):
    if bucket == "A":
        return "C_CONTRACT"
    if bucket == "C":
        return "A_REVENGE_REGRESSION"
    if bucket == "F":
        return "E_THRILLER"
    return None
