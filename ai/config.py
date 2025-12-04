"""
Unified AI Configuration
========================

All tunable parameters for the Vampires vs Werewolves AI in one place.
Edit these values to customize the AI's behavior, or use modes.py for quick preset switching.

REFACTORED VERSION (2024):
Simplified evaluation parameters with clear grouping and linear weights.
See evaluation.py for implementation details.

Categories:
  - Server Connection
  - Search Algorithm
  - Move Generation
  - Evaluation: Material
  - Evaluation: Fragmentation
  - Evaluation: Resources
  - Evaluation: Tactical
  - Mode System
  - Debug & Logging
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
SEARCH_MAX_DEPTH = 10

# Time limit per move in seconds (must be < 2.0 for server)
# Recommended: 1.5-1.8 to leave buffer for network/processing
# Set to 1.6 for safety margin (network latency + GC pauses)
SEARCH_TIME_LIMIT = 2

# Enable iterative deepening (searches depth 1, then 2, then 3, etc.)
# Ensures we always have a move even if we run out of time
SEARCH_ITERATIVE_DEEPENING = True


# ============================================================
# MOVE GENERATION - FRAGMENTATION CONTROL
# ============================================================
# Minimum group size - don't create groups smaller than this
# Higher = less fragmentation, but less tactical flexibility
# Recommended: 5-10
MIN_GROUP_SIZE = 6

# Maximum groups that can move simultaneously per turn
# 1 = simple moves only, 2 = tactical coordination (default), 3 = complex multi-group
MAX_GROUPS_PER_TURN = 3

# Minimum size before allowing a group to split
# Prevents small groups from fragmenting further
# Recommended: 10-15
MIN_SPLIT_SIZE = 6

# Split ratios to consider when moving from a cell
# [1.0] = always move everything (no splits, maximum concentration)
# [1.0, 0.5] = move all OR half (allows strategic 2-group splits)
# [1.0, 2/3, 0.5, 1/3] = more options (more fragmentation risk)
# Recommended: [1.0] for defensive, [1.0, 0.5] for balanced
SPLIT_RATIOS = [1.0, 0.6666666666666666, 0.5]


# ============================================================
# BATTLE MECHANICS
# ============================================================
# Minimum win probability to attack humans/enemies
# 0.5 = 50% chance (aggressive), 0.7 = 70% (balanced), 0.8 = 80% (conservative)
# Higher = fewer attacks, but more likely to win when we do attack
# VERY AGGRESSIVE MODE: 0.4 allows 5v5 (50%) and even 4v5 (40%) attacks
ATTACK_MIN_WIN_PROBABILITY = 0.2


# ============================================================
# EVALUATION: MATERIAL
# ============================================================
# Weight per unit advantage
# Higher = prioritizes growing army size over positioning
# Old: WEIGHT_MATERIAL = 100
EVAL_MATERIAL_WEIGHT = 100


# ============================================================
# EVALUATION: FRAGMENTATION
# ============================================================
# Ideal number of groups to maintain (1-2 recommended)
# Groups <= this threshold receive concentration bonus
# Groups > this threshold receive linear penalties
EVAL_IDEAL_GROUP_COUNT = 2

# Bonus for maintaining concentrated forces (groups <= ideal)
# Old: BONUS_ONE_GROUP = 100
EVAL_CONCENTRATION_BONUS = 100

# Linear penalty per excess group beyond ideal count
# Example: 3 groups with IDEAL=2 → penalty = 1 * 250 = -250
# Old system: 3 groups = -200, 4 groups = -700 (non-linear)
# New: Linear progression, calibrated to match old behavior
EVAL_FRAGMENTATION_PENALTY = 250

# Threshold for "small" groups (penalized separately)
# Old: SMALL_GROUP_THRESHOLD = 10
EVAL_SMALL_GROUP_THRESHOLD = 10

# Penalty per small group
# Old: PENALTY_SMALL_GROUP = 100
EVAL_SMALL_GROUP_PENALTY = 100


# ============================================================
# EVALUATION: RESOURCES (Human Conversion)
# ============================================================
# Maximum distance to consider a human group "accessible"
# Old system: Used <= 2 for close, <= 4 for moderate distance
EVAL_RESOURCE_MAX_DISTANCE = 4

# Minimum win probability to consider a human group "winnable"
# Should match or be close to ATTACK_MIN_WIN_PROBABILITY
# Old system: Used 0.7 for "high confidence"
EVAL_RESOURCE_MIN_WIN_PROB = 0.7

# Value per accessible winnable human group
# Old: WEIGHT_HUMAN_PROXIMITY = 40 (complex distance weighting)
# New: Simple count × value (no distance decay within range)
EVAL_RESOURCE_VALUE = 40


# ============================================================
# EVALUATION: GAME PHASE DETECTION
# ============================================================
# Threshold for determining early game vs mid game
# Based on percentage of board cells with humans
# 0.15 = 15% of cells have humans → early game
# Lower = earlier transition to mid game focus
PHASE_EARLY_GAME_HUMAN_THRESHOLD = 0.15

# Random noise for tie-breaking (helps avoid repetition)
# Set to 0 to disable, or small value like 0.1-1.0
EVAL_RANDOM_NOISE = 0.5


# ============================================================
# EVALUATION: EARLY GAME BEHAVIOR
# ============================================================
# Weight for proximity to nearest humans in early game
# This creates a directional incentive to move TOWARD humans
# Formula: (human_count * weight) / (1 + distance)
# Higher = more aggressive human collection
# 50 = balanced (5-human village at dist 2 = ~83 points)
EVAL_HUMAN_PROXIMITY_WEIGHT = 50

# Whether to use center control in early game
# False = ignore center until mid game (recommended to prevent center rushing)
# True = use minimal center control even in early game
EVAL_EARLY_GAME_CENTER_CONTROL = False


# ============================================================
# EVALUATION: TACTICAL
# ============================================================
# Range to check for combat matchups (threat assessment)
# Old: <= 2 for "close proximity"
EVAL_TACTICAL_THREAT_RANGE = 2

# Strength ratio for "favorable" matchup (1.5 = 50% advantage)
# Old: >= 1.5x to "kill them"
EVAL_TACTICAL_ADVANTAGE_RATIO = 1.5

# Value per favorable (or unfavorable) matchup
# Old: WEIGHT_THREAT_ASSESSMENT = 20
EVAL_TACTICAL_MATCHUP_VALUE = 20

# Weight for center control scoring
# Old: WEIGHT_CENTER_CONTROL = 2
EVAL_CENTER_CONTROL_WEIGHT = 2

# Distance threshold for "enemy is close" (triggers concentration penalty)
# Old: <= 3 for "enemy nearby"
EVAL_TACTICAL_CLOSE_RANGE = 3

# Penalty per excess group when enemy is close
# Old: PENALTY_SPLIT_NEAR_ENEMY = 20
EVAL_SPLIT_NEAR_ENEMY_PENALTY = 20


# ============================================================
# BACKWARD COMPATIBILITY
# ============================================================
# Old parameter names (for reference, not used by new evaluation)
# Kept for any external scripts that might reference them

WEIGHT_MATERIAL = EVAL_MATERIAL_WEIGHT
BONUS_ONE_GROUP = EVAL_CONCENTRATION_BONUS
PENALTY_TWO_GROUPS = 0  # Old: neutral for 2 groups
PENALTY_THREE_GROUPS = EVAL_FRAGMENTATION_PENALTY  # Approximate
PENALTY_EXCESS_GROUPS = EVAL_FRAGMENTATION_PENALTY  # Approximate
PENALTY_SMALL_GROUP = EVAL_SMALL_GROUP_PENALTY
SMALL_GROUP_THRESHOLD = EVAL_SMALL_GROUP_THRESHOLD
WEIGHT_HUMAN_PROXIMITY = EVAL_RESOURCE_VALUE
WEIGHT_CENTER_CONTROL = EVAL_CENTER_CONTROL_WEIGHT
WEIGHT_THREAT_ASSESSMENT = EVAL_TACTICAL_MATCHUP_VALUE
PENALTY_SPLIT_NEAR_ENEMY = EVAL_SPLIT_NEAR_ENEMY_PENALTY

# Old thresholds (not used in new system)
IDEAL_MIN_GROUPS = 1
IDEAL_MAX_GROUPS = EVAL_IDEAL_GROUP_COUNT
EXCESSIVE_GROUPS_THRESHOLD = EVAL_IDEAL_GROUP_COUNT + 1


# ============================================================
# MODE SYSTEM
# ============================================================
# To change AI behavior, use play_game.sh which lets you select a mode,
# or manually run: python3 ai/modes.py <mode_name>
#
# Available modes: balanced, aggressive, defensive, speed, tactical, experimental
# Edit ai/modes.py to customize each mode's parameters


# ============================================================
# ADVANCED: DEBUG & LOGGING
# ============================================================
# Enable verbose logging for move generation
DEBUG_MOVE_GENERATION = False

# Enable search statistics printing
DEBUG_SEARCH_STATS = True

# Log evaluation details
DEBUG_EVALUATION = False
