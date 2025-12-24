import copy
import random

SIZE = 9
EMPTY = 0

# Difficulty configuration: how many cells are pre-filled for each level.
DIFFICULTY_CLUES = {
    "easy": 40,
    "medium": 35,
    "hard": 28,
}

DEFAULT_DIFFICULTY = "medium"
DEFAULT_CLUES = DIFFICULTY_CLUES[DEFAULT_DIFFICULTY]

def deep_copy(board):
    return copy.deepcopy(board)

def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]


def clues_for_difficulty(name):
    """Return the number of clues for a given difficulty name.

    Falls back to DEFAULT_CLUES if the name is not recognized.
    """

    if not name:
        return DEFAULT_CLUES
    return DIFFICULTY_CLUES.get(name.lower(), DEFAULT_CLUES)


def _find_empty_cell(board):
    """Return the position of the next empty cell or None if the board is full."""
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                return row, col
    return None

def is_safe(board, row, col, num):
    # Check row and column
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def fill_board(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True

def _count_solutions(board, limit=2):
    """Count the number of valid solutions for the given board.

    The algorithm stops searching once `limit` solutions have been found to
    keep the search bounded. Callers can use this to check for uniqueness by
    passing ``limit=2`` and verifying that the returned value is exactly 1.
    """

    empty_pos = _find_empty_cell(board)
    if empty_pos is None:
        # No empty cells left: this is a complete valid solution.
        return 1

    row, col = empty_pos
    count = 0
    for num in range(1, SIZE + 1):
        if is_safe(board, row, col, num):
            board[row][col] = num
            count += _count_solutions(board, limit)
            if count >= limit:
                board[row][col] = EMPTY
                break
            board[row][col] = EMPTY

    return count


def has_unique_solution(board):
    """Return True if the given puzzle has exactly one valid solution.

    The input board is not mutated.
    """

    board_copy = deep_copy(board)
    return _count_solutions(board_copy, limit=2) == 1


def remove_cells(board, clues):
    """Remove cells from a full solution while preserving a unique solution.

    This function mutates ``board`` in-place. It attempts to remove exactly
    ``SIZE * SIZE - clues`` cells while ensuring that the resulting puzzle has
    a single solution.
    """

    cells_to_remove = SIZE * SIZE - clues

    while cells_to_remove > 0:
        row = random.randrange(SIZE)
        col = random.randrange(SIZE)

        if board[row][col] == EMPTY:
            continue

        backup = board[row][col]
        board[row][col] = EMPTY

        # Only accept this removal if the puzzle still has a unique solution.
        if has_unique_solution(board):
            cells_to_remove -= 1
        else:
            board[row][col] = backup

def generate_puzzle(clues=35):
    board = create_empty_board()
    fill_board(board)
    solution = deep_copy(board)
    remove_cells(board, clues)
    puzzle = deep_copy(board)
    return puzzle, solution
