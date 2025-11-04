# Contributing to Vampires vs Werewolves AI

Thank you for considering contributing! This project is designed for collaborative AI improvement and analysis.

## 🎯 Areas for Contribution

### 1. Strategic Improvements
- Opening book for common map positions
- Endgame tables for few-unit scenarios
- Dynamic risk threshold based on game state
- Multi-move tactical planning
- Territory control evaluation

### 2. Search Enhancements
- Transposition tables (caching previously evaluated positions)
- Quiescence search (tactical stability)
- Null move pruning (faster pruning)
- Parallel search (multi-threading)
- Better move ordering (history heuristic, killer moves)

### 3. Evaluation Refinement
- Mobility scoring (number of available moves)
- Group cohesion (keeping units together)
- Human conversion timing (when to attack vs wait)
- Tempo evaluation (initiative and momentum)
- Threat detection (identifying dangerous opponent positions)

### 4. Code Quality
- Add edge case tests
- Benchmark different configurations
- Performance profiling
- Game analytics and logging
- Documentation improvements

## 🚀 Getting Started

1. **Fork the repository**
2. **Clone your fork:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/vampires-vs-werewolves-ai.git
   cd vampires-vs-werewolves-ai
   ```

3. **Create a branch:**
   ```bash
   git checkout -b feature/your-improvement
   ```

4. **Make your changes**

5. **Test thoroughly:**
   ```bash
   python3 tests/test_ai.py
   python3 tests/test_filter.py
   ```

6. **Commit and push:**
   ```bash
   git commit -m "Add feature: description"
   git push origin feature/your-improvement
   ```

7. **Open a Pull Request**

## 📋 Contribution Guidelines

### Code Style
- Follow PEP 8
- Use type hints on all functions
- Max line length: 88-100 characters
- Add docstrings to public functions

### Testing
- All existing tests must pass
- Add tests for new features
- Document test results in PR

### Documentation
- Update README.md if adding features
- Add inline comments for complex logic
- Update docs/ if changing architecture

### Performance
- AI must respond within 2 seconds
- Benchmark changes against baseline
- Document performance impact

## 🧪 Testing Your Changes

### Unit Tests
```bash
python3 tests/test_ai.py
```

### Integration Test (Full Game)
```bash
# Terminal 1: Start server
cd server/twilight-master
go run . -map maps/map8.xml

# Terminal 2: Your AI
python3 ai/ai_player.py localhost 5555

# Terminal 3: Baseline AI (for comparison)
git stash  # stash your changes
python3 ai/ai_player.py localhost 5555
```

### Performance Benchmark
```bash
python3 -m cProfile -s cumtime ai/ai_player.py localhost 5555 > profile.txt
```

## 💡 Good First Issues

Looking to get started? Try these:

1. **Add more test maps** - Create interesting map configurations
2. **Improve logging** - Add detailed move explanation output
3. **Add statistics tracking** - Win rate, average depth, node count
4. **Documentation** - Add code comments, improve guides
5. **Mobility evaluation** - Add move count to evaluation function

## 🐛 Bug Reports

When reporting bugs, include:
- Description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Map file (if relevant)
- Game logs
- Python version

## 💬 Discussion

For major changes:
1. Open an issue first to discuss
2. Explain the problem and proposed solution
3. Get feedback before implementing
4. Reference the issue in your PR

## 📊 Performance Benchmarks

When proposing search/evaluation changes, include:
- Search depth achieved
- Nodes explored per second
- Time per move
- Win rate vs baseline (if possible)

## ✅ Pull Request Checklist

- [ ] Code follows PEP 8 style
- [ ] All tests pass
- [ ] New tests added (if applicable)
- [ ] Documentation updated
- [ ] Performance benchmarked
- [ ] Commit messages are clear
- [ ] Branch is up to date with main

## 📝 Commit Message Format

Use clear, descriptive messages:

```
Add feature: transposition table caching

- Implement zobrist hashing for positions
- Cache evaluation results in hashtable
- Improves search speed by 40%
- All tests passing
```

## 🤝 Code Review Process

1. Automated checks run on PR
2. Maintainers review code
3. Discussion and iteration
4. Approval and merge

## 📜 License

By contributing, you agree that your contributions will be licensed under the same license as the project.

## ❓ Questions?

Open an issue with the `question` label or start a discussion.

---

**Happy coding!** 🎮🤖
