# Quick Testing Guide

## Run All Tests
```bash
python3 tests/test_ai.py
python3 tests/test_filter.py
```

Expected output: All tests passing ✓

## Manual Game Test (Local)

### 1. Start Server
```bash
cd server/twilight-master
go run . -map maps/map8.xml
# Server starts on port 5555, UI at http://localhost:8080
```

### 2. Start AI Players (in separate terminals)
```bash
# Terminal 2
python3 ai/ai_player.py localhost 5555

# Terminal 3  
python3 ai/ai_player.py localhost 5555
```

### 3. Watch Game
Open browser: http://localhost:8080

## Available Maps
- **testmap.xml**: 5×6, minimal (1 human each side, 3 units each)
- **map8.xml**: 8×8, symmetric, lots of humans (original suicidal attack scenario)
- **thetrap.xml**: 5×10, asymmetric (tests coordinate handling)

## What to Look For

### Good Signs ✅
- AI connects successfully
- Moves generated every ~2 seconds
- Game progresses to completion
- No error messages
- Strategic human elimination before PvP

### Bad Signs ❌
- Connection refused errors
- Timeout errors (>2 seconds per move)
- Python exceptions/tracebacks
- "Illegal move" in server logs
- Suicidal attacks (equal force battles)

## Quick Verification Commands

### Check AI is thinking
```bash
# Should show depth/nodes/time every 2 seconds
tail -f player_output.log
```

### Count battles in server log  
```bash
grep -c "Attacker won" server.log
grep -c "Human deleted" server.log
```

### Check for errors
```bash
grep -i "error\|exception\|illegal" server.log player*.log
```

## Filter Threshold
Current setting: **70%** minimum win probability for human attacks

- Blocks: 5v5 (50%), 6v5 (60%), 7v5 (68%)
- Allows: 8v5 (76%), 10v5 (100%)

Location: `ai/move_generator.py:186`

## Performance Expectations
- Search depth: 3-4
- Time per move: 1.8s (under 2.0s limit)
- Nodes explored: ~19,000-20,000

## Cleanup
```bash
pkill -f "go run"
pkill -f "ai_player.py"
```
