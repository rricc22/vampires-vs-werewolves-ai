"""Move generation and battle simulation for Vampires VS Werewolves."""
from typing import List, Tuple, Set
import random
from game_state import GameState, Move, Species
from config import (MIN_GROUP_SIZE, MAX_GROUPS_PER_TURN, 
                    MIN_SPLIT_SIZE, SPLIT_RATIOS)


def calculate_battle_probability(attackers: int, defenders: int) -> float:
    """
    Calculate probability that attackers win.
    
    Based on the rules:
    - If E1 == E2: P = 0.5
    - If E1 < E2: P = E1 / (2 * E2)
    - If E1 > E2: P = 0.5 + (E1 - E2) / (2 * E2)
    
    Args:
        attackers: Number of attacking creatures
        defenders: Number of defending creatures
        
    Returns:
        Probability that attackers win (0.0 to 1.0)
    """
    if attackers == defenders:
        return 0.5
    elif attackers < defenders:
        return attackers / (2.0 * defenders)
    else:  # attackers > defenders
        return 0.5 + (attackers - defenders) / (2.0 * defenders)


def simulate_battle(attackers: int, defenders: int, is_human: bool = False) -> Tuple[int, int]:
    """
    Simulate a battle and return survivors.
    
    Args:
        attackers: Number of attacking creatures
        defenders: Number of defending creatures
        is_human: Whether defenders are humans (can be converted)
        
    Returns:
        Tuple of (surviving_attackers, surviving_defenders)
    """
    win_prob = calculate_battle_probability(attackers, defenders)
    
    if random.random() < win_prob:
        # Attackers win
        surviving_attackers = sum(1 for _ in range(attackers) if random.random() < win_prob)
        if is_human:
            # Convert surviving humans
            converted_humans = sum(1 for _ in range(defenders) if random.random() < win_prob)
            return surviving_attackers + converted_humans, 0
        else:
            return surviving_attackers, 0
    else:
        # Defenders win
        surviving_defenders = sum(1 for _ in range(defenders) if random.random() < (1 - win_prob))
        return 0, surviving_defenders


def get_battle_expected_value(attackers: int, defenders: int, is_human: bool = False) -> Tuple[float, float]:
    """
    Calculate expected value of battle outcome.
    
    Args:
        attackers: Number of attacking creatures
        defenders: Number of defending creatures
        is_human: Whether defenders are humans
        
    Returns:
        Tuple of (expected_attackers, expected_defenders)
    """
    win_prob = calculate_battle_probability(attackers, defenders)
    
    if win_prob >= 1.0:
        # Guaranteed win
        return float(attackers), 0.0
    elif win_prob <= 0.0:
        # Guaranteed loss
        return 0.0, float(defenders)
    
    # Expected survivors if attackers win
    expected_survivors_if_win = attackers * win_prob
    if is_human:
        expected_converted = defenders * win_prob
        expected_if_win = expected_survivors_if_win + expected_converted
    else:
        expected_if_win = expected_survivors_if_win
    
    # Expected survivors if defenders win
    expected_defenders_if_lose = defenders * (1 - win_prob)
    
    # Weighted by win probability
    expected_attackers = expected_if_win * win_prob
    expected_defenders = expected_defenders_if_lose * (1 - win_prob)
    
    return expected_attackers, expected_defenders


