#!/bin/bash
# Quick test script to run arena.xml with current debug config

cd "$(dirname "$0")"

echo "=========================================="
echo "Testing arena.xml with debug logging"
echo "ATTACK_MIN_WIN_PROBABILITY = 0.1 (10%)"
echo "DEBUG_MOVE_GENERATION = True"
echo "=========================================="
echo ""

# Clean up any existing processes
pkill -f "twilight.*map" 2>/dev/null
pkill -f "ai_player.py" 2>/dev/null
sleep 1

# Setup logging
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p LOGS
LOG_SERVER="LOGS/arena_server_${TIMESTAMP}.log"
LOG_PLAYER1="LOGS/arena_player1_${TIMESTAMP}.log"
LOG_PLAYER2="LOGS/arena_player2_${TIMESTAMP}.log"

echo "Logs will be saved to:"
echo "  Server:   $LOG_SERVER"
echo "  Player 1: $LOG_PLAYER1"
echo "  Player 2: $LOG_PLAYER2"
echo ""

# Start the server with arena map
echo "Starting server with arena.xml..."
cd server/twilight-master
go run . -map maps/arena.xml > "../../$LOG_SERVER" 2>&1 &
SERVER_PID=$!
cd ../..
sleep 2

# Check if server is running
if ! ps -p $SERVER_PID > /dev/null 2>&1; then
    echo "ERROR: Server failed to start"
    echo "Check logs: $LOG_SERVER"
    exit 1
fi

echo "✓ Server running (PID: $SERVER_PID)"
echo "✓ Web interface: http://localhost:8080"
echo ""

# Start Player 1 (Vampires)
echo "Starting AI Player 1 (Vampires)..."
sleep 1
python3 ai/ai_player.py localhost 5555 > "$LOG_PLAYER1" 2>&1 &
AI1_PID=$!

sleep 2
if ! ps -p $AI1_PID > /dev/null 2>&1; then
    echo "ERROR: Player 1 failed to start"
    echo "Check logs: $LOG_PLAYER1"
    kill $SERVER_PID 2>/dev/null
    exit 1
fi

echo "✓ Player 1 connected (PID: $AI1_PID)"
echo ""

# Start Player 2 (Werewolves)
echo "Starting AI Player 2 (Werewolves)..."
sleep 1
python3 ai/ai_player.py localhost 5555 > "$LOG_PLAYER2" 2>&1 &
AI2_PID=$!

sleep 2
if ! ps -p $AI2_PID > /dev/null 2>&1; then
    echo "ERROR: Player 2 failed to start"
    echo "Check logs: $LOG_PLAYER2"
    kill $SERVER_PID $AI1_PID 2>/dev/null
    exit 1
fi

echo "✓ Player 2 connected (PID: $AI2_PID)"
echo ""

echo "=========================================="
echo "Game is now running!"
echo "=========================================="
echo ""
echo "Watch live: http://localhost:8080"
echo ""
echo "To monitor move generation in real-time:"
echo "  tail -f $LOG_PLAYER1"
echo "  tail -f $LOG_PLAYER2"
echo ""
echo "Waiting 30 seconds for first few moves..."
echo ""

# Wait 30 seconds to capture first few moves
sleep 30

# Show recent moves from logs
echo ""
echo "=========================================="
echo "Player 1 (Vampires) Recent Activity:"
echo "=========================================="
tail -50 "$LOG_PLAYER1" | grep -A 5 "Generating moves"

echo ""
echo "=========================================="
echo "Player 2 (Werewolves) Recent Activity:"
echo "=========================================="
tail -50 "$LOG_PLAYER2" | grep -A 5 "Generating moves"

# Clean up
echo ""
echo "Stopping game..."
kill $AI1_PID $AI2_PID $SERVER_PID 2>/dev/null
wait $AI1_PID $AI2_PID $SERVER_PID 2>/dev/null

echo ""
echo "Game stopped. Check full logs for details:"
echo "  $LOG_PLAYER1"
echo "  $LOG_PLAYER2"
echo ""
