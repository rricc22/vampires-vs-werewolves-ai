# Fix Summary: Map8.xml Suicidal Attack Issue

## Problem Identified

The AI was making suicidal attacks on map8.xml, specifically sending all 5 units to attack 5 humans despite this being a strategically poor move.

### Initial Hypothesis (WRONG)
We initially suspected a coordinate system bug where x/y or row/col were being mixed up.

### Root Cause (CORRECT)
The coordinate system was actually **working correctly**. The real problem was:

1. **Move was strategically valid but tactically terrible**
   - 5 units attacking 5 humans = 50% win probability
   - Even if won, expected survivors = ~2-3 units (heavy losses)
   - Meanwhile opponent has full strength elsewhere
   
2. **Filter threshold too permissive**
   - Old threshold: 30% win probability
   - This allowed 50% win chance moves (5v5)
   - These are "pyrrhic victories" - winning the battle but losing the war

## Solution

**Raised filter threshold from 30% to 70%**

### Changes Made

1. **ai/move_generator.py:182-192** - Updated filter in `generate_moves_from_cell()`
   ```python
   # OLD: if win_prob < 0.3:
   # NEW: if win_prob < 0.7:
   ```

2. **ai/evaluation.py:54-86** - Updated evaluation function to match new threshold
   - Rewards moves with ≥70% win probability strongly
   - Gives small reward for ≥50% win probability
   - Penalizes moves with <50% win probability

3. **Added debug logging** to trace filtering decisions (optional, can be removed)

### Test Results

✓ **Unit tests**: All 6 existing tests pass  
✓ **Filter test**: 
  - Correctly blocks 5v5 attacks (50% < 70%)
  - Correctly allows 10v5 attacks (100% ≥ 70%)

## Coordinate System Verification

For reference, the coordinate system is **correct**:

- **Server protocol**: (x, y) where x=column, y=row, (0,0)=top-left
- **Our internal**: board[row][col], so board[y][x]
- **Move.to_tuple()**: Correctly swaps to (col_from, row_from, count, col_to, row_to)

Example:
- Werewolves at server position X=1, Y=3 (col=1, row=3)
- We store as home_position = (1, 3)
- We access board[home[1]][home[0]] = board[3][1] ✓
- Move from (row=3, col=1) to (row=2, col=2) sends (1,3,count,2,2) ✓

## Performance Impact

The 70% threshold is more conservative, which means:
- **Pros**: Prevents wasteful attacks, preserves army strength
- **Cons**: May miss some opportunistic conversions

However, this is the correct tradeoff because:
1. Preserving army size is crucial in this game
2. Weak attacks leave us vulnerable to opponent
3. Better to wait for high-confidence opportunities

## Files Modified

- `ai/move_generator.py` - Lines 179-192 (filter threshold + debug logging)
- `ai/evaluation.py` - Lines 54-86 (updated evaluation thresholds)
- `ai/ai_player.py` - Lines 35-52 (added MAP debug logging, can be removed)
- `tests/test_filter.py` - NEW file testing the filter threshold

## Recommendations

1. **Keep the 70% threshold** - It prevents strategically poor moves
2. **Consider removing debug logging** in production (optional)
3. **Monitor performance** on various maps to tune threshold if needed
4. **Possible future enhancement**: Context-aware thresholds
   - Use lower threshold (50-60%) when we have overwhelming numbers elsewhere
   - Use higher threshold (80%+) when we're behind in total forces

## How to Test

```bash
# Run all unit tests
python3 tests/test_ai.py

# Run filter-specific test
python3 tests/test_filter.py

# Test on map8.xml (requires server)
cd server/twilight-master && go run . -map maps/map8.xml &
python3 ai/ai_player.py localhost 5555  # Player 1
python3 ai/ai_player.py localhost 5555  # Player 2 (in another terminal)
```
