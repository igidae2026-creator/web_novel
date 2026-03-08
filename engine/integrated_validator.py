
from __future__ import annotations
import os, json, py_compile

REQUIRED = [
    "app.py",
    "engine/pipeline.py",
    "engine/track_loop.py",
    "engine/track_queue.py",
    "engine/portfolio_orchestrator.py",
    "engine/cannibalization_scheduler.py",
    "engine/market_policy_engine.py",
    "engine/model_calibration.py",
    "engine/calibration_history.py",
    "engine/market_inertia.py",
    "engine/competition_reaction.py"
]

def check_files(root: str) -> dict:
    missing=[f for f in REQUIRED if not os.path.exists(os.path.join(root,f))]
    return {"ok": len(missing)==0, "missing": missing}

def compile_all(root: str) -> dict:
    errs=[]
    for dp,_,fns in os.walk(root):
        for fn in fns:
            if fn.endswith(".py"):
                try:
                    py_compile.compile(os.path.join(dp,fn), doraise=True)
                except Exception as e:
                    errs.append({"file": os.path.relpath(os.path.join(dp,fn),root), "error": repr(e)})
    return {"ok": len(errs)==0, "errors": errs}

def quick_runtime_checks(root: str) -> dict:
    # import sanity
    errs=[]
    try:
        import importlib, sys
        sys.path.insert(0, root)
        importlib.import_module("engine.pipeline")
        importlib.import_module("engine.track_loop")
        importlib.import_module("engine.portfolio_orchestrator")
        importlib.import_module("engine.market_policy_engine")
    except Exception as e:
        errs.append(repr(e))
    return {"ok": len(errs)==0, "errors": errs}

def run_all(root: str) -> dict:
    out={"files": check_files(root)}
    out["compile"]=compile_all(root)
    out["imports"]=quick_runtime_checks(root)
    out["ok"]= out["files"]["ok"] and out["compile"]["ok"] and out["imports"]["ok"]
    return out
