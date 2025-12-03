"""
Configuration Presets for Different Play Styles
================================================

Pre-tuned configurations for various strategies and scenarios.
Use configure.py to apply these presets, or manually copy values to config.py.
"""

# Base/Default configuration (current balanced strategy)
BALANCED = {
    "name": "Balanced",
    "description": "Well-rounded strategy with concentration and tactical flexibility",
    "config": {
        # Search
        "SEARCH_MAX_DEPTH": 4,
        "SEARCH_TIME_LIMIT": 1.8,
        
        # Move generation
        "MIN_GROUP_SIZE": 5,
        "MAX_GROUPS_PER_TURN": 2,
        "MIN_SPLIT_SIZE": 10,
        "SPLIT_RATIOS": [1.0, 0.5],
        "ATTACK_MIN_WIN_PROBABILITY": 0.7,
        
        # Evaluation weights
        "WEIGHT_MATERIAL": 100,
        "BONUS_ONE_GROUP": 100,
        "PENALTY_TWO_GROUPS": 0,
        "PENALTY_THREE_GROUPS": 200,
        "PENALTY_EXCESS_GROUPS": 500,
        "PENALTY_SMALL_GROUP": 100,
        "SMALL_GROUP_THRESHOLD": 10,
        "WEIGHT_HUMAN_PROXIMITY": 40,
        "WEIGHT_CENTER_CONTROL": 2,
        "WEIGHT_THREAT_ASSESSMENT": 20,
        "PENALTY_SPLIT_NEAR_ENEMY": 20,
    }
}


# Aggressive configuration - take risks, expand quickly
AGGRESSIVE = {
    "name": "Aggressive",
    "description": "Deep search, risky attacks, multi-group coordination for fast expansion",
    "config": {
        # Search - deeper to evaluate risky plays
        "SEARCH_MAX_DEPTH": 5,
        "SEARCH_TIME_LIMIT": 1.8,
        
        # Move generation - more flexibility
        "MIN_GROUP_SIZE": 3,
        "MAX_GROUPS_PER_TURN": 3,
        "MIN_SPLIT_SIZE": 8,
        "SPLIT_RATIOS": [1.0, 2/3, 0.5],
        "ATTACK_MIN_WIN_PROBABILITY": 0.5,  # 50% chance is acceptable
        
        # Evaluation - encourages expansion over concentration
        "WEIGHT_MATERIAL": 150,  # Prioritize growing army
        "BONUS_ONE_GROUP": 50,   # Less bonus for concentration
        "PENALTY_TWO_GROUPS": 0,
        "PENALTY_THREE_GROUPS": 100,  # Allow more groups
        "PENALTY_EXCESS_GROUPS": 300,
        "PENALTY_SMALL_GROUP": 50,
        "SMALL_GROUP_THRESHOLD": 8,
        "WEIGHT_HUMAN_PROXIMITY": 60,  # Very aggressive human hunting
        "WEIGHT_CENTER_CONTROL": 5,    # More territorial
        "WEIGHT_THREAT_ASSESSMENT": 30,
        "PENALTY_SPLIT_NEAR_ENEMY": 10,  # Less concerned about splitting near enemy
    }
}


# Defensive configuration - prioritize survival and concentration
DEFENSIVE = {
    "name": "Defensive",
    "description": "Strong concentration, safe attacks only, avoid fragmentation at all costs",
    "config": {
        # Search
        "SEARCH_MAX_DEPTH": 4,
        "SEARCH_TIME_LIMIT": 1.8,
        
        # Move generation - maximum concentration
        "MIN_GROUP_SIZE": 8,
        "MAX_GROUPS_PER_TURN": 2,
        "MIN_SPLIT_SIZE": 15,
        "SPLIT_RATIOS": [1.0],  # Never split
        "ATTACK_MIN_WIN_PROBABILITY": 0.8,  # Only very safe attacks
        
        # Evaluation - extreme concentration bonuses
        "WEIGHT_MATERIAL": 80,   # Material less important than safety
        "BONUS_ONE_GROUP": 200,  # Huge bonus for single group
        "PENALTY_TWO_GROUPS": 50,  # Even 2 groups is discouraged
        "PENALTY_THREE_GROUPS": 500,
        "PENALTY_EXCESS_GROUPS": 1000,  # Catastrophic
        "PENALTY_SMALL_GROUP": 150,
        "SMALL_GROUP_THRESHOLD": 12,
        "WEIGHT_HUMAN_PROXIMITY": 30,  # Less aggressive
        "WEIGHT_CENTER_CONTROL": 1,
        "WEIGHT_THREAT_ASSESSMENT": 15,
        "PENALTY_SPLIT_NEAR_ENEMY": 40,  # Never split when threatened
    }
}


# Speed configuration - fast decisions, simpler strategy
SPEED = {
    "name": "Speed",
    "description": "Quick moves with shallow search, good for testing or slow hardware",
    "config": {
        # Search - minimal depth
        "SEARCH_MAX_DEPTH": 3,
        "SEARCH_TIME_LIMIT": 1.0,
        
        # Move generation - simple moves only
        "MIN_GROUP_SIZE": 5,
        "MAX_GROUPS_PER_TURN": 1,  # Single group only
        "MIN_SPLIT_SIZE": 20,
        "SPLIT_RATIOS": [1.0],  # No splits
        "ATTACK_MIN_WIN_PROBABILITY": 0.7,
        
        # Evaluation - simplified
        "WEIGHT_MATERIAL": 100,
        "BONUS_ONE_GROUP": 100,
        "PENALTY_TWO_GROUPS": 0,
        "PENALTY_THREE_GROUPS": 200,
        "PENALTY_EXCESS_GROUPS": 500,
        "PENALTY_SMALL_GROUP": 100,
        "SMALL_GROUP_THRESHOLD": 10,
        "WEIGHT_HUMAN_PROXIMITY": 40,
        "WEIGHT_CENTER_CONTROL": 2,
        "WEIGHT_THREAT_ASSESSMENT": 20,
        "PENALTY_SPLIT_NEAR_ENEMY": 20,
    }
}


