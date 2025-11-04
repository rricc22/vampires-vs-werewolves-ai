# 🎨 Visual Guide - AI in Pictures

A super simple, visual guide to understanding the AI.

---

## 🎮 What Does the AI Do?

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   The AI is like a CHESS PLAYER thinking ahead              │
│                                                             │
│   1. 👀 Look at the board                                   │
│   2. 🤔 Think "What can I do?"                              │
│   3. 🔮 Imagine "What will happen if..."                    │
│   4. 📊 Score "How good is that?"                           │
│   5. ✅ Pick the best move                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 The 7 Files (What Each Does)

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  config.py                                                   │
│  ──────────                                                  │
│  "Where is the server?"                                      │
│  Just stores: IP address and port                           │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  game_state.py                                               │
│  ──────────────                                              │
│  "What does the board look like?"                            │
│  • Cell: One square on the board                            │
│  • Move: Moving creatures from A to B                        │
│  • GameState: The entire board + who we are                  │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  move_generator.py                                           │
│  ──────────────────                                          │
│  "What moves can I make?"                                    │
│  • Looks in 8 directions ↑↗→↘↓↙←↖                          │
│  • Calculates battle odds                                    │
│  • Filters out risky moves (< 70% win chance)                │
│  • Simulates what happens if we move                         │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  evaluation.py                                               │
│  ──────────────                                              │
│  "Is this position good or bad?"                             │
│  Gives points for:                                           │
│    ✓ More creatures than enemy (+100 per unit)              │
│    ✓ Good positioning (+10 to +40)                           │
│    ✓ Being near easy targets (+20)                           │
│    ✗ Being near threats (-50)                                │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  alphabeta.py                                                │
│  ─────────────                                               │
│  "What's the best move?"                                     │
│  THE BRAIN! Thinks ahead 3-4 moves                           │
│  • Tries every possible move                                 │
│  • Predicts opponent's response                              │
│  • Uses smart pruning to skip bad options                    │
│  • Keeps searching until time runs out (1.8s)                │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  client.py                                                   │
│  ──────────                                                  │
│  "Talk to the server"                                        │
│  • Connects via internet (socket)                            │
│  • Receives messages (SET, MAP, UPD)                         │
│  • Sends our moves (MOV)                                     │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ai_player.py                                                │
│  ─────────────                                               │
│  "THE BOSS - Coordinates everything"                         │
│  Main program that:                                          │
│    1. Starts the connection                                  │
│    2. Gets board updates                                     │
│    3. Calls the brain (alphabeta)                            │
│    4. Sends the decision                                     │
│    5. Repeats until game ends                                │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 🔄 How One Turn Works

```
┌─────────────────────────────────────────────────────────────┐
│                        ONE TURN                             │
└─────────────────────────────────────────────────────────────┘

📥 RECEIVE UPDATE
   ↓
   Server says: "Here's the board now"
   Function: get_message() in client.py
   
   ↓
   
🧠 UPDATE BRAIN
   ↓
   Update our mental model
   Function: update_from_upd() in game_state.py
   
   ↓
   
💭 THINK "WHAT CAN I DO?"
   ↓
   Generate ~20 possible moves
   Function: generate_all_moves() in move_generator.py
   
   Example moves:
     • Move 3 units from (4,5) to (4,4)
     • Move 2 units from (4,5) to (3,5)
     • Move 1 unit from (4,5) to (3,4)
     ... and 17 more
   
   ↓
   
🔮 IMAGINE FUTURES
   ↓
   For EACH of the 20 moves, imagine the result
   Function: apply_move_to_state() in move_generator.py
   
   Move 1: "If I move here, I'll have 4 vampires there"
   Move 2: "If I move there, I'll be near the enemy"
   Move 3: "If I attack, I'll convert the human"
   
   ↓
   
📊 SCORE EACH FUTURE
   ↓
   Give points to each imaginary future
   Function: evaluate_state() in evaluation.py
   
   Move 1: +160 points ⭐
   Move 2: +45 points
   Move 3: +120 points
   
   ↓
   
🎯 THINK AHEAD (The Magic!)
   ↓
   "But what will the OPPONENT do?"
   Function: alpha_beta() in alphabeta.py
   
   For Move 1 (+160):
     ├─ If opponent does A → Score becomes +50
     ├─ If opponent does B → Score becomes +20 ← They pick this
     └─ If opponent does C → Score becomes +80
   
   So Move 1's REAL score is +20 (after opponent responds)
   
   Do this for ALL 20 moves!
   
   ↓
   
✅ PICK BEST
   ↓
   After thinking ahead, pick highest score
   Function: alpha_beta_root() in alphabeta.py
   
   Winner: Move 1 with score +20
   
   ↓
   
📤 SEND DECISION
   ↓
   Tell the server "I want to move here"
   Function: send_mov() in client.py
   
   Sends: MOV [1] [5,4,3,4,4]
   
   ↓
   
⏰ WAIT FOR NEXT TURN
```

