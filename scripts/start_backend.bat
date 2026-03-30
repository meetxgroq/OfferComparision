@echo off
echo Starting OfferCompare Pro Backend Server...
echo.

REM Activate conda environment
call conda activate offercompare-pro

REM Navigate to project directory
cd /d C:\Users\AW111\Documents\Offer_Compare\OfferComparision

REM Start the backend server
echo Backend server starting on http://localhost:8001
echo.
echo Watch for tax calculation logs like:
echo   -> Calculating tax for location: Seattle, WA, Total Comp: $265,000
echo   -> Estimated Net Pay: $196,100 (Tax Rate: 26.0%%)
echo.
python api_server.py

pause
