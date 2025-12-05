#!/bin/bash
# Play a full game with server and 2 AI players

cd "$(dirname "$0")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     🎮 Vampires VS Werewolves - AI Tournament 🎮         ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if Go is installed
if ! command -v go &> /dev/null; then
    echo -e "${RED}❌ Go is not installed!${NC}"
    echo ""
    echo -e "${YELLOW}Please install Go:${NC}"
    echo -e "  ${GREEN}sudo apt install golang-go${NC}   # For Ubuntu/Debian"
    echo -e "  ${GREEN}sudo dnf install golang${NC}      # For Fedora"
    echo -e "  ${GREEN}brew install go${NC}              # For macOS"
    echo ""
    echo -e "Or download from: ${BLUE}https://go.dev/dl/${NC}"
    exit 1
fi

# ============================================================
# SELECT MAP
# ============================================================
echo -e "${CYAN}📍 Select Map:${NC}"
echo ""

# Find all available maps
declare -a MAPS
declare -a MAP_FILES
i=1
for map in server/twilight-master/maps/*.xml; do
    if [ -f "$map" ]; then
        MAP_FILES[$i]=$(basename "$map")
        MAPS[$i]=$(basename "$map" .xml)
        echo -e "  ${GREEN}$i.${NC} ${MAPS[$i]}"
        ((i++))
    fi
done

echo -e "  ${GREEN}$i.${NC} Random map"
echo ""

read -p "Choose map (1-$i) [default: 1]: " MAP_CHOICE
MAP_CHOICE=${MAP_CHOICE:-1}

if [ "$MAP_CHOICE" -eq "$i" ]; then
    MAP_ARG="-rand"
    MAP_NAME="Random"
elif [ "$MAP_CHOICE" -ge 1 ] && [ "$MAP_CHOICE" -lt "$i" ]; then
    MAP_FILE="${MAP_FILES[$MAP_CHOICE]}"
    MAP_ARG="-map maps/$MAP_FILE"
    MAP_NAME="${MAPS[$MAP_CHOICE]}"
else
    echo -e "${RED}Invalid choice, using default map${NC}"
    MAP_FILE="${MAP_FILES[1]}"
    MAP_ARG="-map maps/$MAP_FILE"
    MAP_NAME="${MAPS[1]}"
fi

echo -e "${GREEN}✓${NC} Selected map: ${YELLOW}$MAP_NAME${NC}"
echo ""

# ============================================================
# SELECT CONFIGURATION MODE FOR PLAYER 1
# ============================================================
echo -e "${CYAN}⚙️  Select AI Mode for Player 1 (Vampires):${NC}"
echo ""
echo -e "  ${GREEN}1.${NC} balanced     - Default, well-rounded strategy"
echo -e "  ${GREEN}2.${NC} aggressive   - Deep search, risky attacks, fast expansion"
echo -e "  ${GREEN}3.${NC} defensive    - Safe attacks, strong concentration"
echo -e "  ${GREEN}4.${NC} speed        - Fast decisions, shallow search"
echo -e "  ${GREEN}5.${NC} tactical     - Multi-group coordination master"
echo -e "  ${GREEN}6.${NC} experimental - Testing new strategies"
echo -e "  ${GREEN}7.${NC} current      - Use current config without changes"
echo ""

read -p "Choose mode for Player 1 (1-7) [default: 7]: " MODE_CHOICE_P1
MODE_CHOICE_P1=${MODE_CHOICE_P1:-7}

case $MODE_CHOICE_P1 in
    1) MODE_NAME_P1="balanced" ;;
    2) MODE_NAME_P1="aggressive" ;;
    3) MODE_NAME_P1="defensive" ;;
    4) MODE_NAME_P1="speed" ;;
    5) MODE_NAME_P1="tactical" ;;
    6) MODE_NAME_P1="experimental" ;;
    7) MODE_NAME_P1="current" ;;
    *) 
        echo -e "${RED}Invalid choice, using current config${NC}"
        MODE_NAME_P1="current"
        ;;
esac

echo -e "${GREEN}✓${NC} Player 1 mode: ${YELLOW}$MODE_NAME_P1${NC}"
echo ""

# ============================================================
# SELECT CONFIGURATION MODE FOR PLAYER 2
# ============================================================
echo -e "${CYAN}⚙️  Select AI Mode for Player 2 (Werewolves):${NC}"
echo ""
echo -e "  ${GREEN}1.${NC} balanced     - Default, well-rounded strategy"
echo -e "  ${GREEN}2.${NC} aggressive   - Deep search, risky attacks, fast expansion"
echo -e "  ${GREEN}3.${NC} defensive    - Safe attacks, strong concentration"
echo -e "  ${GREEN}4.${NC} speed        - Fast decisions, shallow search"
echo -e "  ${GREEN}5.${NC} tactical     - Multi-group coordination master"
echo -e "  ${GREEN}6.${NC} experimental - Testing new strategies"
echo -e "  ${GREEN}7.${NC} current      - Use current config without changes"
echo ""

read -p "Choose mode for Player 2 (1-7) [default: 7]: " MODE_CHOICE_P2
MODE_CHOICE_P2=${MODE_CHOICE_P2:-7}

case $MODE_CHOICE_P2 in
    1) MODE_NAME_P2="balanced" ;;
    2) MODE_NAME_P2="aggressive" ;;
    3) MODE_NAME_P2="defensive" ;;
    4) MODE_NAME_P2="speed" ;;
    5) MODE_NAME_P2="tactical" ;;
    6) MODE_NAME_P2="experimental" ;;
    7) MODE_NAME_P2="current" ;;
    *) 
        echo -e "${RED}Invalid choice, using current config${NC}"
        MODE_NAME_P2="current"
        ;;
esac

echo -e "${GREEN}✓${NC} Player 2 mode: ${YELLOW}$MODE_NAME_P2${NC}"
echo ""

# ============================================================
# PREPARE CONFIGURATIONS
# ============================================================
# Create temporary config files for each player
mkdir -p /tmp/vvw_configs

# Save original config
cp ai/config.py /tmp/vvw_configs/config_original.py

# Prepare Player 1 config
if [ "$MODE_NAME_P1" != "current" ]; then
    echo -e "${YELLOW}Applying mode for Player 1: $MODE_NAME_P1${NC}"
    python3 ai/modes.py "$MODE_NAME_P1" > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        cp ai/config.py /tmp/vvw_configs/config_p1.py
        echo -e "${GREEN}✓${NC} Player 1 config ready: ${YELLOW}$MODE_NAME_P1${NC}"
    else
        echo -e "${RED}✗${NC} Failed to apply mode for Player 1, using current config"
        cp /tmp/vvw_configs/config_original.py /tmp/vvw_configs/config_p1.py
        MODE_NAME_P1="current"
    fi
else
    cp /tmp/vvw_configs/config_original.py /tmp/vvw_configs/config_p1.py
    echo -e "${GREEN}✓${NC} Player 1 using current configuration"
fi

# Prepare Player 2 config
if [ "$MODE_NAME_P2" != "current" ]; then
    echo -e "${YELLOW}Applying mode for Player 2: $MODE_NAME_P2${NC}"
    python3 ai/modes.py "$MODE_NAME_P2" > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        cp ai/config.py /tmp/vvw_configs/config_p2.py
        echo -e "${GREEN}✓${NC} Player 2 config ready: ${YELLOW}$MODE_NAME_P2${NC}"
    else
        echo -e "${RED}✗${NC} Failed to apply mode for Player 2, using current config"
        cp /tmp/vvw_configs/config_original.py /tmp/vvw_configs/config_p2.py
        MODE_NAME_P2="current"
    fi
else
    cp /tmp/vvw_configs/config_original.py /tmp/vvw_configs/config_p2.py
    echo -e "${GREEN}✓${NC} Player 2 using current configuration"
fi

# Restore original config (so we don't modify the repo)
cp /tmp/vvw_configs/config_original.py ai/config.py

echo ""

# ============================================================
# START GAME
# ============================================================
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}Map:${NC}         $MAP_NAME"
echo -e "${YELLOW}Player 1:${NC}    $MODE_NAME_P1"
echo -e "${YELLOW}Player 2:${NC}    $MODE_NAME_P2"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

# Setup logging
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p LOGS
LOG_SERVER="LOGS/server_${TIMESTAMP}.log"
LOG_PLAYER1="LOGS/player1_${TIMESTAMP}.log"
LOG_PLAYER2="LOGS/player2_${TIMESTAMP}.log"

echo -e "${CYAN}📝 Logs will be saved to:${NC}"
echo -e "   Server:   $LOG_SERVER"
echo -e "   Player 1: $LOG_PLAYER1"
echo -e "   Player 2: $LOG_PLAYER2"
echo ""

# Clean up any existing processes
pkill -f "twilight.*map" 2>/dev/null
pkill -f "ai_player.py" 2>/dev/null
sleep 1

# Start the server
echo -e "${YELLOW}📡 Starting game server...${NC}"
cd server/twilight-master
go run . $MAP_ARG > "../../$LOG_SERVER" 2>&1 &
SERVER_PID=$!
cd ../..

sleep 2

# Check if server is running
if ! ps -p $SERVER_PID > /dev/null 2>&1; then
    echo -e "${RED}❌ Server failed to start${NC}"
    echo -e "${YELLOW}Check logs: $LOG_SERVER${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Server running (PID: $SERVER_PID)${NC}"
echo -e "${BLUE}🌐 Web interface: http://localhost:8080${NC}"
echo ""

# Get absolute path to project root
PROJECT_ROOT="$(pwd)"

# Create temporary Python launcher scripts that import the right config
cat > /tmp/vvw_configs/launch_p1.py << 'PYEOF'
import sys
import importlib.util

# Load player 1's config
spec = importlib.util.spec_from_file_location("config", "/tmp/vvw_configs/config_p1.py")
config = importlib.util.module_from_spec(spec)
sys.modules['config'] = config
spec.loader.exec_module(config)

# Now import and run the AI
sys.path.insert(0, sys.argv[1])  # Add project ai/ directory to path
from ai_player import play_game
import argparse
args = argparse.Namespace(ip=sys.argv[2], port=int(sys.argv[3]), name='AlphaBetaAI_v1')
play_game(args)
PYEOF

cat > /tmp/vvw_configs/launch_p2.py << 'PYEOF'
import sys
import importlib.util

# Load player 2's config
spec = importlib.util.spec_from_file_location("config", "/tmp/vvw_configs/config_p2.py")
config = importlib.util.module_from_spec(spec)
sys.modules['config'] = config
spec.loader.exec_module(config)

# Now import and run the AI
sys.path.insert(0, sys.argv[1])  # Add project ai/ directory to path
from ai_player import play_game
import argparse
args = argparse.Namespace(ip=sys.argv[2], port=int(sys.argv[3]), name='AlphaBetaAI_v1')
play_game(args)
PYEOF

# Start Player 1 (will be Vampires)
echo -e "${YELLOW}🧛 Starting AI Player 1 (Vampires) - Mode: $MODE_NAME_P1...${NC}"
sleep 1
python3 /tmp/vvw_configs/launch_p1.py "$PROJECT_ROOT/ai" localhost 5555 > "$LOG_PLAYER1" 2>&1 &
AI1_PID=$!

sleep 2
if ! ps -p $AI1_PID > /dev/null 2>&1; then
    echo -e "${RED}❌ Player 1 failed to start${NC}"
    echo -e "${YELLOW}Check logs: $LOG_PLAYER1${NC}"
    kill $SERVER_PID 2>/dev/null
    # Restore original config
    cp /tmp/vvw_configs/config_original.py ai/config.py
    exit 1
fi

echo -e "${GREEN}✅ Player 1 connected (PID: $AI1_PID)${NC}"
echo ""

# Start Player 2 (will be Werewolves)  
echo -e "${YELLOW}🐺 Starting AI Player 2 (Werewolves) - Mode: $MODE_NAME_P2...${NC}"
sleep 1
python3 /tmp/vvw_configs/launch_p2.py "$PROJECT_ROOT/ai" localhost 5555 > "$LOG_PLAYER2" 2>&1 &
AI2_PID=$!

sleep 2
if ! ps -p $AI2_PID > /dev/null 2>&1; then
    echo -e "${RED}❌ Player 2 failed to start${NC}"
    echo -e "${YELLOW}Check logs: $LOG_PLAYER2${NC}"
    kill $SERVER_PID $AI1_PID 2>/dev/null
    # Restore original config
    cp /tmp/vvw_configs/config_original.py ai/config.py
    exit 1
fi

echo -e "${GREEN}✅ Player 2 connected (PID: $AI2_PID)${NC}"
echo ""

echo -e "${GREEN}🎲 Game is now running!${NC}"
echo ""
echo -e "${BLUE}📊 Watch the game: http://localhost:8080${NC}"
echo -e "${YELLOW}⏱️  Press Ctrl+C to stop, or wait for game to finish...${NC}"
echo -e "${CYAN}💡 Tail logs: tail -f $LOG_PLAYER1${NC}"
echo ""

# Wait for game to finish
wait $AI1_PID $AI2_PID 2>/dev/null

# Clean up
echo ""
echo -e "${YELLOW}🧹 Cleaning up...${NC}"
kill $SERVER_PID 2>/dev/null
wait $SERVER_PID 2>/dev/null

# Restore original config
cp /tmp/vvw_configs/config_original.py ai/config.py

echo -e "${GREEN}🏁 Game finished!${NC}"
echo ""
echo -e "${CYAN}📝 Logs saved:${NC}"
echo -e "   Server:   $LOG_SERVER"
echo -e "   Player 1: $LOG_PLAYER1"
echo -e "   Player 2: $LOG_PLAYER2"
echo ""
