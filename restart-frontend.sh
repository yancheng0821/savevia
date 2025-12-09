#!/bin/bash

# SaveVia Frontend Restart Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$SCRIPT_DIR/savevia-web"

echo "=========================================="
echo "  SaveVia Frontend Restart"
echo "=========================================="

# Kill existing process on port 5173
echo "Stopping existing frontend process..."
lsof -ti:5173 | xargs kill -9 2>/dev/null

# Wait a moment
sleep 1

# Start frontend
echo "Starting frontend..."
cd "$FRONTEND_DIR"
npm run dev &

echo ""
echo "Frontend started at http://localhost:5173/"
echo "=========================================="
