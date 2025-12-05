#!/usr/bin/env python3
"""Quick test to verify guaranteed conversion logic."""

import sys
sys.path.append('ai')

from game_state import GameState, Species
from move_generator import generate_moves_from_cell, calculate_battle_probability
from config import ATTACK_MIN_WIN_PROBABILITY

# Create a simple test scenario
state = GameState(10, 10)
state.our_species = Species.VAMPIRE

# Test case: 6 vampires at (5,5), 5 humans at (5,6)
state.board[5][5].vampires = 6
state.board[5][6].humans = 5

print("=== Testing Guaranteed Conversion Fix ===")
print(f"Scenario: 6 vampires at (5,5) want to attack 5 humans at (5,6)")
print(f"Battle probability: {calculate_battle_probability(6, 5):.2%}")
print(f"Attack threshold: {ATTACK_MIN_WIN_PROBABILITY:.2%}")
print(f"Expected: Should allow attack (guaranteed conversion since 6 >= 5)")
print()

# Generate moves from the vampire cell
moves = generate_moves_from_cell(state, 5, 5, 6, debug=True)

# Check if there's a move targeting (5,6)
attack_move = None
for move in moves:
    if move.x_to == 5 and move.y_to == 6:
        attack_move = move
        break

print()
if attack_move:
    print(f"✓ SUCCESS: AI will attack! Move: {attack_move.count} units from ({attack_move.x_from},{attack_move.y_from}) to ({attack_move.x_to},{attack_move.y_to})")
else:
    print("✗ FAILED: AI still won't attack (bug not fixed)")

print()
print(f"Total moves generated: {len(moves)}")
