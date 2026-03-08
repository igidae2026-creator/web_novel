param([string]$Dir=".")
Set-Location $Dir
python -c "from engine.auto_validate import auto_validate; import json; r=auto_validate(); print(json.dumps(r, ensure_ascii=False, indent=2)); exit(0 if r.get('ok') else 1)"
if ($LASTEXITCODE -ne 0) { exit 1 }
streamlit run app.py
