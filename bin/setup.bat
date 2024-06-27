@echo off

:: Exit immediately if a command exits with a non-zero status
setlocal enabledelayedexpansion

:: Navigate to Invoice-Vite folder and install Node.js dependencies
cd ..\Invoice-Vite
npm install

:: Navigate back to root dir
cd ..

:: Create a virtual environment
python -m venv .env-invoice

:: Activate the virtual environment
call .env-invoice\Scripts\activate

:: Navigate to backend folder and Install dependencies
cd backend
pip install -r requirements.txt