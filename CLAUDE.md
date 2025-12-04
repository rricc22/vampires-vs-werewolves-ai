# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI player for the Vampires vs Werewolves strategy game using Alpha-Beta pruning with iterative deepening. The AI maintains 1-2 concentrated groups and uses a 70% minimum win probability filter for attacks.

**Tech Stack**: Python 3.7+ (AI, stdlib only), Go 1.16+ (server)

## Common Commands

```bash
# Run complete game (interactive launcher)
bash play_game.sh

# Run tests
python3 tests/test_ai.py

# Run single test
python3 -c "from tests.test_ai import test_game_state; test_game_state()"

# Linting & formatting
ruff check ai/ tests/
black ai/ tests/
mypy ai/ tests/

# Manual game setup (3 terminals)
cd server/twilight-master && go run . -map maps/the_map.xml  # Terminal 1
python3 ai/ai_player.py localhost 5555                        # Terminal 2 & 3
```

## Architecture

```
ai_player.py (Main orchestrator)
    │
    ├─► client.py (TCP protocol: NME/SET/HUM/HME/MAP/UPD/MOV)
    │
    └─► alphabeta.py (Iterative deepening search, 1.8s limit)
         │
         ├─► move_generator.py (Move expansion, 70% win filter, battle probability)
         ├─► game_state.py (2D board, Species enum, Move class)
         └─► evaluation.py (Material + fragmentation penalties + tactical factors)
```

**Data Flow**: Server sends UPD → Alpha-Beta searches moves → Best move sent via MOV

## Key Implementation Details

### Coordinate System
- **Internal** (game_state.py): x=row, y=col
- **Protocol** (client.py): x=col, y=row
- Conversion handled in `Move.to_tuple()`

### Move Generation
- Single and multi-group moves (up to 2 groups per turn)
- Split ratios: `[1.0, 0.5]` (move all or half)
- Filters: 70% win probability for attacks, minimum group size 5

### Evaluation Scoring
- Material: +100 per unit difference (primary factor)
- 1 group: +100 bonus, 2 groups: neutral, 3+ groups: -200 to -2200 penalty
- Small groups (<10 units): -100 each
- Tactical: human proximity +40, center control +2

### Battle Probability
- `P(win) = 0.5 + (A-D)/(2*D)` for attackers A vs defenders D
- Guaranteed outcomes: ≥1.5x for killing opponents, ≥1x for converting humans

## Configuration

Key tuning in `ai/config.py`:
- `SPLIT_RATIOS` - Controls fragmentation (`[1.0]` = no splits, `[1.0, 0.5]` = allow halves)
- `MIN_GROUP_SIZE` - Minimum viable group (default: 5)
- `ATTACK_MIN_WIN_PROBABILITY` - Attack filter (default: 0.7)

Search settings in `ai/ai_player.py`:
- `max_depth=4` - Search depth (3-5 typical)
- `time_limit=1.8` - Must be under 2.0s server limit

Presets available via `python3 ai/configure.py --preset aggressive|defensive|speed|tactical`

## Server Protocol

```
Connect → NME → SET/HUM/HME/MAP → [UPD → MOV]* → END/BYE
```

Move format: `MOV <count> <x1> <y1> <units1> <x2> <y2> [<x3> <y3> <units2> <x4> <y4>]...`

## Known Issues

Server bug in `server/twilight-master/server.go:22`: `defer l.Close()` before error check can panic. Fix: move defer after error check.

## Performance

- Search depth: 3-5 plies
- Nodes explored: 500-5,000 per move
- Time per move: 0.05-1.8 seconds
