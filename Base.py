from z3 import *

# 1. Creiamo il Solutore
s = Solver()

# 2. Definiamo le posizioni (x, y) nei vari istanti di tempo (passo 0, 1 e 2)
# Invece di usare un costrutto while/for, scriviamole esplicitamente.
x0, y0 = Int('x0'), Int('y0') # Stato Iniziale
x1, y1 = Int('x1'), Int('y1') # Passo 1
x2, y2 = Int('x2'), Int('y2') # Passo 2 (Goal)

# 3. STATO INIZIALE: Partiamo dall'origine (0, 0)
s.add(x0 == 0, y0 == 0)

# 4. STATO FINALE (GOAL): Vogliamo arrivare a (1, 1) al passo 2
s.add(x2 == 1, y2 == 1)

# 5. TRANSIZIONI: Quali mosse sono legali tra un passo e l'altro?
# Dobbiamo dire a Z3: "Dal passo 0 al passo 1, spostati di 1 casella"
# E "Dal passo 1 al passo 2, spostati di 1 casella"

# Regola per muoversi dal passo 0 al passo 1 (dx, dy)
dx1 = x1 - x0
dy1 = y1 - y0
s.add(Or(
    And(dx1 == 1,  dy1 == 0),  # Vai a destra
    And(dx1 == -1, dy1 == 0),  # Vai a sinistra
    And(dx1 == 0,  dy1 == 1),  # Vai in alto
    And(dx1 == 0,  dy1 == -1)  # Vai in basso
))

# Regola per muoversi dal passo 1 al passo 2 (dx, dy)
dx2 = x2 - x1
dy2 = y2 - y1
s.add(Or(
    And(dx2 == 1,  dy2 == 0),  
    And(dx2 == -1, dy2 == 0),  
    And(dx2 == 0,  dy2 == 1),  
    And(dx2 == 0,  dy2 == -1)  
))

# (Opzionale in un griglia senza muri, ma la omettiamo per brevità: 
# normally metteremmo i vincoli x >= 0, x < 2, ecc.)

# 6. TROVA LA SOLUZIONE!
if s.check() == sat:
    m = s.model()
    print("Percorso trovato!")
    print(f"Passo 0: ({m[x0]}, {m[y0]})")
    print(f"Passo 1: ({m[x1]}, {m[y1]})")
    print(f"Passo 2: ({m[x2]}, {m[y2]})")
else:
    print("Non esiste un percorso!")
