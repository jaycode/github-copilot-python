# Sudoku Web App

This is a simple Sudoku web application built with Flask on the backend and a small JavaScript frontend. The backend generates valid Sudoku puzzles and exposes a few routes that the frontend uses to start a new game and check the solution.

## Project Structure

- `app.py` – Flask application with routes for the UI, starting a new game, and checking a solution.
- `sudoku_logic.py` – Core Sudoku logic: board generation and helper functions.
- `templates/index.html` – Main HTML page for the Sudoku UI.
- `static/main.js` – Frontend logic for interacting with the backend.
- `static/styles.css` – Styles for the UI.
- `tests/` – Pytest-based test suite for the Sudoku logic and Flask app.

## Requirements

- Python 3.9+ (any recent 3.x version should work)
- pip (Python package manager)

All Python dependencies are listed in `requirements.txt`, including:

- Flask – for the web app
- pytest – for running the test suite

## Installation

1. Open a terminal in the `refactored` project directory.
2. (Optional but recommended) Create and activate a virtual environment:

   **Windows (PowerShell):**

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Running the Web App

From the `refactored` directory, run:

```bash
python app.py
```

Then open `http://127.0.0.1:5000/` in your browser.

## Test Suite

The test suite is implemented with **pytest** and lives in the `tests/` directory.

### What is Covered

- `tests/test_sudoku_logic.py` – Unit tests for:
  - Board creation (`create_empty_board`)
  - Safety checks for moves (`is_safe`)
  - Full board generation (`fill_board`)
  - Puzzle generation (`generate_puzzle`), including clue count and consistency with the solution.
- `tests/test_app.py` – Tests for the Flask application routes:
  - `GET /` returns the main page.
  - `GET /new` creates a new puzzle and updates in-memory state.
  - `POST /check` behavior when:
    - No game is in progress.
    - The submitted board matches the solution.
    - The submitted board has incorrect cells.

### Running the Tests

Make sure you have installed dependencies as described above, and that you are in the `refactored` directory.

Run the test suite with:

```bash
pytest
```

Pytest will automatically discover all tests in the `tests/` directory and run them.

### Running a Single Test File

You can also run an individual test module, for example:

```bash
pytest tests/test_sudoku_logic.py
```

or

```bash
pytest tests/test_app.py
```

This can be helpful when working on a specific part of the app.

## Notes

- The app keeps the current puzzle and solution in a simple in-memory dictionary (`CURRENT` in `app.py`). This is sufficient for local testing and development but is not intended for multi-user production use.
- The Sudoku puzzles are generated randomly, so the exact board will vary from run to run, but the tests check structural correctness and logical consistency rather than specific fixed boards.
