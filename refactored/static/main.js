// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
let puzzle = [];
let timerInterval = null;
let elapsedSeconds = 0;
let gameCompleted = false;

const LEADERBOARD_KEY = 'sudoku_leaderboard_v1';
let hintsUsed = 0;
const THEME_KEY = 'sudoku_theme_v1';

function baseCellClassName(input) {
  const subgrid = input.dataset.subgrid === 'a' ? 'subgrid-a' : 'subgrid-b';
  return `sudoku-cell ${subgrid}`;
}

function updateTimerDisplay() {
  const timerEl = document.getElementById('timer');
  if (!timerEl) return;
  const minutes = Math.floor(elapsedSeconds / 60);
  const seconds = elapsedSeconds % 60;
  timerEl.textContent = `Time: ${minutes}:${seconds.toString().padStart(2, '0')}`;
}

function startTimer() {
  if (timerInterval) {
    clearInterval(timerInterval);
  }
  elapsedSeconds = 0;
  updateTimerDisplay();
  timerInterval = setInterval(() => {
    elapsedSeconds += 1;
    updateTimerDisplay();
  }, 1000);
}

function stopTimer() {
  if (timerInterval) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
}

function loadScores() {
  try {
    const raw = window.localStorage.getItem(LEADERBOARD_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function saveScores(scores) {
  try {
    window.localStorage.setItem(LEADERBOARD_KEY, JSON.stringify(scores));
  } catch {
    // Ignore storage errors; leaderboard is a non-critical feature.
  }
}

function formatTime(seconds) {
  const minutes = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${minutes}:${secs.toString().padStart(2, '0')}`;
}

function renderLeaderboard() {
  const tbody = document.getElementById('leaderboard-body');
  if (!tbody) return;

  const scores = loadScores().slice().sort((a, b) => a.seconds - b.seconds).slice(0, 10);

  tbody.innerHTML = '';
  scores.forEach((s, index) => {
    const tr = document.createElement('tr');

    const rankTd = document.createElement('td');
    rankTd.textContent = String(index + 1);
    tr.appendChild(rankTd);

    const nameTd = document.createElement('td');
    nameTd.textContent = s.name || 'Anonymous';
    tr.appendChild(nameTd);

    const timeTd = document.createElement('td');
    timeTd.textContent = formatTime(s.seconds);
    tr.appendChild(timeTd);

    const levelTd = document.createElement('td');
    levelTd.textContent = s.difficulty || '';
    tr.appendChild(levelTd);

    const hintsTd = document.createElement('td');
    const hints = typeof s.hints === 'number' ? s.hints : 0;
    hintsTd.textContent = String(hints);
    tr.appendChild(hintsTd);

    tbody.appendChild(tr);
  });
}

function applyTheme(theme) {
  const body = document.body;
  const toggle = document.getElementById('theme-toggle');
  const isDark = theme === 'dark';

  if (isDark) {
    body.classList.add('dark-mode');
  } else {
    body.classList.remove('dark-mode');
  }

  if (toggle) {
    // Use icons for a more aesthetic toggle: sun (light) and moon (dark).
    toggle.textContent = isDark ? '☀️' : '🌙';
  }
}

function loadTheme() {
  try {
    const saved = window.localStorage.getItem(THEME_KEY);
    return saved === 'dark' ? 'dark' : 'light';
  } catch {
    return 'light';
  }
}

function saveTheme(theme) {
  try {
    window.localStorage.setItem(THEME_KEY, theme);
  } catch {
    // ignore
  }
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.dataset.row = i;
      input.dataset.col = j;
      const subgridRow = Math.floor(i / 3);
      const subgridCol = Math.floor(j / 3);
      const subgridType = (subgridRow + subgridCol) % 2 === 0 ? 'a' : 'b';
      input.dataset.subgrid = subgridType;
      input.className = baseCellClassName(input);
      input.addEventListener('input', (e) => {
        const val = e.target.value.replace(/[^1-9]/g, '');
        e.target.value = val;
        // Trigger validation on each change for immediate feedback.
        validateBoard(false);
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function readCurrentBoard() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }
  return { board, inputs };
}

function renderPuzzle(puz) {
  puzzle = puz;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.className = `${baseCellClassName(inp)} prefilled`;
      } else {
        inp.value = '';
        inp.disabled = false;
        inp.className = baseCellClassName(inp);
      }
    }
  }
}

async function newGame() {
  const select = document.getElementById('difficulty');
  const difficulty = select ? select.value : '';

  const url = difficulty
    ? `/new?difficulty=${encodeURIComponent(difficulty)}`
    : '/new';

  const res = await fetch(url);
  const data = await res.json();
  renderPuzzle(data.puzzle);
  document.getElementById('message').innerText = '';
  gameCompleted = false;
  hintsUsed = 0;
  startTimer();
}

async function checkSolution() {
  await validateBoard(true);
}

async function validateBoard(showMessages) {
  const { board, inputs } = readCurrentBoard();
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    if (showMessages) {
      msg.style.color = '#d32f2f';
      msg.innerText = data.error;
    }
    return;
  }
  const incorrect = new Set(data.incorrect.map(x => x[0]*SIZE + x[1]));
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) continue;
    inp.className = baseCellClassName(inp);
    if (incorrect.has(idx)) {
      inp.className = `${baseCellClassName(inp)} incorrect`;
    }
  }
  const hasEmpty = board.some(row => row.some(cell => cell === 0));

  if (!hasEmpty && incorrect.size === 0) {
    // Puzzle is completely filled and all entries are correct.
    msg.style.color = '#388e3c';
    msg.innerText = 'Congratulations! You solved it!';
    if (!gameCompleted) {
      gameCompleted = true;
      stopTimer();

      let name = window.prompt('You solved the puzzle! Enter your name:', 'Player');
      if (!name) {
        name = 'Anonymous';
      }
      const difficultySelect = document.getElementById('difficulty');
      const difficulty = difficultySelect ? difficultySelect.value : '';

      const scores = loadScores();
      scores.push({ name, seconds: elapsedSeconds, difficulty, hints: hintsUsed });
      saveScores(scores);
      renderLeaderboard();
    }
  } else if (showMessages) {
    if (incorrect.size === 0) {
      msg.style.color = '#1976d2';
      msg.innerText = 'So far so good.';
    } else {
      msg.style.color = '#d32f2f';
      msg.innerText = 'Some cells are incorrect.';
    }
  }
}

async function requestHint() {
  const { board, inputs } = readCurrentBoard();
  const res = await fetch('/hint', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });

  const data = await res.json();
  const msg = document.getElementById('message');

  if (!res.ok || data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error || 'No hint available.';
    return;
  }

  const { row, col, value } = data;
  if (typeof data.hints_used === 'number') {
    hintsUsed = data.hints_used;
  } else {
    hintsUsed += 1;
  }
  const idx = row * SIZE + col;
  const inp = inputs[idx];
  inp.value = value;
  inp.disabled = true;
  inp.className = `${baseCellClassName(inp)} hint`;

  await validateBoard(false);
}

// Wire buttons
window.addEventListener('load', () => {
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('hint-button').addEventListener('click', requestHint);
  const themeToggle = document.getElementById('theme-toggle');
  if (themeToggle) {
    const initialTheme = loadTheme();
    applyTheme(initialTheme);
    themeToggle.addEventListener('click', () => {
      const current = document.body.classList.contains('dark-mode') ? 'dark' : 'light';
      const next = current === 'dark' ? 'light' : 'dark';
      saveTheme(next);
      applyTheme(next);
    });
  } else {
    applyTheme('light');
  }

  // initialize
  renderLeaderboard();
  newGame();
});