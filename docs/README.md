# 📚 Documentation Index

Welcome to the Vampires vs Werewolves AI documentation!

---

## 🎯 Choose Your Learning Path

### 🚀 Just Want to Get Started?
→ **[QUICKSTART.md](../QUICKSTART.md)** - Run your first game in 2 minutes

### 🎨 Visual Learner?
→ **[VISUAL_GUIDE.md](VISUAL_GUIDE.md)** - Pictures, diagrams, and simple explanations

### 📖 Want the Full Story?
→ **[COMPLETE_WALKTHROUGH.md](COMPLETE_WALKTHROUGH.md)** - Complete guide with examples and function references

### 🔧 Developer?
→ **[AGENTS.md](../AGENTS.md)** - Build commands and coding guidelines

### 🧠 Deep Technical Details?
→ **[AI_DOCUMENTATION.md](AI_DOCUMENTATION.md)** - Original technical documentation

---

## 📊 Documentation Overview

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Quick Start       →  QUICKSTART.md                         │
│  (5 min read)         "How do I run this?"                  │
│                                                             │
│  Visual Guide      →  VISUAL_GUIDE.md                       │
│  (10 min read)        "Show me pictures!"                   │
│                                                             │
│  Complete Guide    →  COMPLETE_WALKTHROUGH.md               │
│  (30 min read)        "Explain everything in detail"        │
│                                                             │
│  Developer Guide   →  AGENTS.md                             │
│  (Reference)          "Commands and code style"             │
│                                                             │
│  Technical Docs    →  AI_DOCUMENTATION.md                   │
│  (Reference)          "Original implementation notes"       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎓 Learning Progression

### Level 1: Beginner (First Hour)

1. Read **QUICKSTART.md** (5 min)
2. Run a game: `bash play_game.sh` (2 min)
3. Watch at http://localhost:8080
4. Read **VISUAL_GUIDE.md** sections:
   - What Does the AI Do?
   - The 7 Files
   - How One Turn Works

**You'll understand**: What the AI does at a high level

---

### Level 2: Intermediate (Next 2 Hours)

1. Read full **VISUAL_GUIDE.md** (15 min)
2. Read **COMPLETE_WALKTHROUGH.md** sections:
   - Project Structure
   - Component Architecture
   - Game Example Walkthrough (30 min)
3. Run tests: `python3 tests/test_ai.py` (5 min)
4. Read the code files in this order:
   - `ai/game_state.py` (board representation)
   - `ai/move_generator.py` (move generation)
   - `ai/evaluation.py` (scoring)

**You'll understand**: How the pieces fit together

---

### Level 3: Advanced (Deep Dive)

1. Read full **COMPLETE_WALKTHROUGH.md** (30 min)
2. Study **Function Call Trace** section carefully
3. Read remaining code files:
   - `ai/alphabeta.py` (search algorithm)
   - `ai/client.py` (networking)
   - `ai/ai_player.py` (main orchestrator)
4. Read **AI_DOCUMENTATION.md** for implementation details
5. Read **AGENTS.md** for development workflow
6. Experiment: Try modifying the 70% threshold in `move_generator.py:192`

**You'll understand**: Every function call and decision

---

## 📁 File Structure Reference

```
vampires-vs-werewolves-ai/
│
├── docs/                           ← YOU ARE HERE
│   ├── README.md                   ← This file
│   ├── VISUAL_GUIDE.md            ← 🎨 Pictures & diagrams
│   ├── COMPLETE_WALKTHROUGH.md    ← 📖 Complete reference
│   ├── AI_DOCUMENTATION.md        ← 🔬 Technical details
│   ├── TESTING_SUMMARY.md         ← ✅ Test results
│   └── Projectv10.pdf             ← 📄 Original spec
│
├── ai/                             ← Source code
│   ├── ai_player.py               ← Main entry point
│   ├── alphabeta.py               ← Search algorithm
│   ├── evaluation.py              ← Position scoring
│   ├── move_generator.py          ← Move generation
│   ├── game_state.py              ← Board state
│   ├── client.py                  ← Network client
│   └── config.py                  ← Settings
│
├── tests/                          ← Unit tests
│   └── test_ai.py
│
├── QUICKSTART.md                   ← 🚀 Start here!
├── AGENTS.md                       ← 🔧 Developer guide
├── README.md                       ← Project overview
└── play_game.sh                    ← Run a game
```

