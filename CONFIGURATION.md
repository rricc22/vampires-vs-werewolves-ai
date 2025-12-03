# AI Configuration Guide

Complete guide to customizing the Vampires vs Werewolves AI behavior.

## Quick Start

### Using Presets (Easiest)

```bash
# Interactive menu
python3 configure.py

# Apply a preset directly
python3 configure.py --preset aggressive

# See all available presets
python3 configure.py --list

# Compare two presets
python3 configure.py --compare balanced aggressive
```

### Manual Configuration

Edit `ai/config.py` directly - all settings are documented with comments.

## Available Presets

### 🎯 Balanced (Default)
**Best for:** General gameplay, learning the AI

Well-rounded strategy with good concentration and tactical flexibility.
- Search depth: 4
- Attack threshold: 70% win probability
- Allows strategic 2-group coordination
- Strong anti-fragmentation

### ⚔️ Aggressive
**Best for:** Fast expansion, risky play, testing limits

Takes more risks to expand quickly.
- Search depth: 5 (deeper thinking)
- Attack threshold: 50% win probability (risky!)
- Allows 3-group coordination
- Less concerned with fragmentation
- Prioritizes growing army size

### 🛡️ Defensive
**Best for:** Survival, conservative play, avoiding losses

Extreme concentration, only safe moves.
- Attack threshold: 80% win probability (very safe)
- Never splits groups
- Huge penalties for fragmentation
- Single concentrated force preferred

### ⚡ Speed
**Best for:** Testing, slow hardware, quick iterations

Fast decisions with simple strategy.
- Search depth: 3 (shallow)
- Time limit: 1.0s (fast)
- Single-group moves only
- No splits, simple evaluation

### 🎲 Tactical
**Best for:** Multi-group coordination, strategic positioning

Master of coordinating multiple groups.
- Allows 3-group coordination
- Less penalty for having 2-3 groups
- Strong territorial control emphasis
- Balanced risk tolerance (65% attack threshold)

### 🧪 Experimental
**Best for:** Testing new ideas, custom strategies

Sandbox for trying new approaches.
- More split options
- Higher center control weight
- Moderate risk tolerance

## Configuration Categories

### 1. Search Algorithm

Controls how the AI "thinks" and plans ahead.

```python
SEARCH_MAX_DEPTH = 4        # How many moves ahead to look (3-5 typical)
SEARCH_TIME_LIMIT = 1.8     # Max seconds per move (must be < 2.0)
```

**Impact:**
- Higher depth = smarter but slower
- Depth 3: Basic strategy, ~0.01-0.1s
- Depth 4: Good strategy, ~0.1-1.0s (default)
- Depth 5: Strong strategy, ~1.0-1.8s

### 2. Move Generation

Controls how groups can move and split.

```python
MIN_GROUP_SIZE = 5          # Minimum viable group size
MAX_GROUPS_PER_TURN = 2     # Max simultaneous group moves
MIN_SPLIT_SIZE = 10         # Min size before allowing splits
SPLIT_RATIOS = [1.0, 0.5]   # Allowed split proportions
```

**Split Ratios Explained:**
- `[1.0]` = Never split (always move everything)
- `[1.0, 0.5]` = Can move all or half (default)
- `[1.0, 2/3, 0.5, 1/3]` = Many options (more fragmentation)

**Trade-offs:**
- More splits = more tactical options BUT more fragmentation risk
- Fewer splits = stronger concentration BUT less flexibility

### 3. Battle Mechanics

Controls attack decision-making.

```python
ATTACK_MIN_WIN_PROBABILITY = 0.7  # Minimum win chance to attack
```

**Values:**
- 0.5 (50%) = Very aggressive, takes even fights
- 0.7 (70%) = Balanced, only good odds (default)
- 0.8 (80%) = Conservative, very safe attacks only

### 4. Evaluation Weights

Controls how the AI scores positions.

#### Material Advantage
```python
WEIGHT_MATERIAL = 100  # How much we value having more units
```
Higher = prioritizes army size over other factors.

#### Group Management
```python
BONUS_ONE_GROUP = 100          # Bonus for single concentrated force
PENALTY_TWO_GROUPS = 0         # Penalty for 2 groups (0 = neutral)
PENALTY_THREE_GROUPS = 200     # Penalty for 3 groups
PENALTY_EXCESS_GROUPS = 500    # Penalty per group beyond 3
PENALTY_SMALL_GROUP = 100      # Penalty per weak group
SMALL_GROUP_THRESHOLD = 10     # What counts as "small"
```

**Fragmentation Control:**
- Higher penalties = stronger concentration
- Lower penalties = more tactical flexibility
- Default heavily discourages 3+ groups

#### Tactical Weights
```python
WEIGHT_HUMAN_PROXIMITY = 40    # Value of being near convertible humans
WEIGHT_CENTER_CONTROL = 2      # Value of controlling map center
WEIGHT_THREAT_ASSESSMENT = 20  # Value of favorable combat positions
PENALTY_SPLIT_NEAR_ENEMY = 20  # Penalty for splitting when enemy nearby
```

## Common Tuning Scenarios

### Make AI More Aggressive
```python
SEARCH_MAX_DEPTH = 5
ATTACK_MIN_WIN_PROBABILITY = 0.5
WEIGHT_MATERIAL = 150
WEIGHT_HUMAN_PROXIMITY = 60
```

### Make AI More Defensive
```python
ATTACK_MIN_WIN_PROBABILITY = 0.8
SPLIT_RATIOS = [1.0]
BONUS_ONE_GROUP = 200
PENALTY_THREE_GROUPS = 500
```

