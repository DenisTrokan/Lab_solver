from src.maze import Maze
from src.solver import MazeSolver

m = Maze(10, 10)
m.generate()
m.add_keys()
print("Keys:", m.keys)
solver = MazeSolver(m)
res = solver.solve_bmc()
path = res['path']
for kr, kc in m.keys:
    if (kr, kc) in path:
        print(f"Key {kr},{kc} Visited!")
    else:
        print(f"Key {kr},{kc} MISSED!")
