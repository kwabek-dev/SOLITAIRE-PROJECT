import math
import random

MIN_SIZE = 5
MAX_SIZE = 13
DEFAULT_SIZE = 7
DEFAULT_TYPE = "English"
DEFAULT_MODE = "Manual"

SQUARE_DIRECTIONS = ((-1, 0), (1,0), (0, -1), (0, 1),
                     (-1, -1), (-1, 1), (1, -1), (1, 1))
HEX_DIRECTIONS = ((1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1))

class Board:
    directions = SQUARE_DIRECTIONS

    def __init__(self, size):
        if type(size) is not int or size < MIN_SIZE or size > MAX_SIZE \
                or size % 2 == 0:
            raise ValueError("Size must be an odd number from 5 to 13")
        self.size = size
        self._cells = frozenset(self.build_cells())
        self._marbles = set()
        self.reset()

    def build_cells(self):
        return set()
    
    @property
    def center(self):
        return (self.size // 2, self.size // 2)
    
    def lattice_xy(self, pos):
        return (pos[1], pos[0])
    
    @property
    def cells(self):
        return self._cells
    
    @property
    def marbles(self):
        return frozenset(self._marbles)
    
    @property
    def marble_count(self):
        return len(self._marbles)
    
    def has_marble(self, pos):
        return pos in self._marbles
    
    def is_empty_hole(self, pos):
        return pos in self._cells and pos not in self._marbles
    
    def reset(self):
        # every hole gets a marble except the center
        self._marbles = set(self._cells)
        self._marbles.discard(self.center)

    def set_marbles(self, positions):
        positions = set(positions)
        if not positions <= self._cells:
            raise ValueError("Marble is outside the board")
        self._marbles = positions

    def randomize(self, rng=None):
        """ Moves the same number of marbles to random holes.
        It tries to give a board that still has a valid move."""
        rng = rng or random
        holes = sorted(self._cells)
        count = len(self._marbles)
        for _ in range(100):
            self._marbles = set(rng.sample(holes, count))
            if self.has_valid_moves():
                return
            
    def jumped_position(self, start, end):
        for dr, dc in self.directions:
            if end == (start[0] + 2 * dr, start[1] + 2 * dc):
                return (start[0] + dr, start[1] + dc)
        return None
    
    def is_valid_move(self, start, end):
        if not self.has_marble(start) or not self.is_empty_hole(end):
            return False
        jumped = self.jumped_position(start, end)
        return jumped is not None and self.has_marble(jumped)
    
    def moves_from(self, start):
        result = []
        for dr, dc in self.directions:
            end = (start[0] + 2 * dr, start[1] + 2 * dc)
            if self.is_valid_move(start, end):
                result.append(end)
        return result
    
    def valid_moves(self):
        moves = []
        for start in sorted(self._marbles):
            for end in self.moves_from(start):
                moves.append((start, end))
        return moves
    
    def make_move(self, start, end):
        if not self.is_valid_move(start, end):
            return False
        jumped = self.jumped_position(start, end)
        self._marbles.remove(start)
        self._marbles.remove(jumped)
        self._marbles.add(end)
        return True
    
    def has_valid_moves(self):
        return len(self.valid_moves()) > 0
    
    def is_game_over(self):
        return not self.has_valid_moves()
    
class EnglishBoard(Board):
    def build_cells(self):
        n = self.size
        band = n // 3
        cells = set()
        for r in range(n):
            for c in range(n):
                if (band <= r <= n - 1 - band or band <= c <= n - 1 - band):
                    cells.add((r, c))
        return cells
    
class DiamondBoard(Board):
    def build_cells(self):
        n = self.size
        mid = n // 2
        cells = set()
        for r in range(n):
            for c in range(n):
                if abs(r - mid) + abs(c - mid) <= mid:
                    cells.add((r, c))
        return cells
    
class HexagonBoard(Board):

    directions = HEX_DIRECTIONS

    def build_cells(self):
        radius = self.size // 2
        cells = set()
        for q in range(-radius, radius + 1):
            for r in range(-radius, radius + 1):
                if abs(q + r) <= radius:
                    cells.add((q, r))
        return cells
    
    @property
    def center(self):
        return (0, 0)
    
    def lattice_xy(self, pos):
        q, r = pos
        return (q + r / 2, r * math.sqrt(3) / 2)
    
BOARD_TYPES = {"English": EnglishBoard,
                "Hexagon": HexagonBoard,
                "Diamond": DiamondBoard}

def create_board(board_type, size):
    if board_type not in BOARD_TYPES:
        raise ValueError("Unknown board type: " + str(board_type))
    return BOARD_TYPES[board_type](size)

class SolitaireGame:
    mode = ""
    player_moves = False    # does a human make the moves?
    auto_plays = False      # does the computer make the moves?

    def __init__(self, board_type=DEFAULT_TYPE, size=DEFAULT_SIZE, rng=None):
        self.board = create_board(board_type, size)
        self.board_type = board_type
        self.size = size
        self.rng = rng or random.Random()
        self.moves_made = 0

    def new_game(self, board_type=None, size=None):
        if board_type is None:
            board_type = self.board_type
        if size is None:
            size = self.size
        board = create_board(board_type, size)
        self.board = board
        self.board_type = board_type
        self.size = size
        self.moves_made = 0 

    @property
    def marble_count(self):
        return self.board.marble_count
    
    def do_move(self, start, end):
        if self.is_game_over():
            return False
        moved = self.board.make_move(start, end)
        if moved:
            self.moves_made += 1
        return moved
    
    def make_move(self, start, end):
        return False
    
    def randomize(self):
        return False
    
    def is_game_over(self):
        return self.board.is_game_over()
    
    def is_won(self):
        return self.is_game_over() and self.board.marble_count == 1
    
    def rating(self):
        if not self.is_game_over():
            return ""
        left = self.board.marble_count
        if left == 1:
            return "Outstanding"
        if left == 2:
            return "Very Good"
        if left == 3:
            return "Good"
        return "Average"
    
class ManualGame(SolitaireGame):
    mode = "Manual"
    player_moves = True

    def make_move(self, start, end):
        return self.do_move(start, end)
    
    def randomize(self):
        if self.is_game_over():
            return False
        self.board.randomize(self.rng)
        return True
    
class AutomatedGame(SolitaireGame):
    mode = "Automated"
    auto_plays = True

    def make_move(self, start, end):
        return False
    
    def auto_move(self):
        moves = self.board.valid_moves()
        if not moves:
            return None
        start, end = self.rng.choice(moves)
        self.do_move(start, end)
        return (start, end)
    
    def play_to_end(self):
        while self.auto_move() is not None:
            pass

GAME_MODES = {"Manual": ManualGame,
              "Automated": AutomatedGame}

def create_game(mode, board_type=DEFAULT_TYPE, size=DEFAULT_SIZE, rng=None):
    if mode not in GAME_MODES:
        raise ValueError("Unknown game mode: " + str(mode))
    return GAME_MODES[mode](board_type, size, rng)
