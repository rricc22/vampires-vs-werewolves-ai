"""
Evaluation function for game states.

REFACTORED VERSION (2024):
Simplified from complex branching logic to linear weighted scoring for easier tuning.

Scoring Components:
1. Material: Simple unit count difference
2. Fragmentation: Linear penalty for excess groups + small group penalties
3. Resources: Count accessible winnable humans within range
4. Tactical: Strength advantages, center control, strategic positioning

Old → New Mapping:
- Material: (our_count - opp_count) * 100 → Same, but configurable weight
- Groups: if/elif chains (1→+100, 2→0, 3→-200, 4+→-500) → Linear penalty per excess group
- Human proximity: Nested loops with complex distance logic → Count accessible targets
- Threat/center/split: Multiple components → Consolidated tactical scoring
"""
from game_state import GameState, Species
import config
import random


def evaluate_state(state: GameState) -> float:
    """
    Evaluate a game state from our perspective.

    Positive values favor us, negative values favor opponent.

    Args:
        state: Game state to evaluate

    Returns:
        Evaluation score (higher is better for us)
    """
    if state.our_species is None or state.opponent_species is None:
        return 0.0

    our_count = state.get_total_count(state.our_species)
    opponent_count = state.get_total_count(state.opponent_species)

    # Terminal states
    if our_count == 0:
        return -10000.0
    if opponent_count == 0:
        return 10000.0

    # Get group information once
    our_groups = state.get_our_groups()
    opponent_groups = state.get_opponent_groups()

    # Calculate all 4 components
    material_score = _evaluate_material(our_count, opponent_count)
    fragmentation_score = _evaluate_fragmentation(our_groups, opponent_groups)
    resource_score = _evaluate_resources(state, our_groups, opponent_groups)
    tactical_score = _evaluate_tactical(state, our_groups, opponent_groups)
    
    total_score = material_score + fragmentation_score + resource_score + tactical_score
    
    # Add small random noise to break ties and prevent infinite loops
    # This helps avoid position repetition in symmetric situations
    if config.EVAL_RANDOM_NOISE > 0:
        noise = random.uniform(-config.EVAL_RANDOM_NOISE, config.EVAL_RANDOM_NOISE)
        total_score += noise
    
    return total_score


# ============================================================
# COMPONENT 1: MATERIAL
# ============================================================

def _evaluate_material(our_count: int, opponent_count: int) -> float:
    """
    Material advantage - simple unit count difference.
    Most important factor in evaluation.
    """
    return (our_count - opponent_count) * config.EVAL_MATERIAL_WEIGHT


# ============================================================
# COMPONENT 2: FRAGMENTATION
# ============================================================

def _evaluate_fragmentation(our_groups: list, opponent_groups: list) -> float:
    """
    Penalize having too many groups (fragmentation).
    Linear penalty for groups beyond ideal count.

    Old system: Complex if/elif (1→+100, 2→0, 3→-200, 4+→-500 each)
    New system: Linear penalty per excess group + concentration bonus
    """
    score = 0.0

    # Our fragmentation
    num_our_groups = len(our_groups)

    # Reward concentration (1-2 groups ideal)
    if num_our_groups <= config.EVAL_IDEAL_GROUP_COUNT:
        score += config.EVAL_CONCENTRATION_BONUS
    else:
        # Linear penalty for excess groups
        excess_groups = num_our_groups - config.EVAL_IDEAL_GROUP_COUNT
        score -= excess_groups * config.EVAL_FRAGMENTATION_PENALTY

    # Penalize small groups (< threshold)
    small_group_count = sum(1 for _, _, count in our_groups
                           if count < config.EVAL_SMALL_GROUP_THRESHOLD)
    score -= small_group_count * config.EVAL_SMALL_GROUP_PENALTY

    # Opponent fragmentation (mirror logic)
    num_opp_groups = len(opponent_groups)

    if num_opp_groups <= config.EVAL_IDEAL_GROUP_COUNT:
        score -= config.EVAL_CONCENTRATION_BONUS
    else:
        excess_groups = num_opp_groups - config.EVAL_IDEAL_GROUP_COUNT
        score += excess_groups * config.EVAL_FRAGMENTATION_PENALTY

    small_opp_count = sum(1 for _, _, count in opponent_groups
                         if count < config.EVAL_SMALL_GROUP_THRESHOLD)
    score += small_opp_count * config.EVAL_SMALL_GROUP_PENALTY

    return score


# ============================================================
# COMPONENT 3: RESOURCES
# ============================================================

