@echo off
cd /d %~dp0
echo Starting Flipkart Automation...
call .venv\Scripts\activate
pytest -s
pause