"""
Evaluation function for game states.

REFACTORED VERSION (2024):
Simplified from complex branching logic to linear weighted scoring for easier tuning.

ENDGAME DETECTION (2024):
Added phase-based evaluation that adapts to game state:
- Early game: Focus on growth and map control
- Mid game: Balance growth with tactical positioning
- Late game: Maximize population advantage and winning chances

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
from enum import Enum
import config
import random


class GamePhase(Enum):
    """Game phase classification for adaptive evaluation."""
    EARLY = "early"   # Lots of humans, focus on growth
    MID = "mid"       # Few humans, both species competing
    LATE = "late"     # No humans, pure combat


def detect_game_phase(state: GameState) -> GamePhase:
    """
    Detect which phase of the game we're in.

    Early game: Lots of humans remaining (growth phase)
    Mid game: Few humans, both species alive (competition phase)
    Late game: No humans, pure combat (endgame)

    Args:
        state: Current game state

    Returns:
        GamePhase enum indicating current phase
    """
    total_humans = state.get_total_count(Species.HUMAN)

    # Count total board cells to get percentage of humans
    total_cells = state.rows * state.cols
    human_percentage = total_humans / max(total_cells, 1)

    # Late game: No humans left, pure combat
    if total_humans == 0:
        return GamePhase.LATE

    # Early game: More than threshold percentage of cells have humans
    # Use config parameter or default to 15% threshold
    early_game_threshold = getattr(config, 'PHASE_EARLY_GAME_HUMAN_THRESHOLD', 0.15)
    if human_percentage >= early_game_threshold:
        return GamePhase.EARLY

    # Mid game: Some humans left but below threshold
    return GamePhase.MID


def evaluate_state(state: GameState) -> float:
    """
    Evaluate a game state from our perspective with phase-based weights.

    The evaluation adapts to the game phase:
    - Early game: Focus on growth potential and spatial control
    - Mid game: Balance population, tactical positioning, and force concentration
    - Late game: Maximize population advantage and elimination threats

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

    # Detect game phase
    phase = detect_game_phase(state)

    # Get group information once
    our_groups = state.get_our_groups()
    opponent_groups = state.get_opponent_groups()

    # Calculate component scores
    growth_potential = _evaluate_growth_potential(state, our_groups, opponent_groups)
    spatial_control = _evaluate_spatial_control(state, our_groups, opponent_groups)
    population_differential = _evaluate_population_differential(our_count, opponent_count)
    tactical_positioning = _evaluate_tactical_positioning(state, our_groups, opponent_groups)
    force_concentration = _evaluate_force_concentration(our_groups, opponent_groups)
    elimination_threats = _evaluate_elimination_threats(state, our_groups, opponent_groups)

    # Apply phase-based weights
    if phase == GamePhase.EARLY:
        # Early game: HUMANS ARE EVERYTHING
        # Increased growth from 70% → 85%, reduced spatial from 20% → 5%
        # This prevents center rushing and prioritizes human collection
        total_score = (
            growth_potential * 0.85 +        # Proximity to humans + accessible humans
            spatial_control * 0.05 +          # Minimal (no center control anymore)
            population_differential * 0.10    # Watch population but don't obsess
        )
    elif phase == GamePhase.MID:
        # Mid game: Balance remaining humans with combat positioning
        # Add small amount of growth to still collect remaining humans
        total_score = (
            population_differential * 0.50 +
            tactical_positioning * 0.30 +
            force_concentration * 0.15 +
            growth_potential * 0.05           # Still grab remaining humans
        )
    else:  # GamePhase.LATE
        # Late game: Pure combat, no humans left
        total_score = (
            population_differential * 0.80 +
            elimination_threats * 0.20
        )

    # Add small random noise to break ties and prevent infinite loops
    # This helps avoid position repetition in symmetric situations
    noise_value = getattr(config, 'EVAL_RANDOM_NOISE', 0)
    if noise_value > 0:
        noise = random.uniform(-noise_value, noise_value)
        total_score += noise

    return total_score


# ============================================================
# PHASE-BASED EVALUATION COMPONENTS
# ============================================================