# Tactical configuration - multi-group coordination expert
TACTICAL = {
    "name": "Tactical",
    "description": "Master of multi-group coordination and strategic positioning",
    "config": {
        # Search
        "SEARCH_MAX_DEPTH": 4,
        "SEARCH_TIME_LIMIT": 1.8,
        
        # Move generation - designed for coordination
        "MIN_GROUP_SIZE": 6,
        "MAX_GROUPS_PER_TURN": 3,
        "MIN_SPLIT_SIZE": 12,
        "SPLIT_RATIOS": [1.0, 0.5],
        "ATTACK_MIN_WIN_PROBABILITY": 0.65,
        
        # Evaluation - balanced but tactical
        "WEIGHT_MATERIAL": 100,
        "BONUS_ONE_GROUP": 80,   # Less emphasis on single group
        "PENALTY_TWO_GROUPS": -20,  # Actually BONUS for 2 groups
        "PENALTY_THREE_GROUPS": 50,  # Much less penalty for 3 groups
        "PENALTY_EXCESS_GROUPS": 400,
        "PENALTY_SMALL_GROUP": 120,
        "SMALL_GROUP_THRESHOLD": 10,
        "WEIGHT_HUMAN_PROXIMITY": 45,
        "WEIGHT_CENTER_CONTROL": 8,   # Strong territorial control
        "WEIGHT_THREAT_ASSESSMENT": 25,
        "PENALTY_SPLIT_NEAR_ENEMY": 15,
    }
}


# Experimental configuration - for testing new ideas
EXPERIMENTAL = {
    "name": "Experimental",
    "description": "Testing ground for new strategies and parameters",
    "config": {
        # Search
        "SEARCH_MAX_DEPTH": 4,
        "SEARCH_TIME_LIMIT": 1.8,
        
        # Move generation
        "MIN_GROUP_SIZE": 5,
        "MAX_GROUPS_PER_TURN": 2,
        "MIN_SPLIT_SIZE": 10,
        "SPLIT_RATIOS": [1.0, 0.6, 0.4],  # More split options
        "ATTACK_MIN_WIN_PROBABILITY": 0.6,
        
        # Evaluation - experimental weights
        "WEIGHT_MATERIAL": 120,
        "BONUS_ONE_GROUP": 150,
        "PENALTY_TWO_GROUPS": -10,  # Small bonus for 2 groups
        "PENALTY_THREE_GROUPS": 150,
        "PENALTY_EXCESS_GROUPS": 400,
        "PENALTY_SMALL_GROUP": 80,
        "SMALL_GROUP_THRESHOLD": 12,
        "WEIGHT_HUMAN_PROXIMITY": 50,
        "WEIGHT_CENTER_CONTROL": 10,  # Very territorial
        "WEIGHT_THREAT_ASSESSMENT": 25,
        "PENALTY_SPLIT_NEAR_ENEMY": 30,
    }
}


# Map all presets for easy access
PRESETS = {
    "balanced": BALANCED,
    "aggressive": AGGRESSIVE,
    "defensive": DEFENSIVE,
    "speed": SPEED,
    "tactical": TACTICAL,
    "experimental": EXPERIMENTAL,
}


def get_preset(name: str) -> dict:
    """Get a preset configuration by name."""
    name_lower = name.lower()
    if name_lower not in PRESETS:
        available = ", ".join(PRESETS.keys())
        raise ValueError(f"Unknown preset '{name}'. Available: {available}")
    return PRESETS[name_lower]


def list_presets():
    """Print all available presets with descriptions."""
    print("\n" + "="*60)
    print("Available Configuration Presets")
    print("="*60 + "\n")
    
    for key, preset in PRESETS.items():
        print(f"📋 {preset['name'].upper()}")
        print(f"   {preset['description']}")
        print(f"   Command: python3 configure.py --preset {key}")
        print()


def compare_presets(preset1: str, preset2: str):
    """Compare two presets side-by-side."""
    p1 = get_preset(preset1)
    p2 = get_preset(preset2)
    
    print(f"\n{'='*80}")
    print(f"Comparing: {p1['name']} vs {p2['name']}")
    print(f"{'='*80}\n")
    
    all_keys = set(p1['config'].keys()) | set(p2['config'].keys())
    
    print(f"{'Parameter':<35} {p1['name']:<20} {p2['name']:<20}")
    print("-" * 80)
    
    for key in sorted(all_keys):
        v1 = p1['config'].get(key, "N/A")
        v2 = p2['config'].get(key, "N/A")
        
        # Highlight differences
        marker = "⚠️ " if v1 != v2 else "  "
        print(f"{marker}{key:<35} {str(v1):<20} {str(v2):<20}")


if __name__ == "__main__":
    # Demo: list all presets
    list_presets()
    
    print("\nExample comparison:")
    print("-" * 60)
    compare_presets("balanced", "aggressive")
