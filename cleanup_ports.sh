#!/bin/bash
# Cleanup script for Vampires vs Werewolves game processes
# Run this if tests fail to cleanup properly

echo "🧹 Cleaning up game processes..."

# Kill game processes
pkill -9 -f "twilight" 2>/dev/null
pkill -9 -f "ai_player.py" 2>/dev/null

# Kill processes on ports
echo "🔌 Freeing ports 5555-5565 and 8080-8090..."
for port in {5555..5565}; do
    fuser -k ${port}/tcp 2>/dev/null
done

for port in {8080..8090}; do
    fuser -k ${port}/tcp 2>/dev/null
done

sleep 2

# Verify cleanup
if ps aux | grep -E "(twilight|ai_player)" | grep -v grep > /dev/null; then
    echo "⚠️  Warning: Some processes still running:"
    ps aux | grep -E "(twilight|ai_player)" | grep -v grep
else
    echo "✅ All processes cleaned up"
fi

# Check ports
if ss -tln 2>/dev/null | grep -E ":(5555|8080)" > /dev/null; then
    echo "⚠️  Warning: Some ports still in use:"
    ss -tln | grep -E ":(5555|8080)"
else
    echo "✅ All ports are free"
fi

echo "✨ Cleanup complete!"
