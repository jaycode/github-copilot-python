import sudoku_logic
from app import app, CURRENT
import pytest


@pytest.fixture
def client():
    app.config["TESTING"] = True

    # Reset global state before each test
    CURRENT["puzzle"] = None
    CURRENT["solution"] = None

    with app.test_client() as client:
        yield client


def test_index_route_returns_ok(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.content_type


def test_new_game_creates_puzzle_and_solution(client):
    clues = 35
    response = client.get(f"/new?clues={clues}")

    assert response.status_code == 200
    data = response.get_json()

    assert "puzzle" in data
    puzzle = data["puzzle"]

    # Basic shape checks
    assert len(puzzle) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in puzzle)

    # Number of non-empty cells should equal clues
    non_empty = sum(1 for row in puzzle for cell in row if cell != sudoku_logic.EMPTY)
    assert non_empty == clues

    # Global state should be updated
    assert CURRENT["puzzle"] is not None
    assert CURRENT["solution"] is not None


@pytest.mark.parametrize(
    "difficulty,expected_clues",
    [
        ("easy", sudoku_logic.DIFFICULTY_CLUES["easy"]),
        ("medium", sudoku_logic.DIFFICULTY_CLUES["medium"]),
        ("hard", sudoku_logic.DIFFICULTY_CLUES["hard"]),
    ],
)
def test_new_game_uses_difficulty_to_determine_clues(client, difficulty, expected_clues):
    response = client.get(f"/new?difficulty={difficulty}")

    assert response.status_code == 200
    data = response.get_json()

    puzzle = data["puzzle"]
    non_empty = sum(1 for row in puzzle for cell in row if cell != sudoku_logic.EMPTY)
    assert non_empty == expected_clues


def test_check_solution_without_active_game_returns_error(client):
    # Ensure no game in progress
    CURRENT["puzzle"] = None
    CURRENT["solution"] = None

    board = sudoku_logic.create_empty_board()
    response = client.post("/check", json={"board": board})

    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_check_solution_with_correct_board_returns_no_incorrect_cells(client):
    # Start a new game to populate CURRENT["solution"]
    client.get("/new")
    solution = CURRENT["solution"]

    response = client.post("/check", json={"board": solution})

    assert response.status_code == 200
    data = response.get_json()

    assert "incorrect" in data
    assert data["incorrect"] == []


def test_check_solution_with_incorrect_board_marks_cells(client):
    # Start a new game to populate CURRENT["solution"]
    client.get("/new")
    solution = sudoku_logic.deep_copy(CURRENT["solution"])

    # Flip the value at (0, 0) to something else (still 1..9)
    original = solution[0][0]
    solution[0][0] = (original % sudoku_logic.SIZE) + 1

    response = client.post("/check", json={"board": solution})

    assert response.status_code == 200
    data = response.get_json()

    assert "incorrect" in data
    assert [0, 0] in data["incorrect"]


def test_check_solution_ignores_empty_cells_and_flags_only_incorrect(client):
    # Start a new game and get the correct solution
    client.get("/new")
    solution = sudoku_logic.deep_copy(CURRENT["solution"])

    # Build a board that is partially filled with correct values and zeros elsewhere
    board = sudoku_logic.create_empty_board()
    board[0][0] = solution[0][0]
    board[1][1] = solution[1][1]

    response = client.post("/check", json={"board": board})
    assert response.status_code == 200
    data = response.get_json()

    # No incorrect entries should be reported; empties are ignored
    assert data["incorrect"] == []

    # Now introduce a single incorrect move
    wrong_board = sudoku_logic.deep_copy(board)
    wrong_board[2][2] = (solution[2][2] % sudoku_logic.SIZE) + 1

    response = client.post("/check", json={"board": wrong_board})
    assert response.status_code == 200
    data = response.get_json()

    assert [2, 2] in data["incorrect"]


def test_hint_without_active_game_returns_error(client):
    # Ensure no game in progress
    CURRENT["puzzle"] = None
    CURRENT["solution"] = None

    board = sudoku_logic.create_empty_board()
    response = client.post("/hint", json={"board": board})

    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_hint_provides_correct_value_for_empty_cell(client):
    # Start a new game
    client.get("/new")
    solution = sudoku_logic.deep_copy(CURRENT["solution"])

    # Use an entirely empty board so the hint fills the first cell
    board = sudoku_logic.create_empty_board()

    response = client.post("/hint", json={"board": board})
    assert response.status_code == 200
    data = response.get_json()

    row = data["row"]
    col = data["col"]
    value = data["value"]

    assert 0 <= row < sudoku_logic.SIZE
    assert 0 <= col < sudoku_logic.SIZE
    assert value == solution[row][col]
    # First hint in a new game should report hints_used == 1
    assert data.get("hints_used") == 1


def test_hint_returns_error_when_board_already_solved(client):
    # Start a new game and immediately request a hint with the solved board
    client.get("/new")
    solution = sudoku_logic.deep_copy(CURRENT["solution"])

    response = client.post("/hint", json={"board": solution})
    assert response.status_code == 400
    data = response.get_json()

    assert "error" in data


def test_multiple_hints_increment_hints_used_counter(client):
    client.get("/new")
    solution = sudoku_logic.deep_copy(CURRENT["solution"])

    # Start with an empty board
    board = sudoku_logic.create_empty_board()

    # First hint
    response1 = client.post("/hint", json={"board": board})
    assert response1.status_code == 200
    data1 = response1.get_json()
    assert data1.get("hints_used") == 1

    # Apply the first hint to the board
    board[data1["row"]][data1["col"]] = data1["value"]

    # Second hint
    response2 = client.post("/hint", json={"board": board})
    assert response2.status_code == 200
    data2 = response2.get_json()
    assert data2.get("hints_used") == 2
