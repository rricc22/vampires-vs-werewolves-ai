# Team Collaboration Guide

## 🎯 Project Overview

This AI uses **Alpha-Beta pruning** to play Vampires vs Werewolves. The recent fix prevents suicidal attacks by filtering moves with <70% win probability.

## 👥 Quick Setup for Team Members

### 1. Clone the Repository
```bash
git clone https://github.com/rricc22/vampires-vs-werewolves-ai.git
cd vampires-vs-werewolves-ai
```

### 2. Test Everything Works
```bash
# Run all tests
python3 tests/test_ai.py
python3 tests/test_filter.py

# Should see: "All tests passed! ✓"
```

### 3. Run a Game
```bash
# Terminal 1: Server (needs Go installed)
cd server/twilight-master
go run . -map maps/map8.xml

# Terminal 2: AI Player 1
python3 ai/ai_player.py localhost 5555

# Terminal 3: AI Player 2
python3 ai/ai_player.py localhost 5555

# Browser: http://localhost:8080
```

## 📁 Key Files to Understand

| File | Purpose | Lines |
|------|---------|-------|
| `ai/alphabeta.py` | Main search algorithm | ~150 |
| `ai/evaluation.py` | Position scoring | ~120 |
| `ai/move_generator.py` | Legal moves + filtering | ~280 |
| `ai/game_state.py` | Board representation | ~200 |

**Start here**: Read `ai/alphabeta.py` to understand the search flow.

## 🔧 Common Tasks

### Add a New Evaluation Feature
1. Edit `ai/evaluation.py`
2. Add your scoring function
3. Integrate into `evaluate_state()`
4. Test: `python3 tests/test_ai.py`

### Change Filter Threshold
1. Edit `ai/move_generator.py:186`
2. Change: `if win_prob < 0.7` to your value
3. Test: `python3 tests/test_filter.py`

### Add a New Test
1. Edit `tests/test_ai.py`
2. Add function: `def test_your_feature():`
3. Run: `python3 tests/test_ai.py`

## 🐛 Debugging Tips

### AI Not Moving
```bash
# Check server is running
lsof -i :5555

# Check AI logs
python3 ai/ai_player.py localhost 5555 2>&1 | tee debug.log
```

### AI Too Slow (>2 seconds)
```bash
# Profile the code
python3 -m cProfile -s cumtime ai/ai_player.py localhost 5555 > profile.txt
grep "alphabeta\|evaluate\|generate" profile.txt
```

### Illegal Move Error
- Check coordinate system: server uses (X,Y) = (col, row)
- Our code uses: board[row][col]
- See `ai/game_state.py:150` for conversion

## 📊 Understanding the AI

### Search Flow
```
ai_player.py (main loop)
    ↓
alphabeta.py (iterative deepening: depth 1, 2, 3...)
    ↓
move_generator.py (generate legal moves, filter risky ones)
    ↓
evaluation.py (score position)
    ↓
game_state.py (apply move, track board state)
```

### Current Strategy
1. **Early game**: Grab humans with >70% win probability
2. **Mid game**: Expand territory, avoid risky fights
3. **Late game**: Hunt opponent when you have advantage

### Key Parameters
- **Search depth**: 3-4 plies (~19k nodes)
- **Time limit**: 1.8s (0.2s safety margin)
- **Filter threshold**: 70% minimum win probability
- **Evaluation weights**: See `ai/evaluation.py`

## 🚀 Improvement Ideas

### Easy (Good for Starting)
- [ ] Add mobility score (count legal moves)
- [ ] Improve center control calculation
- [ ] Add more test maps
- [ ] Improve logging/debugging output

### Medium
- [ ] Opening book (pre-calculated first moves)
- [ ] Better move ordering (try best moves first)
- [ ] Endgame tables (few units remaining)
- [ ] Dynamic risk threshold (change 70% based on state)

### Hard
- [ ] Transposition tables (cache positions)
- [ ] Parallel search (multi-threading)
- [ ] Monte Carlo Tree Search (MCTS)
- [ ] Neural network evaluation

## 📖 Documentation

- **README.md**: Quick start and overview
- **CONTRIBUTING.md**: How to contribute
- **docs/AI_DOCUMENTATION.md**: Technical details
- **docs/TESTING_SUMMARY.md**: Recent fix verification
- **docs/QUICK_TEST_GUIDE.md**: Testing commands

## 💬 Communication

### Before Making Changes
1. Check existing issues
2. Open new issue to discuss
3. Get feedback
4. Create branch and implement

### Branch Naming
- `feature/your-feature-name`
- `fix/bug-description`
- `test/what-youre-testing`

### Commit Messages
```
Good: "Add mobility score to evaluation function"
Bad:  "Update code"

Good: "Fix: prevent negative unit counts in battle"
Bad:  "Fix bug"
```

## 🧪 Testing Checklist

Before pushing:
- [ ] `python3 tests/test_ai.py` passes
- [ ] `python3 tests/test_filter.py` passes
- [ ] Played at least 1 full game without crashes
- [ ] Documented what changed
- [ ] Updated relevant docs

## 📈 Performance Tracking

Current baseline (Nov 4, 2025):
- **Search depth**: 3-4 plies
- **Nodes/sec**: ~10,000-11,000
- **Time/move**: 1.8s average
- **Filter blocks**: 50%, 60%, 68%
- **Filter allows**: 76%, 100%

When improving, compare against baseline!

## ❓ FAQ

**Q: Why 70% threshold?**
A: Prevents coin-flip battles. 50% = equal risk, 70% = clear advantage.

**Q: Why not deeper search?**
A: Time limit is 2 seconds. Depth 4 sometimes exceeds this.

**Q: Can we use external libraries?**
A: Currently stdlib only. Discuss major dependencies first.

**Q: How do I add teammates?**
A: GitHub Settings → Collaborators → Add people

**Q: What if tests fail after my change?**
A: Debug, fix, or ask for help in issue/PR discussion.

## 🔗 Useful Links

- **Repository**: https://github.com/rricc22/vampires-vs-werewolves-ai
- **Game Rules**: `docs/Projectv10.pdf`
- **Protocol**: See `docs/AI_DOCUMENTATION.md`

---

**Let's improve this AI together!** 🤖🎮
