@echo off
set "VENV_DIR=%~dp0.venv"
set "PYTHON_EXE=%VENV_DIR%\\Scripts\\python.exe"

REM Check if venv exists, create if not
if not exist "%VENV_DIR%" (
    echo No virtual environment found. Creating one...
    python -m venv "%VENV_DIR%"
    if %errorlevel% neq 0 (
        echo Failed to create virtual environment. Please ensure Python is installed and in your PATH.
        exit /b 1
    )
)

echo Activating virtual environment...
call "%VENV_DIR%\\Scripts\\activate.bat"

echo Installing backend dependencies...
pip install -r backend/requirements.txt

echo Installing frontend dependencies...
cd frontend
call npm install
cd ..

REM The old command was `python dev.py`, which was not reliably reloading.
REM The new command uses the `flask run` command, which is more robust.
set FLASK_APP=backend.app
set FLASK_ENV=development

start "Backend Server" cmd /k "call "%VENV_DIR%\\Scripts\\activate.bat" && flask run --port=5001"

echo Starting Frontend Server...
start "Frontend Server" cmd /k "cd frontend && npm run dev"

echo.
echo Development servers are starting...
echo Backend: http://localhost:5001
echo Frontend: http://localhost:5173
echo.
echo Press Ctrl+C in the new windows to stop the servers.
timeout /t 10 