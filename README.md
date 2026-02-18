# Maze Reachability Solver (Z3 + Flask)

This project implements a maze solver using **Bounded Model Checking (BMC)** with the **Z3 Theorem Prover**, wrapped in an interactive "Man vs Machine" web game.

## Project Structure

- `src/`: Core logic
    - `maze.py`: Maze generation (DFS) and representation.
    - `solver.py`: SAT encoding for reachability using Z3.
- `app/`: Flask Web Application
    - `app.py`: Backend API and server.
    - `templates/`: HTML frontend.
    - `static/`: CSS and JavaScript game logic.
- `tests/`: Unit tests.

## Installation

1. Create a virtual environment (optional but recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start the Flask application:
   ```bash
   python3 app/app.py
   ```
2. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

## How to Play

1. **New Game**: A random maze is generated. You are the **Blue Square**.
2. **Goal**: Reach the **Green Square**.
3. **Controls**: Use Arrow Keys to move.
4. **Man vs Machine**:
    - Try to solve it yourself!
    - Click **"Let Z3 Solve It"** to see the AI find the optimal path.
    - The AI path will be animated in **Red**.
    - Compare your steps with the AI's optimal steps.

## Theory

The solver uses **Bounded Model Checking**. It attempts to find a path of length $k$ for increasing values of $k$.
For each step $k$, it generates a logical formula $\Phi_k$ that is Satisfiable if and only if there exists a valid path of length $k$ from Start to End.

Variables:
- Play grid positions $(x_t, y_t)$ at time steps $t \in [0, k]$.
- Constraints: Valid moves, obstacle avoidance, boundary checks.

The formula grows with $k$. Z3 checks satisfiability. If `UNSAT`, we try $k+1$. If `SAT`, we extract the model (path).

### Optimizations
To improve performance for larger mazes, we implemented:
1.  **Symmetry Breaking (No U-Turns)**: A constraint $\neg(pos_t == pos_{t-2})$ prevents immediate backtracking, pruning the search space.
2.  **Heuristic Pruning (Distance Envelope)**: We enforce that at any step $t$, the Manhattan distance to the goal must be $\le (k-t)$. This cuts off paths that wander too far to reach the goal within the remaining steps.
