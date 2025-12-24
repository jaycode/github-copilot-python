import sudoku_logic


def _is_valid_complete_board(board):
    size = sudoku_logic.SIZE
    expected = set(range(1, size + 1))

    # Check rows
    for row in board:
        if set(row) != expected:
            return False

    # Check columns
    for col in range(size):
        column_vals = [board[row][col] for row in range(size)]
        if set(column_vals) != expected:
            return False

    # Check 3x3 sub-grids
    for box_row in range(0, size, 3):
        for box_col in range(0, size, 3):
            cells = [
                board[r][c]
                for r in range(box_row, box_row + 3)
                for c in range(box_col, box_col + 3)
            ]
            if set(cells) != expected:
                return False

    return True


def test_create_empty_board_dimensions_and_values():
    board = sudoku_logic.create_empty_board()

    assert len(board) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in board)
    assert all(cell == sudoku_logic.EMPTY for row in board for cell in row)


def test_is_safe_detects_row_column_and_box_conflicts():
    board = sudoku_logic.create_empty_board()

    # Put a value in (0, 0) and ensure same value is unsafe in same row/col/box
    board[0][0] = 5

    # Same row
    assert not sudoku_logic.is_safe(board, 0, 1, 5)
    # Same column
    assert not sudoku_logic.is_safe(board, 1, 0, 5)
    # Same 3x3 box
    assert not sudoku_logic.is_safe(board, 1, 1, 5)

    # A different number should be safe in a non-conflicting cell
    assert sudoku_logic.is_safe(board, 0, 1, 4)


def test_fill_board_produces_valid_complete_solution():
    board = sudoku_logic.create_empty_board()

    # Algorithm should be able to fill the empty board
    filled = sudoku_logic.fill_board(board)
    assert filled is True

    # No empty cells should remain
    assert all(cell != sudoku_logic.EMPTY for row in board for cell in row)

    # The board should represent a valid Sudoku solution
    assert _is_valid_complete_board(board)


def test_generate_puzzle_structure_and_clues_count():
    clues = 30
    puzzle, solution = sudoku_logic.generate_puzzle(clues=clues)

    # Basic shape checks
    assert len(puzzle) == sudoku_logic.SIZE
    assert len(solution) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in puzzle)
    assert all(len(row) == sudoku_logic.SIZE for row in solution)

    # Puzzle must only contain EMPTY or 1..9
    for row in puzzle:
        for cell in row:
            assert cell == sudoku_logic.EMPTY or 1 <= cell <= sudoku_logic.SIZE

    # The number of non-empty cells in the puzzle should match the clues argument
    non_empty = sum(1 for row in puzzle for cell in row if cell != sudoku_logic.EMPTY)
    assert non_empty == clues

    # For every filled cell in the puzzle, value must match the solution
    for r in range(sudoku_logic.SIZE):
        for c in range(sudoku_logic.SIZE):
            if puzzle[r][c] != sudoku_logic.EMPTY:
                assert puzzle[r][c] == solution[r][c]

    # Solution itself must be a valid completed Sudoku
    assert _is_valid_complete_board(solution)


def test_generated_puzzle_has_unique_solution():
    """Generated puzzles should admit exactly one valid solution."""

    clues = 35
    puzzle, _ = sudoku_logic.generate_puzzle(clues=clues)

    # Work on a copy to avoid any incidental mutation in the helper.
    puzzle_copy = sudoku_logic.deep_copy(puzzle)
    assert sudoku_logic.has_unique_solution(puzzle_copy)


def test_clues_for_difficulty_mapping_and_default():
    assert sudoku_logic.clues_for_difficulty("easy") == sudoku_logic.DIFFICULTY_CLUES["easy"]
    assert sudoku_logic.clues_for_difficulty("medium") == sudoku_logic.DIFFICULTY_CLUES["medium"]
    assert sudoku_logic.clues_for_difficulty("hard") == sudoku_logic.DIFFICULTY_CLUES["hard"]

    # Case insensitivity and unknown difficulty fall back to default
    assert sudoku_logic.clues_for_difficulty("EaSy") == sudoku_logic.DIFFICULTY_CLUES["easy"]
    assert sudoku_logic.clues_for_difficulty("unknown") == sudoku_logic.DEFAULT_CLUES
    assert sudoku_logic.clues_for_difficulty("") == sudoku_logic.DEFAULT_CLUES
