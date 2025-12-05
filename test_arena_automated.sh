#!/bin/bash
# Automated arena test with RAM monitoring and detailed analysis
# Non-interactive version for AI testing

cd "$(dirname "$0")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Automated Arena Map Test - AI Performance Analysis${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Setup logging
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p LOGS
LOG_SERVER="LOGS/arena_server_${TIMESTAMP}.log"
LOG_PLAYER1="LOGS/arena_player1_${TIMESTAMP}.log"
LOG_PLAYER2="LOGS/arena_player2_${TIMESTAMP}.log"
LOG_RAM="LOGS/arena_ram_${TIMESTAMP}.log"
LOG_ANALYSIS="LOGS/arena_analysis_${TIMESTAMP}.log"

echo -e "${CYAN}Test Configuration:${NC}"
echo -e "  Map: arena.xml"
echo -e "  Mode: Current configuration (both players)"
echo -e "  RAM Monitoring: Enabled (32GB system)"
echo ""
echo -e "${CYAN}Log files:${NC}"
echo -e "  Server:   $LOG_SERVER"
echo -e "  Player 1: $LOG_PLAYER1"
echo -e "  Player 2: $LOG_PLAYER2"
echo -e "  RAM:      $LOG_RAM"
echo -e "  Analysis: $LOG_ANALYSIS"
echo ""

# Clean up any existing processes
pkill -f "twilight.*map" 2>/dev/null
pkill -f "ai_player.py" 2>/dev/null
sleep 1

# Start the server with arena map
echo -e "${YELLOW}Starting game server with arena map...${NC}"
cd server/twilight-master
go run . -map maps/arena.xml > "../../$LOG_SERVER" 2>&1 &
SERVER_PID=$!
cd ../..

sleep 2

# Check if server is running
if ! ps -p $SERVER_PID > /dev/null 2>&1; then
    echo -e "${RED}Server failed to start${NC}"
    echo -e "${YELLOW}Check logs: $LOG_SERVER${NC}"
    exit 1
fi

echo -e "${GREEN}Server running (PID: $SERVER_PID)${NC}"
echo ""

# Get absolute path to project root
PROJECT_ROOT="$(pwd)"

# Start Player 1 (Vampires)
echo -e "${YELLOW}Starting AI Player 1 (Vampires)...${NC}"
sleep 1
python3 "$PROJECT_ROOT/ai/ai_player.py" localhost 5555 > "$LOG_PLAYER1" 2>&1 &
AI1_PID=$!

sleep 2
if ! ps -p $AI1_PID > /dev/null 2>&1; then
    echo -e "${RED}Player 1 failed to start${NC}"
    echo -e "${YELLOW}Check logs: $LOG_PLAYER1${NC}"
    kill $SERVER_PID 2>/dev/null
    exit 1
fi

echo -e "${GREEN}Player 1 connected (PID: $AI1_PID)${NC}"

# Start Player 2 (Werewolves)
echo -e "${YELLOW}Starting AI Player 2 (Werewolves)...${NC}"
sleep 1
python3 "$PROJECT_ROOT/ai/ai_player.py" localhost 5555 > "$LOG_PLAYER2" 2>&1 &
AI2_PID=$!

sleep 2
if ! ps -p $AI2_PID > /dev/null 2>&1; then
    echo -e "${RED}Player 2 failed to start${NC}"
    echo -e "${YELLOW}Check logs: $LOG_PLAYER2${NC}"
    kill $SERVER_PID $AI1_PID 2>/dev/null
    exit 1
fi

echo -e "${GREEN}Player 2 connected (PID: $AI2_PID)${NC}"
echo ""

