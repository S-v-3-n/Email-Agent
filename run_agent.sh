#!/bin/bash
# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "Please edit .env with your credentials!"
    open .env
    exit 1
fi

# Activate venv
source .venv/bin/activate

# Run main script
python main.py
