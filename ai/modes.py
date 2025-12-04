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
    "SEARCH_MAX_DEPTH": 4,
    "SEARCH_TIME_LIMIT": 1.6,
    
    # Move generation
    "MIN_GROUP_SIZE": 5,
    "MAX_GROUPS_PER_TURN": 2,
    "MIN_SPLIT_SIZE": 10,
    "SPLIT_RATIOS": [1.0, 0.5],
    "ATTACK_MIN_WIN_PROBABILITY": 0.2,
}

AGGRESSIVE = {
    # Search
    "SEARCH_MAX_DEPTH": 10,
    "SEARCH_TIME_LIMIT": 2,
    
    # Move generation
    "MIN_GROUP_SIZE": 6,
    "MAX_GROUPS_PER_TURN": 3,
    "MIN_SPLIT_SIZE": 6,
    "SPLIT_RATIOS": [1.0, 2/3, 0.5],
    "ATTACK_MIN_WIN_PROBABILITY": 0.2
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
    "SEARCH_MAX_DEPTH": 4,
    "SEARCH_TIME_LIMIT": 1.6,
    
    # Move generation
    "MIN_GROUP_SIZE": 6,
    "MAX_GROUPS_PER_TURN": 3,
    "MIN_SPLIT_SIZE": 12,
    "SPLIT_RATIOS": [1.0, 0.5],
    "ATTACK_MIN_WIN_PROBABILITY": 0.65,
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