---

## 🌳 The Thinking Tree

```
                    NOW (My Turn)
                  "I have 3 vampires"
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    Move to A        Move to B       Move to C
   "Attack human"  "Move to empty"  "Move to center"
         │               │               │
         │               │               │
    ┌────┴────┐     ┌────┴────┐     ┌────┴────┐
    │         │     │         │     │         │
   Opp       Opp   Opp       Opp   Opp       Opp
  Move 1    Move 2 Move 1   Move 2 Move 1   Move 2
    │         │     │         │     │         │
 +100      +50   +30       +90   +120      +80

The AI explores ALL these branches!
Then picks the path with the best outcome.

Alpha-Beta Pruning = Smart shortcut
  "Oh, this branch can't be better than what
   I already found, so skip it!"
  
Result: Think TWICE as deep in same time! 🚀
```

---

## 🎲 Battle System

### The 70% Rule

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  Should I attack this human group?                      │
│                                                         │
│  Step 1: Calculate win probability                      │
│  ────────────────────────────────                       │
│                                                         │
│  Example: 3 vampires vs 1 human                         │
│  Formula: 0.5 + (3-1)/(2×1) = 1.5 → 100% win           │
│                                                         │
│  Step 2: Check the 70% filter                           │
│  ────────────────────────────                           │
│                                                         │
│  Is 100% ≥ 70%?  ✅ YES!                                │
│  → SAFE TO ATTACK!                                      │
│                                                         │
│  ───────────────────────────────────────                │
│                                                         │
│  Example: 5 vampires vs 5 humans                        │
│  Formula: 0.5 (equal forces)                            │
│                                                         │
│  Is 50% ≥ 70%?  ❌ NO!                                  │
│  → TOO RISKY! Skip this move                            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Battle Outcomes

```
┌──────────────────────────────────────────────┐
│  GUARANTEED WIN (≥ 1.5x advantage)          │
│  ────────────────────────────────           │
│                                             │
│  10 vampires vs 6 werewolves                │
│  Ratio: 10/6 = 1.67 ≥ 1.5                  │
│  Result: All werewolves die                 │
│          All 10 vampires survive            │
│                                             │
├──────────────────────────────────────────────┤
│  GUARANTEED CONVERSION (≥ 1.0x)             │
│  ────────────────────────────────           │
│                                             │
│  8 vampires vs 8 humans                     │
│  Ratio: 8/8 = 1.0                           │
│  Result: All humans convert                 │
│          We get 16 vampires total!          │
│                                             │
├──────────────────────────────────────────────┤
│  RANDOM BATTLE (< 1.5x)                     │
│  ────────────────────────────────           │
│                                             │
│  7 vampires vs 5 werewolves                 │
│  Ratio: 7/5 = 1.4 < 1.5                    │
│  Win chance: 0.5 + (7-5)/(2×5) = 70%       │
│                                             │
│  🎲 Roll dice!                              │
│  70% chance: ~5 vampires survive            │
│  30% chance: ~3 werewolves survive          │
│                                             │
└──────────────────────────────────────────────┘
```

---

## 📊 Scoring System

