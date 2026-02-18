from flask import Flask, render_template, jsonify, request
import sys
import os

# Add src to path to import backend modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.maze import Maze
from src.solver import MazeSolver

app = Flask(__name__)

# Store current maze in memory (simple for single user/demo)
# Ideally use a database or session for multi-user
current_maze = None

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
    global current_maze
    if not current_maze:
        return jsonify({"error": "No maze generated"}), 400
    
    data = request.json
    max_k = data.get('max_k', current_maze.width * current_maze.height)
    
    solver = MazeSolver(current_maze)
    result = solver.solve_bmc(max_k=max_k)
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=False, port=5000)
