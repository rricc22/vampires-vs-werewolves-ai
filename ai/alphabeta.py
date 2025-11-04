"""Alpha-Beta pruning search algorithm."""
from typing import List, Tuple, Optional
import time
from game_state import GameState, Move
from move_generator import generate_all_moves, apply_move_to_state
from evaluation import evaluate_state


class AlphaBetaSearch:
    """Alpha-Beta pruning search with iterative deepening."""
    
    def __init__(self, max_depth: int = 4, time_limit: float = 1.8):
        """
        Initialize Alpha-Beta search.
        
        Args:
            max_depth: Maximum search depth
            time_limit: Time limit in seconds (default 1.8s to stay under 2s)
        """
        self.max_depth = max_depth
        self.time_limit = time_limit
        self.nodes_explored = 0
        self.start_time = 0.0
        self.best_move_found: Optional[List[Move]] = None
    
    def search(self, state: GameState) -> List[Move]:
        """
        Search for the best move using Alpha-Beta with iterative deepening.
        
        Args:
            state: Current game state
            
        Returns:
            Best move combination found
        """
        self.start_time = time.time()
        self.nodes_explored = 0
        self.best_move_found = None
        
        # Generate all possible moves
        all_moves = generate_all_moves(state, for_opponent=False)
        
        if not all_moves:
            return []
        
        # Iterative deepening
        completed_depth = 0
        for depth in range(1, self.max_depth + 1):
            if self.out_of_time():
                break
            
            try:
                value, best_move = self.alpha_beta_root(state, depth, all_moves)
                if best_move:
                    self.best_move_found = best_move
                    completed_depth = depth
                    print(f"Depth {depth}: value={value:.2f}, nodes={self.nodes_explored}")
            except TimeoutError:
                break
        
        elapsed = time.time() - self.start_time
        print(f"Search complete: depth={completed_depth}, nodes={self.nodes_explored}, time={elapsed:.3f}s")
        
        return self.best_move_found if self.best_move_found else all_moves[0]
    
    def alpha_beta_root(self, state: GameState, depth: int, 
                       moves: List[List[Move]]) -> Tuple[float, Optional[List[Move]]]:
        """
        Root level alpha-beta search.
        
        Args:
            state: Current game state
            depth: Search depth
            moves: List of possible move combinations
            
        Returns:
            Tuple of (best_value, best_move)
        """
        alpha = float('-inf')
        beta = float('inf')
        best_value = float('-inf')
        best_move = None
        
        for move_combo in moves:
            if self.out_of_time():
                raise TimeoutError()
            
            new_state = apply_move_to_state(state, move_combo, for_opponent=False)
            value = self.alpha_beta(new_state, depth - 1, alpha, beta, False)
            
            if value > best_value:
                best_value = value
                best_move = move_combo
            
            alpha = max(alpha, value)
        
        return best_value, best_move
    
    def alpha_beta(self, state: GameState, depth: int, alpha: float, 
                   beta: float, maximizing: bool) -> float:
        """
        Alpha-Beta pruning algorithm.
        
        Args:
            state: Current game state
            depth: Remaining search depth
            alpha: Alpha value for pruning
            beta: Beta value for pruning
            maximizing: True if maximizing player, False if minimizing
            
        Returns:
            Evaluation value of the state
        """
        self.nodes_explored += 1
        
        if self.out_of_time():
            raise TimeoutError()
        
        # Terminal conditions
        if depth == 0 or state.is_terminal():
            return evaluate_state(state)
        
        if maximizing:
            # Our turn (maximizing)
            value = float('-inf')
            moves = generate_all_moves(state, for_opponent=False)
            
            if not moves:
                return evaluate_state(state)
            
            for move_combo in moves:
                new_state = apply_move_to_state(state, move_combo, for_opponent=False)
                value = max(value, self.alpha_beta(new_state, depth - 1, alpha, beta, False))
                alpha = max(alpha, value)
                
                if beta <= alpha:
                    break  # Beta cutoff
            
            return value
        else:
            # Opponent's turn (minimizing)
            value = float('inf')
            moves = generate_all_moves(state, for_opponent=True)
            
            if not moves:
                return evaluate_state(state)
            
            for move_combo in moves:
                new_state = apply_move_to_state(state, move_combo, for_opponent=True)
                value = min(value, self.alpha_beta(new_state, depth - 1, alpha, beta, True))
                beta = min(beta, value)
                
                if beta <= alpha:
                    break  # Alpha cutoff
            
            return value
    
    def out_of_time(self) -> bool:
        """Check if we've exceeded time limit."""
        return (time.time() - self.start_time) >= self.time_limit


def find_best_move(state: GameState, max_depth: int = 4, time_limit: float = 1.8) -> List[Move]:
    """
    Find the best move using Alpha-Beta search.
    
    Args:
        state: Current game state
        max_depth: Maximum search depth
        time_limit: Time limit in seconds
        
    Returns:
        Best move combination
    """
    searcher = AlphaBetaSearch(max_depth=max_depth, time_limit=time_limit)
    return searcher.search(state)
