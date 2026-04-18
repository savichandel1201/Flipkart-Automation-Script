@echo off
:: Use the absolute path to Python since Jenkins service doesn't see User PATH
set PYTHON_EXE=C:\Users\Savi_\AppData\Local\Programs\Python\Python314\python.exe

echo [INFO] Using Python at: %PYTHON_EXE%

:: 1. Check if virtual environment exists, if not create it
if not exist .venv (
    echo [INFO] Creating virtual environment...
    "%PYTHON_EXE%" -m venv .venv
)

:: 2. Activate and install requirements
echo [INFO] Installing/Updating dependencies...
call .venv\Scripts\activate
python -m pip install -r requirements.txt

:: 3. Run tests
echo [INFO] Running tests...
python -m pytest -s
