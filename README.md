# Vampires VS Werewolves - AI Player

An intelligent AI player for the Vampires VS Werewolves game using Alpha-Beta pruning with iterative deepening.

## 🎮 Quick Start

### Run a Complete Game (Easiest!)

```bash
# Run server + 2 AI players automatically
bash play_game.sh
```

This will:
- Start the game server
- Launch 2 AI players (Vampires vs Werewolves)
- Show live game stats
- Watch at http://localhost:8080

### Manual Setup (Advanced)

### 1. Start Server
```bash
cd server/twilight-master
go run . -map maps/map8.xml

```bash
# 1. Start the game server
cd server/twilight-master
./twilight -map maps/testmap.xml

# 2. In another terminal, run AI player 1
python3 ai/ai_player.py localhost 5555

# 3. In another terminal, run AI player 2
python3 ai/ai_player.py localhost 5555

# 4. Watch the game at http://localhost:8080
```

### Run Tests

```bash
python3 tests/test_ai.py
```

## 📁 Project Structure

```
Vamp_wolf_game/
├── ai/                          # AI implementation
│   ├── ai_player.py            # Main entry point
│   ├── alphabeta.py            # Alpha-Beta search
│   ├── evaluation.py           # Position evaluation
│   ├── move_generator.py       # Move generation & battles
│   ├── game_state.py           # Game state representation
│   ├── client.py               # Network client
│   └── config.py               # Configuration
├── tests/                       # Test suite
│   └── test_ai.py              # All tests
├── docs/                        # Documentation
│   ├── AI_DOCUMENTATION.md     # Technical details
│   └── Projectv10.pdf          # Project specification
├── maps/                        # Game maps
│   ├── testmap.xml
│   └── thetrap.xml
├── server/                      # Game server (Go)
│   └── twilight-master/
├── AGENTS.md                    # Agent guidelines
├── QUICKSTART.md                # Quick start guide
└── README.md                    # This file
```

## 🤖 AI Features

- **Alpha-Beta Pruning**: Minimax search with alpha-beta pruning
- **Iterative Deepening**: Achieves depth 3-5 in 1.8 seconds
- **Smart Evaluation**: Considers material, position, threats, and strategy
- **Battle Simulation**: Accurate probability calculations per game rules
- **Time Management**: Always stays under 2-second limit

## 📊 Performance

- **Search depth**: 3-5 plies
- **Nodes explored**: 500-5000 per move
- **Time per move**: ~1.5-1.8 seconds
- **Code**: ~1,050 lines of clean Python

## 🧪 Testing

All tests pass successfully:

```bash
$ python3 tests/test_ai.py
============================================================
Running AI Tests
============================================================
✓ GameState test passed
✓ Battle probability test passed
✓ Move generation test passed
✓ Evaluation test passed
✓ Move application test passed
✓ Alpha-Beta test passed
============================================================
All tests passed! ✓
============================================================
```

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - How to run and use the AI
- **[AGENTS.md](AGENTS.md)** - Guidelines for developers
- **[docs/AI_DOCUMENTATION.md](docs/AI_DOCUMENTATION.md)** - Technical details

## 🎯 Game Rules

- **Objective**: Be the dominant species (Vampires or Werewolves)
- **Convert humans**: Need ≥ equal numbers
- **Kill opponents**: Need ≥ 1.5x their numbers
- **Random battles**: When numbers don't meet thresholds
- **Time limit**: 2 seconds per move

## 🔧 Requirements

- Python 3.7+
- Go 1.16+ (for server)
- No external Python dependencies (stdlib only)

### Building the Server

If the compiled binary isn't present, build it:

```bash
cd server/twilight-master
go build -o twilight .
```

The binary is excluded from git to keep the repository clean.

## ✅ Recent Improvements

### Suicidal Attack Fix (2025-11-04)
- **Fixed**: AI no longer makes risky 50% probability attacks
- **Changed**: Filter threshold raised from 30% → 70% minimum win probability
- **Tested**: Verified on both symmetric (map8) and asymmetric (thetrap) maps
- **Result**: 102-move test game with zero risky attacks
- **Docs**: See `docs/TESTING_SUMMARY.md` for full verification

## 🚀 Future Improvements

1. Opening book for common maps
2. Transposition tables for caching
3. Better move ordering for pruning
4. Multi-group coordinated moves
5. Opponent modeling
6. Dynamic risk threshold based on game state
7. Endgame tables for few-unit scenarios

## 📝 License

Educational project for CentraleSupélec AI course.

## 👤 Author

Riccardo's AI Team

---

**Status**: Production ready ✅ (All tests passing, strategic improvements verified)
