# Vampires vs Werewolves AI

An intelligent AI player for the Vampires vs Werewolves strategy game, using Alpha-Beta pruning with iterative deepening.

## Quick Start

### Run a Complete Game

```bash
bash play_game.sh
```

This starts the server and launches 2 AI players. Watch the game at http://localhost:8080

### Manual Setup

```bash
# Terminal 1: Start server
cd server/twilight-master
go run . -map maps/map8.xml

# Terminal 2: Run AI player 1 (Vampires)
python3 ai/ai_player.py localhost 5555

# Terminal 3: Run AI player 2 (Werewolves)
python3 ai/ai_player.py localhost 5555

# Open browser: http://localhost:8080
```

### Run Tests

```bash
python3 tests/test_ai.py
```

## How It Works

### AI Strategy
- **Alpha-Beta Search**: Looks 3-5 moves ahead in 1.8 seconds
- **Smart Evaluation**: Scores positions based on material, position, threats
- **Battle Simulation**: Calculates win probabilities before attacking
- **Anti-Fragmentation**: Maintains 1-2 strong groups instead of many weak ones
- **Multi-Group Moves**: Can coordinate 2 groups simultaneously

### Key Features
- 70% minimum win probability filter (no risky attacks)
- Iterative deepening for time management
- Multi-group coordination for tactical flexibility
- Concentrated force management (anti-fragmentation)

## Project Structure

```
ai/
├── ai_player.py        # Main entry point
├── alphabeta.py        # Alpha-Beta search algorithm
├── evaluation.py       # Position evaluation function
├── move_generator.py   # Move generation & battle logic
├── game_state.py       # Board state representation
├── client.py           # TCP client for server protocol
├── config.py           # Main configuration file
└── modes.py            # Mode presets (balanced, aggressive, etc.)

tests/
└── test_ai.py          # Unit tests

server/twilight-master/ # Go game server
maps/                   # Game maps (.xml)
```

## Game Rules

- **Objective**: Convert all humans or eliminate the opponent
- **Movement**: Move units 1 cell (horizontal/vertical)
- **Converting Humans**: Need ≥ equal numbers to guarantee conversion
- **Killing Opponents**: Need ≥ 1.5x their numbers to guarantee kill
- **Battles**: Random outcome when numbers don't meet thresholds
- **Time Limit**: 2 seconds per move

## Configuration

The AI has several pre-configured modes for different play styles:

### Using play_game.sh (Recommended)
```bash
bash play_game.sh
# Choose a mode when prompted:
# 1. balanced     - Default, well-rounded strategy
# 2. aggressive   - Deep search, risky attacks, fast expansion
# 3. defensive    - Safe attacks, strong concentration
# 4. speed        - Fast decisions, shallow search
# 5. tactical     - Multi-group coordination master
# 6. experimental - Testing new strategies
# 7. current      - Use current config without changes
```

### Manual Mode Change
```bash
python3 ai/modes.py aggressive
```

### Customize Modes
Edit `ai/modes.py` to adjust parameters for each mode:

```python
AGGRESSIVE = {
    "SEARCH_MAX_DEPTH": 5,           # How deep to search
    "ATTACK_MIN_WIN_PROBABILITY": 0.1,  # Attack threshold
    "SPLIT_RATIOS": [1.0, 2/3, 0.5], # Split options
    # ... more parameters
}
```

### Direct Config Edit
Advanced users can directly edit `ai/config.py` for fine-grained control.

## Requirements

- Python 3.7+ (no external dependencies, stdlib only)
- Go 1.16+ (for server)

## Performance

- **Search Depth**: 3-5 plies
- **Nodes Explored**: 500-5,000 per move
- **Time Per Move**: 0.05-1.8 seconds
- **Code Size**: ~1,050 lines Python

## Development

See [DEVELOPMENT.md](DEVELOPMENT.md) for:
- Build and test commands
- Architecture details
- Code style guidelines
- How to contribute

## Recent Improvements

### Anti-Fragmentation System (2025-12-02)
- **Problem**: AI was creating 5-7 weak groups
- **Solution**: 
  - Reduced split ratios to `[1.0, 0.5]` (all or half)
  - Extreme penalties for 3+ groups (-200 to -2200)
  - Multi-group coordination for tactical flexibility
- **Result**: AI maintains 1-2 strong groups throughout the game

### 70% Attack Filter (2025-11-04)
- **Problem**: AI made 50% probability attacks (too risky)
- **Solution**: Raised filter from 30% → 70% minimum win probability
- **Result**: Zero risky attacks in 102-move test game

## License

Educational project for CentraleSupélec AI course.

## Status

✅ **Production Ready**
- All tests passing
- Strategic improvements verified
- Anti-fragmentation working perfectly