def _evaluate_growth_potential(state: GameState, our_groups: list, opponent_groups: list) -> float:
    """
    Evaluate growth potential - prioritize moving toward CAPTURABLE humans (early game focus).

    Two components:
    1. Proximity to capturable humans (prioritize villages we can actually take!)
    2. Accessible winnable humans (tactical incentive - rewards being in attack range)

    KEY FIX: Weighs proximity by capturability, not just village size.
    A 5-human village we CAN capture is worth more than a 15-human village we CAN'T.
    """
    score = 0.0

    # Get all human positions
    human_cells = []
    for i in range(state.rows):
        for j in range(state.cols):
            if state.board[i][j].humans > 0:
                human_cells.append((i, j, state.board[i][j].humans))

    if not human_cells:
        return 0.0

    # Component 1: Proximity to capturable humans
    # Prioritize villages we can ACTUALLY capture with our current forces
    proximity_score = 0.0
    proximity_weight = getattr(config, 'EVAL_HUMAN_PROXIMITY_WEIGHT', 50)

    for our_x, our_y, our_cnt in our_groups:
        best_capturable_score = 0.0

        for hx, hy, h_cnt in human_cells:
            dist = manhattan_distance(our_x, our_y, hx, hy)

            # Calculate base proximity score
            base_score = proximity_weight / (1 + dist)

            # Determine capturability multiplier
            # KEY: Villages we CAN'T capture should NOT draw us toward them!
            if our_cnt >= h_cnt:
                # GUARANTEED capture - HIGH value, scaled by potential gain
                multiplier = h_cnt * 4.0  # Very strong preference for capturable
                capturable_score = base_score * multiplier
                best_capturable_score = max(best_capturable_score, capturable_score)
            elif our_cnt >= h_cnt * 0.5:
                # POSSIBLE capture (50%+ win probability) - good value
                multiplier = h_cnt * 1.5
                capturable_score = base_score * multiplier
                best_capturable_score = max(best_capturable_score, capturable_score)
            # Villages we CAN'T capture: NO proximity value at all
            # (Don't track best_any_score - we shouldn't be drawn to uncapturable targets)

        # Only count capturable targets (ignore uncapturable villages entirely)
        proximity_score += best_capturable_score

    # Component 2: Accessible winnable humans (existing tactical logic)
    resource_score = _evaluate_resources(state, our_groups, opponent_groups)

    # Combine: proximity to capturable targets + resource accessibility
    return proximity_score + resource_score * 1.5


def _evaluate_spatial_control(state: GameState, our_groups: list, opponent_groups: list) -> float:
    """
    Evaluate spatial control of the map (early game focus).

    REMOVED: Center control (caused center rushing - 108 point advantage!)
    REMOVED: Territory coverage (encouraged splitting - more groups = higher score)

    NEW: Minimal scoring for having reasonable group distribution
    """
    score = 0.0

    # Reward having 1-2 groups for map coverage, but don't reward fragmentation
    # Cap at 2 groups to avoid encouraging splits
    if len(our_groups) >= 1:
        our_coverage = min(len(our_groups), 2) * 10
        score += our_coverage

    if len(opponent_groups) >= 1:
        opp_coverage = min(len(opponent_groups), 2) * 10
        score -= opp_coverage

    return score


def _evaluate_population_differential(our_count: int, opponent_count: int) -> float:
    """
    Evaluate raw population advantage (used in all phases).

    This is the most fundamental metric - having more units is always good.
    """
    weight = getattr(config, 'EVAL_MATERIAL_WEIGHT', 100)
    return (our_count - opponent_count) * weight


def _evaluate_tactical_positioning(state: GameState, our_groups: list, opponent_groups: list) -> float:
    """
    Evaluate tactical positioning advantages (mid game focus).

    Combines favorable matchups, strategic threats, positioning, and pincer opportunities.
    Scaled to match population differential range.
    """
    # Reuse existing tactical evaluation
    tactical_score = _evaluate_tactical(state, our_groups, opponent_groups)

    # Add pincer attack bonus
    pincer_score = _evaluate_pincer_opportunities(state, our_groups, opponent_groups)

    # Scale up for mid game importance
    return (tactical_score + pincer_score) * 3.0


