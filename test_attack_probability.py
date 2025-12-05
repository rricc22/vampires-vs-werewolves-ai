#!/usr/bin/env python3
"""
Test script to verify ATTACK_MIN_WIN_PROBABILITY filtering works correctly.

This script simulates the arena.xml map scenario and tests if the AI:
1. Correctly calculates win probabilities
2. Filters attacks based on ATTACK_MIN_WIN_PROBABILITY threshold
3. Generates moves that should be allowed (60% win prob vs 10% threshold)
"""

import sys
sys.path.insert(0, 'ai')

from game_state import GameState, Species
from move_generator import (
    calculate_battle_probability,
    generate_moves_from_cell,
    generate_all_moves
)
from config import ATTACK_MIN_WIN_PROBABILITY

def test_battle_probability():
    """Test that battle probability calculation is correct."""
    print("=" * 70)
    print("TEST 1: Battle Probability Calculation")
    print("=" * 70)

    test_cases = [
        (6, 5, 0.6),   # 6 vs 5 humans = 60%
        (12, 15, 0.4), # 12 vs 15 humans = 40%
        (10, 10, 0.5), # Equal = 50%
        (15, 10, 0.75), # 15 vs 10 = 75%
    ]

    all_passed = True
    for attackers, defenders, expected in test_cases:
        actual = calculate_battle_probability(attackers, defenders)
        passed = abs(actual - expected) < 0.01
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {attackers} vs {defenders} → {actual:.2%} (expected {expected:.0%})")
        if not passed:
            all_passed = False

    print(f"\nResult: {'All tests passed!' if all_passed else 'Some tests failed!'}\n")
    return all_passed


def test_move_filtering():
    """Test that moves are filtered correctly based on win probability."""
    print("=" * 70)
    print("TEST 2: Move Filtering with ATTACK_MIN_WIN_PROBABILITY")
    print("=" * 70)
    print(f"Current threshold: {ATTACK_MIN_WIN_PROBABILITY:.0%} ({ATTACK_MIN_WIN_PROBABILITY})")
    print()

    # Create a simple test state: Vampires at (0,0) with 12 units, humans at (0,1) with 5 units
    state = GameState(rows=10, cols=10)
    state.our_species = Species.VAMPIRE
    state.opponent_species = Species.WEREWOLF
    state.board[0][0].vampires = 12
    state.board[0][1].humans = 5  # Adjacent cell with 5 humans

    print("Scenario: 12 vampires at (0,0), 5 humans at (0,1)")
    print()

    # Calculate win probability for full group attack
    win_prob = calculate_battle_probability(12, 5)
    print(f"Win probability for 12 vs 5: {win_prob:.2%}")
    print(f"Threshold: {ATTACK_MIN_WIN_PROBABILITY:.0%}")
    print(f"Should be allowed: {win_prob >= ATTACK_MIN_WIN_PROBABILITY}")
    print()

    # Generate moves
    print("Generating moves with DEBUG_MOVE_GENERATION=True...")
    print("-" * 70)
    moves = generate_moves_from_cell(state, 0, 0, 12, debug=True)
    print("-" * 70)
    print()

    # Check if attack move was generated
    attack_moves = [m for m in moves if m.x_to == 0 and m.y_to == 1]

    if attack_moves:
        print(f"✓ PASS: Generated {len(attack_moves)} attack moves to (0,1)")
        for move in attack_moves:
            wp = calculate_battle_probability(move.count, 5)
            print(f"  - Move {move.count} units (win prob: {wp:.2%})")
    else:
        print(f"✗ FAIL: No attack moves generated to (0,1)")
        print(f"  Expected: At least one move attacking the humans")
        print(f"  Generated moves: {len(moves)} total")
        for move in moves[:5]:  # Show first 5 moves
            print(f"    {move}")

    print()
    return len(attack_moves) > 0


def test_arena_scenario():
    """Test the full arena.xml scenario."""
    print("=" * 70)
    print("TEST 3: Arena.xml Scenario")
    print("=" * 70)
    print(f"Current threshold: {ATTACK_MIN_WIN_PROBABILITY:.0%}")
    print()

    # Create arena.xml initial state
    state = GameState(rows=10, cols=10)
    state.our_species = Species.VAMPIRE
    state.opponent_species = Species.WEREWOLF

    # Set up pieces (using internal coordinates: x=row, y=col)
    state.board[0][0].vampires = 12  # Vampires at top-left
    state.board[9][9].werewolves = 12  # Werewolves at bottom-right
    state.board[0][9].humans = 5  # Top-right corner
    state.board[9][0].humans = 5  # Bottom-left corner
    state.board[4][4].humans = 15  # Center
    state.board[5][5].humans = 15  # Center

    print("Initial state:")
    print("  Vampires: 12 at (0,0)")
    print("  Humans: 5 at (0,9), 5 at (9,0), 15 at (4,4), 15 at (5,5)")
    print()

    print("Generating all moves...")
    print("-" * 70)
    all_moves = generate_all_moves(state, for_opponent=False)
    print("-" * 70)
    print()

    print(f"Total move combinations generated: {len(all_moves)}")

    # Analyze move types
    single_moves = [m for m in all_moves if len(m) == 1]
    split_moves = [m for m in all_moves if len(m) == 2]

    print(f"  Single moves: {len(single_moves)}")
    print(f"  Split moves (2 groups): {len(split_moves)}")
    print()

    # Show what moves ARE generated (for debugging)
    if single_moves:
        print("Sample single moves generated:")
        for move_combo in single_moves[:5]:
            move = move_combo[0]
            target_cell = state.board[move.x_to][move.y_to]
            print(f"  - {move.count} units: ({move.x_from},{move.y_from}) → ({move.x_to},{move.y_to}) "
                  f"[H={target_cell.humans} V={target_cell.vampires} W={target_cell.werewolves}]")
        print()

    # Note: Corner humans are 9 cells away - not reachable in one move!
    # This is expected behavior, not a bug.
    print("NOTE: Corner humans at (0,9) and (9,0) are 9 cells away from (0,0)")
    print("      Vampires can only move 1 cell per turn, so they're not reachable yet.")
    print("      This test demonstrates the AI generates valid moves to empty cells.")
    print()

    # The important test is that moves ARE generated and not over-filtered
    has_moves = len(all_moves) > 0
    if has_moves:
        print(f"✓ PASS: AI generated {len(all_moves)} move combinations")
    else:
        print("✗ FAIL: No moves generated at all!")

    print()
    return has_moves


