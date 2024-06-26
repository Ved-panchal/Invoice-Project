@echo off
:: Exit immediately if a command exits with a non-zero status
setlocal enabledelayedexpansion

start cmd /k "cd .. && cd Invoice-Vite && npm run dev"

:: Navigate to backend folder and Start Fastapi
start cmd /k "call ..\.env-invoice\Scripts\activate && cd ..\backend && uvicorn main:app --port 5500"

set /p "num_workers=Enter the number of workers you want to start (Ensure that the API keys are available in .env for each worker): "
for /l %%i in (1, 1, %num_workers%) do (
    :: Start worker.py with argument 1 in a new command window
    start cmd /k "call ..\.env-invoice\Scripts\activate && cd ..\backend && python worker.py %%i"
)