import os, sys, py_compile, importlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

def main():
    # 1) syntax check
    py_files = [p for p in ROOT.rglob("*.py")]
    errs = []
    for p in py_files:
        try:
            py_compile.compile(str(p), doraise=True)
        except Exception as e:
            errs.append((str(p), repr(e)))
    if errs:
        print("SYNTAX_ERRORS:")
        for p,e in errs:
            print("-", p, e)
        raise SystemExit(2)
    print(f"Syntax OK: {len(py_files)} python files")

    # 2) optional import checks (deps must be installed)
    modules = [
        "engine.pipeline",
        "engine.external_rank",
        "engine.prompts",
        "engine.cost",
        "engine.state",
    ]
    for m in modules:
        importlib.import_module(m)
    print("Core imports OK")

    # 3) dependency presence check
    try:
        import openai, streamlit, yaml, dateutil  # noqa
        print("Deps import OK (openai/streamlit/pyyaml/dateutil)")
    except Exception as e:
        print("Deps import check failed (install requirements.txt):", repr(e))

if __name__ == "__main__":
    main()
