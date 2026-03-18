# Complessità Temporale: Bounded Model Checking vs Algoritmi Classici

Sia:
* **$V = W \times H$** il numero totale delle celle (stati) nel labirinto.
* **$E$** il numero di archi (le possibili mosse, che al massimo sono $4 \cdot V$).
* **$K$** la lunghezza massima del percorso.

---

## 1. Scenario Base: Labirinto Senza Chiavi

### Algoritmi Classici (Es. BFS)
Il problema di trovare l'uscita da un labirinto da un punto $A$ a un punto $B$ \`e il problema della raggiugibilit\`a (Reachability) o del Percorso Pi\`u Breve (Shortest Path) su un grafo non pesato.
* **Complessit\`a:** $O(V + E)$.
* **Classe:** Polinomiale (**P**). La BFS \`e rapidissima e la sua espansione \`e lineare rispetto alla grandezza della griglia.

### SAT Solver (Z3 con BMC)
In Z3, stiamo facendo una cosa matematicamente "sconveniente": stiamo riducendo un problema facile (in P) a **SAT**, che è **NP-Completo**.
Per ogni passo $k$, costruiamo una formula con $\approx V \times k$ variabili booleane (sotto forma di interi in z3 SMT).
* **Complessit\`a Teorica del SAT Solver (DPLL/CDCL):** Il tempo nel caso peggiore \`e esponenziale rispetto al numero di variabili, ovvero $O(2^{V \cdot k})$.
* **Nella pratica:** Gli algoritmi CDCL moderni di Z3 abbattono i nodi insoddisfacibili molto in fretta grazie al Clause Learning, ma la complessitàa di base resta alta ($NP$) rispetto a un normale algoritmo ($P$).

---

## 2. Scenario Avanzato: Labirinto Con $C$ Chiavi

Qui il gioco cambia e la potenza dei metodi dichiarativi di Z3 schiaccia i normali algoritmi imperativi.

### Algoritmi Classici (BFS Bruteforce)
Adesso arrivare a $B$ non basta. Dobbiamo toccare $C$ chiavi in un ordine ignoto prima di arrivare a $B$.
Questo problema modella il **Traveling Salesman Problem (TSP)** per un sottoinsieme di nodi su griglia, che è un problema **NP-Hard**.
Se usassimo una mappa classica, l'algoritmo (es. BFS iterata) dovrebbe teoricamente:
1. Trovare il percorso minore per ogni coppia possibile di nodi chiave.
2. Esaminare tutte le \textbf{permutazioni} dell'ordine in cui raccogliere le $C$ chiavi.
* **Complessit\`a (Na\`ive):** $O(C! \times (V+E))$. Costo del fattoriale ($C!$) per testare ogni sequenza possibile (es. "Chiave 1 poi 2", "Chiave 2 poi 1").
* **Complessit\`a (Held-Karp/DP):** Anche usando la programmazione dinamica, la complessit\`a scende ma resta **Esponenziale**: $O(C^2 2^C + V)$. All'aumentare di $C$, il programma "esplode".

### SAT Solver (Z3 con BMC)
Ed ecco il trucco matematico. Quante "nuove" regole o complessit\`a algoritmiche abbiamo inserito in `solver.py` per supportare le chiavi? Nessuna!

1. Abbiamo aggiunto solo $C$ clausole logiche ``Or(path_x[t] == kc... )``.
2. La formula in memoria cresce in spazio di un infinitesimale $O(C \cdot K)$.
3. **Complessit\`a Temporale:** Rimane la stessa di prima, **NP-Completo**, ed \`e sempre governata dai tempi del SAT resolver: worst-case $O(2^{\text{Var}})$. 

**La Verit\`a (Il nocciolo dell'Esame):** 
Con Z3, la nostra complessit\`a **non salta di categoria** quando aggiungiamo complessit\`a alle regole del gioco. Sia "Andare dal punto A al punto B", sia "Disinnescare 5 bombe in un ordine preciso mentre indossi un cappello rosso" vengono scritti in logica proposizionale senza alcun calcolo di permutazioni manuali. 

Il costo computazionale ($\mathcal{O}_{peggiore}$) era asintoticamente catastrofico ($2^N$) sin dall'inizio nell'approccio BMC. Ma proprio perch\'e stavamo gi\`a usando il martello pi\`u pesante della Teoria della Complessit\`a (il SAT-Solving per NP-problemi), rincari di complessit\`a del dominio (Chiavi, Permutazioni, Cicli Hamiltoniani) causano un piccolissimo aumento del numero di vincoli $\Phi$, venendo digeriti naturalmente dal solutore unificato senza dover toccare l'algoritmo di fondo.
