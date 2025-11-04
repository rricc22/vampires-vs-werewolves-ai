# Vampires VS Werewolves - Alpha-Beta AI

## Overview

This is an AI player for the Vampires VS Werewolves game that uses **Alpha-Beta pruning with iterative deepening** to make intelligent decisions.

## Architecture

### Core Components

1. **game_state.py** - Game state representation
   - `GameState`: Complete board state with all creatures
   - `Cell`: Individual grid cell with creature counts
   - `Move`: Represents a single move action
   - `Species`: Enum for creature types (HUMAN, VAMPIRE, WEREWOLF)

2. **move_generator.py** - Move generation and battle simulation
   - `generate_all_moves()`: Generates all legal move combinations
   - `calculate_battle_probability()`: Computes battle win probability
   - `simulate_battle()`: Simulates battle outcomes
   - `apply_move_to_state()`: Applies moves to create new game states

3. **evaluation.py** - State evaluation function
   - `evaluate_state()`: Scores game states (positive = good for us)
   - Considers: material advantage, position, proximity to humans, center control, threats

4. **alphabeta.py** - Alpha-Beta search algorithm
   - `AlphaBetaSearch`: Implements minimax with alpha-beta pruning
   - Iterative deepening for time management
   - 1.8 second time limit per move

5. **ai_player.py** - Main AI player
   - `AIPlayer`: Integrates all components
   - Handles server communication
   - Main game loop

## Algorithm Details

### Alpha-Beta Pruning

The AI uses minimax search with alpha-beta pruning to look ahead several turns:

- **Maximizing player (us)**: Try to maximize evaluation score
- **Minimizing player (opponent)**: Opponent tries to minimize our score
- **Pruning**: Cuts off branches that can't affect the final decision

### Iterative Deepening

To respect the 2-second time limit:
- Starts with depth 1, then 2, 3, etc.
- Always has a valid move ready
- Stops when time runs out
- Typically reaches depth 3-5

### Evaluation Function

Scores game states based on:
1. **Material (100 pts/unit)**: Total creature count difference
2. **Distribution (10 pts/group)**: Bonus for spreading out
3. **Proximity to humans (5 pts)**: Closer to humans = better
4. **Center control (2 pts)**: Control of map center
5. **Tactical threats (±20 pts)**: Nearby enemies we can kill/be killed by

### Battle Probability

Based on game rules:
- Equal forces: P = 0.5
- Attackers < Defenders: P = attackers / (2 * defenders)
- Attackers > Defenders: P = 0.5 + (attackers - defenders) / (2 * defenders)

Expected value calculation accounts for random battle outcomes.

## Usage

### Running the AI

```bash
# Run against server on localhost:5555
python3 ai_player.py

# Run against specific server
python3 ai_player.py 192.168.1.100 5555
```

### Testing

```bash
# Run unit tests
python3 test_ai.py
```

### Starting the Server

```bash
cd twilight-master
go run . -map maps/testmap.xml
# Server runs on port 5555, web UI on http://localhost:8080
```

## Strategy

### Early Game
- Rapidly expand to convert isolated humans
- Avoid enemy contact unless we have 1.5x advantage
- Spread out to control more territory

### Mid Game
- Block opponent's access to remaining humans
- Consolidate forces when necessary for combat
- Maintain material advantage

### Late Game
- Calculate optimal paths to eliminate opponent
- Concentrate forces for decisive battles
- Aggressive positioning when winning

## Performance

- **Search depth**: Typically 3-5 plies in 1.8 seconds
- **Nodes explored**: 500-5000 per move depending on branching
- **Move quality**: Strong tactical and strategic play

## Future Improvements

1. **Opening book**: Pre-computed optimal openings for common maps
2. **Transposition tables**: Cache evaluated positions
3. **Move ordering**: Better heuristics to improve pruning
4. **Quiescence search**: Continue search in volatile positions
5. **Multi-group moves**: Currently simplified to single moves per turn
6. **Opponent modeling**: Learn opponent's patterns
7. **Monte Carlo simulations**: Better handling of random battles

## Files Created

- `game_state.py` - Core game representation (200 lines)
- `move_generator.py` - Move generation & battles (260 lines)
- `evaluation.py` - Evaluation function (110 lines)
- `alphabeta.py` - Alpha-Beta search (180 lines)
- `ai_player.py` - Main AI integration (150 lines)
- `test_ai.py` - Unit tests (150 lines)

Total: ~1050 lines of well-documented Python code

## Command Line Arguments

```bash
python3 ai_player.py [IP] [PORT]

Arguments:
  IP    Server IP address (default: localhost)
  PORT  Server port (default: 5555)
```

## Debugging

The AI prints detailed information during execution:
- Game state updates
- Move computation time
- Search depth and nodes explored
- Moves being sent

## Requirements

- Python 3.7+
- Standard library only (no external dependencies)

## License

Educational project for CentraleSupélec AI course.
