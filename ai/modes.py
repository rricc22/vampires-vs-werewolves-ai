"""
AI Configuration Modes
======================

Simple configuration system with pre-defined modes for different play styles.
Edit the values below to customize each mode.

Usage from code:
    import modes
    modes.apply("aggressive")
"""

# ============================================================
# MODE DEFINITIONS
# ============================================================

BALANCED = {
    # Search
    "SEARCH_MAX_DEPTH": 4,  # Optimal depth ✓
    "SEARCH_TIME_LIMIT": 1.7,  # Slightly higher for better search ✓

    # Move generation
    "MIN_GROUP_SIZE": 5,  # Good flexibility ✓
    "MAX_GROUPS_PER_TURN": 2,  # Optimal tactical coordination ✓
    "MIN_SPLIT_SIZE": 10,  # Prevents excessive fragmentation ✓
    "SPLIT_RATIOS": [1.0, 0.5],  # Strategic splits allowed ✓
    "ATTACK_MIN_WIN_PROBABILITY": 0.65,  # Well-balanced risk/reward ✓
}

AGGRESSIVE = {
    # Search
    "SEARCH_MAX_DEPTH": 4,  # 10 would timeout, keep at 4 ✓
    "SEARCH_TIME_LIMIT": 1.7,  # Must be under 2.0 for server ✓

    # Move generation
    "MIN_GROUP_SIZE": 5,  # Allow smaller groups for more flexibility ✓
    "MAX_GROUPS_PER_TURN": 2,  # 3 creates too much branching ✓
    "MIN_SPLIT_SIZE": 8,  # Lower to allow more tactical splits ✓
    "SPLIT_RATIOS": [1.0, 0.5],
    "ATTACK_MIN_WIN_PROBABILITY": 0.4  # More aggressive but not reckless ✓
}

DEFENSIVE = {
    # Search
    "SEARCH_MAX_DEPTH": 4,
    "SEARCH_TIME_LIMIT": 1.6,
    
    # Move generation
    "MIN_GROUP_SIZE": 8,
    "MAX_GROUPS_PER_TURN": 2,
    "MIN_SPLIT_SIZE": 15,
    "SPLIT_RATIOS": [1.0],  # Never split
    "ATTACK_MIN_WIN_PROBABILITY": 0.8,
}

SPEED = {
    # Search
    "SEARCH_MAX_DEPTH": 3,
    "SEARCH_TIME_LIMIT": 1.0,
    
    # Move generation
    "MIN_GROUP_SIZE": 5,
    "MAX_GROUPS_PER_TURN": 1,
    "MIN_SPLIT_SIZE": 20,
    "SPLIT_RATIOS": [1.0],  # No splits
    "ATTACK_MIN_WIN_PROBABILITY": 0.7,
}

TACTICAL = {
    # Search
    "SEARCH_MAX_DEPTH": 4,  # Standard depth ✓
    "SEARCH_TIME_LIMIT": 1.7,  # More time for complex calculations ✓

    # Move generation
    "MIN_GROUP_SIZE": 5,  # More tactical flexibility ✓
    "MAX_GROUPS_PER_TURN": 2,  # Optimal (3 is too slow) ✓
    "MIN_SPLIT_SIZE": 10,  # Allow tactical positioning ✓
    "SPLIT_RATIOS": [1.0, 0.5],  # Core tactical splits ✓
    "ATTACK_MIN_WIN_PROBABILITY": 0.65,  # Balanced aggression ✓
}

EXPERIMENTAL = {
    # Search
    "SEARCH_MAX_DEPTH": 4,
    "SEARCH_TIME_LIMIT": 1.6,
    
    # Move generation
    "MIN_GROUP_SIZE": 5,
    "MAX_GROUPS_PER_TURN": 2,
    "MIN_SPLIT_SIZE": 10,
    "SPLIT_RATIOS": [1.0, 0.6, 0.4],
    "ATTACK_MIN_WIN_PROBABILITY": 0.6,
}

# ============================================================
# MODE REGISTRY
# ============================================================

MODES = {
    "balanced": BALANCED,
    "aggressive": AGGRESSIVE,
    "defensive": DEFENSIVE,
    "speed": SPEED,
    "tactical": TACTICAL,
    "experimental": EXPERIMENTAL,
}

DESCRIPTIONS = {
    "balanced": "Default, well-rounded strategy",
    "aggressive": "Deep search, risky attacks, fast expansion",
    "defensive": "Safe attacks, strong concentration",
    "speed": "Fast decisions, shallow search",
    "tactical": "Multi-group coordination master",
    "experimental": "Testing new strategies",
}

# ============================================================
# FUNCTIONS
# ============================================================

def apply(mode_name: str):
    """
    Apply a mode by updating config.py values.
    
    Args:
        mode_name: Name of the mode to apply (e.g., "aggressive")
    
    Raises:
        ValueError: If mode_name is not recognized
    """
    mode_name = mode_name.lower()
    
    if mode_name not in MODES:
        available = ", ".join(MODES.keys())
        raise ValueError(f"Unknown mode '{mode_name}'. Available: {available}")
    
    mode = MODES[mode_name]
    
    # Import config to update it
    from pathlib import Path
    config_path = Path(__file__).parent / "config.py"
    
    # Read current config
    with open(config_path, 'r') as f:
        lines = f.readlines()
    
    # Update values
    new_lines = []
    for line in lines:
        updated = False
        for key, value in mode.items():
            if line.strip().startswith(f"{key} ="):
                # Format value properly
                if isinstance(value, str):
                    formatted_value = f'"{value}"'
                elif isinstance(value, list):
                    formatted_value = str(value)
                else:
                    formatted_value = str(value)
                
                new_lines.append(f"{key} = {formatted_value}\n")
                updated = True
                break
        
        if not updated:
            new_lines.append(line)
    
    # Write back
    with open(config_path, 'w') as f:
        f.writelines(new_lines)


def list_modes():
    """Print all available modes."""
    print("\nAvailable AI Modes:")
    print("=" * 60)
    for name, desc in DESCRIPTIONS.items():
        print(f"  {name:<15} - {desc}")
    print()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        list_modes()
        print("Usage: python3 modes.py <mode_name>")
        print("Example: python3 modes.py aggressive")
        sys.exit(1)
    
    mode = sys.argv[1]
    try:
        apply(mode)
        print(f"✓ Applied mode: {mode}")
    except ValueError as e:
        print(f"✗ Error: {e}")
        sys.exit(1)
