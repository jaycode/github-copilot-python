from pathlib import Path


def test_main_js_has_immediate_validation_on_input():
    """Ensure typing in a cell still triggers backend validation.

    This guards the immediate-feedback feature by checking that
    validateBoard(false) is wired to the input event handler.
    """

    js_path = Path("static/main.js")
    src = js_path.read_text(encoding="utf-8")

    # Basic guards: we expect an input listener and a call to validateBoard(false)
    assert "addEventListener('input'" in src or "addEventListener(\"input\"" in src
    assert "validateBoard(false)" in src


def test_styles_define_incorrect_cell_highlight_over_subgrid():
    """Ensure incorrect cells have an explicit highlight style.

    This guards against CSS changes that would hide the red background
    used for immediate feedback on invalid moves.
    """

    css_path = Path("static/styles.css")
    css = css_path.read_text(encoding="utf-8")

    # We require a specific rule that styles incorrect cells, including
    # when combined with subgrid classes.
    assert ".sudoku-cell.subgrid-a.incorrect" in css
    assert "background: #ffcdd2" in css
