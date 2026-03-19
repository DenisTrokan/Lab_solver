# Introduzione al Progetto: Formalizzazione Logica di un Labirinto
**Corso**: Computabilità, Complessità e Logica

## 1. L'Ambiente Fisico (Il Dominio del Problema)
Il nostro progetto si basa sulla risoluzione del classico problema di fuga da un labirinto, ma lo fa avvalendosi della Logica Formale.
L'ambiente consiste in una griglia 2D di dimensioni $W \times H$. 
Ogni settore o cella $(x, y)$ può trovarsi in due soli stati mutuamente esclusivi:
*   **Percorribile** (`0`)
*   **Muro/Ostacolo** (`1`)

Sulla griglia viene posizionato un Agente con il compito di trovare una traiettoria finita che lo porti dalla coordinata fissa di **Partenza** `(0,0)` fino ad una coordinata predeterminata di **Arrivo**.

La complessità emerge quando nel labirinto vengono introdotte delle **Chiavi** (obiettivi intermedi). In questi scenari, l'agente non è più libero di raggiungere l'arrivo nel minor tempo possibile; egli deve invece trovare un percorso che passi obbligatoriamente per tutte le chiavi presenti,prima di arrivare al Goal (Arrivo).

### 1.1 La Topologia del Labirinto (Da Albero a Grafo)
*(Nota Implementativa: Nel codice Python non manipoliamo oggetti `Nodo` o `Arco`. Il set di dati è esclusivamente una fredda **Matrice 2D** di zeri e uni. Tuttavia, i corridoi e le loro intersezioni generano forme matematicamente formalizzabili)*.
Il labirinto che diamo in input non è una banale matrice casuale: l'algoritmo di scavo interno (tramite DFS) edifica in partenza un *Albero di Copertura* (Spanning Tree) perfetto sulla griglia, ossia una matrice in cui esiste costantemente **uno e un solo percorso** ("zero" adiacenti) per giungere da un punto A a un punto B. 
Tuttavia, abbattendo in seconda battuta il 3% dei muri restanti in modo randomico, alteriamo radicalmente la topologia matematica dell'ambiente: lo trasformiamo da semplice "Albero" a vero e proprio **Grafo Ciclico**.
Inoculando dei "loop" (cicli) nel grafo, generiamo bivi complessi e strade circolari. Questa natura ramificata generalizzata è ciò che crea il profondo bisogno computazionale del Bounded Model Checking: l'utilizzo di Z3 serve proprio a navigare formalmente questi cicli per estrarre la radice a lunghezza minima (ottimo globale), tranciando via i "loop" logomorfici.

## 2. I Vincoli
Il movimento all'interno del labirinto non è libero.
1.  **Limiti di campo:** È impossibile oltrepassare i bordi fisici della mappa 2D.
2.  **Spostamento Unitario:** Per ogni istante di tempo Discreto $t$, l'agente può percorrere solo 1 passo sulla griglia in orizzontale o in verticale.
3.  **Muri:** La collisione con una coordinata precedentemente definita come "Muro" deve essere matematicamente negata.

## 3. L'Approccio Classico vs L'Approccio Dichiarativo
In un normale paradigma di programmazione imperativa, si affronterebbe la sfida scrivendo un algoritmo imperativo. 
Spiegherebbe passo-passo al computer **come** visitare l'albero delle stanze (es. con Algoritmo $A^*$ o BFS), memorizzando i bivi passati in uno Stack o in una Coda, e scrivendo codice dedicato per calcolare la permutazione più rapida delle $C$ chiavi da visitare (un problema NP-Hard, ovvero parente stretto del Commesso Viaggiatore).

### Il Nostro Approccio: Bounded Model Checking con SMT
In questo progetto abbandoniamo il metodo "imperativo" e utilizziamo un approccio **Dichiarativo**.
Non stiamo scrivendo un algoritmo per *esplorare il labirinto*. Stiamo invece scrivendo un programma Python (`solver.py`) che **traduce le regole fisiche del nostro mondo in equazioni matematiche (SMT)**.

Utilizziamo una tecnica nota come **Bounded Model Checking (BMC)**. 
Questa tecnica fissa un clock che, partendo da 1 e aumentando progressivamente, chiede a Z3: 
*"Esiste o non esiste una soluzione numerica per cui le coordinate del protagonista soddisfino l'equazione d'arrivo al tempo $K$, senza aver sfondato muri al tempo $K-1$, $K-2$, ecc..?"*

Se i numeri tornano logicamente (la logica decreta la stringa *Vera*), Z3 restituirà il modello esatto delle coordinate (SAT!). Se l'equazione partorisce una contraddizione (magari l'arrivo necessiterebbe di calpestare un muro), Z3 garantisce la bocciatura del percorso (UNSAT) evitandoci inutili tentativi umani alla cieca.

