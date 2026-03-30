@echo off
echo Starting OfferCompare Pro...

echo Starting Backend on Port 8001...
start "OfferCompare Backend" cmd /k "python api_server.py"

echo Waiting for backend to initialize...
timeout /t 5

echo Starting Frontend on Port 3001...
cd frontend
start "OfferCompare Frontend" cmd /k "npm.cmd run dev"

echo.
echo Servers are starting!
echo Backend: http://localhost:8001/health
echo Frontend: http://localhost:3001
echo.
pause
