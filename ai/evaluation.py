"""Evaluation function for game states."""
from game_state import GameState, Species
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
    score += (our_count - opponent_count) * 100
    
    # 2. Position evaluation
    our_groups = state.get_our_groups()
    opponent_groups = state.get_opponent_groups()
    
    # Bonus for number of groups (spread out is better)
    score += len(our_groups) * 10
    score -= len(opponent_groups) * 10
    
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
                        score += 40 / (1 + dist)
                    elif win_prob >= 0.5:
                        # Moderate chance - small reward
                        score += 15 / (1 + dist)
                    elif win_prob < 0.5:
                        # Risky or losing - penalize being too close
                        score -= 50 / (1 + dist)
                elif dist <= 4 and win_prob >= 0.7:
                    # Moderate distance to highly winnable target - small bonus
                    score += 10
        
        # Same for opponent proximity to humans
        for x, y, count in opponent_groups:
            for hx, hy, h_count in human_cells:
                dist = manhattan_distance(x, y, hx, hy)
                win_prob = calculate_battle_probability(count, h_count)
                
                if dist <= 2 and win_prob >= 0.7:
                    # They have high confidence - penalize heavily
                    score -= 40 / (1 + dist)
                elif dist <= 2 and win_prob >= 0.5:
                    # Moderate threat - penalize
                    score -= 15 / (1 + dist)
                elif dist <= 4 and win_prob >= 0.7:
                    score -= 10
    
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
    
    score += (our_center_control - opponent_center_control) * 2
    
    # 5. Threat assessment
    for our_x, our_y, our_cnt in our_groups:
        for opp_x, opp_y, opp_cnt in opponent_groups:
            dist = manhattan_distance(our_x, our_y, opp_x, opp_y)
            if dist <= 2:  # Close proximity
                if our_cnt >= opp_cnt * 1.5:
                    # We can kill them
                    score += 20
                elif opp_cnt >= our_cnt * 1.5:
                    # They can kill us
                    score -= 20
    
    return score


def manhattan_distance(x1: int, y1: int, x2: int, y2: int) -> int:
    """Calculate Manhattan distance between two points."""
    return abs(x2 - x1) + abs(y2 - y1)


def chebyshev_distance(x1: int, y1: int, x2: int, y2: int) -> int:
    """Calculate Chebyshev distance (king's move distance) between two points."""
    return max(abs(x2 - x1), abs(y2 - y1))
