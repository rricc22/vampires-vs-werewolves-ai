#!/bin/bash

echo "=========================================="
echo "Testing AI Improvements"
echo "=========================================="

cd "$(dirname "$0")"

# Kill any existing processes
pkill -f "go run.*map" 2>/dev/null
pkill -f "ai_player.py" 2>/dev/null
sleep 1

echo "Starting server..."
cd server/twilight-master
go run . -map maps/testmap.xml > ../../LOGS/server_logs.txt 2>&1 &
SERVER_PID=$!
cd ../..

echo "Waiting for server to start..."
sleep 2

echo "Starting AI player..."
python3 ai/ai_player.py localhost 5555 > LOGS/ai_player_logs.txt 2>&1 &
AI_PID=$!

echo ""
echo "Server PID: $SERVER_PID"
echo "AI PID: $AI_PID"
echo ""
echo "Logs are being written to:"
echo "  - LOGS/server_logs.txt"
echo "  - LOGS/ai_player_logs.txt"
echo ""
echo "Press Ctrl+C to stop, or wait for game to finish..."
echo "Watch the game at: http://localhost:8080"
echo ""

# Wait for user interrupt or processes to finish
wait $AI_PID 2>/dev/null

echo ""
echo "=========================================="
echo "Game finished! Analyzing results..."
echo "=========================================="

# Analyze the logs
echo ""
echo "Group counts by turn:"
grep "Our groups:" LOGS/ai_player_logs.txt | head -20

echo ""
echo "Multi-group moves:"
grep "Multi-group" LOGS/ai_player_logs.txt | head -10

echo ""
echo "Done! Check LOGS/ for full details."

# Cleanup
kill $SERVER_PID 2>/dev/null
