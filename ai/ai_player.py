"""Main AI player using Alpha-Beta search."""
import time
from typing import List, Tuple
from argparse import ArgumentParser

from client import ClientSocket
from game_state import GameState, Move
from alphabeta import find_best_move


class AIPlayer:
    """AI Player for Vampires VS Werewolves game."""
    
    def __init__(self, name: str = "AlphaBetaAI"):
        self.name = name
        self.game_state = GameState()
        self.position_history = []  # Track recent positions to detect loops
        self.move_history = []  # Track recent moves
    
    def update_from_message(self, message: List):
        """Update game state from server message."""
        if not message:
            return
        
        tag = message[0]
        data = message[1]
        
        print(f"Received: {tag}")
        
        if tag == "set":
            self.game_state.rows, self.game_state.cols = data
        elif tag == "hum":
            # Will be set properly in MAP message
            pass
        elif tag == "hme":
            self.game_state.home_position = (data[0], data[1])
        elif tag == "map":
            # Initialize complete game state
            size = (self.game_state.rows, self.game_state.cols)
            humans = []  # Will be populated from map data
            home = list(self.game_state.home_position) if self.game_state.home_position else [0, 0]
            self.game_state.initialize_from_messages(size, humans, home, data)
        elif tag == "upd":
            self.game_state.update_from_upd(data)
    
    def compute_move(self) -> Tuple[int, List[Tuple[int, int, int, int, int]]]:
        """
        Compute best move using Alpha-Beta search.
        
        Returns:
            Tuple of (number_of_moves, list_of_moves)
        """
        print(f"\n{self.game_state}")
        
        # Show current group status
        our_groups = self.game_state.get_our_groups()
        opp_groups = self.game_state.get_opponent_groups()
        print(f"Our groups: {len(our_groups)}")
        for x, y, count in our_groups:
            print(f"  • {count} units at ({x},{y})")
        print(f"Opponent groups: {len(opp_groups)}")
        
        print("Computing move...")
        
        # Edge case: We have no units (eliminated)
        our_count = self.game_state.get_total_count(self.game_state.our_species) if self.game_state.our_species else 0
        if our_count == 0:
            print("Warning: No units remaining, sending empty move")
            return 0, []
        
        # Edge case: Opponent not yet initialized (shouldn't happen but be safe)
        if self.game_state.opponent_species is None:
            print("Warning: Opponent not initialized yet, using fallback")
            best_moves = self.get_fallback_move()
            move_tuples = [move.to_tuple() for move in best_moves]
            return len(move_tuples), move_tuples
        
        # Check for position repetition (detect loops)
        current_position = self._get_position_hash()
        repetition_count = self.position_history.count(current_position)
        
        if repetition_count >= 2:
            print(f"⚠️  Position repetition detected ({repetition_count+1} times)")
            print("   Breaking loop with randomized move selection...")
        
        start_time = time.time()
        
        # Use Alpha-Beta to find best move (using config settings)
        import config
        from move_generator import generate_all_moves
        import random
        
        best_moves = find_best_move(
            self.game_state, 
            max_depth=config.SEARCH_MAX_DEPTH, 
            time_limit=config.SEARCH_TIME_LIMIT
        )
        
        # If we're in a repetition loop, pick a different move
        if repetition_count >= 2 and best_moves:
            # Generate all possible moves
            all_moves = generate_all_moves(self.game_state, for_opponent=False)
            if len(all_moves) > 1:
                # Filter out the best move (which causes loop)
                alternative_moves = [m for m in all_moves if m != best_moves]
                if alternative_moves:
                    best_moves = random.choice(alternative_moves)
                    print("   → Selected alternative move to break loop")
        
        # Track position history (keep last 10)
        self.position_history.append(current_position)
        if len(self.position_history) > 10:
            self.position_history.pop(0)
        
        elapsed = time.time() - start_time
        print(f"Move computed in {elapsed:.3f}s")
        
        if not best_moves:
            # No valid moves found, try to make at least one move
            print("Warning: No moves found by Alpha-Beta, using fallback")
            best_moves = self.get_fallback_move()
        
        # Convert to protocol format
        move_tuples = [move.to_tuple() for move in best_moves]
        
        # Show what we're doing
        if len(best_moves) == 1:
            move = best_moves[0]
            print(f"→ Single-group move: {move.count} units from ({move.x_from},{move.y_from}) to ({move.x_to},{move.y_to})")
        else:
            print(f"→ Multi-group move! {len(best_moves)} groups acting simultaneously:")
            for i, move in enumerate(best_moves, 1):
                print(f"  {i}. {move.count} units from ({move.x_from},{move.y_from}) to ({move.x_to},{move.y_to})")
        
        return len(move_tuples), move_tuples
    
    def _get_position_hash(self) -> str:
        """
        Generate a hash of current position for loop detection.
        Uses positions of our groups only (opponent included in evaluation).
        """
        our_groups = self.game_state.get_our_groups()
        # Sort to ensure consistent hash
        sorted_groups = sorted(our_groups, key=lambda g: (g[0], g[1]))
        # Create simple hash: "x1,y1,c1;x2,y2,c2;..."
        return ";".join(f"{x},{y},{count}" for x, y, count in sorted_groups)
    
    def get_fallback_move(self) -> List[Move]:
        """Get a simple fallback move if Alpha-Beta fails."""
        groups = self.game_state.get_our_groups()
        
        if not groups:
            return []
        
        # Just move from the largest group to an adjacent cell
        groups.sort(key=lambda g: g[2], reverse=True)
        x, y, count = groups[0]
        
        # Try to move to an adjacent cell
        for dx, dy in GameState.DIRECTIONS:
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < self.game_state.rows and 0 <= new_y < self.game_state.cols:
                return [Move(x, y, new_x, new_y, max(1, count // 2))]
        
        return []


def play_game(args):
    """Main game loop."""
    player = AIPlayer(name="AlphaBetaAI_v1")
    client_socket = ClientSocket(args.ip, args.port)
    
    # Send name
    client_socket.send_nme(player.name)
    print(f"Connected as {player.name}")
    
    # Receive initial messages (SET, HUM, HME, MAP)
    for _ in range(4):
        message = client_socket.get_message()
        player.update_from_message(message)
    
    print("Game initialized, starting main loop...")
    
    # Main game loop
    turn = 0
    while True:
        message = client_socket.get_message()
        
        if not message:
            print("No message received, ending game")
            break
        
        player.update_from_message(message)
        
        if message[0] == "upd":
            turn += 1
            print(f"\n{'='*60}")
            print(f"Turn {turn}")
            print(f"{'='*60}")
            
            try:
                nb_moves, moves = player.compute_move()
                client_socket.send_mov(nb_moves, moves)
            except Exception as e:
                print(f"Error computing move: {e}")
                import traceback
                traceback.print_exc()
                # Try fallback
                fallback = player.get_fallback_move()
                if fallback:
                    move_tuples = [m.to_tuple() for m in fallback]
                    client_socket.send_mov(len(move_tuples), move_tuples)
        
        elif message[0] == "end":
            print("\nGame ended!")
            break


if __name__ == "__main__":
    parser = ArgumentParser(description="Vampires VS Werewolves AI Player")
    parser.add_argument("ip", nargs="?", default="localhost", help="Server IP address")
    parser.add_argument("port", nargs="?", default=5555, type=int, help="Server port")
    
    args = parser.parse_args()
    
    try:
        play_game(args)
    except KeyboardInterrupt:
        print("\nGame interrupted by user")
    except Exception as e:
        # Import here to avoid circular dependency
        from client import ByeException, EndException
        
        # Don't print error for expected game-ending exceptions
        if isinstance(e, (ByeException, EndException)):
            print("\nGame ended normally")
        else:
            print(f"Fatal error: {e}")
            import traceback
            traceback.print_exc()
