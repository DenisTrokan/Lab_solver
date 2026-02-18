import random
import json

class Maze:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[1 for _ in range(width)] for _ in range(height)] # 1 = wall, 0 = path
        self.start = (0, 0)
        self.end = (height - 1, width - 1)

    def generate(self):
        """Generates a random maze using Recursive Backtracking (DFS) with adjustments for solvability and complexity."""
        # Start with all walls
        self.grid = [[1 for _ in range(self.width)] for _ in range(self.height)]
        
        # Helper to check bounds
        def is_valid(r, c):
            return 0 <= r < self.height and 0 <= c < self.width

        # DFS Setup
        stack = [(0, 0)]
        self.grid[0][0] = 0
        
        while stack:
            r, c = stack[-1]
            neighbors = []
            
            # Check neighbors (jump 2 steps)
            directions = [(0, 2), (0, -2), (2, 0), (-2, 0)]
            
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if is_valid(nr, nc) and self.grid[nr][nc] == 1:
                    neighbors.append((nr, nc, dr, dc))
            
            if neighbors:
                nr, nc, dr, dc = random.choice(neighbors)
                # Break wall between current and neighbor
                self.grid[r + dr // 2][c + dc // 2] = 0
                self.grid[nr][nc] = 0
                stack.append((nr, nc))
            else:
                stack.pop()
        
        # --- FIX SOLVABILITY FOR EVEN DIMENSIONS ---
        if self.height % 2 == 0:
            for c in range(0, self.width, 2):
                 if c < self.width and self.grid[self.height-2][c] == 0:
                     if random.random() < 0.7: 
                         self.grid[self.height-1][c] = 0
                         
        if self.width % 2 == 0:
            for r in range(0, self.height, 2):
                if r < self.height and self.grid[r][self.width-2] == 0:
                    if random.random() < 0.7:
                        self.grid[r][self.width-1] = 0

        # Ensure Start and End are explicitly open
        self.grid[self.start[0]][self.start[1]] = 0
        self.grid[self.end[0]][self.end[1]] = 0

        # --- ADD COMPLEXITY LIMITED (LOOPS) ---
        # Reduce density: 3% of total cells of extra holes (was 5%)
        total_walls_to_remove = int((self.width * self.height) * 0.03)
        
        for _ in range(total_walls_to_remove):
             r = random.randint(1, self.height - 2)
             c = random.randint(1, self.width - 2)
             if self.grid[r][c] == 1:
                 # Check if removing this wall connects two previously disconnected neighbors
                 path_neighbors = 0
                 for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                     if self.grid[r+dr][c+dc] == 0:
                         path_neighbors += 1
                 
                 # If it connects at least 2 path cells, it creates a loop
                 if path_neighbors >= 2:
                     self.grid[r][c] = 0


    def add_keys(self):
        """Adds keys (checkpoints) to the maze based on size."""
        # Determine number of keys based on width (assuming square-ish)
        if self.width <= 10:
            num_keys = 1
        elif self.width <= 15:
            num_keys = 2
        else:
            num_keys = 3
        
        self.keys = []
        count = 0
        attempts = 0
        while count < num_keys and attempts < 1000:
            r = random.randint(0, self.height - 1)
            c = random.randint(0, self.width - 1)
            
            # Must be an open path, not start/end, and not already a key
            if (self.grid[r][c] == 0 and 
                (r, c) != self.start and 
                (r, c) != self.end and 
                (r, c) not in self.keys):
                self.keys.append((r, c))
                count += 1
            attempts += 1


    def to_json(self):
        """Serializes the maze to a JSON-compatible format."""
        return {
            "width": self.width,
            "height": self.height,
            "grid": self.grid,
            "start": self.start,
            "end": self.end,
            "keys": getattr(self, 'keys', [])
        }

    @staticmethod
    def from_json(data):
        maze = Maze(data['width'], data['height'])
        maze.grid = data['grid']
        maze.start = tuple(data['start'])
        maze.end = tuple(data['end'])
        maze.keys = [tuple(k) for k in data.get('keys', [])]
        return maze
