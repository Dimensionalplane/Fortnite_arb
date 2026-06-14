#!/bin/bash

# Ensure PYTHONPATH is set to project root
export PYTHONPATH=$PYTHONPATH:$(pwd)

while true
do
  echo "Starting automated trading cycle at $(date)"
  python3 src/trading/engine.py
  echo "Cycle complete. Waiting 1 hour for next cycle..."
  sleep 3600
done
