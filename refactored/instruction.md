# Sudoku Web App – Instructions

## 1. Prerequisites

- Python 3.9+ installed
- `pip` available on your PATH

From the `refactored` directory, install dependencies:

```bash
pip install -r requirements.txt
```

## 2. Running the App

From the same directory:

```bash
python app.py
```

Then open `http://127.0.0.1:5000/` in your browser.

## 3. Gameplay

- **Difficulty selector (left sidebar)**
  - Choose **Easy**, **Medium**, or **Hard**.
  - Click **New Game** to start a puzzle at that difficulty.
- **Board**
  - 9×9 Sudoku grid with alternating 3×3 block colors.
  - Grey cells are prefilled and cannot be edited.
  - White cells are editable; only digits 1–9 are accepted.
  - Invalid entries are highlighted red immediately as you type.
- **Right sidebar controls**
  - **Check**: Manually validates your current board.
  - **Hint**: Fills one helpful cell (either an empty spot or fixes an incorrect cell). Each click increases your hint count for the current game.
- **Timer**
  - Starts when a new game is created.
  - Stops when the puzzle is fully and correctly solved.
- **Messages**
  - Shows feedback such as errors, "So far so good.", or a completion message.

## 4. Leaderboard (Top 10)

Below the board, a **Top 10 Fastest Times** table is shown:

- Columns: **Rank**, **Name**, **Time**, **Level**, **Hints**.
- After solving a puzzle, you are prompted for your name.
- Your time, difficulty, and hints used are saved to `localStorage` in the browser.
- The table shows the 10 fastest times across sessions for that browser.

## 5. Test Suite

Tests are written with **pytest** and live in the `tests/` directory.

- **Logic tests**: `tests/test_sudoku_logic.py`
  - Board creation, solver, puzzle generation, and uniqueness of solutions.
- **API tests**: `tests/test_app.py`
  - Flask routes for `/`, `/new`, `/check`, and `/hint`.
  - Difficulty → clues mapping, hint counter, and error handling.
- **Frontend integration guards**: `tests/test_frontend_integration.py`
  - Verifies that immediate feedback is wired (cell input triggers `validateBoard(false)`).
  - Verifies CSS includes an explicit style for incorrect cells over subgrid backgrounds.

To run all tests:

```bash
pytest
```

To run a specific test module, for example the logic tests:

```bash
pytest tests/test_sudoku_logic.py
```

## 6. Development Notes

- Core game logic is in `sudoku_logic.py`.
- Flask app and routes are in `app.py`.
- Frontend behavior is in `static/main.js` and `static/styles.css`.
- Main HTML template is `templates/index.html`.

When modifying frontend behavior (validation, hints, or styling), ensure the corresponding tests in `tests/` continue to pass.
