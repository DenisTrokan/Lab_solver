# Funzionamento delle Chiavi in Z3 (Bounded Model Checking)

Questo documento esplora in dettaglio come viene modellata la raccolta delle chiavi nel *Maze Solver*, analizzando il passaggio dal problema informale alla formula logica risolta da Z3.

## 1. Il Problema Informale
In un labirinto standard, l'obiettivo è trovare una sequenza di mosse valide dal punto di partenza **Start** al punto di arrivo **End**.
Quando aggiungiamo le **chiavi**, il problema cambia: l'obiettivo diventa trovare un percorso valido da **Start** a **End** che **passi obbligatoriamente sopra ogni chiave** presente sulla griglia.

In un algoritmo imperativo classico come la Ricerca in Ampiezza (BFS), questo richiederebbe di:
1. Trovare tutte le permutazioni possibili dell'ordine di raccolta delle chiavi.
2. Eseguire la BFS tra ogni nodo intermedio (Start $\rightarrow$ Chiave 1 $\rightarrow$ Chiave 2 $\rightarrow$ End).
3. Gestire uno stato complesso (es. `(x, y, chiavi_raccolte)`).

In Z3, grazie all'approccio dichiarativo, non dobbiamo codificare la nozione di "ordine di raccolta". Dobbiamo solo esprimere una **proprietà vincolante** sull'intero percorso.

## 2. La Modellazione Logica (L'Encoding in Z3)

Nel paradigma del *Bounded Model Checking* (BMC), calcoliamo percorsi di lunghezza fissa $k$. Il percorso è rappresentato da una sequenza di variabili intere:
$(x_0, y_0), (x_1, y_1), \dots, (x_k, y_k)$

Supponiamo di avere una singola chiave alla coordinata `(kc, kr)`.
Il nostro obiettivo logico è dire: *"Nel percorso di $k$ passi, deve esistere almeno un istante di tempo $t$ (tra $0$ e $k$) in cui il giocatore si trovava esattamente sulla chiave"*.

### L'espressione del Quantificatore Esistenziale ($\exists$)
In logica del primo ordine, la proprietà si scrive come:
$$ \exists t \in [0, k] : (x_t = kc) \land (y_t = kr) $$

Tuttavia, Z3 non elabora i quantificatori su liste in modo nativo su cicli `while` standard. Dobbiamo "srotolare" (unroll) questo quantificatore esistenziale in una grande disgiunzione logica (OR) che copra ogni singolo passo temporale.

### La traduzione Python/Z3
Ecco il framing esatto utilizzato nel codice:

```python
# Per ogni chiave (kr, kc)...
key_visited = Or([ And(path_x[t] == kc, path_y[t] == kr) for t in range(k + 1) ])
s.add(key_visited)
```

La *List Comprehension* in Python genera una lista di espressioni logiche, una per ogni tempo $t$, e la funzione `Or()` di Z3 le unisce. Se $k=5$, la formula generata è letteralmente:

$$
\begin{align*}
\Phi_{chiave} = \ & (x_0 = kc \land y_0 = kr) \ \lor \\
                  & (x_1 = kc \land y_1 = kr) \ \lor \\
                  & (x_2 = kc \land y_2 = kr) \ \lor \\
                  & (x_3 = kc \land y_3 = kr) \ \lor \\
                  & (x_4 = kc \land y_4 = kr) \ \lor \\
                  & (x_5 = kc \land y_5 = kr)
\end{align*}
$$

Basta che **una sola** di queste clausole sia Vera, affinché l'intero `Or()` sia Vero, soddisfacendo il vincolo.

## 3. L'Impatto sulla Soddisfacibilità (SAT) e l'Esecuzione

In che modo questo vincolo altera il comportamento del Solver?

### Scenario A: Nessuna Chiave
Se Z3 sta cercando la soluzione a $k=12$ passi (distanza minima Start-Goal), trova un percorso diretto. Tutte le variabili $(x_t, y_t)$ si incastrano per arrivare a destinazione. Il risultato è `SAT`, e l'algoritmo termina.

### Scenario B: Con la Chiave fuori dal percorso originario
Supponiamo che la chiave sia lontana dal tragitto più breve.
Al passo $k=12$, Z3 genera un percorso per il traguardo. Z3 controllerà l'enorme `Or` generato dalla formula della chiave.
Poiché il percorso diretto non tocca mai `(kc, kr)`, l'espressione `Or` valuterà il falso per ogni $t$. Dato che abbiamo aggiunto questo `Or` come un vincolo obbligatorio all'interno dell'istanza del solver (con `s.add()`), l'intera formula diventa contraddittoria.

Il verdetto sarà **`UNSAT`**.

### La magia del Bounded Model Checking
L'algoritmo Python reagisce al verdetto `UNSAT` incrementando la profondità della ricerca a $k=13$, costruendo nuove variabili per il tempo 13, aggiungendole all'`Or` della chiave, e riprovando.

Questo processo continua ($k=14$, $k=15$, $\dots$) finché Z3 non ha a disposizione un "serpentone temporale" di variabili abbastanza lungo da potersi snodare verso la chiave e poi verso il traguardo.
Solo nel momento esatto in cui il percorso generato soddisferà i vincoli fisici del labirinto, il Goal, **E** anche l'`Or` della chiave, la formula "scatterà", restituendo `SAT` con l'esatto cammino percorso.

## 4. Differenza tra le Condizioni Z3 e JavaScript (Frontend vs Backend)

Potresti notare che giocando manualmente nella pagina web, se raggiungi il traguardo verde senza prendere le chiavi, vinci comunque. Quando chiedi a Z3 di farlo, invece, è costretto a deviare.

* **Z3 (Backend)**: È implacabile. Se aggiungiamo una regola formale all'oggetto `Solver`, Z3 la rispetta al 100%. Senza l'`Or` risolto positivamente, restituisce errore.
* **JavaScript (Frontend)**: Nel client, controlliamo solo la collisione con il quadratino finale (`playerPos.r === currentMaze.end[0]`). Non c'è alcun frammento di codice che conta le chiavi prese dall'utente prima di permettere la vittoria.

Questi comportamenti disallineati dimostrano che Z3 non lavora tramite logica di "videogioco", ma obbedisce ciecamente alle stringenti regole matematiche che gli imponiamo.
