# config.py

# Server configuration
SERVER_IP = "localhost"
SERVER_PORT = 5555

# Move generation configuration
MIN_GROUP_SIZE = 5  # Don't create groups smaller than this (increased from 3)
MAX_GROUPS_PER_TURN = 2  # Maximum number of groups that can move simultaneously
MIN_SPLIT_SIZE = 10  # Minimum size before allowing splits (increased from 5)

# Split ratios to try (fewer options = less fragmentation)
# Allow some strategic splitting: all or half
# This allows creating 2 groups maximum from one split
SPLIT_RATIOS = [1.0, 0.5]  # Move ALL or HALF (was [1.0] which was too restrictive)

# Group evaluation thresholds  
IDEAL_MIN_GROUPS = 1  # 1-2 groups is actually best
IDEAL_MAX_GROUPS = 2  # 2 groups max is ideal
EXCESSIVE_GROUPS_THRESHOLD = 3  # More than 2 is penalized (was 4)
SMALL_GROUP_THRESHOLD = 10  # Groups smaller than this are penalized (was 5)
