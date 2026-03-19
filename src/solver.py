from z3 import *
import time

class MazeSolver:
    def __init__(self, maze):
        self.maze = maze
        self.formula_lines = []

    def solve_bmc(self, max_k=100):
        """Solves the maze using Bounded Model Checking with incremental solving."""
        start_time = time.time()
        
        # Reset formula lines for new solve
        self.formula_lines = []
        
        # Minimum steps needed (Manhattan distance)
        min_k = abs(self.maze.end[0] - self.maze.start[0]) + abs(self.maze.end[1] - self.maze.start[1])

        s = Solver()
        
        # Store variables to retrieve path later
        path_x = []
        path_y = []

        # --- Base Case (k=0) ---
        x_0 = Int("x_0")
        y_0 = Int("y_0")
        path_x.append(x_0)
        path_y.append(y_0)

        # 1. Init State
        self.formula_lines.append(f"; Initial state at step 0")
        self.formula_lines.append(f"(x_0 = {self.maze.start[1]}) ∧ (y_0 = {self.maze.start[0]})")
        s.add(x_0 == self.maze.start[1], y_0 == self.maze.start[0])
        
        # 2. Domain & Wall constraints for t=0
        self.formula_lines.append(f"; Domain constraints for step 0")
        self.formula_lines.append(f"(0 ≤ x_0 < {self.maze.width}) ∧ (0 ≤ y_0 < {self.maze.height})")
        s.add(x_0 >= 0, x_0 < self.maze.width)
        s.add(y_0 >= 0, y_0 < self.maze.height)
        
        # Pre-calculate wall coordinates to optimize constraint generation
        walls = []
        for r in range(self.maze.height):
            for c in range(self.maze.width):
                if self.maze.grid[r][c] == 1:
                    walls.append((r, c))
                    
        if walls:
            self.formula_lines.append(f"; Wall constraints ({len(walls)} walls)")
            s.add(And([Or(x_0 != c, y_0 != r) for r, c in walls]))

        # --- Loop for k ---
        for k in range(1, max_k + 1):
            
            # Create variables for step k
            x_k = Int(f"x_{k}")
            y_k = Int(f"y_{k}")
            path_x.append(x_k)
            path_y.append(y_k)

            x_prev = path_x[k-1]
            y_prev = path_y[k-1]

            # 1. Domain & Wall constraints for step k
            s.add(x_k >= 0, x_k < self.maze.width)
            s.add(y_k >= 0, y_k < self.maze.height)

            # Optimized Wall Constraints: Single huge AND clause instead of N small assertions
            # This prevents Python recursion depth issues and reduces Z3 overhead
            if walls:
                s.add(And([Or(x_k != c, y_k != r) for r, c in walls]))

            # 2. Transition from k-1 to k
            dx = x_k - x_prev
            dy = y_k - y_prev
            
            self.formula_lines.append(f"; Transition k-1→k: (dx,dy) ∈ {{(±1,0), (0,±1)}}")
            
            s.add(Or(
                And(dx == 1, dy == 0),
                And(dx == -1, dy == 0),
                And(dx == 0, dy == 1),
                And(dx == 0, dy == -1)
            ))

            # Optimization: No U-Turns (Symmetry Breaking)
            # Cannot go back to exactly the state of k-2 immediately
            if k >= 2:
                x_prev2 = path_x[k-2]
                y_prev2 = path_y[k-2]
                self.formula_lines.append(f"; No U-turn: (x_{k}, y_{k}) ≠ (x_{k-2}, y_{k-2})")
                s.add(Or(x_k != x_prev2, y_k != y_prev2))

            # 3. Check Goal AND Keys (Incremental)
            if k >= min_k:
                s.push() # Save state
                
                # Optimization: Reachability Pruning (Distance Envelope)
                # At step t, we must be close enough to the goal to reach it in (k-t) steps
                # if we assume no obstacles. This prunes paths wandering too far away.
                # Only apply this inside the check scope because 'k' changes.
                
                # Goal Pruning
                end_x, end_y = self.maze.end[1], self.maze.end[0]
                for t in range(k):
                    dist_to_goal = If(path_x[t] > end_x, path_x[t] - end_x, end_x - path_x[t]) + \
                                   If(path_y[t] > end_y, path_y[t] - end_y, end_y - path_y[t])
                    s.add(dist_to_goal <= (k - t))

                # If keys exist, we could add pruning for keys too, but it's more complex (TSP).
                # The Goal Pruning is a strong baseline.

                # Goal Constraint
                self.formula_lines.append(f"; Goal: reach ({end_x}, {end_y}) by step {k}")
                self.formula_lines.append(f"(x_{k} = {end_x}) ∧ (y_{k} = {end_y})")
                s.add(x_k == end_x, y_k == end_y)

                # Keys Constraint: For ALL keys, there MUST be a time t <= k where we visited it
                if hasattr(self.maze, 'keys') and self.maze.keys:
                    for (kr, kc) in self.maze.keys:
                        # Construct logic: Exists t in [0..k] such that (path_x[t] == kc AND path_y[t] == kr)
                        # In Z3 (SAT): Or( (x_0==kc ^ y_0==kr), ..., (x_k==kc ^ y_k==kr) )
                        self.formula_lines.append(f"; Key at ({kc}, {kr}) must be visited at some step ≤ {k}")
                        key_visited = Or([ And(path_x[t] == kc, path_y[t] == kr) for t in range(k + 1) ])
                        s.add(key_visited)
                
                result = s.check()
                if result == sat:
                    m = s.model()
                    final_path = []
                    for t in range(k + 1):
                        final_path.append((m[path_y[t]].as_long(), m[path_x[t]].as_long()))
                    
                    duration = time.time() - start_time
                    return {
                        "found": True,
                        "k": k,
                        "path": final_path,
                        "solve_time": duration,
                        "formula_size": len(s.assertions()),
                        "formula": "\n".join(self.formula_lines)
                    }
                
                s.pop() # Restore state (remove goal constraint) to continue to k+1
        
        duration = time.time() - start_time
        return {
            "found": False,
            "solve_time": duration,
            "formula_size": len(s.assertions()),
            "formula": "\n".join(self.formula_lines),
            "formula_size": len(s.assertions())
        }
