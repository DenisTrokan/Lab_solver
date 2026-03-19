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
        """
        genera un labirinto random utilizzando DFS, con il metodo di backtraking

        """
        # inizi con tutto muro = grid[x][y] = 1
        self.grid = [[1 for _ in range(self.width)] for _ in range(self.height)]
        

        # controlla se le coordinate sono all'interno del labirinto,e se non sono all'interno, restituisce False
        def is_valid(r, c):
            return 0 <= r < self.height and 0 <= c < self.width

        # DFS Setup
        stack = [(0, 0)] # inizializza la pila con la posizione iniziale
        self.grid[0][0] = 0 # apre la cella iniziale
        
        while stack:   
            r, c = stack[-1] # prende l'ultima posizione dalla pila
            # r = riga
            # c = colonna
            neighbors = [] # lista di vicini
            directions = [(0, 2), (0, -2), (2, 0), (-2, 0)]

            for dr, dc in directions: 
                # calcola le coordinate del vicino
                nr, nc = r + dr, c + dc 
                if is_valid(nr, nc) and self.grid[nr][nc] == 1: # se la cella e valida ed e' una parete
                    neighbors.append((nr, nc, dr, dc)) # aggiunge la cella alla lista dei vicini
            
            if neighbors:#se ci sono vicini
                nr, nc, dr, dc = random.choice(neighbors)
                #rimuove il muro tra la cella corrente e il vicino
                self.grid[r + dr // 2][c + dc // 2] = 0
                self.grid[nr][nc] = 0
                stack.append((nr, nc))
            else:
                stack.pop()
        #rende risolvibile per dimensioni pari

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

        #rendi start e end percorribili
        self.grid[self.start[0]][self.start[1]] = 0
        self.grid[self.end[0]][self.end[1]] = 0

        #crea loop togliendo dei muri
        total_walls_to_remove = int((self.width * self.height) * 0.03)
        

        for _ in range(total_walls_to_remove):
             r = random.randint(1, self.height - 2)
             c = random.randint(1, self.width - 2)
             if self.grid[r][c] == 1:
                #controlla se la cella e' collegata ad almeno 2 celle percorribili
                 path_neighbors = 0
                 for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                     if self.grid[r+dr][c+dc] == 0:
                         path_neighbors += 1
                 
                 #se la cella e' collegata ad almeno 2 celle percorribili (quindi crea un loop)
                 if path_neighbors >= 2:
                     self.grid[r][c] = 0


    def add_keys(self):
        """Aggiungi le chiavi, in base alla grandezza del labirinto."""
        # Determina il numero di chiavi in base alla grandezza del labirinto (assumendo un labirinto quadrato)
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
            
            # deve essere un percorso aperto, non start/end, e non gia' una chiave
            if (self.grid[r][c] == 0 and 
                (r, c) != self.start and 
                (r, c) != self.end and 
                (r, c) not in self.keys):
                self.keys.append((r, c))
                count += 1
            attempts += 1


    def to_json(self):
        """Serializza il labirinto in un formato JSON compatibile.""" 
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
