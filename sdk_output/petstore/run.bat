@echo off
echo ==============================================
echo Demarrage du SDK TestSDK
echo ==============================================
echo 1. Installation des dependances...
pip install -r requirements.txt

echo 2. Demarrage du Backend FastAPI (en arriere-plan)...
start cmd /k "uvicorn backend.main:app --reload"

echo Patientez 3 secondes pour que le serveur demarre...
timeout /t 3 >nul

echo 3. Demarrage du Frontend Tkinter...
python frontend/main.py
