#!/bin/bash

# Start frontend development server
gnome-terminal -- bash -c "cd .. && cd Invoice-Vite && npm run dev; exec bash"

# Start FastAPI server
gnome-terminal -- bash -c "source ../.env-invoice/bin/activate && cd ../backend && uvicorn api:app --port 5500; exec bash"

# Prompt for number of workers
read -p "Enter the number of workers you want to start (Ensure that the API keys are available in .env for each worker): " num_workers

# Start worker.py instances
for ((i = 1; i <= num_workers; i++)); do
    gnome-terminal -- bash -c "source ../.env-invoice/bin/activate && cd ../backend && python worker.py $i; exec bash"
done