# Start RAM monitoring in background
echo -e "${YELLOW}Starting RAM monitoring...${NC}"
(
    echo "Timestamp,RSS_MB_P1,RSS_MB_P2,Total_MB,Percent_Used" > "$LOG_RAM"
    while true; do
        if ps -p $SERVER_PID > /dev/null 2>&1; then
            # Get memory usage for AI players
            P1_MEM=$(ps -o rss= -p $AI1_PID 2>/dev/null | awk '{print $1/1024}')
            P2_MEM=$(ps -o rss= -p $AI2_PID 2>/dev/null | awk '{print $1/1024}')

            if [ -n "$P1_MEM" ] && [ -n "$P2_MEM" ]; then
                TOTAL=$(echo "$P1_MEM + $P2_MEM" | bc)
                PERCENT=$(echo "scale=2; $TOTAL / 32768 * 100" | bc)
                echo "$(date +%H:%M:%S),$P1_MEM,$P2_MEM,$TOTAL,$PERCENT" >> "$LOG_RAM"
            fi
            sleep 1
        else
            break
        fi
    done
) &
RAM_MONITOR_PID=$!

START_TIME=$(date +%s)
echo -e "${GREEN}Game is running!${NC}"
echo -e "${BLUE}Web interface: http://localhost:8080${NC}"
echo -e "${YELLOW}Waiting for game to finish...${NC}"
echo ""

# Wait for game to finish
wait $AI1_PID $AI2_PID 2>/dev/null
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

# Clean up
echo ""
echo -e "${YELLOW}Cleaning up...${NC}"
kill $SERVER_PID $RAM_MONITOR_PID 2>/dev/null
wait $SERVER_PID $RAM_MONITOR_PID 2>/dev/null

echo -e "${GREEN}Game finished!${NC}"
echo -e "${CYAN}Duration: ${DURATION}s${NC}"
echo ""

# Perform analysis
echo -e "${YELLOW}Analyzing game logs...${NC}"
echo ""
echo "═══════════════════════════════════════════════════════════" > "$LOG_ANALYSIS"
echo "  ARENA MAP TEST - PERFORMANCE ANALYSIS" >> "$LOG_ANALYSIS"
echo "═══════════════════════════════════════════════════════════" >> "$LOG_ANALYSIS"
echo "" >> "$LOG_ANALYSIS"
echo "Test Date: $(date)" >> "$LOG_ANALYSIS"
echo "Duration: ${DURATION}s" >> "$LOG_ANALYSIS"
echo "" >> "$LOG_ANALYSIS"

# Analyze Player 1
echo "--- PLAYER 1 (Vampires) ---" >> "$LOG_ANALYSIS"
echo "" >> "$LOG_ANALYSIS"

P1_MOVES=$(grep -c "Sending move:" "$LOG_PLAYER1" 2>/dev/null || echo "0")
P1_AVG_TIME=$(grep "Search completed in" "$LOG_PLAYER1" 2>/dev/null | awk '{sum+=$4; count++} END {if(count>0) printf "%.3f", sum/count; else print "N/A"}')
P1_AVG_NODES=$(grep "explored" "$LOG_PLAYER1" 2>/dev/null | grep -oP '\d+ nodes' | awk '{sum+=$1; count++} END {if(count>0) printf "%.0f", sum/count; else print "N/A"}')
P1_TIMEOUTS=$(grep -i "timeout\|took too long" "$LOG_PLAYER1" 2>/dev/null | wc -l)
P1_ERRORS=$(grep -i "error\|exception\|failed" "$LOG_PLAYER1" 2>/dev/null | wc -l)
P1_ATTACKS=$(grep "MOV" "$LOG_PLAYER1" 2>/dev/null | grep -v "MOV 0" | wc -l)

echo "Total Moves: $P1_MOVES" >> "$LOG_ANALYSIS"
echo "Average Time per Move: ${P1_AVG_TIME}s" >> "$LOG_ANALYSIS"
echo "Average Nodes Explored: $P1_AVG_NODES" >> "$LOG_ANALYSIS"
echo "Timeouts: $P1_TIMEOUTS" >> "$LOG_ANALYSIS"
echo "Errors: $P1_ERRORS" >> "$LOG_ANALYSIS"
echo "Active Moves (non-pass): $P1_ATTACKS" >> "$LOG_ANALYSIS"
echo "" >> "$LOG_ANALYSIS"

# Analyze Player 2
echo "--- PLAYER 2 (Werewolves) ---" >> "$LOG_ANALYSIS"
echo "" >> "$LOG_ANALYSIS"

