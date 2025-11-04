# Agent Guidelines

## Build & Test Commands
- **Install:** No external dependencies required (uses Python stdlib only)
- **Run AI:** `python3 ai/ai_player.py [ip] [port]` (default: localhost 5555)
- **Run all tests:** `python3 tests/test_ai.py`
- **Run single test:** `python3 tests/test_ai.py` then edit file to run only one function, or use: `python3 -c "from tests.test_ai import test_game_state; test_game_state()"`
- **Available tests:** `test_game_state`, `test_battle_probability`, `test_move_generation`, `test_evaluation`, `test_alpha_beta`, `test_move_application`
- **Run server:** `cd server/twilight-master && go run . -map maps/testmap.xml` (port 5555, UI at http://localhost:8080)
- **Lint:** `ruff check ai/ tests/` or `flake8 ai/ tests/` or `pylint ai/ tests/`
- **Format:** `black ai/ tests/` or `ruff format ai/ tests/`
- **Type check:** `mypy ai/ tests/` (note: imports may show false positives but code runs fine)

## Code Style
- **Imports:** stdlib → third-party → local (alphabetically sorted, grouped with blank lines)
- **Formatting:** Follow PEP 8, max line length 88-100 chars, use Black/Ruff formatter
- **Types:** Add type hints to all function signatures: `def foo(x: int) -> str:`
- **Naming:** snake_case for functions/variables, PascalCase for classes, UPPER_CASE for constants
- **Docstrings:** Use Google or NumPy style for public functions/classes
- **Error handling:** Prefer specific exceptions (EndException, ByeException) over broad catches
- **Testing:** Write descriptive test names: `test_battle_probability_equal_forces`

## Game-Specific
- Server runs on port 5555 (Go backend in server/twilight-master/), web UI at http://localhost:8080
- Client connects via TCP socket: NME → SET/HUM/HME/MAP → UPD loop → MOV responses
- 2-second time limit per move (AI uses 1.8s to be safe)
- Configure server IP/port via CLI args: `python3 ai/ai_player.py <ip> <port>`

## AI Architecture
- **ai/game_state.py**: Board representation (GameState, Cell, Move classes), species tracking
- **ai/move_generator.py**: Legal move generation (rules 1-6), battle probability, move application
- **ai/evaluation.py**: State evaluation (material, position, proximity to humans, center control)
- **ai/alphabeta.py**: Alpha-Beta pruning with iterative deepening (depth 3-5 in 1.8s)
- **ai/client.py**: TCP socket client for server protocol (EndException, ByeException)
- **ai/ai_player.py**: Main entry point, integrates all components with server protocol
- **tests/test_ai.py**: Comprehensive unit tests for all components
