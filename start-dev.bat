@echo off
echo Starting Loggers Development Environment...
echo.

echo Starting Backend Server...
start "Backend Server" cmd /k "cd backend && python dev.py"

echo Starting Frontend Server...
start "Frontend Server" cmd /k "cd frontend && npm run dev"

echo.
echo Development servers are starting...
echo Backend: http://localhost:5000
echo Frontend: http://localhost:5173
echo.
echo Press any key to exit this launcher...
pause > nul 