def _evaluate_resources(state: GameState, our_groups: list, opponent_groups: list) -> float:
    """
    Evaluate access to human resources.
    Counts accessible winnable humans within range (no nested loops).

    Old system: Nested loops (groups × humans) with complex distance/probability logic
    New system: For each human, check if accessible by ANY of our groups
    """
    from move_generator import calculate_battle_probability

    score = 0.0

    # Collect all human positions
    human_cells = []
    for i in range(state.rows):
        for j in range(state.cols):
            if state.board[i][j].humans > 0:
                human_cells.append((i, j, state.board[i][j].humans))

    if not human_cells:
        return 0.0

    # For each human group, check if we (or opponent) can win it
    for hx, hy, h_count in human_cells:
        # Check our access
        our_best_group = None
        our_best_dist = float('inf')
        our_can_win = False

        for gx, gy, g_count in our_groups:
            dist = manhattan_distance(gx, gy, hx, hy)
            win_prob = calculate_battle_probability(g_count, h_count)

            if dist <= config.EVAL_RESOURCE_MAX_DISTANCE and win_prob >= config.EVAL_RESOURCE_MIN_WIN_PROB:
                our_can_win = True
                if dist < our_best_dist:
                    our_best_dist = dist
                    our_best_group = (gx, gy, g_count)

        # Check opponent access
        opp_can_win = False
        opp_best_dist = float('inf')

        for gx, gy, g_count in opponent_groups:
            dist = manhattan_distance(gx, gy, hx, hy)
            win_prob = calculate_battle_probability(g_count, h_count)

            if dist <= config.EVAL_RESOURCE_MAX_DISTANCE and win_prob >= config.EVAL_RESOURCE_MIN_WIN_PROB:
                opp_can_win = True
                if dist < opp_best_dist:
                    opp_best_dist = dist

        # Score based on accessibility
        if our_can_win and not opp_can_win:
            # We can get it, they can't - full value
            score += config.EVAL_RESOURCE_VALUE
        elif our_can_win and opp_can_win:
            # Contested - partial value, favor closer group
            if our_best_dist < opp_best_dist:
                score += config.EVAL_RESOURCE_VALUE * 0.5
            elif our_best_dist > opp_best_dist:
                score -= config.EVAL_RESOURCE_VALUE * 0.5
        elif opp_can_win and not our_can_win:
            # They can get it, we can't
            score -= config.EVAL_RESOURCE_VALUE

    return score


# ============================================================
# COMPONENT 4: TACTICAL
# ============================================================

def _evaluate_tactical(state: GameState, our_groups: list, opponent_groups: list) -> float:
    """
    Tactical positioning and advantages.
    Combines: favorable matchups, center control, strategic positioning.

    Old system: Separate logic for center, threats, split penalties
    New system: Consolidated tactical scoring
    """
    score = 0.0

    # 1. Combat advantages - count favorable matchups
    favorable_matchups = 0
    unfavorable_matchups = 0
    closest_enemy_dist = float('inf')

    for our_x, our_y, our_cnt in our_groups:
        for opp_x, opp_y, opp_cnt in opponent_groups:
            dist = manhattan_distance(our_x, our_y, opp_x, opp_y)
            closest_enemy_dist = min(closest_enemy_dist, dist)

            if dist <= config.EVAL_TACTICAL_THREAT_RANGE:
                # Check strength ratio
                if our_cnt >= opp_cnt * config.EVAL_TACTICAL_ADVANTAGE_RATIO:
                    favorable_matchups += 1
                elif opp_cnt >= our_cnt * config.EVAL_TACTICAL_ADVANTAGE_RATIO:
                    unfavorable_matchups += 1

    score += (favorable_matchups - unfavorable_matchups) * config.EVAL_TACTICAL_MATCHUP_VALUE

    # 2. Center control
    center_x, center_y = state.rows // 2, state.cols // 2
    our_center_control = 0.0
    opp_center_control = 0.0

    for x, y, count in our_groups:
        dist_to_center = manhattan_distance(x, y, center_x, center_y)
        our_center_control += count / (1 + dist_to_center)

    for x, y, count in opponent_groups:
        dist_to_center = manhattan_distance(x, y, center_x, center_y)
        opp_center_control += count / (1 + dist_to_center)

    score += (our_center_control - opp_center_control) * config.EVAL_CENTER_CONTROL_WEIGHT

    # 3. Penalize fragmentation when enemy is close
    if closest_enemy_dist <= config.EVAL_TACTICAL_CLOSE_RANGE:
        num_groups = len(our_groups)
        if num_groups > config.EVAL_IDEAL_GROUP_COUNT:
            excess = num_groups - config.EVAL_IDEAL_GROUP_COUNT
            score -= excess * config.EVAL_SPLIT_NEAR_ENEMY_PENALTY

    return score


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def manhattan_distance(x1: int, y1: int, x2: int, y2: int) -> int:
    """Calculate Manhattan distance between two points."""
    return abs(x2 - x1) + abs(y2 - y1)


def chebyshev_distance(x1: int, y1: int, x2: int, y2: int) -> int:
    """Calculate Chebyshev distance (king's move distance) between two points."""
    return max(abs(x2 - x1), abs(y2 - y1))
