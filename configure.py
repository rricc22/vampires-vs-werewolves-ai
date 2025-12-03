#!/usr/bin/env python3
"""
Interactive Configuration Tool for Vampires vs Werewolves AI
=============================================================

Easy-to-use CLI for managing AI configuration.

Usage:
    python3 configure.py                    # Interactive menu
    python3 configure.py --list             # List all presets
    python3 configure.py --preset aggressive # Apply a preset
    python3 configure.py --show             # Show current config
    python3 configure.py --compare balanced aggressive  # Compare presets
    python3 configure.py --reset            # Reset to default
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any

# Add ai directory to path
sys.path.insert(0, str(Path(__file__).parent / "ai"))

import config
from config_presets import PRESETS, get_preset, list_presets, compare_presets


class ConfigurationManager:
    """Manages AI configuration interactively."""
    
    def __init__(self):
        self.config_path = Path(__file__).parent / "ai" / "config.py"
        self.current_config = self.load_current_config()
    
    def load_current_config(self) -> Dict[str, Any]:
        """Load current configuration values."""
        import importlib
        importlib.reload(config)
        
        cfg = {}
        for key in dir(config):
            if key.isupper() and not key.startswith('_'):
                cfg[key] = getattr(config, key)
        return cfg
    
    def show_current_config(self):
        """Display current configuration."""
        print("\n" + "="*70)
        print("CURRENT AI CONFIGURATION")
        print("="*70 + "\n")
        
        categories = {
            "Server": ["SERVER_IP", "SERVER_PORT"],
            "Search": ["SEARCH_MAX_DEPTH", "SEARCH_TIME_LIMIT", "SEARCH_ITERATIVE_DEEPENING"],
            "Move Generation": ["MIN_GROUP_SIZE", "MAX_GROUPS_PER_TURN", "MIN_SPLIT_SIZE", 
                               "SPLIT_RATIOS", "ATTACK_MIN_WIN_PROBABILITY"],
            "Evaluation - Material": ["WEIGHT_MATERIAL", "BONUS_ONE_GROUP", "PENALTY_TWO_GROUPS",
                                     "PENALTY_THREE_GROUPS", "PENALTY_EXCESS_GROUPS"],
            "Evaluation - Groups": ["PENALTY_SMALL_GROUP", "SMALL_GROUP_THRESHOLD"],
            "Evaluation - Tactical": ["WEIGHT_HUMAN_PROXIMITY", "WEIGHT_CENTER_CONTROL",
                                     "WEIGHT_THREAT_ASSESSMENT", "PENALTY_SPLIT_NEAR_ENEMY"],
        }
        
        for category, keys in categories.items():
            print(f"📁 {category}")
            print("-" * 70)
            for key in keys:
                value = self.current_config.get(key, "N/A")
                print(f"  {key:<35} = {value}")
            print()
    
    def apply_preset(self, preset_name: str):
        """Apply a preset configuration."""
        try:
            preset = get_preset(preset_name)
        except ValueError as e:
            print(f"❌ Error: {e}")
            return False
        
        print(f"\n{'='*70}")
        print(f"Applying Preset: {preset['name']}")
        print(f"{'='*70}")
        print(f"Description: {preset['description']}\n")
        
        # Show what will change
        changes = []
        for key, new_value in preset['config'].items():
            old_value = self.current_config.get(key)
            if old_value != new_value:
                changes.append((key, old_value, new_value))
        
        if not changes:
            print("✅ Configuration already matches this preset.")
            return True
        
        print("The following parameters will be changed:\n")
        print(f"{'Parameter':<35} {'Current':<20} {'New':<20}")
        print("-" * 70)
        for key, old, new in changes:
            print(f"{key:<35} {str(old):<20} → {str(new):<20}")
        
        print(f"\n{len(changes)} parameter(s) will be updated.")
        
        # Confirm
        confirm = input("\nApply these changes? (yes/no): ").strip().lower()
        if confirm not in ['yes', 'y']:
            print("❌ Cancelled.")
            return False
        
        # Apply changes
        self.write_config_changes(preset['config'])
        print(f"\n✅ Successfully applied '{preset['name']}' preset!")
        print(f"📝 Configuration saved to: {self.config_path}")
        return True
    
    def write_config_changes(self, new_values: Dict[str, Any]):
        """Write configuration changes to config.py."""
        # Read current file
        with open(self.config_path, 'r') as f:
            lines = f.readlines()
        
        # Update values
        new_lines = []
        for line in lines:
            updated = False
            for key, value in new_values.items():
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
        with open(self.config_path, 'w') as f:
            f.writelines(new_lines)
    
    def reset_to_default(self):
        """Reset configuration to balanced preset."""
        print("\n⚠️  This will reset all configuration to the default 'Balanced' preset.")
        confirm = input("Continue? (yes/no): ").strip().lower()
        if confirm not in ['yes', 'y']:
            print("❌ Cancelled.")
            return
        
        self.apply_preset("balanced")
    
    def interactive_menu(self):
        """Display interactive menu."""
        while True:
            print("\n" + "="*70)
            print("🎮 VAMPIRES VS WEREWOLVES - AI CONFIGURATION MANAGER")
            print("="*70)
            print("\n1. 📋 List available presets")
            print("2. ✨ Apply a preset")
            print("3. 📊 Show current configuration")
            print("4. 🔄 Compare presets")
            print("5. ↩️  Reset to default")
            print("6. 🚪 Exit")
            
            choice = input("\nSelect an option (1-6): ").strip()
            
            if choice == "1":
                list_presets()
            
            elif choice == "2":
                print("\nAvailable presets:")
                for i, key in enumerate(PRESETS.keys(), 1):
                    preset = PRESETS[key]
                    print(f"  {i}. {preset['name']} - {preset['description']}")
                
                preset_choice = input("\nEnter preset name or number: ").strip().lower()
                
                # Handle number input
                if preset_choice.isdigit():
                    idx = int(preset_choice) - 1
                    if 0 <= idx < len(PRESETS):
                        preset_choice = list(PRESETS.keys())[idx]
                
                self.apply_preset(preset_choice)
            
            elif choice == "3":
                self.show_current_config()
            
            elif choice == "4":
                preset_list = list(PRESETS.keys())
                print("\nAvailable presets:", ", ".join(preset_list))
                p1 = input("First preset: ").strip().lower()
                p2 = input("Second preset: ").strip().lower()
                
                try:
                    compare_presets(p1, p2)
                except ValueError as e:
                    print(f"❌ Error: {e}")
            
            elif choice == "5":
                self.reset_to_default()
            
            elif choice == "6":
                print("\n👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid choice. Please select 1-6.")


def main():
    """Main entry point."""
    manager = ConfigurationManager()
    
    # Parse command line arguments
    if len(sys.argv) == 1:
        # No arguments - interactive mode
        manager.interactive_menu()
    
    elif sys.argv[1] == "--list":
        list_presets()
    
    elif sys.argv[1] == "--show":
        manager.show_current_config()
    
    elif sys.argv[1] == "--preset" and len(sys.argv) == 3:
        preset_name = sys.argv[2]
        manager.apply_preset(preset_name)
    
    elif sys.argv[1] == "--compare" and len(sys.argv) == 4:
        try:
            compare_presets(sys.argv[2], sys.argv[3])
        except ValueError as e:
            print(f"❌ Error: {e}")
    
    elif sys.argv[1] == "--reset":
        manager.reset_to_default()
    
    elif sys.argv[1] in ["-h", "--help"]:
        print(__doc__)
    
    else:
        print("❌ Invalid arguments. Use --help for usage information.")
        sys.exit(1)


if __name__ == "__main__":
    main()