---

## 🎯 Quick Reference

### Common Questions

**Q: How do I run a game?**  
A: `bash play_game.sh` - Watch at http://localhost:8080

**Q: How do I run tests?**  
A: `python3 tests/test_ai.py`

**Q: Which file is the "brain"?**  
A: `ai/alphabeta.py` - The search algorithm

**Q: Where is the 70% filter?**  
A: `ai/move_generator.py` line 192

**Q: How do I change the search depth?**  
A: `ai/ai_player.py` line 70, change `max_depth=4`

**Q: Where does it talk to the server?**  
A: `ai/client.py` - All network communication

---

## 🔍 Find What You Need

Looking for information about:

- **Getting started** → QUICKSTART.md
- **How it works (simple)** → VISUAL_GUIDE.md sections 1-4
- **Search algorithm** → COMPLETE_WALKTHROUGH.md "alphabeta.py" section
- **Battle mechanics** → VISUAL_GUIDE.md "Battle System"
- **Move generation** → COMPLETE_WALKTHROUGH.md "move_generator.py"
- **Scoring positions** → VISUAL_GUIDE.md "Scoring System"
- **Function calls** → COMPLETE_WALKTHROUGH.md "Function Call Trace"
- **Example game** → COMPLETE_WALKTHROUGH.md "Game Example Walkthrough"
- **Testing** → TESTING_SUMMARY.md
- **Commands** → AGENTS.md
- **Code style** → AGENTS.md "Code Style"

---

## 🎨 Visual Learning Resources

The **VISUAL_GUIDE.md** contains:

- 🎮 What the AI does (in pictures)
- 📁 File explanations (simple language)
- 🔄 Turn-by-turn flow (step-by-step)
- 🌳 Thinking tree visualization
- 🎲 Battle system diagrams
- 📊 Scoring examples
- ⏱️ Time management illustration
- 🔁 Game loop flowchart
- 🎯 Function lookup table

---

## 📖 Complete Documentation Resources

The **COMPLETE_WALKTHROUGH.md** contains:

- 📁 Project structure (detailed)
- 🔄 Component architecture
- 📚 Every function explained
- 🎮 Complete game example (4 turns)
- 🔍 Function call trace (execution path)
- 🎓 Simplified explanations
- 📊 Performance metrics

---

## 💡 Tips for Learning

1. **Start visual** - Read VISUAL_GUIDE.md first if you're new to AI
2. **Run before reading** - Play a game to see it in action
3. **Follow one turn** - Track a single turn through all the functions
4. **Modify and test** - Change the 70% threshold and see what happens
5. **Use the traces** - The function call trace shows exact execution order

---

## 🚀 Next Steps

After reading the docs, try:

1. **Run a game**: `bash play_game.sh`
2. **Read the code**: Start with `ai/ai_player.py`
3. **Run tests**: `python3 tests/test_ai.py`
4. **Modify something**: Change evaluation weights in `ai/evaluation.py`
5. **Test your change**: Run tests again and play a game
6. **Contribute**: Read AGENTS.md for contribution guidelines

---

## 📝 Documentation Status

| Document | Status | Last Updated | Size |
|----------|--------|--------------|------|
| VISUAL_GUIDE.md | ✅ Complete | Nov 4, 2025 | 594 lines |
| COMPLETE_WALKTHROUGH.md | ✅ Complete | Nov 4, 2025 | 1118 lines |
| QUICKSTART.md | ✅ Complete | Nov 4, 2025 | - |
| AGENTS.md | ✅ Complete | Nov 4, 2025 | - |
| AI_DOCUMENTATION.md | ✅ Complete | Nov 4, 2025 | - |

---

## 🎓 Additional Resources

- **Project Homepage**: See main README.md
- **Issue Tracking**: See .github/ISSUE_TEMPLATE/
- **Team Collaboration**: See TEAM_COLLABORATION.md
- **Test Results**: See TESTING_SUMMARY.md

---

**Happy Learning! 🎉**

Start with [VISUAL_GUIDE.md](VISUAL_GUIDE.md) if you want simple explanations with pictures!

Or jump to [COMPLETE_WALKTHROUGH.md](COMPLETE_WALKTHROUGH.md) for the full detailed guide!
