#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Navigate to Invoice-Vite folder and install Node.js dependencies
cd ..\Invoice-Vite
npm install

# Navigate back to root directory
cd ..

# Create a virtual environment
python3 -m venv .env-invoice

# Activate the virtual environment
source .env-invoice/bin/activate

# Navigate to backend folder and install dependencies
cd backend
pip install -r requirements.txt

# Navigate back to root directory
cd ..