#!/bin/bash

# Activate the conda environment
eval "$(conda shell.bash hook)"
conda activate UniRig

# Start the FastAPI server
cd "$(dirname "$0")"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload 