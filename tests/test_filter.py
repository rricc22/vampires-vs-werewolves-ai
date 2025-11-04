#!/usr/bin/env python3
"""Test that the 70% filter prevents risky attacks on humans."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai'))

from game_state import GameState, Species, Move
from move_generator import generate_moves_from_cell, calculate_battle_probability

def test_filter_prevents_5v5_attack():
    """Test that 5 units won't attack 5 humans (50% win probability)."""
    print("\n" + "="*60)
    print("Test: Filter prevents 5v5 attack on humans")
    print("="*60)
    
    # Create game state
    state = GameState(rows=8, cols=8)
    state.our_species = Species.WEREWOLF
    state.opponent_species = Species.VAMPIRE
    
    # Place 5 werewolves at (3, 1)
    state.board[3][1].werewolves = 5
    
    # Place 5 humans at (2, 2) - adjacent diagonally
    state.board[2][2].humans = 5
    
    print(f"\nSetup:")
    print(f"  Werewolves at (3,1): 5 units")
    print(f"  Humans at (2,2): 5 units")
    print(f"  Distance: diagonal (adjacent)")
    
    # Calculate win probability
    win_prob = calculate_battle_probability(5, 5)
    print(f"\nWin probability for 5v5: {win_prob:.1%}")
    
    # Generate moves
    print(f"\nGenerating moves from (3,1)...")
    moves = generate_moves_from_cell(state, 3, 1, 5, debug=True)
    
    # Check if any move targets (2,2)
    attack_moves = [m for m in moves if m.x_to == 2 and m.y_to == 2]
    
    print(f"\nMoves targeting (2,2) with humans:")
    if attack_moves:
        for m in attack_moves:
            print(f"  {m}")
        print(f"\n✗ FAIL: Filter allowed {len(attack_moves)} attack(s) on 5 humans")
        print(f"  These attacks have {win_prob:.1%} win probability < 70% threshold")
        return False
    else:
        print(f"  None")
        print(f"\n✓ PASS: Filter correctly blocked attacks with {win_prob:.1%} win probability")
        return True

def test_filter_allows_10v5_attack():
    """Test that 10 units CAN attack 5 humans (80% win probability)."""
    print("\n" + "="*60)
    print("Test: Filter allows 10v5 attack on humans")
    print("="*60)
    
    # Create game state
    state = GameState(rows=8, cols=8)
    state.our_species = Species.WEREWOLF
    state.opponent_species = Species.VAMPIRE
    
    # Place 10 werewolves at (3, 1)
    state.board[3][1].werewolves = 10
    
    # Place 5 humans at (2, 2)
    state.board[2][2].humans = 5
    
    print(f"\nSetup:")
    print(f"  Werewolves at (3,1): 10 units")
    print(f"  Humans at (2,2): 5 units")
    
    # Calculate win probability
    win_prob = calculate_battle_probability(10, 5)
    print(f"\nWin probability for 10v5: {win_prob:.1%}")
    
    # Generate moves
    print(f"\nGenerating moves from (3,1)...")
    moves = generate_moves_from_cell(state, 3, 1, 10)
    
    # Check if any move targets (2,2)
    attack_moves = [m for m in moves if m.x_to == 2 and m.y_to == 2]
    
    print(f"\nMoves targeting (2,2) with humans:")
    if attack_moves:
        print(f"  Found {len(attack_moves)} moves (with different unit counts)")
        # Check if "all 10" move is included
        full_attack = [m for m in attack_moves if m.count == 10]
        if full_attack:
            print(f"  Including full attack: {full_attack[0]}")
        print(f"\n✓ PASS: Filter allows attacks with {win_prob:.1%} win probability")
        return True
    else:
        print(f"  None")
        print(f"\n✗ FAIL: Filter blocked attacks with {win_prob:.1%} win probability")
        print(f"  This is above the 70% threshold and should be allowed!")
        return False

if __name__ == "__main__":
    test1 = test_filter_prevents_5v5_attack()
    test2 = test_filter_allows_10v5_attack()
    
    print("\n" + "="*60)
    if test1 and test2:
        print("✓ All filter tests passed!")
        print("="*60)
        sys.exit(0)
    else:
        print("✗ Some filter tests failed")
        print("="*60)
        sys.exit(1)
