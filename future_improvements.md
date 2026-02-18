# Future Improvements & Advanced Constraints (Notes for Exam)

Queste sono idee per possibili estensioni del progetto, utili da discutere all'esame per dimostrare la flessibilità dell'approccio basato su Z3 e SAT Solving.

## 1. Zone Proibite Dinamiche (Trappole) 💣
**Concetto**: Celle che non sono muri statici, ma che diventano accessibili o inaccessibili dinamicamente, o che semplicemente non possono essere attraversate.
**Implementazione Z3**:
- Aggiungere un vincolo che impedisce di essere in una certa coordinata $(tx, ty)$ a qualsiasi passo $t$:
  $$ \forall t . \neg (x_t = tx \wedge y_t = ty) $$
**Interesse Teorico**: Dimostra la capacità di gestire ostacoli puntuali senza modificare la struttura dati del labirinto.

## 2. Ordine delle Chiavi (Ordered Checkpoints) 🔢
**Concetto**: Le chiavi devono essere raccolte in un ordine specifico (es. Prima la Chiave A, poi la B).
**Implementazione Z3**:
- Se $t_A$ è il passo in cui visito la Chiave A e $t_B$ per la Chiave B.
- Aggiungo il vincolo: $t_A < t_B$.
**Interesse Teorico**: Questo è un vincolo **temporale** molto difficile da gestire per algoritmi di ricerca standard (come BFS), ma banale per un solver logico che ha una visione "globale" del tempo.

## 3. Vincolo di Risorse ("Carburante") ⛽
**Concetto**: Il movimento ha un costo. L'agente ha un budget limitato di energia.
**Implementazione Z3**:
- Introdurre una variabile $fuel_t$.
- Transizione: $fuel_{t+1} = fuel_t - cost(mossa)$.
- Vincolo: $fuel_t \ge 0$.
**Interesse Teorico**: Introduce il concetto di **stateful constraints** (vincoli con stato) oltre alla semplice posizione geometrica.

## 4. Snake Mode (Cammino Auto-evitante) 🐍
**Concetto**: Non puoi visitare la stessa cella due volte (il percorso non può intersecarsi).
**Implementazione Z3**:
- Utilizzare il vincolo globale `Distinct`:
  $$ \text{Distinct}((x_0, y_0), (x_1, y_1), \dots, (x_k, y_k)) $$
**Interesse Teorico**: Dimostra la potenza dei **Global Constraints** nei solver moderni. È un problema NP-hard su grafi generici (Hamiltonian Path è un caso speciale).

## 5. Portali di Teletrasporto 🌀
**Concetto**: Entrare in $(x1, y1)$ ti porta istantaneamente a $(x2, y2)$.
**Implementazione Z3**:
- Modificare la relazione di transizione $T(s_i, s_{i+1})$ per includere il salto non adiacente.
**Interesse Teorico**: Mostra come è facile modificare la topologia dello spazio di ricerca cambiando solo la formula logica.

---

## 🟥 Perché BFS/DFS falliscono con questi vincoli? (Esplosione degli Stati)

Mentre Z3 gestisce questi vincoli aggiungendo clausole logiche, un algoritmo classico come BFS (Breadth-First Search) deve codificare tutto nello **stato**.

### Il Problema dello "Stato" in BFS
In una BFS standard, lo stato è definito solo dalla posizione $(x, y)$.
Quando si aggiungono vincoli "storici" o "globali", la posizione non basta più. Bisogna ricordare *cosa è successo prima*.

$$ \text{Stato} = (\text{Posizione}, \text{Memoria Extra}) $$

Questo causa **l'Esplosione Combinatoria** dello spazio degli stati.

### Esempio 1: Ordine delle Chiavi (Ordered Checkpoints)
Devi prendere $K$ chiavi in un ordine specifico (o anche parziale).
*   **BFS Classica**: Spazio stati = $N \times M$
*   **BFS con Chiavi**: Per sapere quale è la "prossima" chiave da prendere, lo stato deve includere l'indice dell'ultima chiave presa.
    *   Stato = $(x, y, \text{index\_chiave})$.
    *   Dimensione = $N \times M \times K$.
*   **BFS con Chiavi (Ordine Libero)**: Se l'ordine non è fissato, devi ricordare *l'insieme* delle chiavi prese.
    *   Stato = $(x, y, \{k_1, k_2, \dots\})$.
    *   Dimensione = $N \times M \times 2^K$.
    *   Con 20 chiavi, lo spazio aumenta di $2^{20} \approx 1.000.000$ volte. La BFS diventa intrattabile.

### Esempio 2: Snake Mode (Il caso peggiore)
Non puoi visitare la stessa cella due volte.
Per verificare questo vincolo, devi sapere *esattamente* quali celle hai già visitato nel percorso corrente.
*   **Stato necessario**: $(x, y, \text{percorso\_visitato})$.
*   Il "percorso visitato" può essere qualsiasi sottoinsieme delle celle del labirinto.
*   Dimensione dello spazio degli stati $\approx (N \times M) \times 2^{(N \times M)}$.
*   Anche per un labirinto minuscolo $5 \times 5$, $2^{25} \approx 33$ Milioni di stati.
*   Per un $10 \times 10$, $2^{100}$ è superiore al numero di atomi nell'universo.

### Perché Z3 vince?
Z3 non esplora esplicitamente tutti gli stati. Usa tecniche di deduzione logica (SAT Solving, Conflict-Driven Clause Learning) per "potare" enormi rami di ricerca che sono logicamente impossibili, senza doverli visitare uno per uno.
Invece di dire " provo tutti i percorsi", Z3 dice: "Se passo di qui, violo il vincolo X, quindi *nessun* percorso che passa di qui è valido".

---

## 🟩 Possiamo usare A* (A-Star)?

**Sì e No.**

### Cos'è A*?
A* è un'evoluzione della BFS che usa una "guida" (euristica) per scegliere quale nodo esplorare prima.
$$ f(n) = g(n) + h(n) $$
- $g(n)$: Costo per arrivare al nodo $n$ (passi fatti).
- $h(n)$: Stima del costo per arrivare al goal (es. Distanza Manhattan).
A* esplora prima i nodi che sembrano più promettenti (basso $f(n)$).

### Lo abbiamo già implementato! (In modo dichiarativo)
L'ottimizzazione **Distance Envelope** che abbiamo aggiunto al solver Z3 è esattamente il concetto di A* tradotto in logica:
$$ \text{Dist}(pos_t, Goal) \le (k - t) $$
Questa formula dice: *"Se la stima euristica $h(n)$ è maggiore dei passi rimasti, non esplorare questo stato"*.
Quindi, abbiamo integrato l'intelligenza di A* dentro la potenza deduttiva di Z3.

### Vantaggi/Svantaggi
- **A* Puro (Imperativo)**: Velocissimo per pathfinding semplice, ma soffre della stessa **Esplosione degli Stati** della BFS se aggiungiamo vincoli complessi (Snake Mode, Ordine Chiavi).
- **Z3 + Euristica A* (Il nostro approccio)**: Più lento per labirinti vuoti, ma incredibilmente robusto per vincoli complessi.
