# Configuration System

## Quick Start

**Running a game with a specific mode:**
```bash
bash play_game.sh
# Select mode when prompted (1-7)
```

**Change mode manually:**
```bash
python3 ai/modes.py aggressive
```

---

## File Structure

### `ai/modes.py` (EDIT THIS TO CUSTOMIZE MODES)
Simple file with all mode definitions. This is where you configure each mode.

**Example:**
```python
AGGRESSIVE = {
    "SEARCH_MAX_DEPTH": 5,           # Search deeper
    "ATTACK_MIN_WIN_PROBABILITY": 0.1,  # Take more risks
    "SPLIT_RATIOS": [1.0, 2/3, 0.5], # Allow more splits
    # ... more parameters
}
```

### `ai/config.py` (AUTO-UPDATED)
Main configuration file. Gets updated automatically when you apply a mode.
You can also edit this directly for fine-tuning.

---

## Available Modes

| Mode | Description | Key Characteristics |
|------|-------------|---------------------|
| `balanced` | Default, well-rounded | Depth 4, 70% attack threshold, 1-2 groups |
| `aggressive` | Fast expansion, risky | Depth 5, 50% attack threshold, 2-3 groups |
| `defensive` | Safe, concentrated | Depth 4, 80% attack threshold, 1 group only |
| `speed` | Fast decisions | Depth 3, 1.0s time limit, 1 group only |
| `tactical` | Multi-group coordination | Depth 4, 65% attack threshold, 2-3 groups |
| `experimental` | Testing ground | Various experimental settings |

---

## Key Parameters Explained

### Search Parameters
- `SEARCH_MAX_DEPTH`: How many moves ahead to look (3-5)
- `SEARCH_TIME_LIMIT`: Max time per move in seconds (must be < 2.0)

### Move Generation
- `MIN_GROUP_SIZE`: Minimum units in a group (prevents tiny groups)
- `MAX_GROUPS_PER_TURN`: How many groups can move simultaneously (1-3)
- `SPLIT_RATIOS`: How to split groups when moving
  - `[1.0]` = always move everything (no fragmentation)
  - `[1.0, 0.5]` = move all OR half
  - `[1.0, 2/3, 0.5]` = more options (more fragmentation)

### Battle Mechanics
- `ATTACK_MIN_WIN_PROBABILITY`: Minimum chance to attack (0.0-1.0)
  - `0.5` = aggressive (50% chance OK)
  - `0.7` = balanced
  - `0.8` = conservative (only very safe attacks)

---

## How It Works

1. **play_game.sh** asks you to select a mode
2. Runs `python3 ai/modes.py <mode>`
3. **modes.py** updates values in **config.py**
4. AI players use the updated **config.py** settings

---

## Examples

### Create a New Custom Mode
Edit `ai/modes.py` and add:

```python
CUSTOM = {
    "SEARCH_MAX_DEPTH": 4,
    "ATTACK_MIN_WIN_PROBABILITY": 0.6,
    "SPLIT_RATIOS": [1.0, 0.5],
    # ... other parameters
}

# Add to MODES dictionary
MODES = {
    # ... existing modes
    "custom": CUSTOM,
}

# Add description
DESCRIPTIONS = {
    # ... existing descriptions
    "custom": "My custom strategy",
}
```

Then use it:
```bash
python3 ai/modes.py custom
```

### Quick Test Different Modes
```bash
# Try aggressive mode
python3 ai/modes.py aggressive
python3 ai/ai_player.py localhost 5555

# Try defensive mode
python3 ai/modes.py defensive
python3 ai/ai_player.py localhost 5555
```

---

## Migration from Old System

**Old files (can be deleted):**
- `ai/configure.py` - Complex CLI tool (replaced by simple modes.py)
- `ai/config_presets.py` - Preset definitions (merged into modes.py)

**New simplified system:**
- `ai/modes.py` - ONE file to rule them all
- `ai/config.py` - Gets updated automatically

**What changed:**
- No more interactive confirmation prompts
- Simpler file structure
- Easier to customize modes
- Same functionality, less complexity