def test_adjacent_humans():
    """Test with various human groups at different distances and sizes."""
    print("=" * 70)
    print("TEST 4: Adjacent Humans (Different Attack Strengths)")
    print("=" * 70)
    print(f"Current threshold: {ATTACK_MIN_WIN_PROBABILITY:.0%}")
    print()

    # Create state with humans at various positions
    state = GameState(rows=10, cols=10)
    state.our_species = Species.VAMPIRE
    state.opponent_species = Species.WEREWOLF

    # Vampires at (5,5) with humans in adjacent cells at different strengths
    state.board[5][5].vampires = 20

    # Easy target: 2 humans (should definitely attack)
    state.board[4][5].humans = 2  # North: 20 vs 2 = 95% win
    # Medium target: 10 humans (should attack)
    state.board[5][6].humans = 10  # East: 20 vs 10 = 75% win
    # Hard target: 30 humans (borderline, should not attack initially)
    state.board[6][5].humans = 30  # South: 20 vs 30 = 33% win
    # Very hard: 50 humans (should definitely not attack)
    state.board[5][4].humans = 50  # West: 20 vs 50 = 20% win

    print("Scenario: 20 vampires at (5,5) with adjacent human groups:")
    print("  North (4,5): 2 humans  → P(win) = 95%")
    print("  East (5,6): 10 humans  → P(win) = 75%")
    print("  South (6,5): 30 humans → P(win) = 33%")
    print("  West (5,4): 50 humans  → P(win) = 20%")
    print()

    # Generate moves
    print("Generating moves with DEBUG_MOVE_GENERATION=True...")
    print("-" * 70)
    moves = generate_moves_from_cell(state, 5, 5, 20, debug=True)
    print("-" * 70)
    print()

    # Analyze which attacks were generated
    attack_analysis = {
        (4, 5): ("2 humans (95% win)", 2),
        (5, 6): ("10 humans (75% win)", 10),
        (6, 5): ("30 humans (33% win)", 30),
        (5, 4): ("50 humans (20% win)", 50),
    }

    print("Attack Analysis:")
    all_correct = True
    for (x, y), (desc, h_count) in attack_analysis.items():
        attacks = [m for m in moves if m.x_to == x and m.y_to == y]
        win_prob = calculate_battle_probability(20, h_count)
        should_attack = win_prob >= ATTACK_MIN_WIN_PROBABILITY

        if attacks:
            status = "✓" if should_attack else "⚠"
            print(f"  {status} {desc}: {len(attacks)} attack moves (P={win_prob:.0%}, threshold={ATTACK_MIN_WIN_PROBABILITY:.0%})")
            if not should_attack:
                print(f"      WARNING: Attacks generated but win prob {win_prob:.0%} < threshold {ATTACK_MIN_WIN_PROBABILITY:.0%}")
                all_correct = False
        else:
            status = "✓" if not should_attack else "✗"
            print(f"  {status} {desc}: No attacks (P={win_prob:.0%}, threshold={ATTACK_MIN_WIN_PROBABILITY:.0%})")
            if should_attack:
                print(f"      ERROR: No attacks but win prob {win_prob:.0%} >= threshold {ATTACK_MIN_WIN_PROBABILITY:.0%}!")
                all_correct = False

    print()
    print(f"Result: {'All filtering correct!' if all_correct else 'Some filtering incorrect!'}")
    print()
    return all_correct


def main():
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  ATTACK_MIN_WIN_PROBABILITY Filter Test Suite".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")
    print()

    results = []

    # Run tests
    results.append(("Battle Probability Calculation", test_battle_probability()))
    results.append(("Move Filtering", test_move_filtering()))
    results.append(("Adjacent Humans (Various Strengths)", test_adjacent_humans()))
    results.append(("Arena Scenario", test_arena_scenario()))

    # Summary
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")

    print()
    all_passed = all(r[1] for r in results)
    if all_passed:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed. Check output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
