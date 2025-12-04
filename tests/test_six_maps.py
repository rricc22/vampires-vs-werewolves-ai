#!/usr/bin/env python3
"""
Six-Map AI Test Framework

Runs AI games on 6 maps, collects statistics, and generates reports.
Supports parallel execution for faster testing.

Usage:
    python3 tests/test_six_maps.py                          # All maps, sequential
    python3 tests/test_six_maps.py --parallel 3             # Run 3 games in parallel
    python3 tests/test_six_maps.py --p1 aggressive          # Custom strategy
    python3 tests/test_six_maps.py --maps arena.xml         # Specific map
    python3 tests/test_six_maps.py --rounds 3 --output json # Multiple rounds
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
AI_SCRIPT = PROJECT_ROOT / "ai" / "ai_player.py"
SERVER_DIR = PROJECT_ROOT / "server" / "twilight-master"
MAPS_DIR = SERVER_DIR / "maps"
LOGS_DIR = PROJECT_ROOT / "LOGS"
CONFIGURE_SCRIPT = PROJECT_ROOT / "ai" / "configure.py"

# Default 6 maps
DEFAULT_MAPS = [
    "testmap.xml",
    "testmap2.xml",
    "map8.xml",
    "thetrap.xml",
    "corridor.xml",
    "arena.xml",
]

# Available presets
PRESETS = ["balanced", "aggressive", "defensive", "speed", "tactical", "experimental"]

# Base ports for parallel execution
BASE_TCP_PORT = 5555
BASE_WEB_PORT = 8080

# Thread-safe print lock
print_lock = threading.Lock()


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class GameStatistics:
    """Statistics collected from a single game."""
    map_name: str
    winner: str  # "player1", "player2", "draw", "timeout"
    total_turns: int
    duration_seconds: float
    human_conversions: int
    pvp_battles: int
    tcp_port: int = 5555
    web_port: int = 8080
    error: Optional[str] = None


@dataclass
class TestResults:
    """Results from a complete test run."""
    games: List[GameStatistics] = field(default_factory=list)
    total_duration: float = 0.0
    config: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Statistics Collector
# =============================================================================

class StatisticsCollector:
    """Parses game logs to extract statistics."""

    def __init__(self, server_log: Path):
        self.server_log = server_log

    def parse(self) -> Dict[str, Any]:
        """Parse server log and return statistics."""
        if not self.server_log.exists():
            return {
                "winner": "error",
                "total_turns": 0,
                "human_conversions": 0,
                "pvp_battles": 0,
                "error": "Server log not found",
            }

        content = self.server_log.read_text()

        # Determine winner
        if "Player 0 won" in content:
            winner = "player1"
        elif "Player 1 won" in content:
            winner = "player2"
        elif "Equality" in content:
            winner = "draw"
        else:
            winner = "draw"  # No winner found, likely timeout or max rounds

        # Count turns (movements)
        movements = re.findall(r"===== Movement (\d+)", content)
        total_turns = max([int(m) for m in movements]) + 1 if movements else 0

        # Count human conversions
        human_conversions = content.count("Human deleted")

        # Count PvP battles
        pvp_battles = content.count("Attacker won") + content.count("Defender won")

        return {
            "winner": winner,
            "total_turns": total_turns,
            "human_conversions": human_conversions,
            "pvp_battles": pvp_battles,
        }


# =============================================================================
# Game Runner
# =============================================================================

class GameRunner:
    """Manages server and player processes for a single game."""

    def __init__(
        self,
        map_name: str,
        log_dir: Path,
        p1_preset: str = "balanced",
        p2_preset: str = "balanced",
        timeout: int = 120,
        verbose: bool = True,
        tcp_port: int = 5555,
        web_port: int = 8080,
        game_id: int = 0,
    ):
        self.map_name = map_name
        self.log_dir = log_dir
        self.p1_preset = p1_preset
        self.p2_preset = p2_preset
        self.timeout = timeout
        self.verbose = verbose
        self.tcp_port = tcp_port
        self.web_port = web_port
        self.game_id = game_id

        # Log file paths (include port to avoid conflicts in parallel mode)
        map_base = map_name.replace(".xml", "")
        self.server_log = log_dir / f"{map_base}_server.log"
        self.p1_log = log_dir / f"{map_base}_player1.log"
        self.p2_log = log_dir / f"{map_base}_player2.log"

        # Process handles
        self.server_proc: Optional[subprocess.Popen] = None
        self.p1_proc: Optional[subprocess.Popen] = None
        self.p2_proc: Optional[subprocess.Popen] = None

    def log(self, message: str):
        """Print message if verbose mode enabled (thread-safe)."""
        if self.verbose:
            with print_lock:
                print(message)

    def apply_preset(self, preset: str):
        """Apply an AI configuration preset."""
        if preset not in PRESETS:
            return

        try:
            subprocess.run(
                ["python3", str(CONFIGURE_SCRIPT), "--preset", preset],
                cwd=PROJECT_ROOT,
                capture_output=True,
                timeout=5,
            )
        except Exception as e:
            self.log(f"  [{self.map_name}] Warning: Failed to apply preset {preset}: {e}")

    def start_server(self) -> bool:
        """Start the game server with custom ports."""
        map_path = f"maps/{self.map_name}"

        # Check map exists
        if not (MAPS_DIR / self.map_name).exists():
            self.log(f"  [{self.map_name}] Error: Map not found")
            return False

        try:
            self.server_proc = subprocess.Popen(
                [
                    "go", "run", ".",
                    "-map", map_path,
                    "-port", str(self.tcp_port),
                    "-webport", str(self.web_port),
                ],
                cwd=SERVER_DIR,
                stdout=open(self.server_log, "w"),
                stderr=subprocess.STDOUT,
            )
            time.sleep(2)  # Wait for server to start

            # Check server is running
            if self.server_proc.poll() is not None:
                self.log(f"  [{self.map_name}] Error: Server failed to start")
                return False

            return True
        except Exception as e:
            self.log(f"  [{self.map_name}] Error starting server: {e}")
            return False

    def start_player(self, player_id: int, preset: str, log_file: Path) -> Optional[subprocess.Popen]:
        """Start an AI player."""
        # Apply preset before starting (only for player 1 to avoid race conditions)
        if player_id == 1:
            self.apply_preset(preset)

        try:
            proc = subprocess.Popen(
                ["python3", str(AI_SCRIPT), "localhost", str(self.tcp_port)],
                cwd=PROJECT_ROOT,
                stdout=open(log_file, "w"),
                stderr=subprocess.STDOUT,
            )
            return proc
        except Exception as e:
            self.log(f"  [{self.map_name}] Error starting player {player_id}: {e}")
            return None

    def run(self) -> GameStatistics:
        """Run a complete game and return statistics."""
        self.log(f"  [{self.map_name}] Starting on port {self.tcp_port} (web: {self.web_port})...")
        start_time = time.time()

        try:
            # Start server
            if not self.start_server():
                return GameStatistics(
                    map_name=self.map_name,
                    winner="error",
                    total_turns=0,
                    duration_seconds=0,
                    human_conversions=0,
                    pvp_battles=0,
                    tcp_port=self.tcp_port,
                    web_port=self.web_port,
                    error="Server failed to start",
                )

            # Start player 1 (Vampires)
            self.p1_proc = self.start_player(1, self.p1_preset, self.p1_log)
            if not self.p1_proc:
                self.cleanup()
                return GameStatistics(
                    map_name=self.map_name,
                    winner="error",
                    total_turns=0,
                    duration_seconds=0,
                    human_conversions=0,
                    pvp_battles=0,
                    tcp_port=self.tcp_port,
                    web_port=self.web_port,
                    error="Player 1 failed to start",
                )

            time.sleep(1)  # Stagger connections

            # Start player 2 (Werewolves)
            self.p2_proc = self.start_player(2, self.p2_preset, self.p2_log)
            if not self.p2_proc:
                self.cleanup()
                return GameStatistics(
                    map_name=self.map_name,
                    winner="error",
                    total_turns=0,
                    duration_seconds=0,
                    human_conversions=0,
                    pvp_battles=0,
                    tcp_port=self.tcp_port,
                    web_port=self.web_port,
                    error="Player 2 failed to start",
                )

            # Wait for game completion
            game_start = time.time()
            while time.time() - game_start < self.timeout:
                # Check if both players have finished
                p1_done = self.p1_proc.poll() is not None
                p2_done = self.p2_proc.poll() is not None

                if p1_done and p2_done:
                    break

                time.sleep(0.5)

            duration = time.time() - start_time

            # Check for timeout
            if time.time() - game_start >= self.timeout:
                self.log(f"  [{self.map_name}] Game timed out after {self.timeout}s")

            # Parse statistics
            collector = StatisticsCollector(self.server_log)
            stats = collector.parse()

            result = GameStatistics(
                map_name=self.map_name,
                winner=stats["winner"],
                total_turns=stats["total_turns"],
                duration_seconds=round(duration, 1),
                human_conversions=stats["human_conversions"],
                pvp_battles=stats["pvp_battles"],
                tcp_port=self.tcp_port,
                web_port=self.web_port,
                error=stats.get("error"),
            )

            self.log(f"  [{self.map_name}] Done: {result.winner} in {result.total_turns} turns ({result.duration_seconds}s)")
            return result

        finally:
            self.cleanup()

    def cleanup(self):
        """Terminate all processes."""
        for proc in [self.server_proc, self.p1_proc, self.p2_proc]:
            if proc and proc.poll() is None:
                try:
                    proc.terminate()
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                except Exception:
                    pass


# =============================================================================
# Report Generator
# =============================================================================

class ReportGenerator:
    """Generates test reports in multiple formats."""

    def __init__(self, results: TestResults):
        self.results = results

    def terminal_report(self) -> str:
        """Generate terminal report."""
        lines = []
        sep = "=" * 80

        lines.append(sep)
        lines.append("                    VAMPIRES VS WEREWOLVES - TEST REPORT")
        lines.append(sep)
        lines.append("")

        # Configuration
        config = self.results.config
        lines.append("Test Configuration:")
        lines.append(f"  Maps Tested:    {len(self.results.games)}")
        lines.append(f"  Player 1:       {config.get('p1_preset', 'balanced')} (Vampires)")
        lines.append(f"  Player 2:       {config.get('p2_preset', 'balanced')} (Werewolves)")
        if config.get('parallel', 1) > 1:
            lines.append(f"  Parallel Games: {config.get('parallel')}")
        lines.append("")

        lines.append(sep)
        lines.append("                              GAME RESULTS")
        lines.append(sep)
        lines.append("")

        # Results table
        header = f"{'Map':<20} | {'Winner':<10} | {'Turns':>5} | {'Human Conv':>10} | {'PvP':>4} | {'Duration':>8}"
        lines.append(header)
        lines.append("-" * len(header))

        for game in self.results.games:
            winner_str = game.winner if game.winner != "error" else f"ERROR"
            row = f"{game.map_name:<20} | {winner_str:<10} | {game.total_turns:>5} | {game.human_conversions:>10} | {game.pvp_battles:>4} | {game.duration_seconds:>7.1f}s"
            lines.append(row)

        lines.append("")
        lines.append(sep)
        lines.append("                            SUMMARY STATISTICS")
        lines.append(sep)
        lines.append("")

        # Summary
        p1_wins = sum(1 for g in self.results.games if g.winner == "player1")
        p2_wins = sum(1 for g in self.results.games if g.winner == "player2")
        draws = sum(1 for g in self.results.games if g.winner == "draw")
        errors = sum(1 for g in self.results.games if g.winner == "error")
        total = len(self.results.games)

        lines.append("Overall Results:")
        lines.append(f"  Player 1 Wins:  {p1_wins} ({100*p1_wins/total:.1f}%)" if total else "  Player 1 Wins:  0")
        lines.append(f"  Player 2 Wins:  {p2_wins} ({100*p2_wins/total:.1f}%)" if total else "  Player 2 Wins:  0")
        lines.append(f"  Draws:          {draws} ({100*draws/total:.1f}%)" if total else "  Draws:          0")
        if errors:
            lines.append(f"  Errors:         {errors}")
        lines.append("")

        # Averages
        valid_games = [g for g in self.results.games if g.winner != "error"]
        if valid_games:
            avg_turns = sum(g.total_turns for g in valid_games) / len(valid_games)
            avg_duration = sum(g.duration_seconds for g in valid_games) / len(valid_games)
            total_human_conv = sum(g.human_conversions for g in valid_games)
            total_pvp = sum(g.pvp_battles for g in valid_games)

            lines.append("Average Game Metrics:")
            lines.append(f"  Turns per Game:       {avg_turns:.1f}")
            lines.append(f"  Duration per Game:    {avg_duration:.1f}s")
            lines.append("")
            lines.append("Battle Statistics:")
            lines.append(f"  Total Human Conv:     {total_human_conv}")
            lines.append(f"  Total PvP Battles:    {total_pvp}")

        lines.append("")
        lines.append(sep)
        lines.append(f"Total Test Duration: {self.results.total_duration:.1f}s")
        lines.append(f"Logs saved to: {config.get('log_dir', 'LOGS/')}")
        lines.append(sep)

        return "\n".join(lines)

    def json_report(self) -> str:
        """Generate JSON report."""
        data = {
            "test_run": {
                "timestamp": datetime.now().isoformat(),
                "total_duration_seconds": self.results.total_duration,
                "configuration": self.results.config,
            },
            "summary": {
                "total_games": len(self.results.games),
                "player1_wins": sum(1 for g in self.results.games if g.winner == "player1"),
                "player2_wins": sum(1 for g in self.results.games if g.winner == "player2"),
                "draws": sum(1 for g in self.results.games if g.winner == "draw"),
                "errors": sum(1 for g in self.results.games if g.winner == "error"),
            },
            "games": [asdict(g) for g in self.results.games],
        }
        return json.dumps(data, indent=2)


# =============================================================================
# Test Runner
# =============================================================================

class SixMapTestRunner:
    """Orchestrates running AI games across multiple maps."""

    def __init__(
        self,
        maps: List[str],
        p1_preset: str = "balanced",
        p2_preset: str = "balanced",
        rounds: int = 1,
        timeout: int = 120,
        verbose: bool = True,
        parallel: int = 1,
    ):
        self.maps = maps
        self.p1_preset = p1_preset
        self.p2_preset = p2_preset
        self.rounds = rounds
        self.timeout = timeout
        self.verbose = verbose
        self.parallel = parallel

        # Create timestamped log directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_dir = LOGS_DIR / f"test_run_{timestamp}"
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def log(self, message: str):
        """Print message if verbose mode enabled (thread-safe)."""
        if self.verbose:
            with print_lock:
                print(message)

    def _cleanup_all_processes(self):
        """Kill any existing server/player processes."""
        try:
            subprocess.run(["pkill", "-f", "twilight"], capture_output=True, timeout=5)
            subprocess.run(["pkill", "-f", "ai_player.py"], capture_output=True, timeout=5)
            time.sleep(1)
        except Exception:
            pass

    def run_single_game(self, map_name: str, game_id: int, map_index: int) -> GameStatistics:
        """Run a single game with assigned ports based on map index."""
        # Use map_index to ensure each map gets unique ports (never reused)
        tcp_port = BASE_TCP_PORT + map_index
        web_port = BASE_WEB_PORT + map_index

        runner = GameRunner(
            map_name=map_name,
            log_dir=self.log_dir,
            p1_preset=self.p1_preset,
            p2_preset=self.p2_preset,
            timeout=self.timeout,
            verbose=self.verbose,
            tcp_port=tcp_port,
            web_port=web_port,
            game_id=game_id,
        )

        return runner.run()

    def run(self) -> TestResults:
        """Run all configured games (sequential or parallel)."""
        results = TestResults(
            config={
                "maps": self.maps,
                "p1_preset": self.p1_preset,
                "p2_preset": self.p2_preset,
                "rounds": self.rounds,
                "timeout": self.timeout,
                "parallel": self.parallel,
                "log_dir": str(self.log_dir),
            }
        )

        start_time = time.time()

        # Build list of all games to run with their map indices
        games_to_run = []
        for round_num in range(self.rounds):
            for map_idx, map_name in enumerate(self.maps):
                games_to_run.append((map_name, map_idx))

        total_games = len(games_to_run)

        self.log(f"\nStarting test run: {total_games} games ({len(self.maps)} maps x {self.rounds} rounds)")
        self.log(f"Player 1 preset: {self.p1_preset}")
        self.log(f"Player 2 preset: {self.p2_preset}")
        if self.parallel > 1:
            self.log(f"Parallel execution: {self.parallel} concurrent games")
            self.log(f"Web UIs: http://localhost:{BASE_WEB_PORT} - http://localhost:{BASE_WEB_PORT + len(self.maps) - 1}")
        else:
            self.log(f"Web UI: http://localhost:{BASE_WEB_PORT}")
        self.log(f"Logs: {self.log_dir}")
        self.log("")

        if self.parallel > 1:
            # Clean up any existing processes before parallel execution
            self._cleanup_all_processes()
            # Parallel execution - each map gets unique ports based on map_index
            with ThreadPoolExecutor(max_workers=self.parallel) as executor:
                futures = {}
                for game_id, (map_name, map_idx) in enumerate(games_to_run):
                    future = executor.submit(self.run_single_game, map_name, game_id, map_idx)
                    futures[future] = map_name
                    # Stagger starts to avoid Go compilation race conditions
                    time.sleep(3)

                for future in as_completed(futures):
                    game_stats = future.result()
                    results.games.append(game_stats)
        else:
            # Sequential execution
            for game_id, (map_name, map_idx) in enumerate(games_to_run):
                game_stats = self.run_single_game(map_name, game_id, map_idx)
                results.games.append(game_stats)

        results.total_duration = round(time.time() - start_time, 1)
        return results


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Run AI games on 6 maps with statistics collection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 tests/test_six_maps.py                              # All 6 maps, sequential
  python3 tests/test_six_maps.py --parallel 3                 # Run 3 games at once
  python3 tests/test_six_maps.py --maps arena.xml corridor.xml
  python3 tests/test_six_maps.py --p1 aggressive --p2 defensive
  python3 tests/test_six_maps.py --rounds 3 --output json
""",
    )

    parser.add_argument(
        "--maps", "-m",
        nargs="+",
        default=DEFAULT_MAPS,
        help=f"Maps to test (default: all 6)",
    )

    parser.add_argument(
        "--p1", "--player1",
        default="balanced",
        choices=PRESETS,
        help="AI preset for Player 1/Vampires (default: balanced)",
    )

    parser.add_argument(
        "--p2", "--player2",
        default="balanced",
        choices=PRESETS,
        help="AI preset for Player 2/Werewolves (default: balanced)",
    )

    parser.add_argument(
        "--rounds", "-r",
        type=int,
        default=1,
        help="Number of games per map (default: 1)",
    )

    parser.add_argument(
        "--timeout", "-t",
        type=int,
        default=120,
        help="Timeout per game in seconds (default: 120)",
    )

    parser.add_argument(
        "--parallel", "-p",
        type=int,
        default=1,
        help="Number of games to run in parallel (default: 1 = sequential)",
    )

    parser.add_argument(
        "--output", "-o",
        choices=["terminal", "json", "all"],
        default="all",
        help="Output format (default: all)",
    )

    parser.add_argument(
        "--outfile",
        type=str,
        default=None,
        help="Output file for JSON report",
    )

    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress progress output",
    )

    args = parser.parse_args()

    # Run tests
    runner = SixMapTestRunner(
        maps=args.maps,
        p1_preset=args.p1,
        p2_preset=args.p2,
        rounds=args.rounds,
        timeout=args.timeout,
        verbose=not args.quiet,
        parallel=args.parallel,
    )

    results = runner.run()

    # Generate reports
    report_gen = ReportGenerator(results)

    if args.output in ["terminal", "all"]:
        print(report_gen.terminal_report())

    if args.output in ["json", "all"]:
        json_report = report_gen.json_report()

        # Save JSON to file
        outfile = args.outfile or (runner.log_dir / "summary.json")
        Path(outfile).write_text(json_report)

        if args.output == "json":
            print(json_report)
        else:
            print(f"\nJSON report saved to: {outfile}")


if __name__ == "__main__":
    main()
