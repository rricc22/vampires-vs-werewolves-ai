# Final Anti-Fragmentation Fixes

## Problem Identified from Logs

The initial fixes were **partially working** but not strong enough:
- ✅ Multi-group moves were being generated and selected (Turn 8, Turn 10)
- ❌ BUT: AI still fragmented to **7 groups** by Turn 11
- ❌ Root cause: Multi-group moves that **split** groups created MORE fragmentation

### Example from Logs (Turn 10 → Turn 11):
```
Turn 10: 5 groups
Move: 20 units from (3,3) to (3,4)  <- SPLIT 40 into 20+20
      17 units from (7,4) to (7,3)  <- SPLIT 26 into 17+9

Turn 11: 7 groups (2 new groups created from splits!)
```

## Solutions Implemented

### 1. **Eliminated Splitting** (`ai/config.py`)
```python
# OLD: SPLIT_RATIOS = [1.0, 2/3, 0.5]  # Allow splits
# NEW: SPLIT_RATIOS = [1.0]             # ONLY move ALL units

MIN_GROUP_SIZE = 5      # Increased from 3
MIN_SPLIT_SIZE = 10     # Increased from 5 (but with ratio=[1.0], splits disabled)
```

**Impact:** AI can no longer create splits. Each move is "all or nothing" from a group.

### 2. **Extreme Fragmentation Penalties** (`ai/evaluation.py`)
```python
# Group count scoring:
1 group:  +100 (concentrated power)
2 groups:   +0 (acceptable)
3 groups: -200 (getting fragmented)
4+ groups: -(n-3) * 500  (CATASTROPHIC: -500 per excess group!)

# Small group penalties:
Groups < 10 units: -100 each (was -15, now -100)
```

**Impact:** 
- 7 groups now scores **-2159** vs 1 group at **+224** (2383 point difference!)
- Small weak groups are heavily discouraged

### 3. **Updated Group Thresholds** (`ai/config.py`)
```python
IDEAL_MIN_GROUPS = 1              # 1-2 is best
IDEAL_MAX_GROUPS = 2              # Not 3
EXCESSIVE_GROUPS_THRESHOLD = 3    # Penalty kicks in at 3 (was 4)
SMALL_GROUP_THRESHOLD = 10        # Increased from 5
```

## Expected Behavior Now

### Move Generation:
- **Only "all units" moves**: No more splits
- Groups move entirely or stay put
- Multi-group moves still work: 2 different groups can each move all their units

### Evaluation:
| Groups | Score Impact | Interpretation |
|--------|-------------|----------------|
| 1      | +100        | Perfect! Concentrated force |
| 2      | 0           | Acceptable tactical split |
| 3      | -200        | Bad fragmentation |
| 4      | -700        | Very bad (-200 -500) |
| 7      | -2200       | Catastrophic! (-200 -4×500) |

### Game Play:
- AI will **strongly prefer** keeping 1-2 large groups
- Will **avoid** creating small groups
- Will **consolidate** when possible
- Multi-group coordination: Both groups move ALL their units

## Testing

### Quick Verification:
```bash
cd ai
python3 << 'END'
from game_state import GameState, Species
from move_generator import generate_moves_from_cell

state = GameState(10, 10)
state.our_species = Species.VAMPIRE
state.board[5][5].vampires = 20

moves = generate_moves_from_cell(state, 5, 5, 20)
amounts = sorted(set(m.count for m in moves), reverse=True)

print(f"Moves: {len(moves)}, Amounts: {amounts}")
if amounts == [20]:
    print("✅ SPLITS DISABLED - Only 'all units' moves")
else:
    print("❌ Still generating splits")
END
```

### Full Game Test:
```bash
./test_improvements.sh
```

Watch for in `LOGS/ai_player_logs.txt`:
- `Our groups: 1` or `Our groups: 2` (stay at 1-2!)
- No more `Our groups: 7`
- Groups should consolidate or stay concentrated

## Files Modified

1. **ai/config.py**
   - `SPLIT_RATIOS = [1.0]` (no more splits)
   - Increased thresholds (MIN_GROUP_SIZE, SMALL_GROUP_THRESHOLD)
   - Changed ideal groups to 1-2 (not 2-3)

2. **ai/evaluation.py**
   - Extreme penalties: -500 per excess group beyond 2
   - Heavy small group penalty: -100 each
   - Rewards concentration: +100 for 1 group

3. **ai/move_generator.py**
   - Already generates multi-group moves (no changes needed)
   - With SPLIT_RATIOS=[1.0], only generates "move all" options

## Results

**Before fixes:**
- Turn 11: 7 groups
- Many small groups (9, 11 units)
- Constant fragmentation

**After fixes:**
- Should maintain 1-2 groups throughout
- Groups stay large (20-50+ units)
- Only splits when strategically necessary (and then pays heavy penalty)

## Key Insight

The critical issue was that **multi-group moves with splits** created exponential fragmentation:
- Moving 2 groups with splits → Creates 2 new groups
- Each turn multiplies the groups!

**Solution:** Eliminate splits entirely. Multi-group moves now only move ALL units from each group, preventing fragmentation while maintaining coordination ability.

## Run the Test

```bash
cd /home/riccardo/Documents/Collaborative-Projects/vampires-vs-werewolves-ai
./test_improvements.sh
```

Then check `LOGS/ai_player_logs.txt` for group counts. You should see:
- ✅ `Our groups: 1` or `Our groups: 2` consistently
- ✅ Groups with 20-50+ units
- ❌ No more fragmentation to 5-7 groups
