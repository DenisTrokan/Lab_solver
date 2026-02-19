const mazeContainer = document.getElementById('maze-container');
const userStepsSpan = document.getElementById('user-steps');
const z3StepsSpan = document.getElementById('z3-steps');
const z3TimeSpan = document.getElementById('z3-time');
const formulaSizeSpan = document.getElementById('formula-size');
const statusDiv = document.getElementById('status-message');
const addKeysBtn = document.getElementById('add-keys-btn');

let currentMaze = null;
let playerPos = { r: 0, c: 0 };
let userSteps = 0;
let gameActive = false;

let currentSize = { width: 10, height: 10 };

// Initialize
document.getElementById('new-game-btn').addEventListener('click', newGame);
document.getElementById('solve-btn').addEventListener('click', solveMaze);
if (addKeysBtn) {
    addKeysBtn.addEventListener('click', addKeys);
}
document.addEventListener('keydown', handleInput);

document.querySelectorAll('.size-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        // UI Update
        document.querySelectorAll('.size-btn').forEach(b => b.classList.remove('selected'));
        e.target.classList.add('selected');

        // Logic Update
        const size = e.target.dataset.size;
        if (size === 'small') currentSize = { width: 10, height: 10 };
        else if (size === 'medium') currentSize = { width: 15, height: 15 };
        else if (size === 'large') currentSize = { width: 20, height: 20 };

        // Restart game with new size
        newGame();
    });
});

// Start a game on load
newGame();

async function newGame() {
    // Reset stats
    userSteps = 0;
    userStepsSpan.innerText = '0';
    z3StepsSpan.innerText = '-';
    z3TimeSpan.innerText = '-';
    formulaSizeSpan.innerText = '-';
    statusDiv.innerText = '';
    statusDiv.className = 'status';
    gameActive = true;

    // Enable Add Keys button for new game
    if (addKeysBtn) {
        addKeysBtn.disabled = false;
        addKeysBtn.innerText = "+ Add Keys";
    }

    try {
        const response = await fetch('/api/new_maze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(currentSize)
        });
        currentMaze = await response.json();
        playerPos = { r: currentMaze.start[0], c: currentMaze.start[1] };
        renderMaze();
    } catch (error) {
        console.error('Error fetching maze:', error);
        statusDiv.innerText = 'Error loading maze.';
    }
}

async function addKeys() {
    if (!currentMaze || !gameActive) return;

    // Disable button immediately to prevent double clicks
    if (addKeysBtn) addKeysBtn.disabled = true;

    try {
        const response = await fetch('/api/add_keys', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        currentMaze = await response.json();
        renderMaze();
        statusDiv.innerText = "Keys added! Collect them all.";
    } catch (error) {
        console.error('Error adding keys:', error);
        if (addKeysBtn) addKeysBtn.disabled = false; // Re-enable on error
    }
}

function renderMaze() {
    if (!currentMaze) return;

    mazeContainer.innerHTML = '';
    mazeContainer.style.gridTemplateColumns = `repeat(${currentMaze.width}, 30px)`;
    mazeContainer.style.gridTemplateRows = `repeat(${currentMaze.height}, 30px)`;

    for (let r = 0; r < currentMaze.height; r++) {
        for (let c = 0; c < currentMaze.width; c++) {
            const cell = document.createElement('div');
            cell.classList.add('cell');
            cell.id = `cell-${r}-${c}`;

            if (currentMaze.grid[r][c] === 1) {
                cell.classList.add('wall');
            } else {
                cell.classList.add('path');
            }

            if (r === currentMaze.start[0] && c === currentMaze.start[1]) {
                cell.classList.add('start');
            }
            if (r === currentMaze.end[0] && c === currentMaze.end[1]) {
                cell.classList.add('end');
            }

            // Check keys
            if (currentMaze.keys) {
                for (let k of currentMaze.keys) {
                    if (k[0] === r && k[1] === c) {
                        cell.classList.add('key');
                    }
                }
            }

            mazeContainer.appendChild(cell);
        }
    }
    updatePlayerPosition();
}

function updatePlayerPosition() {
    // Clear previous player class
    document.querySelectorAll('.player').forEach(el => el.classList.remove('player'));

    // Add player class to new pos
    const cell = document.getElementById(`cell-${playerPos.r}-${playerPos.c}`);
    if (cell) cell.classList.add('player');
}

function handleInput(e) {
    if (!gameActive || !currentMaze) return;

    let dr = 0, dc = 0;
    if (e.key === 'ArrowUp') dr = -1;
    else if (e.key === 'ArrowDown') dr = 1;
    else if (e.key === 'ArrowLeft') dc = -1;
    else if (e.key === 'ArrowRight') dc = 1;
    else return;

    e.preventDefault();

    const nr = playerPos.r + dr;
    const nc = playerPos.c + dc;

    // Check bounds and walls
    if (nr >= 0 && nr < currentMaze.height && nc >= 0 && nc < currentMaze.width) {
        if (currentMaze.grid[nr][nc] === 0) {

            // First move check - Disable adding keys once user starts moving
            if (userSteps === 0) {
                if (addKeysBtn) addKeysBtn.disabled = true;
            }

            playerPos = { r: nr, c: nc };
            userSteps++;
            userStepsSpan.innerText = userSteps;
            updatePlayerPosition();

            // Mark visited path for visual trail
            const cell = document.getElementById(`cell-${nr}-${nc}`);
            if (cell) cell.classList.add('user-path');

            checkWin();
        }
    }
}

function checkWin() {
    if (playerPos.r === currentMaze.end[0] && playerPos.c === currentMaze.end[1]) {
        gameActive = false;
        statusDiv.innerText = 'You Reached the Goal!';
        statusDiv.classList.add('win');
        statusDiv.classList.remove('lose');
    }
}

async function solveMaze() {
    if (!currentMaze) return;

    const solveBtn = document.getElementById('solve-btn');

    // Disable buttons to prevent multiple requests
    if (addKeysBtn) addKeysBtn.disabled = true;
    solveBtn.disabled = true;
    const originalBtnText = solveBtn.innerText;
    solveBtn.innerText = "Solving...";

    const maxK = document.getElementById('solver-depth').value || 100;

    try {
        const response = await fetch('/api/solve', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ max_k: parseInt(maxK) }) // Uses current maze on server
        });
        const result = await response.json();

        if (result.found) {
            z3StepsSpan.innerText = result.k; // or result.path.length - 1
            z3TimeSpan.innerText = result.solve_time.toFixed(4);
            formulaSizeSpan.innerText = result.formula_size;
            statusDiv.innerText = 'Z3 Found a solution!';

            animateSolution(result.path);
        } else {
            statusDiv.innerText = 'Z3 says: UNSAT (No path found)';
            statusDiv.classList.add('lose');
        }

    } catch (error) {
        console.error('Error solving maze:', error);
        statusDiv.innerText = 'Error solving maze.';
    } finally {
        solveBtn.disabled = false;
        solveBtn.innerText = originalBtnText;
    }
}

function animateSolution(path) {
    let i = 0;
    const interval = setInterval(() => {
        if (i >= path.length) {
            clearInterval(interval);
            return;
        }
        const [r, c] = path[i];
        const cell = document.getElementById(`cell-${r}-${c}`);
        if (cell) {
            // Don't overwrite player or start/end totally, just add class
            cell.classList.add('z3-path');
        }
        i++;
    }, 100); // 100ms per step
}