def generate_all_moves(state: GameState, for_opponent: bool = False) -> List[List[Move]]:
    """
    Generate all legal move combinations.
    
    FIXED: Now supports multi-group moves per turn.
    - Single-group moves: Each group moves independently
    - Multi-group moves: Top strategic groups can move simultaneously (up to MAX_GROUPS_PER_TURN)
    - Uses smart heuristics to avoid combinatorial explosion:
      * Prioritizes larger groups
      * Only combines groups that are far apart (distance > 3)
      * Respects Rule 5: No cell can be both source and target
    
    Rules:
    1. At least one movement per turn
    2. Can only move your species
    3. Must have enough creatures to perform all moves from a cell
    4. Can move in 8 directions (unless on borders)
    5. A cell cannot be both target and source in the same turn
    6. Must move at least one creature
    
    Args:
        state: Current game state
        for_opponent: If True, generate moves for opponent
        
    Returns:
        List of move combinations (each combination is a list of moves)
    """
    species = state.opponent_species if for_opponent else state.our_species
    if species is None:
        return []
    
    groups = state.get_opponent_groups() if for_opponent else state.get_our_groups()
    
    if not groups:
        return []
    
    all_move_combos = []
    
    # Generate single-group moves for each group
    group_moves = []  # List of (group_info, moves_list)
    for x, y, count in groups:
        moves = generate_moves_from_cell(state, x, y, count)
        if moves:
            group_moves.append(((x, y, count), moves))
            # Add each single move as a combo
            all_move_combos.extend([[move] for move in moves])
    
    # Generate multi-group moves (strategic combinations)
    # To avoid combinatorial explosion, we use smart heuristics:
    # 1. Only combine top groups by size
    # 2. Validate Rule 5 for each combination (no source/target overlap)
    if len(group_moves) >= 2:
        # Sort groups by size (descending) to prioritize important groups
        sorted_group_moves = sorted(group_moves, key=lambda gm: gm[0][2], reverse=True)
        
        # Take top groups (up to MAX_GROUPS_PER_TURN)
        top_groups = sorted_group_moves[:min(MAX_GROUPS_PER_TURN, len(sorted_group_moves))]
        
        # Try combining moves from top groups
        if len(top_groups) == 2:
            (x1, y1, c1), moves1 = top_groups[0]
            (x2, y2, c2), moves2 = top_groups[1]
            
            # Generate combinations of moves from both groups
            # FIXED: Instead of checking distance, we check actual Rule 5 violations
            # This allows more realistic multi-group moves
            multi_count = 0
            for move1 in moves1[:10]:  # Limit to top 10 moves per group to control branching
                for move2 in moves2[:10]:
                    # Check Rule 5: source and target can't overlap
                    sources = {(move1.x_from, move1.y_from), (move2.x_from, move2.y_from)}
                    targets = {(move1.x_to, move1.y_to), (move2.x_to, move2.y_to)}
                    if not sources & targets:  # No overlap
                        all_move_combos.append([move1, move2])
                        multi_count += 1

    
    return all_move_combos if all_move_combos else [[]]


def generate_moves_from_cell(state: GameState, x: int, y: int, count: int, debug: bool = False) -> List[Move]:
    """
    Generate all possible moves from a single cell.
    
    FIXED: Reduced split ratios to prevent excessive fragmentation.
    Now uses configurable SPLIT_RATIOS (default: all, 2/3, 1/2) instead of (all, 3/4, 1/2, 1/4, 1).
    Also enforces MIN_GROUP_SIZE and MIN_SPLIT_SIZE to avoid creating tiny ineffective groups.
    
    Args:
        state: Current game state
        x, y: Source cell coordinates (in our internal format: x=row, y=col)
        count: Number of creatures in the cell
        debug: Enable debug logging
        
    Returns:
        List of possible moves from this cell
    """
    moves = []
    
    if debug:
        print(f"\n=== Generating moves from cell ({x},{y}) with {count} units ===")
    
    # Try all 8 directions
    for dx, dy in GameState.DIRECTIONS:
        target_x = x + dx
        target_y = y + dy
        
        # Check if target is valid
        if not (0 <= target_x < state.rows and 0 <= target_y < state.cols):
            continue
        
        # Check target cell contents
        target_cell = state.board[target_x][target_y]
        
        if debug:
            print(f"  Direction ({dx},{dy}) → target ({target_x},{target_y}): H={target_cell.humans} V={target_cell.vampires} W={target_cell.werewolves}")
        
        # Generate moves with different creature counts
        # FIXED: Use configured split ratios to reduce fragmentation
        move_amounts = set()
        
        # Always include moving all units
        move_amounts.add(count)
        
        # Only allow splits if we have enough units
        if count >= MIN_SPLIT_SIZE:
            for ratio in SPLIT_RATIOS:
                if ratio < 1.0:  # Don't duplicate the "all" case
                    amount = max(MIN_GROUP_SIZE, int(count * ratio))
                    # Only add if it creates meaningful groups
                    remaining = count - amount
                    if remaining >= MIN_GROUP_SIZE or remaining == 0:
                        move_amounts.add(amount)
        
        # If we're too small to split, just move all or nothing
        # (the "all" case is already added)
        
        for amount in move_amounts:
            if amount > 0 and amount <= count:
                # Filter out risky attacks on human groups
                if target_cell.humans > 0:
                    win_prob = calculate_battle_probability(amount, target_cell.humans)
                    # Only attack humans if we have at least 70% win chance
                    # This prevents weak attacks like 5v5 (50% chance) that lead to pyrrhic victories
                    # We want to be confident we'll win AND maintain enough forces
                    if win_prob < 0.7:
                        if debug:
                            print(f"    FILTERED: {amount} units vs {target_cell.humans} humans (win prob {win_prob:.2%} < 70%)")
                        continue
                    elif debug:
                        print(f"    ALLOWED: {amount} units vs {target_cell.humans} humans (win prob {win_prob:.2%})")
                
                moves.append(Move(x, y, target_x, target_y, amount))
    
    if debug:
        print(f"  Total moves generated: {len(moves)}")
    
    return moves


