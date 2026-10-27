import math

MIN_SIZE = 5
MAX_SIZE = 13
DEFAULT_SIZE = 7
DEFAULT_TYPE = "English"

# jump directions: straight and diagonal
SQUARE_DIRECTIONS = ((-1, 0), (1, 0), (0, -1), (0, 1),
                     (-1, -1), (-1, 1), (1, -1), (1, 1))
HEX_DIRECTIONS = ((1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1))

class Board:
    directions = SQUARE_DIRECTIONS

    def __init__(self, size):
        if type(size) is not int or size < MIN_SIZE or size > MAX_SIZE \
                or size % 2 == 0:
            raise ValueError("Size must be an odd number from 5 to 13")
        self.size = size
        self.cells = self.build_cells()
        self.marbles = set()
        self.reset()

    def build_cells(self):
        return set()
    
    @property
    def center(self):
        return (self.size // 2, self.size // 2)
    
    def lattice_xy(self, pos):
        return (pos[1], pos[0])
    
    @property
    def marble_count(self):
        return len(self.marbles)
    
    def has_marble(self, pos):
        return pos in self.marbles
    
    def is_empty_hole(self, pos):
        return pos in self.cells and pos not in self.marbles
    
    def reset(self):
        # every hole gets a marble the center
        self.marbles = set(self.cells)
        self.marbles.discard(self.center)

    def set_marbles(self, positions):
        positions = set(positions)
        if not positions <= self.cells:
            raise ValueError("Marble is outside the board")
        self.marbles = positions

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
        for start in sorted(self.marbles):
            for end in self.moves_from(start):
                moves.append((start, end))
        return moves
    
    def make_move(self, start, end):
        if not self.is_valid_move(start, end):
            return False
        jumped = self.jumped_position(start, end)
        self.marbles.remove(start)
        self.marbles.remove(jumped)
        self.marbles.add(end)
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
                if band <= r <= n - 1 - band or band <= c <= n - 1 - band:
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
        return(0, 0)
    
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

    def __init__(self, board_type=DEFAULT_TYPE, size=DEFAULT_SIZE):
        self.board = create_board(board_type, size)
        self.board_type = board_type
        self.size = size
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

    def make_move(self, start, end):
        if self.is_game_over():
            return False
        moved = self.board.make_move(start, end)
        if moved:
            self.moves_made += 1
        return moved
    
    def is_game_over(self):
        return self.board.is_game_over()
    
    def is_won(self):
        return self.is_game_over() and self.board.marble_count == 1

            