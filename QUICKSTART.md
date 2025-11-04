# Quick Start Guide

## Running the AI

### 1. Start the game server (in one terminal)
```bash
cd server/twilight-master
go run . -map maps/testmap.xml
```
The server will start on port 5555 and web interface on http://localhost:8080

### 2. Run your AI player (in another terminal)
```bash
python3 ai/ai_player.py localhost 5555
```

### 3. Watch the game
Open http://localhost:8080 in your browser to see the visualization

## Testing the AI

Run the test suite:
```bash
python3 tests/test_ai.py
```

Expected output:
```
============================================================
Running AI Tests
============================================================

Testing GameState...
✓ GameState test passed

Testing battle probabilities...
✓ Battle probability test passed

Testing move generation...
✓ Move generation test passed

Testing evaluation function...
✓ Evaluation test passed

Testing move application...
✓ Move application test passed

Testing Alpha-Beta search...
✓ Alpha-Beta test passed

============================================================
All tests passed! ✓
============================================================
```

## Understanding the Output

When the AI runs, you'll see:
```
Connected as AlphaBetaAI_v1
Received: set
Received: hum
Received: hme
Received: map
Game initialized, starting main loop...

============================================================
Turn 1
============================================================
GameState(rows=10, cols=10, our_species=1, total_ours=8, total_opponent=8)
Computing move...
Depth 1: value=250.47, nodes=40
Depth 2: value=237.37, nodes=219
Depth 3: value=245.12, nodes=1523
Search complete: depth=3, nodes=1523, time=1.652s
Move computed in 1.652s
Sending moves: [(5, 5, 4, 4, 3)]
```

## Key Files

- **ai/ai_player.py** - Main file to run
- **ai/game_state.py** - Game board representation
- **ai/alphabeta.py** - Search algorithm
- **ai/move_generator.py** - Move generation & battle logic
- **ai/evaluation.py** - Position evaluation
- **tests/test_ai.py** - Tests

## Troubleshooting

### "Connection refused"
- Make sure the server is running first
- Check the port number (default: 5555)

### "No moves found"
- This is rare, AI will use fallback
- Check that game state is initialized properly

### Slow performance
- Reduce max_depth in ai/alphabeta.py (currently 4)
- Reduce time_limit (currently 1.8s)

### AI makes bad moves
- Tune evaluation function weights in ai/evaluation.py
- Increase search depth for better lookahead
- Check battle probability calculations

## Next Steps

1. Test against the server with different maps
2. Tune evaluation function weights for your strategy
3. Add opening book for common starting positions
4. Implement multi-group coordinated moves
5. Add transposition tables for speed
6. Test in tournament conditions
