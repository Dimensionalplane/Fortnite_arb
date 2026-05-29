#!/bin/bash

while true
do
  echo "Starting automated market scan at $(date)"
  python3 src/scanner.py
  echo "Scan complete. Waiting 1 hour for next scan..."
  sleep 3600
done
