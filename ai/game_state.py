"""Game state representation and move generation for Vampires VS Werewolves."""
from typing import List, Tuple, Optional, Dict
from enum import IntEnum
import copy


class Species(IntEnum):
    """Species types in the game."""
    HUMAN = 0
    VAMPIRE = 1
    WEREWOLF = 2


class Cell:
    """Represents a cell on the game board."""
    
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.humans = 0
        self.vampires = 0
        self.werewolves = 0
    
    def get_count(self, species: Species) -> int:
        """Get count for a specific species."""
        if species == Species.HUMAN:
            return self.humans
        elif species == Species.VAMPIRE:
            return self.vampires
        elif species == Species.WEREWOLF:
            return self.werewolves
        return 0
    
    def set_count(self, species: Species, count: int):
        """Set count for a specific species."""
        if species == Species.HUMAN:
            self.humans = count
        elif species == Species.VAMPIRE:
            self.vampires = count
        elif species == Species.WEREWOLF:
            self.werewolves = count
    
    def is_empty(self) -> bool:
        """Check if cell has no creatures."""
        return self.humans == 0 and self.vampires == 0 and self.werewolves == 0
    
    def __repr__(self) -> str:
        return f"Cell({self.x},{self.y}: H={self.humans} V={self.vampires} W={self.werewolves})"


class Move:
    """Represents a move from one cell to another."""
    
    def __init__(self, x_from: int, y_from: int, x_to: int, y_to: int, count: int):
        self.x_from = x_from
        self.y_from = y_from
        self.x_to = x_to
        self.y_to = y_to
        self.count = count
    
    def to_tuple(self) -> Tuple[int, int, int, int, int]:
        """Convert to tuple for protocol communication.
        
        Server protocol expects: (x_from, y_from, count, x_to, y_to)
        where x=column, y=row.
        
        Internally we use: x=row, y=col
        So we swap: (col_from, row_from, count, col_to, row_to)
        """
        return (self.y_from, self.x_from, self.count, self.y_to, self.x_to)
    
    def __repr__(self) -> str:
        return f"Move({self.x_from},{self.y_from}→{self.x_to},{self.y_to}:{self.count})"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Move):
            return False
        return (self.x_from == other.x_from and self.y_from == other.y_from and
                self.x_to == other.x_to and self.y_to == other.y_to and
                self.count == other.count)
    
    def __hash__(self) -> int:
        return hash((self.x_from, self.y_from, self.x_to, self.y_to, self.count))


class GameState:
    """Represents the complete game state."""
    
    # 8 directions: N, NE, E, SE, S, SW, W, NW
    DIRECTIONS = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]
    
    def __init__(self, rows: int = 10, cols: int = 10):
        self.rows = rows
        self.cols = cols
        self.board: List[List[Cell]] = [[Cell(i, j) for j in range(cols)] for i in range(rows)]
        self.our_species: Optional[Species] = None
        self.opponent_species: Optional[Species] = None
        self.home_position: Optional[Tuple[int, int]] = None
    
    def initialize_from_messages(self, size: Tuple[int, int], humans: List[List[int]], 
                                  home: List[int], map_data: List[Tuple[int, int, int, int, int]]):
        """Initialize game state from server messages."""
        self.rows, self.cols = size
        self.board = [[Cell(i, j) for j in range(self.cols)] for i in range(self.rows)]
        self.home_position = (home[0], home[1])
        
        # Set humans
        for x, y in humans:
            self.board[y][x].humans = 1  # Initial human count (will be updated by MAP)
        
        # Set initial board state from MAP
        for x, y, humans_count, vampires_count, werewolves_count in map_data:
            cell = self.board[y][x]
            cell.humans = humans_count
            cell.vampires = vampires_count
            cell.werewolves = werewolves_count
        
        # Determine our species based on home position
        home_cell = self.board[home[1]][home[0]]
        if home_cell.vampires > 0:
            self.our_species = Species.VAMPIRE
            self.opponent_species = Species.WEREWOLF
        elif home_cell.werewolves > 0:
            self.our_species = Species.WEREWOLF
            self.opponent_species = Species.VAMPIRE
    
    def update_from_upd(self, updates: List[Tuple[int, int, int, int, int]]):
        """Update game state from UPD message."""
        for x, y, humans_count, vampires_count, werewolves_count in updates:
            cell = self.board[y][x]
            cell.humans = humans_count
            cell.vampires = vampires_count
            cell.werewolves = werewolves_count
    
    def get_cell(self, x: int, y: int) -> Optional[Cell]:
        """Get cell at position, returns None if out of bounds."""
        if 0 <= x < self.rows and 0 <= y < self.cols:
            return self.board[x][y]
        return None
    
    def is_adjacent(self, x1: int, y1: int, x2: int, y2: int) -> bool:
        """Check if two positions are adjacent (8-directional)."""
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        return dx <= 1 and dy <= 1 and (dx + dy) > 0
    
    def get_our_groups(self) -> List[Tuple[int, int, int]]:
        """Get all cells with our species. Returns [(x, y, count), ...]."""
        groups = []
        if self.our_species is None:
            return groups
        for i in range(self.rows):
            for j in range(self.cols):
                cell = self.board[i][j]
                count = cell.get_count(self.our_species)
                if count > 0:
                    groups.append((i, j, count))
        return groups
    
    def get_opponent_groups(self) -> List[Tuple[int, int, int]]:
        """Get all cells with opponent species. Returns [(x, y, count), ...]."""
        groups = []
        if self.opponent_species is None:
            return groups
        for i in range(self.rows):
            for j in range(self.cols):
                cell = self.board[i][j]
                count = cell.get_count(self.opponent_species)
                if count > 0:
                    groups.append((i, j, count))
        return groups
    
    def get_total_count(self, species: Species) -> int:
        """Get total count of a species on the board."""
        total = 0
        for i in range(self.rows):
            for j in range(self.cols):
                total += self.board[i][j].get_count(species)
        return total
    
    def is_terminal(self) -> bool:
        """Check if game is in terminal state (one species eliminated)."""
        if self.our_species is None or self.opponent_species is None:
            return False
        our_count = self.get_total_count(self.our_species)
        opponent_count = self.get_total_count(self.opponent_species)
        return our_count == 0 or opponent_count == 0
    
    def clone(self) -> 'GameState':
        """Create a deep copy of the game state."""
        new_state = GameState(self.rows, self.cols)
        new_state.our_species = self.our_species
        new_state.opponent_species = self.opponent_species
        new_state.home_position = self.home_position
        
        for i in range(self.rows):
            for j in range(self.cols):
                new_state.board[i][j].humans = self.board[i][j].humans
                new_state.board[i][j].vampires = self.board[i][j].vampires
                new_state.board[i][j].werewolves = self.board[i][j].werewolves
        
        return new_state
    
    def __repr__(self) -> str:
        our_total = self.get_total_count(self.our_species) if self.our_species else 0
        opp_total = self.get_total_count(self.opponent_species) if self.opponent_species else 0
        return (f"GameState(rows={self.rows}, cols={self.cols}, "
                f"our_species={self.our_species}, "
                f"total_ours={our_total}, "
                f"total_opponent={opp_total})")