```
┌──────────────────────────────────────────────────────────┐
│             HOW WE SCORE A POSITION                      │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Imagine this board state:                               │
│    • We have: 12 vampires                                │
│    • Enemy has: 10 werewolves                            │
│    • Humans: 3 remaining                                 │
│                                                          │
│  ┌────────────────────────────────────────────┐         │
│  │ 1. MATERIAL COUNT                          │         │
│  │    (12 - 10) × 100 = +200 points          │         │
│  │    "We're winning in numbers!"             │         │
│  └────────────────────────────────────────────┘         │
│                                                          │
│  ┌────────────────────────────────────────────┐         │
│  │ 2. GROUP SPREAD                            │         │
│  │    We have 2 groups: +20 points            │         │
│  │    They have 1 group: -10 points           │         │
│  │    "Spreading out is safer"                │         │
│  └────────────────────────────────────────────┘         │
│                                                          │
│  ┌────────────────────────────────────────────┐         │
│  │ 3. HUMAN TARGETS                           │         │
│  │    Close to 2 humans (80% win): +40        │         │
│  │    "Easy pickings nearby!"                 │         │
│  └────────────────────────────────────────────┘         │
│                                                          │
│  ┌────────────────────────────────────────────┐         │
│  │ 4. CENTER CONTROL                          │         │
│  │    We control center: +15 points           │         │
│  │    "High ground advantage"                 │         │
│  └────────────────────────────────────────────┘         │
│                                                          │
│  ┌────────────────────────────────────────────┐         │
│  │ 5. THREATS                                 │         │
│  │    We can kill their group: +20            │         │
│  │    They can't kill ours: +0                │         │
│  │    "We have the advantage"                 │         │
│  └────────────────────────────────────────────┘         │
│                                                          │
│  ═══════════════════════════════════════════            │
│  TOTAL SCORE: +285 points                               │
│  ═══════════════════════════════════════════            │
│                                                          │
│  Higher score = Better position for us! ✅              │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## ⏱️ Time Management

```
┌──────────────────────────────────────────────────────────┐
│         ITERATIVE DEEPENING (Getting Smarter)            │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Time Budget: 1.8 seconds                                │
│  Goal: Think as deep as possible                         │
│                                                          │
│  0.0s  ├─ START                                          │
│        │                                                 │
│        ├─ Depth 1 (Quick scan)                           │
│  0.1s  │  Look at immediate moves                        │
│        │  Best found: Move A (+50)                       │
│        │  ✅ "At least I have SOMETHING"                 │
│        │                                                 │
│        ├─ Depth 2 (Think ahead 1 move)                   │
│  0.4s  │  Consider opponent responses                    │
│        │  Best found: Move B (+70)                       │
│        │  ✅ "This is better!"                           │
│        │                                                 │
│        ├─ Depth 3 (Think ahead 2 moves)                  │
│  0.9s  │  Our move → Their move → Our response          │
│        │  Best found: Move B (+65)                       │
│        │  ✅ "Still Move B"                              │
│        │                                                 │
│        ├─ Depth 4 (Think ahead 3 moves)                  │
│  1.5s  │  Even deeper analysis...                        │
│        │  Best found: Move C (+80)                       │
│        │  ✅ "Aha! Found something better!"             │
│        │                                                 │
│  1.8s  ├─ TIME'S UP! ⏰                                  │
│        │                                                 │
│        └─ Return: Move C                                 │
│           (Last completed depth)                         │
│                                                          │
│  ───────────────────────────────────────────             │
│                                                          │
│  Why this is smart:                                      │
│    ✓ Always have a valid answer                         │
│    ✓ Get better answers with more time                  │
│    ✓ Never run out of time!                             │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## 🔁 The Complete Game Loop

```
START PROGRAM
     │
     ├─ Connect to server (client.py)
     │  "Hello! I'm AlphaBetaAI_v1"
     │
     ├─ Receive setup messages
     │  SET: "Board is 5×6"
     │  HUM: "Humans are at (2,2) and (4,4)"
     │  HME: "You start at (5,4)"
     │  MAP: "Here's the full board"
     │
     ├─ Determine species
     │  "I'm Vampires! 🧛"
     │
     └─────────────────────────────────────┐
                                          │
     ┌────────────────────────────────────┘
     │
     ▼
╔════════════════════════════════════════════╗
║           MAIN GAME LOOP                   ║
║         (Repeats Every Turn)               ║
╚════════════════════════════════════════════╝
     │
     ├─ 📥 Receive UPD
     │  "Board changed! Here's what's new"
     │
     ├─ 🔄 Update game state
     │  Update our mental model
     │
     ├─ 🧠 THINK (The Brain Work!)
     │  │
     │  ├─ Generate moves (~20 options)
     │  ├─ Simulate each move
     │  ├─ Score each outcome
     │  ├─ Think ahead (3-4 levels)
     │  └─ Pick the best
     │
     ├─ 📤 Send move to server
     │  "MOV: I choose Move C!"
     │
     ├─ ⏰ Wait for next turn...
     │
     └─────────────────────────┐
                              │
     ┌────────────────────────┘
     │
     ▼
   Is game over?
     │
     ├─ NO  → Loop back to UPD
     │
     └─ YES → GAME OVER!
              Show results
              Exit program
```

