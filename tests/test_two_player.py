#!/usr/bin/env python3
"""
Simple test to run two AI players against each other and capture logs.
This helps diagnose issues when both players connect to the server.
"""

import subprocess
import time
import threading
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
AI_SCRIPT = PROJECT_ROOT / "ai" / "ai_player.py"
SERVER_DIR = PROJECT_ROOT / "server" / "twilight-master"


def run_server(map_name="testmap.xml", timeout=30):
    """Run the game server."""
    print(f"[SERVER] Starting with {map_name}...")
    cmd = ["go", "run", ".", "-map", f"maps/{map_name}"]
    
    process = None
    try:
        process = subprocess.Popen(
            cmd,
            cwd=SERVER_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Read output
        if process.stdout:
            for line in process.stdout:
                print(f"[SERVER] {line.rstrip()}")
            
    except Exception as e:
        print(f"[SERVER] Error: {e}")
    finally:
        if process:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                process.kill()


def run_ai_player(player_id, ip="localhost", port=5555, timeout=30):
    """Run an AI player."""
    print(f"[PLAYER {player_id}] Starting...")
    
    cmd = ["python3", str(AI_SCRIPT), ip, str(port)]
    
    process = None
    try:
        process = subprocess.Popen(
            cmd,
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Read output
        stdout = process.stdout
        if stdout:
            for line in stdout:
                print(f"[PLAYER {player_id}] {line.rstrip()}")
            
    except Exception as e:
        print(f"[PLAYER {player_id}] Error: {e}")
    finally:
        if process:
            try:
                process.terminate()
                process.wait(timeout=5)
            except Exception:
                process.kill()


def test_two_player_game(map_name="testmap.xml"):
    """
    Test two AI players against each other.
    
    Args:
        map_name: Name of the map file to use
    """
    print(f"\n{'='*70}")
    print(f"Testing two-player game on {map_name}")
    print(f"{'='*70}\n")
    
    # Start server in a thread
    server_thread = threading.Thread(
        target=run_server,
        args=(map_name, 60),
        daemon=True
    )
    server_thread.start()
    
    # Wait for server to start
    print("Waiting for server to start...")
    time.sleep(2)
    
    # Start both AI players
    player1_thread = threading.Thread(
        target=run_ai_player,
        args=(1, "localhost", 5555, 60),
        daemon=True
    )
    
    player2_thread = threading.Thread(
        target=run_ai_player,
        args=(2, "localhost", 5555, 60),
        daemon=True
    )
    
    player1_thread.start()
    time.sleep(1)  # Stagger the connections
    player2_thread.start()
    
    # Wait for game to complete (max 60 seconds)
    print("\nGame in progress...")
    player1_thread.join(timeout=60)
    player2_thread.join(timeout=60)
    
    print(f"\n{'='*70}")
    print("Test complete")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    map_name = sys.argv[1] if len(sys.argv) > 1 else "testmap.xml"
    
    print("""
┌─────────────────────────────────────────────────────────────────┐
│  Integration Test: Two AI Players                              │
│  This test runs both AI players against each other to verify   │
│  correct behavior in a real game scenario.                      │
└─────────────────────────────────────────────────────────────────┘
""")
    
    test_two_player_game(map_name)
