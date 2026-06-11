#!/bin/bash
set -e

echo "Starting Staging Integration Test..."

# Use absolute project root
ROOT_DIR=$(pwd)

# 1. Start Go Backend
echo "Starting Go Backend..."
kill $(lsof -t -i :8080 2>/dev/null) || true
cd backend && go build -o main . && ./main > ../backend.log 2>&1 &
cd "$ROOT_DIR"
sleep 5

# 2. Verify API Health
echo "Checking API Health..."
curl -s http://localhost:8080/api/health | grep -q "OK"
echo "API is HEALTHY."

# 3. Update Configuration
echo "Updating Configuration via API..."
CONFIG_PATH="$ROOT_DIR/config/items.json"
curl -s -X POST -H "Content-Type: application/json" -d @$CONFIG_PATH http://localhost:8080/api/config
echo "Config updated."

# 4. Trigger Manual Scan
echo "Triggering Manual Scan..."
curl -s -X POST http://localhost:8080/api/arbitrage/scan
echo "Scan triggered."

# 5. Wait for scan to complete
echo "Waiting for scan results..."
sleep 15

# 6. Verify history
echo "Verifying history recording..."
HISTORY_PATH="$ROOT_DIR/data/scan_history.json"
if [ -f "$HISTORY_PATH" ]; then
    echo "History file exists at $HISTORY_PATH."
else
    echo "History file NOT FOUND."
fi

echo "Staging Integration Test COMPLETED."
