from flask import Flask, render_template, jsonify, request
import sudoku_logic

app = Flask(__name__)

# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
    'solution': None,
    'hints': 0,
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
    # Prefer a named difficulty if provided; fall back to explicit clues or
    # the default number of clues from the sudoku_logic module.
    difficulty = request.args.get('difficulty')
    if difficulty:
        clues = sudoku_logic.clues_for_difficulty(difficulty)
    else:
        clues = int(request.args.get('clues', sudoku_logic.DEFAULT_CLUES))

    puzzle, solution = sudoku_logic.generate_puzzle(clues)
    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    CURRENT['hints'] = 0
    return jsonify({'puzzle': puzzle})

@app.route('/check', methods=['POST'])
def check_solution():
    data = request.json
    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    incorrect = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            # Treat empty cells (0) as "not yet filled" rather than incorrect.
            if board[i][j] == sudoku_logic.EMPTY:
                continue
            if board[i][j] != solution[i][j]:
                incorrect.append([i, j])
    return jsonify({'incorrect': incorrect})


@app.route('/hint', methods=['POST'])
def get_hint():
    """Return a single helpful cell (row, col, value) for the current game.

    Prefers filling an empty cell; if none are empty but there are incorrect
    entries, it will correct the first incorrect cell. If the board already
    matches the solution, an error is returned.
    """

    data = request.json
    board = data.get('board')
    solution = CURRENT.get('solution')

    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400

    size = sudoku_logic.SIZE

    # First, look for an empty cell to fill.
    for i in range(size):
        for j in range(size):
            if board[i][j] == sudoku_logic.EMPTY and solution[i][j] != sudoku_logic.EMPTY:
                CURRENT['hints'] += 1
                return jsonify({'row': i, 'col': j, 'value': solution[i][j], 'hints_used': CURRENT['hints']})

    # If there are no empty cells, look for an incorrect one to correct.
    for i in range(size):
        for j in range(size):
            if board[i][j] != solution[i][j]:
                CURRENT['hints'] += 1
                return jsonify({'row': i, 'col': j, 'value': solution[i][j], 'hints_used': CURRENT['hints']})

    # Board already matches the solution; no hint to provide.
    return jsonify({'error': 'No hint available'}), 400

if __name__ == '__main__':
    app.run(debug=True)