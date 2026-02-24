from flask import Flask, render_template, jsonify, request
import sys
import os
import threading

# Add src to path to import backend modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.maze import Maze
from src.solver import MazeSolver

app = Flask(__name__)

# Store current maze in memory (simple for single user/demo)
# Ideally use a database or session for multi-user
current_maze = None
current_solver = None
solving_thread = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/new_maze', methods=['POST'])
def new_maze():
    global current_maze
    data = request.json
    width = data.get('width', 10)
    height = data.get('height', 10)
    
    current_maze = Maze(width, height)
    current_maze.generate()
    
    return jsonify(current_maze.to_json())

@app.route('/api/add_keys', methods=['POST'])
def add_keys():
    global current_maze
    if not current_maze:
        return jsonify({"error": "No maze generated"}), 400
        
    current_maze.add_keys()
    return jsonify(current_maze.to_json())

@app.route('/api/solve', methods=['POST'])
def solve():
    global current_maze, current_solver, solving_thread
    if not current_maze:
        return jsonify({"error": "No maze generated"}), 400
    
    data = request.json
    max_k = data.get('max_k', current_maze.width * current_maze.height)
    
    # Create solver and store reference so we can access formula_lines during solving
    current_solver = MazeSolver(current_maze)
    
    # Dictionary to store result from thread
    result_holder = {}
    
    def run_solver():
        result_holder['result'] = current_solver.solve_bmc(max_k=max_k)
    
    # Run solver in a thread so formula updates can be fetched
    solving_thread = threading.Thread(target=run_solver)
    solving_thread.start()
    
    # Wait for solver to complete
    solving_thread.join()
    
    result = result_holder.get('result', {"error": "Solver failed"})
    current_solver = None
    solving_thread = None
    
    return jsonify(result)

@app.route('/api/solve_progress', methods=['GET'])
def solve_progress():
    global current_solver
    if not current_solver:
        return jsonify({"formula": "", "is_solving": False})
    
    # Return current formula lines being built
    formula = "\n".join(current_solver.formula_lines)
    is_solving = True
    
    return jsonify({
        "formula": formula,
        "is_solving": is_solving,
        "lines_count": len(current_solver.formula_lines)
    })

if __name__ == '__main__':
    app.run(debug=False, port=5000)
