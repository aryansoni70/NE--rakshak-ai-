@echo off
echo ========================================================
echo   Starting NE-RAKSHAK AI Platform (MDoNER / SIH26002)
echo ========================================================
echo.
echo [1/2] Launching FastAPI Backend Server on http://localhost:8000 ...
start "NE-RAKSHAK Backend (FastAPI)" cmd /k "python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload"

echo [2/2] Launching Frontend Mission Control on http://localhost:3000 ...
start "NE-RAKSHAK Frontend (React/Vite)" cmd /k "npm --prefix frontend run dev"

echo.
echo Platform is online!
echo -> UI Dashboard:   http://localhost:3000
echo -> Backend API:    http://localhost:8000/docs
echo ========================================================
pause
