@echo off
setlocal
if "%OPENAI_API_KEY%"=="" (
  echo OPENAI_API_KEY is not set.
  echo set OPENAI_API_KEY=YOUR_KEY
  exit /b 1
)
python -m pip install -r requirements.txt
streamlit run app.py
