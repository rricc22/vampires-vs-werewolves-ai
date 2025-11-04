"""Move generation and battle simulation for Vampires VS Werewolves."""
from typing import List, Tuple, Set
import random
from game_state import GameState, Move, Species


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
    
    # For each group, generate possible splits and moves
    for x, y, count in groups:
        # Generate moves from this single group
        single_group_moves = generate_moves_from_cell(state, x, y, count)
        if single_group_moves:
            all_move_combos.extend([[move] for move in single_group_moves])
    
    # TODO: Add multi-group move combinations (for now, single moves per turn)
    # This is a simplification to keep the branching factor manageable
    
    return all_move_combos if all_move_combos else [[]]


def generate_moves_from_cell(state: GameState, x: int, y: int, count: int, debug: bool = False) -> List[Move]:
    """
    Generate all possible moves from a single cell.
    
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
        # Try moving different amounts: all, 3/4, 1/2, 1/4, or at least 1
        move_amounts = set([count])  # Always include moving all
        if count > 1:
            move_amounts.add(max(1, count * 3 // 4))
            move_amounts.add(max(1, count // 2))
            move_amounts.add(max(1, count // 4))
            move_amounts.add(1)
        
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