### Speed Up Decision Making
```python
SEARCH_MAX_DEPTH = 3
SEARCH_TIME_LIMIT = 1.0
MAX_GROUPS_PER_TURN = 1
```

### Enable Multi-Group Tactics
```python
MAX_GROUPS_PER_TURN = 3
SPLIT_RATIOS = [1.0, 2/3, 0.5]
PENALTY_TWO_GROUPS = -20  # Actually BONUS for 2 groups
PENALTY_THREE_GROUPS = 50  # Reduced penalty
```

### Reduce Fragmentation
```python
SPLIT_RATIOS = [1.0]
MIN_SPLIT_SIZE = 20
BONUS_ONE_GROUP = 200
PENALTY_THREE_GROUPS = 500
PENALTY_EXCESS_GROUPS = 1000
```

## CLI Commands Reference

```bash
# Show all commands
python3 configure.py --help

# Interactive menu (recommended for beginners)
python3 configure.py

# List all available presets
python3 configure.py --list

# Show current configuration
python3 configure.py --show

# Apply a preset
python3 configure.py --preset balanced
python3 configure.py --preset aggressive
python3 configure.py --preset defensive
python3 configure.py --preset speed
python3 configure.py --preset tactical
python3 configure.py --preset experimental

# Compare two presets
python3 configure.py --compare balanced aggressive
python3 configure.py --compare defensive speed

# Reset to default (balanced)
python3 configure.py --reset
```

## Testing Your Configuration

After changing configuration, test it:

```bash
# Run unit tests
python3 tests/test_ai.py

# Quick game test
bash play_game.sh

# Watch game at: http://localhost:8080
```

## Understanding the Impact

### Search Depth Impact

| Depth | Nodes Explored | Time    | Strategy Level |
|-------|---------------|---------|----------------|
| 2     | ~20-50        | 0.01s   | Reactive       |
| 3     | ~100-500      | 0.05s   | Basic planning |
| 4     | ~500-5000     | 0.5s    | Good strategy  |
| 5     | ~2000-20000   | 1.5s    | Strong play    |

### Group Count Impact

| Groups | Strength | Flexibility | Risk     |
|--------|----------|-------------|----------|
| 1      | Maximum  | Low         | Safe     |
| 2      | High     | Good        | Balanced |
| 3      | Medium   | High        | Risky    |
| 4+     | Low      | Very high   | Dangerous|

### Attack Threshold Impact

| Threshold | Attacks/Game | Wins | Losses | Style        |
|-----------|--------------|------|--------|--------------|
| 50%       | Many (~15)   | 8    | 7      | Aggressive   |
| 70%       | Moderate (~8)| 7    | 1      | Balanced     |
| 80%       | Few (~4)     | 4    | 0      | Conservative |

## Advanced: Custom Profiles

Create your own preset in `ai/config_presets.py`:

```python
MY_CUSTOM = {
    "name": "My Custom Strategy",
    "description": "Description of your strategy",
    "config": {
        "SEARCH_MAX_DEPTH": 4,
        "ATTACK_MIN_WIN_PROBABILITY": 0.65,
        # ... other parameters
    }
}

# Add to PRESETS dict
PRESETS["my_custom"] = MY_CUSTOM
```

Then use: `python3 configure.py --preset my_custom`

## Troubleshooting

### AI Makes Bad Moves
1. Check `SEARCH_MAX_DEPTH` - increase if too low
2. Check `ATTACK_MIN_WIN_PROBABILITY` - may be too aggressive
3. Run tests: `python3 tests/test_ai.py`

### AI Too Slow
1. Decrease `SEARCH_MAX_DEPTH` (4 → 3)
2. Decrease `SEARCH_TIME_LIMIT` (1.8 → 1.0)
3. Reduce `SPLIT_RATIOS` options
4. Set `MAX_GROUPS_PER_TURN = 1`

### AI Fragments Too Much
1. Use defensive preset: `python3 configure.py --preset defensive`
2. Set `SPLIT_RATIOS = [1.0]`
3. Increase `PENALTY_THREE_GROUPS` to 500+
4. Increase `BONUS_ONE_GROUP` to 200+

### Config Not Taking Effect
1. Restart the AI player
2. Check for syntax errors in `ai/config.py`
3. Verify changes saved: `python3 configure.py --show`

## Best Practices

1. **Start with presets** - Don't manually tune until you understand them
2. **Change one thing at a time** - Easier to see impact
3. **Test after changes** - Run `python3 tests/test_ai.py`
4. **Keep backups** - Copy `ai/config.py` before major changes
5. **Use version control** - Commit good configurations

## Performance Guidelines

### For Competitive Play
```python
SEARCH_MAX_DEPTH = 4
SEARCH_TIME_LIMIT = 1.8
ATTACK_MIN_WIN_PROBABILITY = 0.7
```

### For Development/Testing
```python
SEARCH_MAX_DEPTH = 3
SEARCH_TIME_LIMIT = 1.0
DEBUG_SEARCH_STATS = True
```

### For Demonstrations
```python
SEARCH_MAX_DEPTH = 5
SEARCH_TIME_LIMIT = 1.8
WEIGHT_CENTER_CONTROL = 10  # More dramatic
```

## Next Steps

1. Try each preset to see different play styles
2. Experiment with one category at a time
3. Create your own custom preset
4. Compare against default to measure improvement
5. Share successful configurations!

## Questions?

- Check README.md for general project info
- Check DEVELOPMENT.md for architecture details
- Open an issue on GitHub for help
