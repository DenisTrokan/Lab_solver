import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.maze import Maze
from src.solver import MazeSolver

class TestMazeSolver(unittest.TestCase):
    def test_maze_generation(self):
        m = Maze(10, 10)
        m.generate()
        self.assertEqual(len(m.grid), 10)
        self.assertEqual(len(m.grid[0]), 10)
        # Start and end should be open (0)
        self.assertEqual(m.grid[m.start[0]][m.start[1]], 0)
        self.assertEqual(m.grid[m.end[0]][m.end[1]], 0)

    def test_solver_simple(self):
        # Create a simple 3x3 open maze
        m = Maze(3, 3)
        m.grid = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
        ]
        m.start = (0, 0)
        m.end = (2, 2)
        
        solver = MazeSolver(m)
        result = solver.solve_bmc(max_k=10)
        
        self.assertTrue(result['found'])
        self.assertGreater(len(result['path']), 0)
        # Optimal path should be length 5 (start + 4 steps: (0,0)->(0,1)->(0,2)->(1,2)->(2,2)) or similar
        # Manhattan distance is 4 steps, so k=4, path length 5 nodes.
        # However, BMC finds *shortest* path. 
        # (0,0) -> (1,0) -> (2,0) -> (2,1) -> (2,2) is also valid.
        
        self.assertEqual(len(result['path']), 5) # 4 steps + start position

    def test_solver_wall(self):
        # 3x3 with wall blocking
        m = Maze(3, 3)
        m.grid = [
            [0, 1, 0],
            [0, 1, 0],
            [0, 1, 0]
        ]
        m.start = (0, 0)
        m.end = (0, 2)
        
        solver = MazeSolver(m)
        result = solver.solve_bmc(max_k=10)
        
        self.assertFalse(result['found'])

if __name__ == '__main__':
    unittest.main()