def _evaluate_pincer_opportunities(state: GameState, our_groups: list, opponent_groups: list) -> float:
    """
    Evaluate pincer attack opportunities - reward positions where multiple groups
    can converge on the same enemy target.

    This encourages tactical formations like:
    - Two groups positioned to attack same enemy from different sides
    - Combined force that exceeds 1.5x enemy for guaranteed kills

    Returns:
        Bonus score for pincer opportunities
    """
    from move_generator import calculate_battle_probability

    score = 0.0

    if len(our_groups) < 2:
        return 0.0  # Need at least 2 groups for pincer

    # For each opponent group, check if we can attack from multiple angles
    for opp_x, opp_y, opp_cnt in opponent_groups:
        # Find all our groups that can reach this enemy (within 2 moves)
        attacking_groups = []
        total_attacking_force = 0

        for our_x, our_y, our_cnt in our_groups:
            dist = chebyshev_distance(our_x, our_y, opp_x, opp_y)
            if dist <= 2:  # Within striking range (1-2 moves)
                attacking_groups.append((our_x, our_y, our_cnt, dist))
                total_attacking_force += our_cnt

        # Pincer bonus: multiple groups can converge
        if len(attacking_groups) >= 2:
            # Base bonus for having pincer position
            score += 50

            # Bonus if combined force can overwhelm enemy
            if total_attacking_force >= opp_cnt * 1.5:
                score += 100  # Guaranteed kill with combined force
            elif total_attacking_force >= opp_cnt:
                # Good chance with combined attack
                win_prob = calculate_battle_probability(total_attacking_force, opp_cnt)
                score += win_prob * 80

            # Extra bonus for immediate pincer (both groups adjacent)
            adjacent_count = sum(1 for _, _, _, d in attacking_groups if d == 1)
            if adjacent_count >= 2:
                score += 75  # Can execute pincer next turn

    # Check if opponent has pincer threats against us (penalty)
    if len(opponent_groups) >= 2:
        for our_x, our_y, our_cnt in our_groups:
            opp_attacking = []
            opp_force = 0

            for opp_x, opp_y, opp_cnt in opponent_groups:
                dist = chebyshev_distance(our_x, our_y, opp_x, opp_y)
                if dist <= 2:
                    opp_attacking.append((opp_x, opp_y, opp_cnt, dist))
                    opp_force += opp_cnt

            if len(opp_attacking) >= 2:
                score -= 40  # We're in danger of pincer

                if opp_force >= our_cnt * 1.5:
                    score -= 80  # Critical danger

    return score


def _evaluate_force_concentration(our_groups: list, opponent_groups: list) -> float:
    """
    Evaluate force concentration vs fragmentation (mid game focus).

    In mid game, maintaining concentrated forces is crucial for combat effectiveness.
    Scaled to match population differential range.
    """
    # Reuse existing fragmentation evaluation
    fragmentation_score = _evaluate_fragmentation(our_groups, opponent_groups)

    # Scale up for mid game importance
    return fragmentation_score * 2.0


def _evaluate_elimination_threats(state: GameState, our_groups: list, opponent_groups: list) -> float:
    """
    Evaluate immediate elimination threats (late game focus).

    Can we eliminate opponent groups? Can they eliminate ours?
    This becomes critical in endgame when no humans remain.
    """
    from move_generator import calculate_battle_probability

    score = 0.0

    # Check if we can eliminate any opponent groups
    our_can_eliminate = 0
    for our_x, our_y, our_cnt in our_groups:
        for opp_x, opp_y, opp_cnt in opponent_groups:
            dist = manhattan_distance(our_x, our_y, opp_x, opp_y)
            if dist <= 2:  # Within striking range
                win_prob = calculate_battle_probability(our_cnt, opp_cnt)
                if win_prob >= 0.9:  # Very high chance to eliminate
                    our_can_eliminate += 1
                elif win_prob >= 0.7:  # Good chance
                    our_can_eliminate += 0.5

    # Check if opponent can eliminate any of our groups
    opp_can_eliminate = 0
    for opp_x, opp_y, opp_cnt in opponent_groups:
        for our_x, our_y, our_cnt in our_groups:
            dist = manhattan_distance(our_x, our_y, opp_x, opp_y)
            if dist <= 2:  # Within striking range
                win_prob = calculate_battle_probability(opp_cnt, our_cnt)
                if win_prob >= 0.9:  # They can eliminate us
                    opp_can_eliminate += 1
                elif win_prob >= 0.7:
                    opp_can_eliminate += 0.5

    # Score based on elimination potential
    score += (our_can_eliminate - opp_can_eliminate) * 200

    # In late game, heavily penalize being outnumbered with fragmented forces
    if len(our_groups) > len(opponent_groups):
        our_total = sum(cnt for _, _, cnt in our_groups)
        opp_total = sum(cnt for _, _, cnt in opponent_groups)
        if opp_total > our_total:
            # We're fragmented AND outnumbered - very bad in endgame
            score -= (len(our_groups) - len(opponent_groups)) * 100

    return score


# ============================================================
# LEGACY COMPONENT FUNCTIONS (used by phase-based evaluation)
# ============================================================
# These are the original evaluation components, now called by
# the phase-based functions above.
# ============================================================

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
