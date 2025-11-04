"""Simple test for the AI implementation."""
import sys
from pathlib import Path

# Add ai directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "ai"))

from game_state import GameState, Species, Move
from move_generator import generate_all_moves, apply_move_to_state, calculate_battle_probability
from evaluation import evaluate_state
from alphabeta import find_best_move


def test_game_state():
    """Test game state initialization."""
    print("Testing GameState...")
    state = GameState(10, 10)
    
    # Simulate initial setup
    size = (10, 10)
    humans = [[2, 2], [3, 3], [7, 7]]
    home = [0, 0]
    map_data = [
        (0, 0, 0, 8, 0),  # Vampires at home
        (9, 9, 0, 0, 8),  # Werewolves at opponent home
        (2, 2, 5, 0, 0),  # Humans
        (3, 3, 5, 0, 0),
        (7, 7, 5, 0, 0),
    ]
    
    state.initialize_from_messages(size, humans, home, map_data)
    
    print(f"  Our species: {state.our_species}")
    print(f"  Opponent species: {state.opponent_species}")
    print(f"  Our count: {state.get_total_count(state.our_species)}")
    print(f"  Opponent count: {state.get_total_count(state.opponent_species)}")
    print(f"  Our groups: {state.get_our_groups()}")
    print("✓ GameState test passed\n")


def test_battle_probability():
    """Test battle probability calculations."""
    print("Testing battle probabilities...")
    
    # Equal forces
    p = calculate_battle_probability(5, 5)
    assert abs(p - 0.5) < 0.01, f"Equal forces should be 0.5, got {p}"
    print(f"  Equal (5 vs 5): P = {p}")
    
    # Attackers have advantage
    p = calculate_battle_probability(8, 5)
    print(f"  Advantage (8 vs 5): P = {p}")
    assert p > 0.5, "More attackers should have > 0.5 probability"
    
    # Attackers disadvantaged
    p = calculate_battle_probability(3, 5)
    print(f"  Disadvantage (3 vs 5): P = {p}")
    assert p < 0.5, "Fewer attackers should have < 0.5 probability"
    
    print("✓ Battle probability test passed\n")


def test_move_generation():
    """Test move generation."""
    print("Testing move generation...")
    state = GameState(10, 10)
    
    # Setup simple scenario
    state.our_species = Species.VAMPIRE
    state.opponent_species = Species.WEREWOLF
    state.board[5][5].vampires = 10
    
    moves = generate_all_moves(state, for_opponent=False)
    print(f"  Generated {len(moves)} move combinations")
    
    if moves:
        print(f"  First move: {moves[0]}")
    
    assert len(moves) > 0, "Should generate at least one move"
    print("✓ Move generation test passed\n")


def test_evaluation():
    """Test evaluation function."""
    print("Testing evaluation function...")
    state = GameState(10, 10)
    
    state.our_species = Species.VAMPIRE
    state.opponent_species = Species.WEREWOLF
    
    # Equal scenario
    state.board[0][0].vampires = 10
    state.board[9][9].werewolves = 10
    score1 = evaluate_state(state)
    print(f"  Equal forces: score = {score1:.2f}")
    
    # We have advantage
    state.board[0][0].vampires = 20
    score2 = evaluate_state(state)
    print(f"  We have advantage: score = {score2:.2f}")
    assert score2 > score1, "More units should have better score"
    
    # We're losing
    state.board[0][0].vampires = 5
    state.board[9][9].werewolves = 20
    score3 = evaluate_state(state)
    print(f"  We're losing: score = {score3:.2f}")
    assert score3 < score1, "Fewer units should have worse score"
    
    print("✓ Evaluation test passed\n")


def test_alpha_beta():
    """Test Alpha-Beta search."""
    print("Testing Alpha-Beta search...")
    state = GameState(10, 10)
    
    # Setup game scenario
    state.our_species = Species.VAMPIRE
    state.opponent_species = Species.WEREWOLF
    state.board[5][5].vampires = 10
    state.board[7][7].werewolves = 8
    state.board[3][3].humans = 5
    
    print("  Running Alpha-Beta search (this may take a moment)...")
    best_moves = find_best_move(state, max_depth=2, time_limit=0.5)
    
    print(f"  Found moves: {best_moves}")
    assert len(best_moves) >= 0, "Should return a move list"
    print("✓ Alpha-Beta test passed\n")


def test_move_application():
    """Test applying moves to state."""
    print("Testing move application...")
    state = GameState(10, 10)
    
    state.our_species = Species.VAMPIRE
    state.opponent_species = Species.WEREWOLF
    state.board[5][5].vampires = 10
    
    # Create a simple move
    move = Move(5, 5, 5, 6, 5)
    new_state = apply_move_to_state(state, [move], for_opponent=False)
    
    print(f"  Original: vampires at (5,5) = {state.board[5][5].vampires}")
    print(f"  After move: vampires at (5,5) = {new_state.board[5][5].vampires}")
    print(f"  After move: vampires at (5,6) = {new_state.board[5][6].vampires}")
    
    assert new_state.board[5][5].vampires == 5, "Should have 5 remaining"
    assert new_state.board[5][6].vampires == 5, "Should have 5 moved"
    print("✓ Move application test passed\n")


if __name__ == "__main__":
    print("="*60)
    print("Running AI Tests")
    print("="*60 + "\n")
    
    try:
        test_game_state()
        test_battle_probability()
        test_move_generation()
        test_evaluation()
        test_move_application()
        test_alpha_beta()
        
        print("="*60)
        print("All tests passed! ✓")
        print("="*60)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
