"""
Unified AI Configuration
========================

All tunable parameters for the Vampires vs Werewolves AI in one place.
Edit these values to customize the AI's behavior, or use configure.py for interactive setup.

Categories:
  - Server Connection
  - Search Algorithm  
  - Move Generation
  - Evaluation Weights
  - Play Style Presets
"""

# ============================================================
# SERVER CONNECTION
# ============================================================
SERVER_IP = "localhost"
SERVER_PORT = 5555


# ============================================================
# SEARCH ALGORITHM
# ============================================================
# How deep the AI looks ahead (higher = smarter but slower)
# Typical range: 3-5
# - 3: Fast, basic strategy
# - 4: Balanced (default)
# - 5: Deep, strong play (may timeout on complex positions)
SEARCH_MAX_DEPTH = 4

# Time limit per move in seconds (must be < 2.0 for server)
# Recommended: 1.5-1.8 to leave buffer for network/processing
SEARCH_TIME_LIMIT = 1.8

# Enable iterative deepening (searches depth 1, then 2, then 3, etc.)
# Ensures we always have a move even if we run out of time
SEARCH_ITERATIVE_DEEPENING = True


# ============================================================
# MOVE GENERATION - FRAGMENTATION CONTROL
# ============================================================
# Minimum group size - don't create groups smaller than this
# Higher = less fragmentation, but less tactical flexibility
# Recommended: 5-10
MIN_GROUP_SIZE = 5

# Maximum groups that can move simultaneously per turn
# 1 = simple moves only, 2 = tactical coordination (default), 3 = complex multi-group
MAX_GROUPS_PER_TURN = 2

# Minimum size before allowing a group to split
# Prevents small groups from fragmenting further
# Recommended: 10-15
MIN_SPLIT_SIZE = 10

# Split ratios to consider when moving from a cell
# [1.0] = always move everything (no splits, maximum concentration)
# [1.0, 0.5] = move all OR half (allows strategic 2-group splits)
# [1.0, 2/3, 0.5, 1/3] = more options (more fragmentation risk)
# Recommended: [1.0] for defensive, [1.0, 0.5] for balanced
SPLIT_RATIOS = [1.0, 0.5]


# ============================================================
# BATTLE MECHANICS
# ============================================================
# Minimum win probability to attack humans/enemies
# 0.5 = 50% chance (risky), 0.7 = 70% (default), 0.8 = 80% (conservative)
# Higher = fewer attacks, but more likely to win when we do attack
ATTACK_MIN_WIN_PROBABILITY = 0.7


# ============================================================
# EVALUATION WEIGHTS - MATERIAL & GROUPS
# ============================================================
# How much we value having more units than opponent
# Higher = prioritizes growing army size
WEIGHT_MATERIAL = 100

# Bonus for having exactly 1 group (concentrated force)
# Positive = encourages concentration
BONUS_ONE_GROUP = 100

# Penalty for having 2 groups
# 0 = acceptable, positive = penalize
PENALTY_TWO_GROUPS = 0

# Penalty for having 3 groups (fragmentation starting)
# Higher = strongly discourages splitting beyond 2 groups
PENALTY_THREE_GROUPS = 200

# Penalty PER group beyond 3 (catastrophic fragmentation)
# Higher = extremely discourages 4+ groups
PENALTY_EXCESS_GROUPS = 500

# Penalty per small group (below SMALL_GROUP_THRESHOLD)
# Higher = discourages keeping small weak groups
PENALTY_SMALL_GROUP = 100

# Threshold for what counts as a "small" group
# Groups with fewer units than this are penalized
SMALL_GROUP_THRESHOLD = 10


# ============================================================
# EVALUATION WEIGHTS - TACTICAL
# ============================================================
# How much we value being close to winnable human groups
# Higher = more aggressive human conversion
WEIGHT_HUMAN_PROXIMITY = 40

# How much we value controlling the center of the map
# Higher = more territorial/strategic play
WEIGHT_CENTER_CONTROL = 2

# How much we value favorable combat matchups
# Higher = more aggressive when we have advantage
WEIGHT_THREAT_ASSESSMENT = 20

# Penalty for splitting when enemy is nearby (distance <= 3)
# Higher = more likely to concentrate forces when threatened
PENALTY_SPLIT_NEAR_ENEMY = 20


# ============================================================
# GROUP STRATEGY THRESHOLDS
# ============================================================
# Ideal group count range (for evaluation logic)
IDEAL_MIN_GROUPS = 1
IDEAL_MAX_GROUPS = 2

# When we start applying excessive group penalties
EXCESSIVE_GROUPS_THRESHOLD = 3


# ============================================================
# PLAY STYLE PRESETS
# ============================================================
# Uncomment a preset below to quickly change play style
# Or use: python3 configure.py --preset <name>

# ------------------------------------------------------------
# AGGRESSIVE: Deep search, risky attacks, multi-group tactics
# ------------------------------------------------------------
# SEARCH_MAX_DEPTH = 5
# MAX_GROUPS_PER_TURN = 3
# ATTACK_MIN_WIN_PROBABILITY = 0.5
# SPLIT_RATIOS = [1.0, 2/3, 0.5]
# PENALTY_THREE_GROUPS = 100
# WEIGHT_HUMAN_PROXIMITY = 60

# ------------------------------------------------------------
# DEFENSIVE: Strong concentration, safe attacks only
# ------------------------------------------------------------
# SEARCH_MAX_DEPTH = 4
# MAX_GROUPS_PER_TURN = 2
# ATTACK_MIN_WIN_PROBABILITY = 0.8
# SPLIT_RATIOS = [1.0]
# PENALTY_THREE_GROUPS = 500
# BONUS_ONE_GROUP = 200

# ------------------------------------------------------------
# SPEED: Fast decisions, less computation
# ------------------------------------------------------------
# SEARCH_MAX_DEPTH = 3
# SEARCH_TIME_LIMIT = 1.0
# MAX_GROUPS_PER_TURN = 1
# SPLIT_RATIOS = [1.0]

# ------------------------------------------------------------
# EXPERIMENTAL: Testing new strategies
# ------------------------------------------------------------
# SEARCH_MAX_DEPTH = 4
# ATTACK_MIN_WIN_PROBABILITY = 0.6
# WEIGHT_CENTER_CONTROL = 10
# MAX_GROUPS_PER_TURN = 3


# ============================================================
# ADVANCED: DEBUG & LOGGING
# ============================================================
# Enable verbose logging for move generation
DEBUG_MOVE_GENERATION = False

# Enable search statistics printing
DEBUG_SEARCH_STATS = True

# Log evaluation details
DEBUG_EVALUATION = False
