# Relazione Progetto: Maze Solver con Z3 e Bounded Model Checking
**Corso:** Computabilità, Complessità e Logica (CCL)

Questa relazione illustra come il progetto _Maze Solver_ applica concretamente i concetti teorici del corso, in particolare nell'ambito della Logica Proposizionale, della Soddisfacibilità (SAT) e della Verifica Formale.

---

## 1. Formalizzazione del Problema
Nel corso abbiamo visto come un problema decisionale possa essere formalizzato tramite linguaggi e macchine astratte. In questo progetto, il problema è la **raggiungibilità** in un grafo (il labirinto).

*   **Stati**: Ogni cella $(r, c)$ del labirinto è uno stato.
*   **Transizioni**: Le regole di movimento (su, giù, destra, sinistra) definiscono la relazione di transizione tra stati.
*   **Obiettivo**: Esiste una sequenza di stati $s_0, s_1, \dots, s_k$ tale che $s_0 = Start$, $s_k = End$ e ogni $(s_i, s_{i+1})$ sia una transizione valida?

Questo è un classico problema di **Model Checking**, che noi risolviamo tramite **SAT/SMT Solving**.

## 2. Collegamento con la Logica (SAT & SMT)

### Il Problema SAT
Il cuore del progetto è **Z3**, un SMT Solver (Satisfiability Modulo Theories).
*   **SAT (Boolean Satisfiability)**: Il problema di determinare se esiste un assegnamento di verità che rende vera una formula proposizionale. Come visto nel **Teorema di Cook-Levin**, SAT è il primo problema dimostrato **NP-Completo**.
*   **SMT**: Z3 estende SAT. Invece di sole variabili booleane, usa predicati su teorie specifiche (es. Aritmetica Lineare per interi). Nel nostro caso, usiamo variabili intere (`Int`) per le coordinate, ma la struttura logica sottostante è riconducibile a SAT.

### Codifica Logica (Encoding)
Per trasformare il problema del labirinto in una formula logica $\phi$, usiamo la tecnica del **Bounded Model Checking (BMC)**.
Costruiamo una formula $\phi_k$ che è soddisfacibile **se e solo se** esiste un percorso di lunghezza $k$.

La formula è una congiunzione di vincoli (simile alla **Forma Normale Congiuntiva - CNF**):
$$ \phi_k = I(s_0) \wedge \bigwedge_{i=0}^{k-1} T(s_i, s_{i+1}) \wedge G(s_k) $$

Dove:
1.  **$I(s_0)$ (Stato Iniziale)**: $x_0 = start\_x \wedge y_0 = start\_y$
2.  **$G(s_k)$ (Goal)**: $x_k = end\_x \wedge y_k = end\_y$
3.  **$T(s_i, s_{i+1})$ (Transizioni)**: Vincola il movimento valido.
    $$ (x_{i+1} = x_i \pm 1 \wedge y_{i+1} = y_i) \vee (x_{i+1} = x_i \wedge y_{i+1} = y_i \pm 1) $$
    *(Corrisponde alla disgiunzione delle possibili mosse)*
4.  **Vincoli di Dominio (Muri)**: $\neg Wall(x_i, y_i)$. Nel codice:
    $$ \forall t, \forall (r,c) \in Muri, \neg (x_t = c \wedge y_t = r) $$

Questa struttura rispecchia fedelmente la definizione di **validità di una deduzione**: se le premesse (regole del gioco) sono vere, allora la conclusione (raggiungimento del goal) deve essere derivabile.

## 3. Strategia di Risoluzione e Complessità

### Bounded Model Checking (BMC)
L'approccio "Bounded" (limitato) cerca soluzioni incrementando la lunghezza del percorso $k$:
1.  Prova per $k=1$. Esiste un modello per $\phi_1$? (Z3 risponde UNSAT)
2.  Prova per $k=2$. (UNSAT)
...
3.  Prova per $k=N$. (SAT -> Trovato percorso!)

Questo si collega al concetto di **Semidecidibilità** (o decidibilità per linguaggi finiti). Dato che il labirinto è finito, il diametro è limitato, quindi il processo termina sempre (è Decidibile).

4.  **Ottimizzazioni del Solver (Novità)**
    *   **No U-Turns (Symmetry Breaking)**:
        $$ \forall t \ge 2 . \neg (x_t = x_{t-2} \wedge y_t = y_{t-2}) $$
        Impedisce cicli banali di lunghezza 2 ($A \to B \to A$), riducendo il fattore di ramificazione. In una BFS questo è implicito (non si ri-aggiunge il padre alla coda), ma in SAT va esplicitato.
    *   **Distance Envelope (Pruning Euristico)**:
        $$ \text{Dist}(pos_t, Goal) \le (k - t) $$
        Se al passo $t$ mancano $k-t$ passi alla fine, ma la distanza geometrica è maggiore, quel ramo è inutile.
        *Confronto con algoritmi classici*: Questa è l'idea alla base di **A\*** (A-Star) o **IDA\***. In Z3, lo implementiamo come un vincolo *dichiarativo*: "Non considerare stati che violano questa proprietà geometrica".

### Euristiche e Ottimizzazione (Precedenti)
5.  **Lower Bound per Chiavi**:
    *   Stimiamo un lower-bound risolvendo un problema simile al **TSP (Traveling Salesman Problem)** in modo approssimato (Greedy Nearest Neighbor) per evitare chiamate inutili al solver.

### Complessità
*   Il problema del labirinto su griglia è in **P** (risolvibile con BFS in tempo polinomiale).
*   Noi lo stiamo riducendo a SAT (che è **NP-Completo**).
*   *Domanda d'esame*: "Perché usare un solver NP-completo per un problema P?"
    *   *Risposta*: Per la **flessibilità espressiva**. Aggiungere vincoli complessi come "passa per i checkpoint A, B, C in qualsiasi ordine" rende il problema più difficile da modellare con semplici algoritmi imperativi, ma banale per un solver logico (basta aggiungere clausole alla congiunzione).

## 4. Dimostrazione Pratica (Demo)
Durante la dimostrazione al docente mostreremo:
1.  **Generazione**: Creazione di un'istanza del problema.
2.  **Risoluzione Base**: Z3 trova il percorso minimo.
3.  **Vincoli Aggiuntivi (Chiavi)**: Qui Z3 brilla. Aggiungendo vincoli globali ($\exists t . Pos(t) = Key_i$), il solver deduce automaticamente che deve deviare dal percorso più breve per soddisfare la formula. È un esempio tangibile di **Deducibilità Semantica**.

---
**In sintesi**: Il progetto è un'applicazione pratica della logica proposizionale e del primo ordine (uso di variabili e quantificatori limitati) per risolvere problemi di reachability, dimostrando la potenza dei metodi dichiarativi rispetto a quelli imperativi.