---

## 🎯 Quick Function Lookup

Need to find a function? Here's what it does:

```
┌──────────────────────────────────────────────────────────┐
│  "I want to..."                    "Use this function:"  │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Know what moves I can make        generate_all_moves()  │
│  Try a move in my head             apply_move_to_state() │
│  Score a position                  evaluate_state()      │
│  Think ahead multiple moves        alpha_beta()          │
│  Check if I can win a battle       calculate_battle_*()  │
│  Find my groups on the board       get_our_groups()      │
│  Find enemy groups                 get_opponent_groups() │
│  Copy the board                    clone()               │
│  Count total creatures             get_total_count()     │
│  Check if game is over             is_terminal()         │
│  Talk to the server                send_mov()            │
│  Receive from server               get_message()         │
│  Calculate distance                manhattan_distance()  │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## 🎓 Key Concepts

### Alpha-Beta Pruning

```
Without pruning:           With pruning:
  Explore 1000 positions    Explore 500 positions
  Time: 2.0 seconds         Time: 1.0 seconds
  Depth: 3 moves            Depth: 4 moves ✨

How?
  "This path can't be better than what I found,
   so skip it!"
```

### The 70% Safety Filter

```
❌ BEFORE (Old AI):
  "5 vs 5? Let's attack!" (50% chance)
  → Lost half the time

✅ AFTER (Fixed Nov 2024):
  "5 vs 5? Too risky, need 70%+"
  → Only attacks when confident
  → Preserves forces for better opportunities
```

### Evaluation Heuristics

```
Think of it like a video game score:

  +100  for each unit advantage
  +40   for good positioning
  +20   for threatening enemy
  -50   for being threatened
  
The AI tries to maximize this score!
```

---

## 📈 Performance Stats

```
┌──────────────────────────────────────┐
│  Typical Turn Statistics:           │
├──────────────────────────────────────┤
│                                      │
│  Time per move:     1.2 - 1.8s      │
│  Positions checked: 500 - 5,000     │
│  Search depth:      3 - 5 moves     │
│  Moves generated:   20 - 100        │
│  Win rate:          ~60% vs random  │
│                                      │
└──────────────────────────────────────┘
```

---

## 🎨 Map Visualization

```
Small Map (5×6):              Large Map (10×10):
Fast games, simple tactics    Strategic depth

    0 1 2 3 4 5                 0 1 2 3 4 5 6 7 8 9
  ┌─┬─┬─┬─┬─┬─┐               ┌─┬─┬─┬─┬─┬─┬─┬─┬─┬─┐
0 │ │ │ │ │ │ │             0 │ │ │ │ │ │ │ │ │ │ │
  ├─┼─┼─┼─┼─┼─┤               ├─┼─┼─┼─┼─┼─┼─┼─┼─┼─┤
1 │ │ │ │ │ │ │             1 │ │H│ │ │ │ │ │ │W│ │
  ├─┼─┼─┼─┼─┼─┤               ├─┼─┼─┼─┼─┼─┼─┼─┼─┼─┤
2 │ │ │H│ │ │ │             2 │ │ │V│ │ │ │ │ │ │ │
  ├─┼─┼─┼─┼─┼─┤               ├─┼─┼─┼─┼─┼─┼─┼─┼─┼─┤
3 │ │ │W│ │ │ │             3 │ │ │ │H│ │ │H│ │ │ │
  ├─┼─┼─┼─┼─┼─┤               └─┴─┴─┴─┴─┴─┴─┴─┴─┴─┘
4 │ │ │ │ │H│V│              More room to maneuver!
  └─┴─┴─┴─┴─┴─┘               
Quick showdown!
```

---

## 🚀 Next Steps

Want to learn more?

1. **Read code**: Start with `ai_player.py` (main entry)
2. **Run tests**: `python3 tests/test_ai.py`
3. **Watch a game**: `bash play_game.sh`
4. **Modify**: Try changing the 70% threshold!
5. **Deep dive**: Read `COMPLETE_WALKTHROUGH.md`

---

**Remember**: The AI is just asking itself 4 questions:
1. What CAN I do?
2. What WILL happen?
3. How GOOD is that?
4. Which is BEST?

Everything else is just doing this really fast! ⚡
