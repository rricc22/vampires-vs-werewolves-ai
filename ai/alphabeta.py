"""Alpha-Beta pruning search algorithm with move ordering."""
from typing import List, Tuple, Optional
import time
from game_state import GameState, Move
from move_generator import generate_all_moves, apply_move_to_state
from evaluation import evaluate_state


def score_move_combo(state: GameState, move_combo: List[Move], for_opponent: bool = False) -> int:
    """
    Score a move combination for move ordering (higher = more promising).

    Priorities:
    - Captures/attacks on enemies: +1000
    - Conversions (attacking humans): +500 (+300 if guaranteed)
    - Moves toward CAPTURABLE human villages: +200
    - Moves toward any humans: +50
    - Larger moves: +count

    Args:
        state: Current game state
        move_combo: List of moves to score
        for_opponent: If True, score for opponent

    Returns:
        Score for move ordering (higher = try first)
    """
    score = 0
    species = state.opponent_species if for_opponent else state.our_species
    enemy_species = state.our_species if for_opponent else state.opponent_species

    # Collect all human positions for proximity scoring
    human_cells = []
    for i in range(state.rows):
        for j in range(state.cols):
            if state.board[i][j].humans > 0:
                human_cells.append((i, j, state.board[i][j].humans))

    for move in move_combo:
        target_cell = state.board[move.x_to][move.y_to]

        # Attacking enemies (highest priority)
        enemy_count = target_cell.get_count(enemy_species) if enemy_species else 0
        if enemy_count > 0:
            score += 1000
            # Bonus for favorable odds
            if move.count >= enemy_count * 1.5:
                score += 500  # Guaranteed kill

        # Converting humans (high priority)
        elif target_cell.humans > 0:
            score += 500
            # Bonus for guaranteed conversion
            if move.count >= target_cell.humans:
                score += 300

        # Movement toward capturable human villages (key improvement!)
        # Prioritize moving toward villages we can actually capture
        elif human_cells:
            best_capturable_improvement = 0
            best_any_improvement = 0

            for hx, hy, h_count in human_cells:
                dist_before = abs(move.x_from - hx) + abs(move.y_from - hy)
                dist_after = abs(move.x_to - hx) + abs(move.y_to - hy)
                improvement = dist_before - dist_after

                if improvement > 0:
                    # Check if this village is capturable with our force
                    if move.count >= h_count:
                        # Guaranteed capture - high priority!
                        best_capturable_improvement = max(best_capturable_improvement, improvement * 2)
                    elif move.count >= h_count * 0.5:
                        # Possible capture (50%+ win) - medium priority
                        best_capturable_improvement = max(best_capturable_improvement, improvement)

                    best_any_improvement = max(best_any_improvement, improvement)

            # Score based on approach to capturable targets
            if best_capturable_improvement > 0:
                score += 200 + best_capturable_improvement * 20  # Strong bonus for capturable
            elif best_any_improvement > 0:
                score += 50 + best_any_improvement * 5  # Smaller bonus for any approach

        # Larger moves are generally more impactful
        score += move.count

    return score


def order_moves(state: GameState, moves: List[List[Move]], for_opponent: bool = False) -> List[List[Move]]:
    """
    Order moves by score (best first) for better alpha-beta pruning.

    Args:
        state: Current game state
        moves: List of move combinations
        for_opponent: If True, order for opponent

    Returns:
        Sorted list of moves (best first)
    """
    if len(moves) <= 1:
        return moves

    # Score and sort moves (descending by score)
    scored_moves = [(score_move_combo(state, m, for_opponent), m) for m in moves]
    scored_moves.sort(key=lambda x: x[0], reverse=True)

    return [m for _, m in scored_moves]


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

        # Order moves for better pruning at root level
        all_moves = order_moves(state, all_moves, for_opponent=False)

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

        # Check time every 500 nodes instead of every node (saves 50-250ms)
        if self.nodes_explored % 500 == 0 and self.out_of_time():
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

            # Order moves for better pruning (best moves first)
            moves = order_moves(state, moves, for_opponent=False)

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

            # Order moves for better pruning (best moves first for opponent)
            moves = order_moves(state, moves, for_opponent=True)

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
