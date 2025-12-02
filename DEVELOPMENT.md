# Development Guide

## Build & Test Commands

### Running the AI
```bash
# Default (localhost:5555)
python3 ai/ai_player.py

# Custom server
python3 ai/ai_player.py <ip> <port>
```

### Running the Server
```bash
cd server/twilight-master
go run . -map maps/map8.xml      # Port 5555, UI at http://localhost:8080

# Other maps
go run . -map maps/testmap.xml
go run . -map maps/thetrap.xml
```

### Testing
```bash
# Run all tests
python3 tests/test_ai.py

# Run single test
python3 -c "from tests.test_ai import test_game_state; test_game_state()"
```

Available tests:
- `test_game_state` - Board representation
- `test_battle_probability` - Battle calculations
- `test_move_generation` - Move generation logic
- `test_evaluation` - Position scoring
- `test_alpha_beta` - Search algorithm
- `test_move_application` - State updates

### Code Quality
```bash
# Linting
ruff check ai/ tests/
# or: flake8 ai/ tests/
# or: pylint ai/ tests/

# Formatting
black ai/ tests/
# or: ruff format ai/ tests/

# Type checking
mypy ai/ tests/
```

## Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────┐
│                     ai_player.py                        │
│  Main orchestrator - connects to server, runs game loop │
└──────────────┬──────────────────────────────────────────┘
               │
      ┌────────┴────────┐
      │                 │
┌─────▼─────┐     ┌────▼───────┐
│ client.py │     │ alphabeta  │
│ TCP comms │     │ .py        │
└───────────┘     │ Search     │
                  └────┬───────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
   ┌────▼───┐    ┌────▼────────┐  ┌─▼─────────┐
   │ game_  │    │ move_       │  │ evaluation│
   │ state  │◄───┤ generator   │  │ .py       │
   │ .py    │    │ .py         │  │ Scoring   │
   └────────┘    └─────────────┘  └───────────┘
```

### File Responsibilities

**ai/ai_player.py** (Main entry point)
- Connects to server via TCP
- Receives game state updates
- Calls alpha-beta search for best move
- Sends moves back to server
- Handles game loop and timing

**ai/alphabeta.py** (Search algorithm)
- Implements alpha-beta pruning
- Iterative deepening (depth 1 → 2 → 3 → 4...)
- Time management (stops before 1.8s)
- Returns best move found

**ai/evaluation.py** (Position scoring)
- Scores game states (-∞ to +∞)
- Factors: material, position, threats, groups
- Penalty for fragmentation (-200 to -2200 for 3-7 groups)
- Bonus for concentration (+100 for 1 group)

**ai/move_generator.py** (Move generation)
- Generates all legal moves (single + multi-group)
- Battle probability calculations
- 70% win probability filter
- Multi-group move validation (Rule 5)

**ai/game_state.py** (State representation)
- Board representation (2D grid)
- Species tracking (vampires, werewolves, humans)
- Move application
- State copying for search tree

**ai/client.py** (Network client)
- TCP socket communication
- Protocol: NME → SET/HUM/HME/MAP → UPD loop → MOV
- Exception handling (EndException, ByeException)

**ai/config.py** (Configuration)
- Server settings (IP, port)
- Group thresholds and split ratios
- Evaluation penalties and bonuses

## Code Style

### General
- **Python 3.7+** with type hints
- **PEP 8** formatting (88-100 char lines)
- **No external dependencies** (stdlib only)

### Imports
```python
# stdlib imports
import socket
import time
from typing import List, Optional

# third-party imports (none currently)

# local imports
from game_state import GameState, Species
from evaluation import evaluate_state
```

### Naming
- Functions/variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_CASE`
- Private: `_leading_underscore`

### Type Hints
```python
def evaluate_state(state: GameState) -> float:
    """Always include type hints."""
    score: float = 0.0
    return score
```

### Docstrings
```python
def calculate_battle_probability(attackers: int, defenders: int) -> float:
    """
    Calculate probability of attackers winning a battle.
    
    Args:
        attackers: Number of attacking units
        defenders: Number of defending units
        
    Returns:
        Probability of attackers winning (0.0 to 1.0)
    """
```

## Testing

### Test Structure
```python
def test_feature_name():
    """Test description."""
    # Arrange
    state = GameState(10, 10)
    
    # Act
    result = some_function(state)
    
    # Assert
    assert result == expected_value
    print("✓ Test passed")
```

### Running Tests
Tests are in `tests/test_ai.py` and use simple assertions (no pytest/unittest needed):

```bash
python3 tests/test_ai.py  # Runs all tests
```

### Test Coverage
- GameState: Board operations, species tracking
- Move generation: Legal moves, battle probabilities, filters
- Evaluation: Scoring logic, fragmentation penalties
- Alpha-beta: Search depth, time limits, best move selection
- Move application: State updates, battles, conversions

## Configuration & Tuning

### Anti-Fragmentation Settings (`ai/config.py`)