def apply_move_to_state(state: GameState, moves: List[Move], for_opponent: bool = False) -> GameState:
    """
    Apply a move combination to create a new game state.
    
    Args:
        state: Current game state
        moves: List of moves to apply
        for_opponent: If True, moves are for opponent
        
    Returns:
        New game state after applying moves
    """
    new_state = state.clone()
    species = new_state.opponent_species if for_opponent else new_state.our_species
    
    if species is None:
        return new_state
    
    # Track sources and targets to validate rules
    sources: Set[Tuple[int, int]] = set()
    targets: Set[Tuple[int, int]] = set()
    
    # First pass: validate and track
    for move in moves:
        sources.add((move.x_from, move.y_from))
        targets.add((move.x_to, move.y_to))
    
    # Rule 5: A cell cannot be both source and target
    if sources & targets:
        # Invalid move combination
        return new_state
    
    # Second pass: apply moves
    for move in moves:
        source_cell = new_state.board[move.x_from][move.y_from]
        target_cell = new_state.board[move.x_to][move.y_to]
        
        # Remove creatures from source
        current_count = source_cell.get_count(species)
        if current_count < move.count:
            # Invalid move: not enough creatures
            continue
        
        source_cell.set_count(species, current_count - move.count)
        
        # Resolve target cell
        target_count = target_cell.get_count(species)
        enemy_species = new_state.opponent_species if not for_opponent else new_state.our_species
        enemy_count = target_cell.get_count(enemy_species) if enemy_species else 0
        human_count = target_cell.humans
        
        if enemy_count > 0:
            # Battle with enemy
            if move.count >= enemy_count * 1.5:
                # Guaranteed kill
                target_cell.set_count(enemy_species, 0)
                target_cell.set_count(species, target_count + move.count)
            elif enemy_count >= move.count * 1.5:
                # Guaranteed loss - attackers die
                pass  # Attackers don't survive
            else:
                # Random battle - use expected value
                expected_win, expected_lose = get_battle_expected_value(move.count, enemy_count, False)
                target_cell.set_count(species, target_count + int(expected_win))
                target_cell.set_count(enemy_species, int(expected_lose))
        
        elif human_count > 0:
            # Battle/conversion with humans
            if move.count >= human_count:
                # Guaranteed conversion
                target_cell.humans = 0
                target_cell.set_count(species, target_count + move.count + human_count)
            else:
                # Random battle
                expected_win, expected_humans = get_battle_expected_value(move.count, human_count, True)
                target_cell.set_count(species, target_count + int(expected_win))
                target_cell.humans = int(expected_humans)
        
        else:
            # Empty cell or friendly cell
            target_cell.set_count(species, target_count + move.count)
    
    return new_state
