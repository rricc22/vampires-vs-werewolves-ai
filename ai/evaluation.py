"""Evaluation function for game states."""
from game_state import GameState, Species
import config
import math


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
    
    score = 0.0
    
    # 1. Material advantage (most important)
    score += (our_count - opponent_count) * config.WEIGHT_MATERIAL
    
    # 2. Position evaluation - HEAVILY penalize fragmentation
    our_groups = state.get_our_groups()
    opponent_groups = state.get_opponent_groups()
    
    # Strategic group count evaluation
    # CRITICAL FIX: EXTREME penalties to prevent fragmentation
    num_our_groups = len(our_groups)
    if num_our_groups == 1:
        # Single group is actually good - concentrated power
        score += config.BONUS_ONE_GROUP
    elif num_our_groups == 2:
        # Two groups is acceptable
        score += config.PENALTY_TWO_GROUPS  # Usually 0 (neutral)
    elif num_our_groups == 3:
        # Three groups is already bad
        score -= config.PENALTY_THREE_GROUPS
    elif num_our_groups >= 4:
        # 4+ groups is CATASTROPHICALLY penalized
        score -= (num_our_groups - 3) * config.PENALTY_EXCESS_GROUPS
    
    # HEAVILY penalize small groups - they are almost useless
    for x, y, count in our_groups:
        if count < config.SMALL_GROUP_THRESHOLD:
            # Small groups waste resources
            score -= config.PENALTY_SMALL_GROUP
    
    # Evaluate opponent's group count (mirror logic)
    num_opp_groups = len(opponent_groups)
    if num_opp_groups == 1:
        score -= config.BONUS_ONE_GROUP
    elif num_opp_groups == 2:
        score -= config.PENALTY_TWO_GROUPS
    elif num_opp_groups == 3:
        score += config.PENALTY_THREE_GROUPS
    elif num_opp_groups >= 4:
        score += (num_opp_groups - 3) * config.PENALTY_EXCESS_GROUPS
    
    for x, y, count in opponent_groups:
        if count < config.SMALL_GROUP_THRESHOLD:
            score += config.PENALTY_SMALL_GROUP
    
    # 3. Proximity to humans (with risk assessment)
    human_cells = []
    for i in range(state.rows):
        for j in range(state.cols):
            if state.board[i][j].humans > 0:
                human_cells.append((i, j, state.board[i][j].humans))
    
    if human_cells:
        # Import here to avoid circular dependency
        from move_generator import calculate_battle_probability
        
        # Evaluate proximity to winnable human groups
        for x, y, count in our_groups:
            for hx, hy, h_count in human_cells:
                dist = manhattan_distance(x, y, hx, hy)
                win_prob = calculate_battle_probability(count, h_count)
                
                if dist <= 2:  # Close proximity
                    if win_prob >= 0.7:
                        # High confidence win - reward being close
                        score += config.WEIGHT_HUMAN_PROXIMITY / (1 + dist)
                    elif win_prob >= 0.5:
                        # Moderate chance - small reward
                        score += (config.WEIGHT_HUMAN_PROXIMITY * 0.375) / (1 + dist)
                    elif win_prob < 0.5:
                        # Risky or losing - penalize being too close
                        score -= (config.WEIGHT_HUMAN_PROXIMITY * 1.25) / (1 + dist)
                elif dist <= 4 and win_prob >= 0.7:
                    # Moderate distance to highly winnable target - small bonus
                    score += config.WEIGHT_HUMAN_PROXIMITY * 0.25
        
        # Same for opponent proximity to humans
        for x, y, count in opponent_groups:
            for hx, hy, h_count in human_cells:
                dist = manhattan_distance(x, y, hx, hy)
                win_prob = calculate_battle_probability(count, h_count)
                
                if dist <= 2 and win_prob >= 0.7:
                    # They have high confidence - penalize heavily
                    score -= config.WEIGHT_HUMAN_PROXIMITY / (1 + dist)
                elif dist <= 2 and win_prob >= 0.5:
                    # Moderate threat - penalize
                    score -= (config.WEIGHT_HUMAN_PROXIMITY * 0.375) / (1 + dist)
                elif dist <= 4 and win_prob >= 0.7:
                    score -= config.WEIGHT_HUMAN_PROXIMITY * 0.25
    
    # 4. Control of center (strategic advantage)
    center_x, center_y = state.rows // 2, state.cols // 2
    our_center_control = 0.0
    opponent_center_control = 0.0
    
    for x, y, count in our_groups:
        dist_to_center = manhattan_distance(x, y, center_x, center_y)
        our_center_control += count / (1 + dist_to_center)
    
    for x, y, count in opponent_groups:
        dist_to_center = manhattan_distance(x, y, center_x, center_y)
        opponent_center_control += count / (1 + dist_to_center)
    
    score += (our_center_control - opponent_center_control) * config.WEIGHT_CENTER_CONTROL
    
    # 5. Threat assessment and strategic concentration
    # Reward concentration when facing concentrated enemy forces
    # Penalize spreading out when close to enemy
    min_dist_to_enemy = float('inf')
    for our_x, our_y, our_cnt in our_groups:
        for opp_x, opp_y, opp_cnt in opponent_groups:
            dist = manhattan_distance(our_x, our_y, opp_x, opp_y)
            min_dist_to_enemy = min(min_dist_to_enemy, dist)
            
            if dist <= 2:  # Close proximity
                if our_cnt >= opp_cnt * 1.5:
                    # We can kill them
                    score += config.WEIGHT_THREAT_ASSESSMENT
                elif opp_cnt >= our_cnt * 1.5:
                    # They can kill us
                    score -= config.WEIGHT_THREAT_ASSESSMENT
    
    # Strategic concentration evaluation:
    # When close to enemy (min distance <= 3), reward concentration
    if min_dist_to_enemy <= 3 and num_our_groups > 2:
        # Enemy nearby - should concentrate forces, not split
        score -= (num_our_groups - 2) * config.PENALTY_SPLIT_NEAR_ENEMY
    
    # Count winnable human targets within reach (distance <= 3)
    winnable_targets = 0
    if human_cells:
        from move_generator import calculate_battle_probability
        for hx, hy, h_count in human_cells:
            for our_x, our_y, our_cnt in our_groups:
                dist = manhattan_distance(our_x, our_y, hx, hy)
                if dist <= 3:
                    win_prob = calculate_battle_probability(our_cnt, h_count)
                    if win_prob >= 0.7:
                        winnable_targets += 1
                        break  # Count each human group only once
    
    # Only reward splitting if there are multiple high-value targets
    # and we're not under immediate threat
    if winnable_targets >= 2 and min_dist_to_enemy > 3:
        # Multiple targets available and safe to split
        if num_our_groups >= 2:
            score += 10  # Small bonus for being positioned to capture multiple targets
    
    return score


def manhattan_distance(x1: int, y1: int, x2: int, y2: int) -> int:
    """Calculate Manhattan distance between two points."""
    return abs(x2 - x1) + abs(y2 - y1)


def chebyshev_distance(x1: int, y1: int, x2: int, y2: int) -> int:
    """Calculate Chebyshev distance (king's move distance) between two points."""
    return max(abs(x2 - x1), abs(y2 - y1))
