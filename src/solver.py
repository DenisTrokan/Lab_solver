from z3 import *
import time

class MazeSolver:
    def __init__(self, maze):
        self.maze = maze
        self.formula_lines = []

    def solve_bmc(self, max_k=100):
        """Solves the maze using Bounded Model Checking with incremental solving."""
        start_time = time.time()
        #svuotiamo la memoria della formula prec.
        self.formula_lines = []
        
        #Passi minimi necessari per arrivare alla fine, se facciamo meno di questi passi c'è qualcosa che non va
        min_k = abs(self.maze.end[0] - self.maze.start[0]) + abs(self.maze.end[1] - self.maze.start[1])
        s = Solver()
        path_x = []
        path_y = []

        #caso base
        x_0 = Int("x_0")
        y_0 = Int("y_0")
        path_x.append(x_0)
        path_y.append(y_0) 
        #il nostro path inizia da 0,0 (lo start)

        #prima aggiunta di vincoli, ossia l'insieme di clausole iniziale che ci indicano la proprietà : "si parte da 0,0"
        self.formula_lines.append(f"; Initial state at step 0")
        self.formula_lines.append(f"(x_0 = {self.maze.start[1]}) ∧ (y_0 = {self.maze.start[0]})")
        s.add(x_0 == self.maze.start[1], y_0 == self.maze.start[0])
        
        # Dominio delle x e delle y (devono essere all'interno del labirinto)
        self.formula_lines.append(f"; Domain constraints for step 0")
        self.formula_lines.append(f"(0 ≤ x_0 < {self.maze.width}) ∧ (0 ≤ y_0 < {self.maze.height})")
        s.add(x_0 >= 0, x_0 < self.maze.width)
        s.add(y_0 >= 0, y_0 < self.maze.height)
        
        # lista di coordinate di muri per facilitare la descrizione di mosse possibili
        walls = []
        for r in range(self.maze.height):
            for c in range(self.maze.width):
                if self.maze.grid[r][c] == 1:
                    walls.append((r, c))
        # aggiungiamo i vincoli del tipo: " la nostra pozizione attuale non ci può far stare nelle caselle con muri"
        if walls:
            self.formula_lines.append(f"; Wall constraints ({len(walls)} walls)")
            s.add(And([Or(x_0 != c, y_0 != r) for r, c in walls]))

        for k in range(1, max_k + 1):
            
            #variabili per il passo successivo
            x_k = Int(f"x_{k}")
            y_k = Int(f"y_{k}")
            path_x.append(x_k)
            path_y.append(y_k)

            x_prev = path_x[k-1]
            y_prev = path_y[k-1]

            # come prima vincoli sia per stare all'interno del labirinto sia per i muri
            s.add(x_k >= 0, x_k < self.maze.width)
            s.add(y_k >= 0, y_k < self.maze.height)

            #anzichè creare n clausole piccole, creiamo una singola clausola grande collegata da AND
            # questo è utile per evitare problemi di ricorsione e riempimento dello stack di z3 (che abbiamo avuto)
            if walls:
                s.add(And([Or(x_k != c, y_k != r) for r, c in walls]))

            # passaggio da k-1(prec) all'attuale k
            dx = x_k - x_prev
            dy = y_k - y_prev
            
            self.formula_lines.append(f"; Transition k-1→k: (dx,dy) ∈ {{(±1,0), (0,±1)}}")
                #insieme di passi possibili
            s.add(Or(
                And(dx == 1, dy == 0),
                And(dx == -1, dy == 0),
                And(dx == 0, dy == 1),
                And(dx == 0, dy == -1)
            ))

            # ottimizazzione: Non possiamo tornare allo stato k-2 immediatamente(ossia non facciamo "mosse ad U attorno una cella")
            if k >= 2:
                x_prev2 = path_x[k-2]
                y_prev2 = path_y[k-2]
                self.formula_lines.append(f"; No U-turn: (x_{k}, y_{k}) ≠ (x_{k-2}, y_{k-2})")
                s.add(Or(x_k != x_prev2, y_k != y_prev2)) #vincolo per l'appunto

            # controlliamo se siamo alla  fine e se abbiamo ottenuto le eventuali keys
            if k >= min_k:
                s.push() #salva lo stato per z3
                #ottimizazzione: controlliamo di essere in un ramo coerente, cioe se siamo in un ramo che è <= di (k-t) caselle (con t distanza minima rimasta per arrivare alla fine) 
                end_x, end_y = self.maze.end[1], self.maze.end[0]
                for t in range(k):
                    dist_to_goal = If(path_x[t] > end_x, path_x[t] - end_x, end_x - path_x[t]) + \
                                   If(path_y[t] > end_y, path_y[t] - end_y, end_y - path_y[t])
                    s.add(dist_to_goal <= (k - t))
                #aggiungiamo il vincolo di fine(che le x,y al punto k siano uguali a quelle di fine)
                self.formula_lines.append(f"; Goal: reach ({end_x}, {end_y}) by step {k}")
                self.formula_lines.append(f"(x_{k} = {end_x}) ∧ (y_{k} = {end_y})")
                s.add(x_k == end_x, y_k == end_y)

                #vincolo per le chiavi: per ogni chiave, ci deve essere un tempo t (o passo k) in cui le abbiamo visitate
                if hasattr(self.maze, 'keys') and self.maze.keys:
                    for (kr, kc) in self.maze.keys:
                        #logica del tipo: esiste t in [0,....,k] tale che (path_x[t] == kc AND path_y[t] == kr)
                            #con kc,kr coordinate x,y di ogni chiave
                                # In z3: Or( (x_0==kc ^ y_0==kr), ..., (x_k==kc ^ y_k==kr) )
                        self.formula_lines.append(f"; Key at ({kc}, {kr}) must be visited at some step ≤ {k}")
                        key_visited = Or([ And(path_x[t] == kc, path_y[t] == kr) for t in range(k + 1) ])
                        s.add(key_visited)
                
                result = s.check() #ci dice se il modello attuale è soddisfacibile(sat) o meno
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
                
                s.pop() #Per continuare al passo successivo(k+1), togliamo il vincolo di arrivo(che xk,yk == x_end, y_end)
                #chiusura for, si va al passo k+1
        duration = time.time() - start_time
        return {
            "found": False,
            "solve_time": duration,
            "formula_size": len(s.assertions()),
            "formula": "\n".join(self.formula_lines),
            "formula_size": len(s.assertions())
        }
