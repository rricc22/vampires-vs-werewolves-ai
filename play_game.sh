#!/bin/bash
# Play a full game with server and 2 AI players

cd "$(dirname "$0")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     🎮 Vampires VS Werewolves - AI Tournament 🎮         ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Clean up any existing processes
pkill -f "twilight.*map" 2>/dev/null
pkill -f "ai_player.py" 2>/dev/null
sleep 1

# Start the server
echo -e "${YELLOW}📡 Starting game server...${NC}"
cd server/twilight-master
go run . -map maps/testmap.xml &
SERVER_PID=$!
cd ../..

sleep 2

# Check if server is running
if ! ps -p $SERVER_PID > /dev/null 2>&1; then
    echo -e "${RED}❌ Server failed to start${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Server running (PID: $SERVER_PID)${NC}"
echo -e "${BLUE}🌐 Web interface: http://localhost:8080${NC}"
echo ""

# Start Player 1 (will be Vampires)
echo -e "${YELLOW}🧛 Starting AI Player 1 (Vampires)...${NC}"
sleep 1
python3 ai/ai_player.py localhost 5555 &
AI1_PID=$!

sleep 2
if ! ps -p $AI1_PID > /dev/null 2>&1; then
    echo -e "${RED}❌ Player 1 failed to start${NC}"
    kill $SERVER_PID 2>/dev/null
    exit 1
fi

echo -e "${GREEN}✅ Player 1 connected (PID: $AI1_PID)${NC}"
echo ""

# Start Player 2 (will be Werewolves)  
echo -e "${YELLOW}🐺 Starting AI Player 2 (Werewolves)...${NC}"
sleep 1
python3 ai/ai_player.py localhost 5555 &
AI2_PID=$!

sleep 2
if ! ps -p $AI2_PID > /dev/null 2>&1; then
    echo -e "${RED}❌ Player 2 failed to start${NC}"
    kill $SERVER_PID $AI1_PID 2>/dev/null
    exit 1
fi

echo -e "${GREEN}✅ Player 2 connected (PID: $AI2_PID)${NC}"
echo ""

echo -e "${GREEN}🎲 Game is now running!${NC}"
echo ""
echo -e "${BLUE}📊 Watch the game: http://localhost:8080${NC}"
echo -e "${YELLOW}⏱️  Game will run for up to 60 seconds...${NC}"
echo ""

# Wait for game to finish (max 60 seconds)
for i in {1..60}; do
    sleep 1
    # Check if any process has finished
    if ! ps -p $SERVER_PID > /dev/null 2>&1 || \
       ! ps -p $AI1_PID > /dev/null 2>&1 || \
       ! ps -p $AI2_PID > /dev/null 2>&1; then
        break
    fi
    echo -ne "${YELLOW}\r⏱️  Running... ${i}s${NC}"
done

echo -e "\n"

# Clean up
echo -e "${YELLOW}🧹 Cleaning up...${NC}"
kill $SERVER_PID $AI1_PID $AI2_PID 2>/dev/null
wait $SERVER_PID $AI1_PID $AI2_PID 2>/dev/null

echo -e "${GREEN}🏁 Game finished!${NC}"
echo ""
