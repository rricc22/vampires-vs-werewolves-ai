# Configuration Quick Start

## 🚀 Fastest Way to Configure

```bash
# Interactive menu (easiest!)
python3 configure.py
```

## 📋 Preset Cheat Sheet

| Preset       | When to Use                           | Key Features                    |
|--------------|---------------------------------------|---------------------------------|
| **balanced** | General play, learning                | Default, well-rounded           |
| **aggressive**| Fast expansion, risky play           | Deep search, 50% attacks        |
| **defensive**| Safe play, avoid losses              | 80% attacks, never splits       |
| **speed**    | Testing, slow hardware                | Shallow search, fast decisions  |
| **tactical** | Multi-group coordination              | 3-group moves, territorial      |
| **experimental**| Testing new ideas                  | Sandbox configuration           |

## ⚡ Quick Commands

```bash
# Apply a preset
python3 configure.py --preset aggressive

# See all presets
python3 configure.py --list

# Compare presets
python3 configure.py --compare balanced aggressive

# Show current settings
python3 configure.py --show

# Reset to default
python3 configure.py --reset
```

## 🎯 Common Tweaks

### Want AI to be more aggressive?
```bash
python3 configure.py --preset aggressive
```

### Want AI to play it safe?
```bash
python3 configure.py --preset defensive
```

### Need faster moves?
```bash
python3 configure.py --preset speed
```

### Manual tuning?
Edit `ai/config.py` directly - all settings are documented!

## 📖 Full Documentation

See [CONFIGURATION.md](CONFIGURATION.md) for:
- Complete parameter reference
- Tuning guide
- Custom preset creation
- Performance guidelines
- Troubleshooting tips

## ✅ Test Your Changes

```bash
# Run tests
python3 tests/test_ai.py

# Play a game
bash play_game.sh
```

Watch at: http://localhost:8080