```python
# Movement configuration
MIN_GROUP_SIZE = 5           # Don't create groups smaller than this
MAX_GROUPS_PER_TURN = 2      # Max groups moving simultaneously
MIN_SPLIT_SIZE = 10          # Minimum size before allowing splits

# Split ratios - controls fragmentation
SPLIT_RATIOS = [1.0, 0.5]    # [1.0] = no splits (most conservative)
                              # [1.0, 0.5] = allow strategic half-splits
                              # [1.0, 2/3, 0.5] = more flexibility, more fragmentation

# Group evaluation
IDEAL_MIN_GROUPS = 1         # Prefer 1-2 groups
IDEAL_MAX_GROUPS = 2
EXCESSIVE_GROUPS_THRESHOLD = 3  # Penalty starts here
SMALL_GROUP_THRESHOLD = 10      # Groups below this penalized
```

### Search Settings (`ai/ai_player.py`)

```python
best_move = alpha_beta_search(
    state=self.game_state,
    max_depth=4,        # Maximum search depth (3-5 typical)
    time_limit=1.8,     # Time limit in seconds (under 2.0)
    debug=False         # Enable debug output
)
```

### Evaluation Weights (`ai/evaluation.py`)

```python
# Material value
score += our_total * 10.0

# Group count penalties
if num_groups == 1:
    score += 100  # Concentration bonus
elif num_groups == 2:
    score += 0    # Acceptable
elif num_groups == 3:
    score -= 200  # Fragmentation penalty
else:
    score -= 200 + (num_groups - 3) * 500  # Catastrophic

# Small groups
small_groups = [g for g in groups if g < 10]
score -= len(small_groups) * 100

# Proximity to humans (encourages conversion)
score += human_proximity_score

# Center control (strategic positioning)
score += center_control_score
```

## Game Protocol

### Server Communication

```
1. Client connects → Server: "NME" (name query)
2. Client → "AlphaBetaAI_v1"

3. Server → "SET n" (you are player n: 0=vampires, 1=werewolves)
4. Server → "HUM n x1 y1 ... xn yn" (human positions)
5. Server → "HME n x1 y1 ... xn yn" (your starting position)
6. Server → "MAP rows cols" (board dimensions)

7. Game loop:
   Server → "UPD n x1 y1 c1 ... xn yn cn" (state update)
   Client → "MOV n x1 y1 c1 x2 y2 ... xn yn cn xn+1 yn+1"
   
8. Game end:
   Server → "END" (game over)
   Server → "BYE" (disconnect)
```

### Move Format

Single move: `MOV 1 x1 y1 count1 x2 y2`
- Move `count1` units from `(x1, y1)` to `(x2, y2)`

Multi-group: `MOV 2 x1 y1 c1 x2 y2 x3 y3 c2 x4 y4`
- Move `c1` units from `(x1, y1)` to `(x2, y2)`
- AND move `c2` units from `(x3, y3)` to `(x4, y4)`

## Troubleshooting

### "Connection refused"
```bash
# Make sure server is running first
cd server/twilight-master
go run . -map maps/map8.xml

# Wait for "Starting tcp server" message
# Then connect AI
```

### "Port already in use"
```bash
# Kill existing server
lsof -ti:5555 -ti:8080 | xargs kill -9

# Restart server
cd server/twilight-master
go run . -map maps/map8.xml
```

### "AI makes bad moves"
1. Check evaluation weights in `ai/evaluation.py`
2. Increase search depth in `ai/ai_player.py` (max_depth)
3. Verify 70% filter in `ai/move_generator.py:192`
4. Check group thresholds in `ai/config.py`

### "AI too slow"
1. Reduce max_depth (4 → 3)
2. Reduce time_limit (1.8 → 1.5)
3. Reduce SPLIT_RATIOS options (fewer moves to consider)

### "AI fragments too much"
1. Set `SPLIT_RATIOS = [1.0]` (no splits)
2. Increase penalties in evaluation.py
3. Lower `EXCESSIVE_GROUPS_THRESHOLD` (3 → 2)

## Server Bug Fix

**Known Issue**: `server/twilight-master/server.go:22` has a bug where `defer l.Close()` is called before checking if `Listen()` succeeded. This causes a panic if the port is already in use.

**Fix**:
```go
// BEFORE (buggy)
l, err := net.Listen("tcp", ":5555")
defer l.Close()  // Can panic if l is nil
if err != nil {
    panic(err.Error())
}

// AFTER (fixed)
l, err := net.Listen("tcp", ":5555")
if err != nil {
    panic(err.Error())
}
defer l.Close()  // Safe: only called if Listen succeeded
```

## Performance Metrics

### Typical Performance
- **Search depth**: 3-5 plies
- **Nodes explored**: 500-5,000 per move
- **Time per move**: 0.05-1.8 seconds
- **Early game**: Depth 4-5 (few moves)
- **Late game**: Depth 3 (many moves)

### Optimization Tips
1. **Move ordering**: Order moves by evaluation to improve pruning
2. **Transposition tables**: Cache evaluated positions
3. **Opening book**: Pre-compute first 3-5 moves for common maps
4. **Endgame tables**: Pre-compute win/loss for few-unit scenarios

## Contributing

1. Follow code style guidelines above
2. Add type hints to all functions
3. Write tests for new features
4. Run test suite before committing
5. Update this doc if adding new features

## Additional Resources

- **Game Spec**: `docs/Projectv10.pdf`
- **GitHub Issues**: `.github/ISSUE_TEMPLATE/`
- **Test Script**: `test_improvements.sh`
- **Play Script**: `play_game.sh`