P2_MOVES=$(grep -c "Sending move:" "$LOG_PLAYER2" 2>/dev/null || echo "0")
P2_AVG_TIME=$(grep "Search completed in" "$LOG_PLAYER2" 2>/dev/null | awk '{sum+=$4; count++} END {if(count>0) printf "%.3f", sum/count; else print "N/A"}')
P2_AVG_NODES=$(grep "explored" "$LOG_PLAYER2" 2>/dev/null | grep -oP '\d+ nodes' | awk '{sum+=$1; count++} END {if(count>0) printf "%.0f", sum/count; else print "N/A"}')
P2_TIMEOUTS=$(grep -i "timeout\|took too long" "$LOG_PLAYER2" 2>/dev/null | wc -l)
P2_ERRORS=$(grep -i "error\|exception\|failed" "$LOG_PLAYER2" 2>/dev/null | wc -l)
P2_ATTACKS=$(grep "MOV" "$LOG_PLAYER2" 2>/dev/null | grep -v "MOV 0" | wc -l)

echo "Total Moves: $P2_MOVES" >> "$LOG_ANALYSIS"
echo "Average Time per Move: ${P2_AVG_TIME}s" >> "$LOG_ANALYSIS"
echo "Average Nodes Explored: $P2_AVG_NODES" >> "$LOG_ANALYSIS"
echo "Timeouts: $P2_TIMEOUTS" >> "$LOG_ANALYSIS"
echo "Errors: $P2_ERRORS" >> "$LOG_ANALYSIS"
echo "Active Moves (non-pass): $P2_ATTACKS" >> "$LOG_ANALYSIS"
echo "" >> "$LOG_ANALYSIS"

# RAM Analysis
if [ -f "$LOG_RAM" ]; then
    echo "--- RAM USAGE ---" >> "$LOG_ANALYSIS"
    echo "" >> "$LOG_ANALYSIS"

    MAX_RAM=$(tail -n +2 "$LOG_RAM" | awk -F, '{print $4}' | sort -n | tail -1)
    AVG_RAM=$(tail -n +2 "$LOG_RAM" | awk -F, '{sum+=$4; count++} END {if(count>0) printf "%.2f", sum/count; else print "N/A"}')
    MAX_PERCENT=$(tail -n +2 "$LOG_RAM" | awk -F, '{print $5}' | sort -n | tail -1)

    echo "Peak RAM Usage: ${MAX_RAM} MB (${MAX_PERCENT}% of 32GB)" >> "$LOG_ANALYSIS"
    echo "Average RAM Usage: ${AVG_RAM} MB" >> "$LOG_ANALYSIS"
    echo "" >> "$LOG_ANALYSIS"
fi

# Game Outcome
echo "--- GAME OUTCOME ---" >> "$LOG_ANALYSIS"
echo "" >> "$LOG_ANALYSIS"

if grep -q "You win" "$LOG_PLAYER1" 2>/dev/null; then
    echo "Winner: Player 1 (Vampires)" >> "$LOG_ANALYSIS"
elif grep -q "You win" "$LOG_PLAYER2" 2>/dev/null; then
    echo "Winner: Player 2 (Werewolves)" >> "$LOG_ANALYSIS"
else
    echo "Winner: Unknown (check logs)" >> "$LOG_ANALYSIS"
fi
echo "" >> "$LOG_ANALYSIS"

echo "═══════════════════════════════════════════════════════════" >> "$LOG_ANALYSIS"

# Display analysis
cat "$LOG_ANALYSIS"

echo ""
echo -e "${GREEN}Analysis complete!${NC}"
echo -e "${CYAN}Full analysis saved to: $LOG_ANALYSIS${NC}"
echo ""
echo -e "${YELLOW}All logs:${NC}"
echo -e "  Server:   $LOG_SERVER"
echo -e "  Player 1: $LOG_PLAYER1"
echo -e "  Player 2: $LOG_PLAYER2"
echo -e "  RAM:      $LOG_RAM"
echo -e "  Analysis: $LOG_ANALYSIS"
echo ""
