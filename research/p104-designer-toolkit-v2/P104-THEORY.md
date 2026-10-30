# The P104 frontier word: what it looks like, and why
Scope: write-up of the structure of the frontier word and of the floor arguments. No new computation. Paths are relative to this directory unless stated; references to `ext/...` and to the original lane notes name research-workspace artifacts that are not part of this package (the statements and numbers are given in full here).

---

## Summary (one page)

**The claim, stated so it cannot be over-read.** The frontier word **#6030** (kappa **.003125811557911897**, R0eq 8022.4 against the bar 8015.2) is
(i) built on a code and a tiling that are *forced*, (ii) *rebuildable from rules* on all five of its sides at exactly its own kappa, and
(iii) *locally rigid* in every model we tested. It is **not** proved globally optimal. The only proved lower bound is **794.53 R0 (about 10% of the word; PROVED under SCOPE own=22/owns=18, R0 <= 8000)**.
"Optimal P104 word" in this document therefore means "a word whose every local choice is explained by three principles and cannot be improved by any edit we can express".

**Forced structure (PROVED/EXACT).**
- The decoder code is E8. Any rank-8 completion of the P104 pattern is the E8 line Gram up to diagonal gauge (Theorem U; prior art #1212).
  The rank is >= 8 (the clique number is 8). The rank-9 door is closed inside the natural family F (Theorem R9F), so the 56 owned ranks (8 roots x 7) are a floor and a tie.
- Parity: ports, l_k and u_k all have odd weight, so q(d) = wt(d)/2 mod 2 splits directions into a D3 class (q = 0) and an orthogonal class (q = 1).
  An orthogonal ("non-D3") pairing has an exact parity obstruction.
- Tiling: the D3 cosets paired by XOR 384 give 14 octets. T = 384 is the unique octet system that tiles the residual E with rank-1 blocks.
  Its octet frames O_r have no readers, so a dim-4 octet frame can only be a cleanup hub.

**Cost law (SPEC + EXACT).** 1/kappa = 130.27 + .02364 (R0 + 380 (paid - 56)). R0 is a sum of chain taxes, and the marginal tax of a stop is concave in its level.
Events are free. The exact split is R0 = F(skeleton) + Mains - L(lifetimes). Against the octet word P1, #6030 pays +32 in skeleton and +455 in mains, and buys 872 of lifetimes.

**Three principles (PRINCIPLES).** P1 cost, P3 nesting, P4 instance geometry. P2 (span conservation, including the new outflow-corank law P2c) is a theorem of P3.
17 of the ~25 pinned rules derive from these, 4 more derive given one measured premise, and 7 do not reduce.

**Five sides, each rebuilt from rules at #6030's exact kappa.**
| side | rule source | rebuilt |
|---|---|---|
| markets (duals G_r) | ALIGNLAW, MKT4, PSOLVE6030 | 12/14 exact; 2/14 at the measured price of one unconstructed owned bracket (6.18 R0 each) |
| hubs (octet frames O_r) | HUBRULES, OWNEDHUB, TOPGEN | 18/18 public end frames + 4 owned; 14 jointly |
| routing (Y reads) | YROUTE | 55/55 octet pairs, unique solution = swarm; 131 sites jointly |
| skeleton (source parks) | SKELORIGIN | 12/14 octets exact, 2 at equal kappa (free ties) |
| signal (root feeds/returns) | SIGPIN | 8/8 roots, 16 steps jointly |
COMPOSE puts all five in one word: kappa .003125811557911897, SPAN5/JR 0 on 999/999 frames, native 0 bad of 2922, 22860 events (after MKTCOMPACT).
FULLWORD (the original lane notes (not shipped), ext/FULLWORD/out/FULL_final.json.gz): all 22 hubs, all 14 market duals (compact), skeleton, routing and signal in ONE word: kappa .003125811557911897 exact, 23333 events, SPAN5/JR 0, native 0 bad, shipcheck passes; 85.0% of events identical to #6030, 15.0% rebuilt/changed (one signal step kept).

**Honest ledger (EXACT taxes, no-mechanism yardstick).** Markets 73.3 + twin-tied ends 143.2 + other ends/births 60.4 + reader-level Y reads 447.7 [391.7, 505.9]
= **724.6 [668.6, 782.8]** R0. The older forced-skeleton figures (markets 241, hubs 277) are superseded.

**Rigidity (EXACT, scoped).** About 3,200 exact edit tests on #6030 (SURGERY, SURGERY2, RESKEL6030, PSOLVE6030) found 0 improvements. 12 of 14 market columns are
OPTIMAL = swarm tax in the principle column model (the 2 owned-assisted duals are outside its kinds). Every legal skeleton alternative prices at dk = 0 or worse.

**Open.** (1) The skeleton class: no from-scratch generator reaches #6030's skeleton (the best from-scratch word is kappa .0027748). (2) Global optimality
(the gap between 794.53 and about 8000 is a factor of 10). (3) The 7 non-reducing regularities, above all the exit rule E.

---

## 0. Conventions

### 0.1 Status labels (used on every claim)
| label | meaning |
|---|---|
| **SPEC** | part of the verifier or problem statement (legal.py, the kappa formula) |
| **PROVED** | a proof is written here or in the cited note (some audited, as stated) |
| **EXACT** | a certified computation (rational / mod-p arithmetic, exact replay, `tk price`) on a stated instance |
| **MEASURED** | a census on #6030 (or #5907): a regularity, not derived |
| **MODEL** | needs an extra assumption (stated) |
| **CEILING** | a relaxation (optimistic bound) |
| **SCOPE** | a PROVED statement that rests on a stated measured constant |
| **OPEN** | not settled |

### 0.2 Objects
- **Ports** p_i (104), **readers** q_j (the same 104 vectors on the Y side), in F2^9 (frames are subspaces, dims 0..9; F0 = {0}, F9 = everything).
- **Registers**: X_i (one per port), Y_j (one per reader), public helpers H, and owned registers (signal roots). A register has a **chain**: it is born at dim b,
  holds one frame per dim, ascends with nested frames, and ends at dim e. Endpoint rule (SPEC): helpers and X end at their initial value; Y_j ends at y_j + x_j.
- **Residual** E = M - I on the 4992 orthogonal port pairs (|E| = 1/2). The **signal** is the rank-8 part, delivered by 8 owned roots (l_k, u_k, H_k = u_k^perp).
- **D3** = {120, 85, 75, 51, 102, 30, 45}: it splits the ports into 28 cosets (20 x 4 + 8 x 3).
  **Octet** r: a D3 coset c together with c XOR 384 (14 octets: 6 of 8 ports, 8 of 7 ports). Its span is the **octet frame O_r** (dim 4),
  its **dual** is G_r = O_r^perp (dim 5), and Q_j = q_j^perp (dim 8) is Y_j's final frame.
- **Words**: #6030 (frontier, `words/6030.json.gz`); #5907 (its predecessor, same census where stated); P1 = the octet residual word p1nr (8133.2 R0, no lifetimes).

### 0.3 A note on the kappa print
OWNEDHUB and PSOLVE6030 print the base as .003125811557911862; every other lane prints .003125811557911897. Both are #6030 printed at different display
precision or by a different price path; no lane reports a kappa change between them. "Exact kappa" below means "equal to #6030 under `tk price`".

---

## 1. Problem and cost law

### 1.1 The law (SPEC, used lane-wide; constants not re-derived here)
**1/kappa = 130.27 + .02364 (R0 + 380 (paid - 56))**, with R0 = sum over registers of tax(chain) and paid = owned MOVE ranks.
- tax(chain) = D ln D - sum_i r_i ln r_i, where D = e - b and r_i are the jump lengths (SPEC, legal.py).
- Bar kappa .0031274 = **R0eq 8015.2**. #6030 = R0eq 8022.4.

### 1.2 Facts of the cost law (PROVED; PRINCIPLES sec 2)
- **(a) Concavity.** A stop at d inside a jump a -> b costs mu(a,d,b) = (b-a)ln(b-a) - (d-a)ln(d-a) - (b-d)ln(b-d) > 0.
  *Proof.* d^2 mu / dd^2 = -1/(d-a) - 1/(b-d) < 0. So the marginal tax of a stop is concave in its level, and the cheapest feasible level is an endpoint of the feasible interval. ∎
- **(b)** A single jump costs 0: tax(0,d) = tax(d,9) = tax(0,9) = 0. Lifetimes (multi-stop chains), not stops, are the large cost.
- **(c)** The dim-7 stop between 6 and 8 costs 2 ln 2 = 1.386 on any chain. This is the source of exact ties (a stop at 7 on a proxy vs on a newborn).
- **(d)** Events do not enter kappa (only the event-count literal, 26000, bounds them).
- Constants used throughout:
  | constant | value | meaning |
  |---|---|---|
  | 6 ln 6 - 5 ln 5 | 2.70 | a dim-5 stop on (0,6,...); an X stop at 4 on (1,2,3,9) |
  | 9 ln 9 - 6 ln 6 - 4 ln 4 | 3.48 | born at 5 instead of 0 |
  | 2.70 + 3.48 | 6.18 | a full birth/end save at an O or G frame |
  | Y stop | <= 5.55 | |
  | courier | >= 6.15 (8.43 for (0,3,8,9); 9.89 for a copy (0,3,6,9); 8.40 un-identify) | |

### 1.3 The exact additive split (EXACT; LAWFIRST sec 1)
R0 = F(skeleton) + Mains(chains) - L(lifetimes) [+ signal carriers], where F is every helper's tax with birth forced to 0 and end forced to 9 (stop set unchanged),
and L = F - actual helper tax. Error 0 on all reproduced words.

**Where #6030 sits against P1 (EXACT, residual-only split; ALIGNLAW sec 1a).**
| | F (helpers forced 0->9) | X | Y | L | R0 |
|---|---|---|---|---|---|
| #6030 residual | 6524.5 | 1074.0 | 1022.2 | 872.0 | 7748.6 |
| P1 (octet p1nr) | 6492.1 | 767.0 | 874.0 | 0 | 8133.2 |
| difference | **+32** | **+307** | **+148** | **-872** | -385 |
The 385 R0 lead is bought in the mains (+455) and spent on lifetimes, not on the skeleton. The brief's "+321 skeleton premium" compared a word with signal against a residual-only word (corrected, sec 5.3).
Of the +32, about 224 is lifetime-enabling helper stops, so #6030's piece skeleton is about 190 *cheaper* than P1's: it uses fewer, longer helpers (EXACT, hshape.py).

---

## 2. Forced structure: code, parity, tiling

### 2.1 The code is E8
**Theorem (r >= 8) (EXACT; SIGNCODE2).** The graph of non-orthogonal port pairs has clique number 8. On a clique, CS = I_8, so any decoder has rank >= 8:
at least 8 distinct signal versions, for any coefficients and geometry.

**Theorem U (PROVED; two proofs; prior art).** Every real 104 x 104 M of rank 8 with M_ij = delta_ij on all non-orthogonal pairs (diagonal included) equals
D M0 D^-1, where M0 is the Gram matrix of the 104 E8 lines and D is an invertible diagonal.
- *Proof outline (ROOTARCH sec 3, computer-assisted; `ext/ROOTARCH/uniq.py, p1global.py, p2signed.py`).*
  - P0: the 759 cliques of size 8 are affine 3-flats. M[Q,Q] = I_8 and rank 8 give M = M[:,Q] M[Q,:]. Every port outside Q is orthogonal to exactly 4 clique members.
  - P1: 1 = M_ii = sum over those 4 of pi_iq (pi = M_iq M_qi, gauge invariant). The global system (72,864 equations, 2,496 unknowns) has full rank, so pi = 1/4 on every orthogonal edge.
  - P2: 4-cycle products are forced to -1/16. The cycles have full rank over Q (2393), and the GF(2) rank (2392) fixes the signs up to E -> -E. That flip has rank 104, not 8. ∎
- A hand proof (UNIQ8, Sonnet audit PASS, `cards/UNIQ8/THEORY.md`) extends it to any field of char != 2 for the iff zero pattern with nonzero diagonal.
- **Prior art:** this is a special case of the swarm's merged #1212 (rank-8 rigidity). Cite #1212; do not present Theorem U as new.
- **Corollary C1 (EXACT up to a standard root-system fact).** A hyperplane of R^8 holds <= 55 of the 104 lines. So every nonzero row/column-space vector has >= 49 nonzeros.

**The 56 owned floor (PROVED; scope: exactly 8 distinct read vectors; ROOTARCH sec 4).** Owned forests with copies, additions along branches and public relays all cost
>= 8 x 7 = 56. Support >= 49 > beta(7) = 36 forces dim-8 gathers, and every landing depth costs >= 7. This is tight (#5795's 56).

**Theorem R9F (PROVED inside family F; RANK9 sec 2).** Every 9-signal factorisation of a rank-9 completion M = D M0 D' + beta gamma^T costs >= 56 owned ranks. A tie needs
one degenerate rk_s = 1 signal. Multi-landing does not help.
- Scope: outside F only SAMPLED. 38/38 converged ALS completions lie in F; a small-basin non-F component is not excluded (escape E1).

So the "paid - 56" term of the law is 0 at the optimum of every family we can reason about. **The code is fixed. The design problem is R0.**

### 2.2 Parity (EXACT; NOND3, LKMEET)
- On the even space, q(d) = wt(d)/2 mod 2. Directions with q = 1 (wt 2/6) give only orthogonal port pairs; directions with q = 0 (wt 4/8, D3's class) give only non-orthogonal pairs.
- **Parity obstruction (EXACT, all 5356 pairs).** par(p_i ^ p_k, p_i) = 1 - par(p_i, p_k). So for an orthogonal pair along d, the mirrored reader pair is never jointly
  orthogonal to span(p_i, p_k). The self-dual design that makes D3 coherent is impossible for q = 1 directions.
  - In the route-B model the best non-D3 joint pairing is +1244 R0, about -8% kappa (MODEL, provisional kill with escape routes; NOND3 sec 3).
- **Parity lemma (EXACT; LKMEET sec 1).** Every port, l_k and u_k has odd weight; D3 directions and 384 are even. So p ^ l_k is never a port.
  - A dim-d frame holds <= 2^(d-1) ports, and a frame containing l_k holds <= 2^(d-1) - 1.
  - In particular a 2+2 (4-port) frame never contains l_k, and a reader frame containing u_k holds <= 3 readers.
  - D3's 8 three-cosets complete {u_0..3, l_4..7}, so each root has one cheap side. This explains the 4 + 4 split of roots into feeder-aligned and source-aligned (sec 4.5).
- Complementary classes in #6030: market Y-cliques are D3 (q = 0) cosets. Cross-octet co-reading Ys have orthogonal normals at 125/131 sites (q = 1; MEASURED, base rate 46%).

### 2.3 Tiling (EXACT; QUADHUB sec 4, audited by TILEAUDIT)
- For each 2-dim W in D3 there are 3 pairings, T in {135, 263, 384}. Meetable entry (j,i): i in a dim-3 port frame g, j in a dim-3 reader frame h, g ⊥ h.
  | T | covers E | blocks | ranks |
  |---|---|---|---|
  | 135 | 4608/4992 | 316 | - |
  | 263 | **exactly once** | 364 | 208 rank-3 + 156 rank-4, **no rank-1** |
  | 384 | **exactly once** | 364 | **336 rank-1** + 16 rank-3 + 12 rank-4 |
- **Statement (TILEAUDIT wording).** Among all 512 global XORs and all 2187 per-W pairings, exactly 2 tile E exactly (263 and 384). **384 is the unique one with the rank-1 property.**
  Not tested: octets pairing cosets of different W, unequal octets.
- Block graph: 28 full-rank coset blocks + 56 six-cycles (rank 3 each). Component rank 264; the sum of block ranks is 432 = "crossings".
  432 matches the ~440-448 boundary pieces measured on b0 and the swarm. (The early wording "364 rank-1 blocks" was loose; corrected.)
- **Octet frames have no readers (EXACT, 14/14).** So no live piece can sit at O_r, and **O_r is a pure cleanup frame**: only registers that are done may stop there (QUADHUB sec 1).
- The swarm realises the tiling (MEASURED):
  - #5907 is octet-laminar at both ends, and all 62 dim-5 births sit at O^perp (the 16 dim-7/8 births do not);
  - 162/187 of its 3 -> 6 helper MOVEs carry a block piece (no null test was run).
  - #6030 reproduces the dual census exactly (MARKETORIGIN).
- The meet model's 8518 forced residual is MODEL and was not verified by the audit.

**Summary of sec 2.** E8 fixes the signal. Parity forces D3 pairs. The rank-1 tiling forces the octets T = 384. Reader-free octet frames force hubs to be cleanup frames, and their duals are the market frames.
None of this is a template copied from the swarm: each piece falls out of E.

---

## 3. The principles and the derivation map (PRINCIPLES.md)

### 3.1 The principles
- **P1 Cost (SPEC).** kappa depends only on R0 (chain taxes) and the paid owned ranks; events are free. Facts 1.2(a)-(d).
- **P3 Nesting (SPEC F1/F2).** One frame per dim per register, ascending and nested. Two registers interact only at a common frame. A Y's frames lie inside Q_j.
  - **P3a content-in-frame (PROVED).** The x-support of a public register lies on the ports of its current frame.
    *Proof.* Induction over the program: X_i starts at <p_i>, an ADD at a common frame f moves only f-supported content, and a MOVE goes to a superset frame.
    Owned reads are exempt. ∎ Checked on #6030 (cif.py): 18372 public ADDs, 0 violations outside owned-tainted registers.
  - **P3b dim budget.** Above G a register gains at most one piece direction per dim.
- **P4 Geometry (instance data).** Sec 2: the code, D3 cosets, the T = 384 tiling, reader-free O, and parity.
- **P2 Conservation (THEOREM of P3 + op semantics).**
  - (P2x) span(arrivals) = span(departures) in x where nobody ends (SPAN5, a projection of JR);
  - (P2j) the same over junk, with the junk-ratio law (PROVLP);
  - **(P2c) outflow-corank law (PROVED, count form).** Let Phi_phi map the departures at a birth frame phi to the uncleanable finals (Ys, and registers ending below F9).
    *Proof.* The block T at phi is invertible. A newborn's junk must vanish from those finals; a 0-born register's junk can be cancelled by F0 pre-reads.
    So the newborn columns of T are |N| independent vectors in ker Phi_phi, and **#newborns(phi) <= #registers(phi) - rank Phi_phi**. ∎
    - EXACT check: the 3-proxy + 1-skip G0 variant (7 registers at G, rank 4) is UNSOLVABLE in full coordinates.
    - **OPEN (placement form):** "the 0-born registers span the outflow". It holds under the realiser's load convention only (PRINCIPLES gap 0).

**Minimality (PROVED in the sense stated).** Irreducible = {P1, P3, P4}. P1 is the only source of "which feasible option", and P3 the only source of feasibility.

**Two corrections to the conjectured principle list.**
- K5 ("never park at the reader's final frame") *contradicts* P1, since the final-frame park is tax-cheaper. It is a junk effect: MODEL, MEASURED.
- "Defer cleanup to F9" is not a cost rule: it follows from P3 (every F9 row is a unit row) plus free events.

### 3.2 Derivation map (compressed; full table in PRINCIPLES sec 3)
| rule | side | from | status |
|---|---|---|---|
| M1 #proxies >= rank of served-Y space (4, or 3 in a triangle) | market | P2c | PROVED-necessary |
| M2 market saturated: births = members - rank | market | P1 + P2c | PROVED (column model) |
| M3 pay rule 3.48/birth - 2.70/proxy | market | P1 | PROVED |
| M5 Y-clique = D3 coset; triangle anchor = 4th affine point | market | P4 | EXACT |
| B1 <= 2 pieces per member by dim 7, so 8 members | top | P3a + P3b | PROVED |
| B2 served Ys = residual rows | top | P2x | EXACT |
| B3 unique pair matching inside both Q's | top | P3 + P2x | PROVED-necessary, EXACT unique |
| B3b triangle: single-Y pair meets at Q (no d7 stop) | top | P1 + P3 | PROVED |
| H0 hub of octet r is at O_r | hub | P4 + P3 | PROVED |
| H1/H2 span conservation; departures pinned by D | hub | P2 | PROVED / EXACT |
| H3 8 = 4 up + 4 down; ender leaves as e_a + v_a | hub | P2 + P3 | EXACT ("up = octet characters" MEASURED) |
| H4 late visitors span the down space | hub | P2 (Redundancy Lemma) | PROVED |
| T1-T3 twins: arrival values count; twin iff P-span circuit; tied <= circuits | hub | P2 (JR) | PROVED |
| T5 hub pay rule 4 x 6.18 - (down rank) x 2.70 | hub | P1 + H4 | PROVED |
| A1 one register cannot sit in two dual cones | routing | P3 | PROVED |
| R1 Y_j reaches s only at f_d(s) <= Q_j | routing | P3 | PROVED |
| R2 Y stop (<= 5.55) beats courier (>= 6.15) | routing | P1 | EXACT |
| R0 direct low read iff c <= e, free slot, nests | routing | P3 + P3a | PROVED-necessary; sufficiency MEASURED 131/131 |
| R4 exit E implies q_low ⊥ q_high | routing | P3 + parity | PROVED given E |
| S0 sandwich L <= f <= U | skeleton | P3 + P3a | PROVED |
| S2 level = cheaper end | skeleton | P1(a) | PROVED |
| S1 closure f = L or f = U | skeleton | P1 + P3 | PROVED given S0 is the only constraint (MEASURED 504/507) |
| S3 completion = span(piece) | skeleton | P3a + P4 | PROVED lower bound; tight 101/131 |
| S5/K1 read in place before parking/copying | skeleton | P1 + P3 | PROVED |
| C-F9 defer cleanup to F9 | all | P3 + free events | EXACT |
Count: 17 derive (PROVED/EXACT), 4 derive given one measured premise, 7 do not reduce (sec 8.3).

### 3.3 Generativity (EXACT; PRINCIPLES sec 5, PSOLVE6030)
A CP-SAT column solver that knows only P1-P4 (no pairing, proxy, birth or frame-list rule) re-derives market columns at the swarm's tax:
- f118 (8-port): OPTIMAL 69.092, **identical** to the swarm (pair frames 969-972, 4 x (0,5,6,7,8,9) + 4 x (5,6,7,8,9));
- f1049 (triangle): OPTIMAL 57.364, an equal-tax P1(c) variant.
Both are realised LEGAL at #6030's kappa (SPAN5 0 / JR 0 on 999/999, native 0/2922). PSOLVE6030 extends this to 12 of the 14 duals, 2 of them (1027/115) with the E1 channel added (sec 6).
**The negative that taught P2c:** the natural rule "#proxies >= rank of the newborns' adjoints" gave a column 2.70 cheaper that is infeasible (kernel dim 3 < 4 newborns).

---

## 4. The five sides of the design

Notation per side: **rules** (with status), **rebuild** (what was stripped / what was kept), **evidence**. Every rebuild below is a *strip-and-rebuild*:
one class of events or stops is deleted and re-solved from D = target - replay(rest), with no swarm coefficient, pairing, proxy set or time read.
Common checks: `tk price` = #6030's kappa, `validate.py --all` SPAN5 law 0 / JR 0 on 999/999 frames, and `tk check --native` 0 bad of 2922 frame pairs.

### 4.1 Markets at the duals G_r (ALIGNLAW sec 4-5, MKT4, MARKETORIGIN, PSOLVE6030)
**What a market is (MEASURED + EXACT).** G_r is a pure junk-cancel lounge. Members are 8 helpers: 3-4 proxies (0,5,6,7,8,9) and 4-5 newborns (5,6,7,8,9).
The only events at G are proxy += c * newborn loads.
- Rank is created at F0: k = 3-4 Ys of one D3 coset pre-read all k unwritten proxies (a K_{k,k} block). In a 7-port octet the coset is a triangle, and its missing 4th affine point IS the anchor.
- 62/62 births have their adjoint in the span of their pre-readers' adjoints (MEASURED: numeric lstsq < 1e-9, weak test, no replay).

**Rules.**
| rule | content | status |
|---|---|---|
| A1 | one register cannot serve two dual cones | PROVED-necessary |
| B1 | dim budget: <= 2 pieces per member, 8 members | PROVED-necessary |
| B2 | served Ys = residual rows; exactly 8 of 22 candidate pieces on every 8-port dual | EXACT |
| B3 | the unique perfect matching with pair frames inside both Qs, invertible 2x2 block; pieces butterfly on the complementary matching (self-dual 16-register top) | EXACT unique on 10/10 (matching); complementary butterfly MEASURED |
| B4 | closed-form butterfly coefficients | EXACT |
| C1 = M1 | #proxies = rank of served-Y space | PROVED-necessary |
| C2 | the loads solve linearly | EXACT-sufficient by construction |
| C3 | proxy count forced, identity free (24/56 subsets realise at G=1049) | EXACT examples |
| C4 = M2 | saturated: 5/3 on G0 infeasible 4/4 | PROVED in column model; realiser evidence not independent (tool limit) |
| B1' | the read unit is the d6 frame, not the register | PROVED |
| E1 | a dim-8 stop read downstream (owned relay/public hub) is a served target | EXACT-sufficient; relay skeleton MODEL |
| E2 | a resident at G after the channel was fed is a readable source | EXACT-sufficient |
| O1 | (0,5) ender as a pure junk source | MODEL |
| O2 | owned scratch at G (cyclic/singular update) | MODEL, **not constructed** |

**Rebuild evidence.**
| duals | result |
|---|---|
| 118, 1050, 116, 1048, 114, 1052 (8-port); 1049, 1051, 1053, 120 (triangle) | every member event deleted; LEGAL, **kappa = #6030** (ALIGNLAW) |
| 1027, 115 (root channel) | E1 + B1'; **identical** kappa, pairs = swarm's (MKT4) |
| 1031, 117 (owned-assisted) | LEGAL at **-1.4314e-6** = exactly one proxy conversion (6.18 R0) each: 4 up-going proxies replace 3 + ender because O2 is unbuilt (MKT4) |
- MKTO2 (`ext/MKTO2/`) attempted O2 (gate/scratch realiser, ablations). It left code and output words but **no notes and no STATE line**, so no result is claimed here.

**Pricing (EXACT, no-mechanism yardstick).** 3.48 per newborn - 2.70 per proxy: +3.10 per 4/4 market (x8), +9.29 per 5/3, +2.00 at 143. Total **73.3 R0**, confirmed independently (m5_cf.py 73.27).

### 4.2 Hubs at the octet frames O_r (HUBRULES, OWNEDHUB, TWINORIGIN, TOPGEN)
**What a hub is.** O_r is reader-free (sec 2.3), so the hub is where the octet's bottom registers finish. Members:
- enders (0-born 01234 helpers);
- X suppliers with chains 1234(8)9 (X is *done at dim 3* and stops at O);
- a 0123489 mate;
- late 012349 helpers.

**Rules.**
| rule | content | status |
|---|---|---|
| H0 | hub of octet r at O_r | PROVED-necessary |
| H1 | span conservation of every ADD/SCALE block | PROVED |
| H2 | continuing departures are unique given D and equal the swarm's | EXACT |
| H3 | 4-ender hub: the 8-dim port space splits 4 UP (octet characters for the top) + 4 DOWN; each ender leaves as e_a + v_a with v_a UNIQUE | EXACT per hub (given arrivals); up = characters MEASURED |
| H4 | down vectors leave only via later arrivals holding them; the late visitors must span rank 4; derived cleaners = TWINORIGIN's supplier set register for register; dropping any one infeasible | PROVED-necessary |
| H5 | block realisation (split V = W + <dep_s>) | EXACT-sufficient by construction |
| twin R1-R3 | arrival values count; s is a twin iff P(A_s) in the span of the other survivors; tied enders <= circuits | PROVED |
| twin R4 | F0-preloaded 0-born mate + d2-butterflied X pair in g + X_c <-> mate butterfly | MEASURED construction |
| twin R5 | pay rule: enabling circuit stops < tied units x s_v | EXACT |
| time-ordered pinning | a later arrival = ARR0 + earlier departures' changes (triangular in time) | EXACT (33/33 at 1090/1091) |
Free (MEASURED): event order inside blocks, block timing, and which down vectors ride X mains vs helpers.

**Rebuild evidence.**
- 18/18 public end frames (dim-4 hubs 232, 234, 235, 237, 242, 244, 306, 516, plus dims 2/5/6/7/8 incl. relay 246): every event at g deleted (85-93 per dim-4 hub). All LEGAL at exact kappa.
- 10 jointly: kappa .003125811557911897, 22676 events.
- Owned hubs 240/243/1090/1091: rebuilt by time-ordered pinning. With the 10 public hubs, 14 jointly LEGAL at exact kappa, 22605 events.
- Twin loading at dims 0-2 rebuilt for 424/602/232/235: all coefficients equal the swarm's.
  - Scope: the relay/reader *structure* is taken from the TWINORIGIN trace. The coefficients are pinned by descent given fixed downstream readers (MEASURED; uniqueness not tested).
- **hsolve (TOPGEN, chain level):** strip every event and every stop at O_r. The nesting + D-pinning + H4 + min-tax solver regenerates hubs 235/232/242/244/237/234 **uniquely = swarm**.
  The candidates are about the members, so the hub is rigid. Octet pair 0 (hub 235 + market 118) in one word: exact kappa, shipcheck as-is.
- No candidate: 89 single stop drops 0 LEGAL; the 26 late-visitor drops are PROVED infeasible.

**Pricing (EXACT, no-mechanism yardstick).** Ender save 6.18 if its O stop does content work, else 3.48; enabling suppliers and owned parks are charged.
4-hubs +13.92 each, 240 +21.08, 243 +24.56, ... Total **+143.2** (gross 234.9 - 91.7). Twin-specific enabling cost: 29.8.
Each 4-hub pure X pair secures >= 2 ends: **>= +6.96 per hub (PROVED lower bound, rest fixed)**.

### 4.3 Routing: reader-level split of shared pieces (YROUTE, YREADORIGIN)
**The mechanism (MEASURED; cost EXACT).** A content source needed by two reader octets is read at *two different levels of its own chain*:
one octet's Ys descend to it low (Y stop at dim 2-3, 2.8-3.6), and it climbs into the other octet's dual cone. It is never copied (9.89) or un-identified (8.40).
- #6030: 99/468 Y content sources serve >= 2 reader octets (238 reads, 131 non-primary sites). P1: 11/476.

**Rules.**
| rule | content | status |
|---|---|---|
| A1 | one register cannot serve two dual cones | PROVED |
| R0 | a direct low read needs completion level c <= exit level e, a free dim-e slot on Y_a, and f_e(s) nesting between Y_a's stops | PROVED-necessary; sufficient MEASURED 131/131 |
| R1 | Y_j reaches s only at f_d(s) <= Q_j | PROVED |
| R1x | every read is at the reader's own EXIT frame | MEASURED 237/238 (not content-forced: 93/131 have a lower frame with the same x-content) |
| R1t | the read happens once s is settled | MEASURED 55/55 |
| R2 | a Y stop pays iff it is cheaper than the carrier it displaces | EXACT |
| R3 | primary = max-exit octet | MEASURED 78/99 |
| R4 | the exit step adjoins the low reader's own port, so q_low ⊥ q_high | mechanism PROVED given E; E MEASURED 166/171 |
| R5 | stream law | MODEL |
**Route B reconciled (EXACT, one inequality R2).** In route B a Y stop displaces only a 1.39 segment, so it loses. In #6030 it displaces a full courier (>= 6.15), so it wins.

**Rebuild evidence (EXACT).** For each of the 55 (primary, low) octet pairs, every non-primary read and every emptied Y stop was deleted (131 sites, 116 stops).
Rebuilt from R1x + R1t + nesting over all 499 candidates by one exact solve: **55/55 UNIQUE solution = the swarm's reads** (coefficients 76 x 1, 55 x -1/2).
All 131 jointly (by composition; a one-shot strip is bilinear with a 17-dim null space): same event multiset, exact kappa, all checks.
Scope: the source chains are kept.

**Pricing.** Against the honest courier counterfactual: +505.9 (couriers 1046.5 - dedicated Y stops 347.0 - source visits 186.5; 0/99 sources negative).
Cheaper local carriers (MODEL legality) give the bracket **[391.7, 505.9], central 447.7**.
- The ALIGNLAW header's "~110 R0 routing" is the same mechanism measured against *P1's* cheaper-than-courier routing, not against couriers. Both figures are correct on their own yardsticks.

### 4.4 Skeleton: source chains (SKELORIGIN, RESKEL6030)
**What the skeleton is (EXACT census, 99 multi-octet sources).**
- Completion stops: the piece is assembled at span(piece). Tight 101/131: own port (1), a D3 pair (2), or a T=384 tiling frame g (3).
- Park stops: 91 read-only stops at dims 3/5/6/7 = 14/36/19/12, where a low reader's Y meets the source before the source absorbs that reader's port.
- No source visits G_r or O_r, so the skeleton is disjoint from markets and hubs.

**Rules.**
| rule | content | status |
|---|---|---|
| S0 | sandwich L <= f <= U (join of content + previous frames; meet of next frames + Q_Y) | PROVED (content term via P3a) |
| S1 | f = L or f = U | PROVED given S0 is the only constraint; MEASURED 504/507 |
| S2 | level = cheaper end (concave tax) | PROVED; 23 exact ties are free |
| S3 | completion = span(piece) | PROVED lower bound, tight 101/131 |
| S4 | exit adjoins the low reader's own port (= YROUTE E) | MEASURED 131/131 |
| S5 | read in place when it nests, else one park per closure component | EXACT cost |
| K5 | never park at Q_Y unless forced | MEASURED; anti-P1 (sec 3.1) |
| L4 (RESKEL) | the completion frame is a closure over *everything co-present* | EXACT on 288/288 write visits |

**Rebuild evidence.** Per low-reader octet, every non-primary read was deleted with its emptied park and Y stops. Parks were rebuilt from S0-S5 + K5, then routing by YROUTE.
- **12/14 octets EXACT** (chains, event multiset, kappa); octets 5 and 12 LEGAL at equal kappa (one tie each).
- 12 octets + 10 hubs jointly: exact kappa, all checks. A wrong same-level park is UNSOLVABLE (negative control).
- Scope: the (s, Y) incidence is taken from YROUTE; completion stops with writes are kept. The tie-break is not pinned (a balance rule gets 20/23).

**Trade (EXACT tax).** 91 parks 186.5 + dedicated Y stops 347.0 against couriers 1046.5: net 512.9 (the per-source form of sec 4.3's +505.9).

### 4.5 Signal: root feeds and returns (SIGPIN)
**Cost (EXACT).** 273.25 = sigmarg 233.1 + owned staging 40.15. Honest: **317.4** (+44.2 of fan-in stops booked as residual by sigmarg; 330.0 with shared partner stops).
| | feeder-aligned roots (4) | source-aligned roots (4) | exchange hubs (5) |
|---|---|---|---|
| total (honest) | 137.7 | 154.9 | 24.8 |

**Rules.**
| rule | content | status |
|---|---|---|
| D0 | every descent frame contains l_k and lies in H_k; one root per frame; 7 paid units per root | PROVED |
| D1 | l-octet roots park at O_r (dim 4) and a 3-port dim-3 frame; source-aligned roots stage at a 20-port relay's dim-7 frame | MEASURED 8/8; cost EXACT |
| F1 | S4_k on each whole octet in H_k is fed by an UP-departure of that octet's hub; at each 4-hub exactly 2 of 4 up-departures feed roots | MEASURED 27/28; rebuild EXACT |
| F2 | 2+2 pieces O_r ∩ H_k fed by 2 dual-cone top members (dim-8 frame = H_k) + one dim-7 relay | MEASURED 4/4; rebuild EXACT |
| R1 | return: 2-4 bottom helpers/Ys take a dim-1 stop at <l_k> | rebuild EXACT at chain level |
| R2 | couriers cancel at the parked copy or at the dim-7 relay | MEASURED |

**Rebuild evidence (EXACT).** Per root, every feed (or every return read) plus the 26 emptied public stops was stripped and re-solved.
- Feeds 8/8 MATCH the swarm's events; reads re-derive every stop (events free at equal kappa).
- All 16 steps jointly: exact kappa, all checks, `tk shipcheck --base 6030` SHIPPABLE AS-IS.
- Scope: the descent skeleton, fan-in ADDs and exchange hubs are kept.

**Why the signal is cheap.** The residual top already holds the roots' sums: hub up-departures (F1) and dual-cone members (F2). This couples the signal to sides 4.1-4.2.

### 4.6 Capstone: all five composed (COMPOSE, MKTCOMPACT) — EXACT
The chain SKELORIGIN (14 octets) -> YROUTE -> HUBRULES (10 hubs) -> ALIGNLAW markets (10 duals) -> SIGPIN (16 steps) was run in one word:
- 22/22 steps OK; **kappa .003125811557911897**; SPAN5/JR 0/999; native 0/2922.
- After MKTCOMPACT batches the market cleanup at a mid-word time: **22860 events** (was 30187, over the 26000 literal). No `--freebounds` needed.
- **The five rule sets are mutually consistent.**

**Inputs still taken from #6030 (COMPOSE sec 2; verbatim scope):**
1. the (source, reader-Y) incidence: which octet climbs and which reads low;
2. the register population and every unstripped chain (completion stops with writes, X/Y main chains);
3. hub arrivals at dims 0-2 (twin loading; partly rebuilt by OWNEDHUB), and 8 single-built end frames not in the joint;
4. market members (8 per dual) and the pieces' d6 frames; duals 1027/115/1031/117 not in the joint chain;
5. signal descent D1, the fan-in ADDs, the 5 exchange hubs;
6. (closed by MKTCOMPACT) event compaction.

**What the rules pin, in one sentence.** Given the population and the incidence, every event, coefficient and stop of #6030 that was stripped is the *unique* (or equal-kappa) solution of its side's rules.

---

## 5. The honest lifetime ledger

### 5.1 Three yardsticks (name them, or the numbers look contradictory)
| yardstick | definition | used by |
|---|---|---|
| **forced** | every helper born 0 / ended 9, stop set unchanged (L = 872) | LAWFIRST, ALIGNLAW 1b, SURGERY |
| **no-mechanism (honest)** | drop a stop only if it does no content work; charge enabling suppliers and owned parks | ALIGNLAW 1d, TWINORIGIN, ENDREST, YREADORIGIN |
| **drop-all-O stops** | chain tax only, every O_r stop removed, feasibility of the dropped content work unchecked | TOPGEN nohub.py (MODEL) |

### 5.2 Ledger on the honest yardstick (EXACT chain taxes; legality MODEL where noted)
| mechanism | net R0 | source | status |
|---|---|---|---|
| markets (14 duals) | **73.3** | ALIGNLAW 1d, MARKETORIGIN m5_cf | EXACT |
| twin-tied ends at hubs (15 tied frames) | **143.2** | TWINORIGIN | EXACT tax; content flag MEASURED |
| other ends (36) + non-market births (36) + interaction | **60.4** (to 70.9 with owned parks uncharged) | ENDREST | EXACT tax; legality 35/36 weak test; no replay |
| reader-level Y reads (99 sources) | **447.7 [391.7, 505.9]** | YREADORIGIN | EXACT tax; MODEL legality |
| **sum** | **724.6 [668.6, 782.8]** | | |
| joint strip of all mechanisms (ALIGNGEN) | 769.8 (no-mechanism word 8518.4 vs 7748.63) | ALIGNGEN | EXACT |
- The joint value exceeds the sub-lane sum by about 45: the mechanisms interact. About 147 [89, 203] of the forced 872 is not attributed.
  This is **a yardstick residue, not a hunt target**: 872 is forced-split currency, while the Y-read value is a routing saving.
- Like-for-like decomposition (derived, not a check): 725 = 385 (gap to P1) + ~340 (P1's no-mechanism base is cheaper than #6030 stripped to couriers).

### 5.3 Superseded figures (old -> corrected)
| claim | old | corrected | why | source |
|---|---|---|---|---|
| market net | 241 / ~236 (forced) | **73.3** | the newborn's dim-5 stop exists only for the market | ALIGNLAW 1d, MARKETORIGIN check |
| hub / tied ends | 88-142 net, 277.3 gross (forced) | **143.2** net (gross 234.9) | honest content-work flag | TWINORIGIN |
| other ends + births | ~315 gross (163 + 152 "unpriced") | **60.4** | 12/36 ends and 27/36 births have honest gross 0 | ENDREST |
| SURGERY's markets / hubs | 259 / 198 net | 73.3 / 143.2 | forced yardstick | ALIGNLAW sec 4 note |
| skeleton premium vs P1 | +321 | **+32** (mains +455) | the +321 compared with-signal vs residual-only | ALIGNLAW 1a |
| SKELGEN residual vs swarm | +33 | **~+70** | honest residual ~7705 (8022.3 - 317.4) | SIGPIN |
| octet P1 realised | 7703 | 8096 (OCTLIFE) | the LKMEET premise was off the critical path | LKMEET header |
| tiling blocks | "364 rank-1" | 336 rank-1 + 28 full-rank | wording | TILEAUDIT |
| PROVED R0 floor | 1521.5 (NETLB) / 1666.9 (SIGNOBS) | invalid -> 742.9 -> 736.3 -> 752.85 -> **794.53** | sec 7 | FRAMELP..ORBITLP |

### 5.4 The third yardstick, stated without contradiction
TOPGEN's nohub counterfactual drops every O_r stop of #6030: R0 changes by **-117.9** (X -132.8, H members -141.7, enders +156.6).
It measures what the O stops cost in chain tax, not whether their content work could happen elsewhere (unchecked, MODEL). TWINORIGIN's +143.2 charges only the enabling stops
(those doing no content work). The two numbers answer different questions. Neither refutes the other.

### 5.5 Signal (sec 4.5)
273.25 sigmarg / **317.4 honest** / 330.0 with shared partner stops. Like-for-like, the honest residual of #6030 is ~7705, and the residual bar at swarm-honest signal is ~7698.

---

## 6. Optimality and rigidity results (each with its scope)
**Local rigidity is not optimality.** Every row below is relative to #6030's frozen remainder, or to a stated column model.

| result | scope | tests | outcome | status |
|---|---|---|---|---|
| market columns OPTIMAL (PRINCIPLES, PSOLVE6030) | P1-P4 column model, rest frozen, --maxextra 1, placement form of P2c | 14 duals | 12 OPTIMAL = swarm tax (incl. 1027/115 with E1); 1031/117 outside solver kinds | EXACT (CP-SAT OPTIMAL) |
| joint 2-column solves | 12 clean duals | census | separable: no shared member, piece or target | EXACT |
| 9th foreign register at G (H709 @118) | within the column; P2c premise | 1 lead | **PROVED infeasible**: a visitor whose G-arrival row is outside the readable content eats one kernel dim (rank <= 7 < 8) | PROVED |
| hubs | rest frozen | 89 drops | 0 LEGAL; 26 PROVED infeasible; departures unique (H2) | EXACT/PROVED |
| hub solver hsolve | chain level, 6 hubs | 6 | unique = swarm | EXACT |
| routing | source chains kept | 55 pairs | unique = swarm; 1 nest-feasible lower frame unsolvable | EXACT |
| anti-K5 Q_Y parks per site | per site | 13 | 9 UNSOLVABLE, 3 SCHEDULE (untested), 1 equal | EXACT (numeric GN) |
| SURGERY: kills, kill+rehost | exact linear replanner at existing co-presences | 1817 | 0 feasible; 9 Lemma-pass ends are receiver-twin illusions | EXACT within scope |
| SURGERY2: compound skeleton edits | inline couriers, source-visit deletes, Y-stop moves | ~1250 | 0 feasible; 395/397 dedicated source visits forced by readers' chains; 22 couriers 0 removable | EXACT |
| RESKEL6030: skeleton classes | T ties, M park merges, O orientation flip, C completion lifts | 140 runs + 3 geometry screens | T: dk = 0 (58 legal; full chain re-run exact). M: 0/64 by geometry (empty bracket 32/32). O: 0/24. C: 266 one level, 22 argmin/tie, 0 cheaper; s495 dk -1.05e-7 | EXACT |
| market saturation | column model | 5/3 on G0 | infeasible 4/4; from scratch 0/56 realise | PROVED (P2c, column model); realiser 0/56 is not an independent proof (tool limit) |
| twin pure X pair | rest fixed | per 4-hub | >= +6.96 | PROVED lower bound |

**What these say together.** Within each side, given the others, #6030 is the unique (or equal-kappa) optimum the rules allow. Every cross-side edit we could express is infeasible.
The free choices (23 S2 ties, proxy identity, block order) are kappa-neutral (EXACT).
**What they do not say.** Nothing here excludes a different skeleton class, a different register population, or a different incidence (sec 8).

---

## 7. Lower bounds
**Setting.** A type LP over chain types, with rows from proved laws. The certificate is exact rational weak duality, re-checked independently.
- **SCOPE:** own = 22 / owns = 18 dirty helper endpoints (measured on #5907), and R0 <= 8000 for column bounds.

| step | floor (R0) | % of 7990 | what changed | status |
|---|---|---|---|---|
| NETLB / SIGNOBS (inherited) | 1521.5 / 1666.9 | - | omitted helper types that read at their birth frame (legal per legal.py; toy checked); with them the old rows give 82.3 | **INVALID** (FRAMELP sec 0) |
| FRAMELP | 742.9 | 9.3 | Theorem JR (junk-aware frame rank law) | superseded by a soundness fix |
| PROVLP | **736.28** | 9.2 | fix: keep zero-coverage types (FRAMELP dropped legal ones); junk-ratio / provenance laws PL, LCL, CL, LCR | PROVED (SCOPE) |
| CHARTLP | **752.85** | 9.42 | Redundancy Lemma + coverage corollary | PROVED (SCOPE) |
| ORBITLP | **794.53** | **9.94** | TIE-CAP | PROVED (SCOPE), `recheck.py cert_t1.pkl` matches |
| MODEL tiers | 1631.75 (no late-born ties) / 1668.76 (no ties) | 20.4 / 20.9 | | **refuted as laws** by the clean legal toy T8 |

### 7.1 Theorem JR (PROVED; FRAMELP sec 1)
At a chart m, let A_m = arrival values + initial values of registers born at m (in the local program P').
- (i) Every value held at m lies in span(A_m). *Proof:* every op that changes a public value at m reads a public source at m.
- (ii) With N = the clean helper enders at m, the unit vectors e_h (h in N) lie in pi(span A_m) ∩ ker phi. Hence
  rho_m <= Cc(m) + min(PJc(m), NCe(m)) + [Y ends at m] + [X born at m] + dirty(m).
- (iii) Coverage: the entries covered by landings at m are <= R(d,v) rho_m.
- (iv) The transpose gives the departure mirror.
P2x/SPAN5 is a projection of JR.

### 7.2 Redundancy Lemma (PROVED; CHARTLP; deficiency form)
Enders N at frame f need survivors S with q = dim(xspan(A_f)/xspan(S)) <= |S| - rank_P(S), where P drops e_N and the owned symbols.
A clean ender's last hop adds x-rank only through tied survivors, so **a twin must be a second copy (a survivor whose arrival agrees with the ender outside e_N), never the receiver of a merge.**
- Validated: 0 violations on #5907's 82 realised early ends (LAWFIRST host.py), and tight in every tie.
- This lemma is the bridge between the lower bounds and the design: H4 and twin R2 are instances of it.

### 7.3 TIE-CAP (PROVED; ORBITLP sec 2)
A tie element is one ender's own content, so it covers at most that ender's own last-hop cap C(last, 9 - v), not the generic R(d,v)
(for example R(8,8) = 30 vs 2 for a (2,8) single hop). This lifted the floor by +41.7.

### 7.4 Gap
The floor is 794.53 against #6030's ~8000. Custody/containment chart pricing gives 0 lift (ORBITLP sec 1, scoped argument), and an orbit LP was not built.
The open lever is a per-unit tie cost (twin + displaced coordinate). **The lower bounds certify about 10% of the word; they say nothing about whether #6030 is globally optimal.**

### 7.5 Addendum (FLOOR2, Oct 28) -- per-unit tie cost: PROVED floor 813.31
> **ADDENDUM (FLOOR2; supersedes the 794.53 figure in the table above and in the Summary).**
> - **Lemma R+ (PROVED; the original lane notes (not shipped)).** At a chart g, let E be any set of clean helper enders and C the other arrivals. Then
>   dim(xspan A_g / xspan C) <= #(C-arrivals holding some e_h, h in E). So a clean ender is NEVER a tie token, whatever its last hop:
>   every tie unit is charged a distinct continuing register, a Y ending at g, or a dirty ender (ORBITLP's open lever, in count form; the
>   displaced-coordinate escape needs no pinning). Mirror by the transpose. EXACT: 0 violations on #5907, #6030 and both transposes
>   (136 chart/threshold checks, tight in 70); toys T7-T11 OK (T11 = the old optimum's free single-hop token, built: forced dirty).
> - **PROVED floor 813.31 R0** (`flp.py ... red tcap rplus`, exact recheck matches): **10.18% of 7990, 10.50% of #6030's residual 7748.63**.
>   SCOPE unchanged (own = 22 / owns = 18, R0 <= 8000). MODEL tiers unchanged (lbt 1631.75, notie 1668.76).
> - P2c (count form), the parity lemmas, the X-split, all-roots-alike and the skeleton condition add no row with force in a type LP:
>   P2c is implied by JR (iv); the skeleton condition by Theorem LC; parity/X-split are chart-identity facts; all-roots-alike is owned-layer.
> - The 20-30% target is NOT reached. What remains is chart identity (custody: a token's previous chart must contain the ender's birth chart),
>   which needs the orbit LP. Binding now: cover rows both sides, n1 (lines), line-born newborns' first hops (tnD), dirty budgets (~2-3 R0/unit).

### 7.6 Addendum (CHARTORB, Oct 28) -- SOUNDNESS CORRECTION: the 7.1-7.5 floors are INVALID; corrected PROVED floor 754.14
> **ADDENDUM (CHARTORB; supersedes the figures in the table above, in 7.5 and in the Summary).**
> - **INVALID (EXACT):** the inherited `cap48` row bounds the SUM of per-crossing caps by 48 n_u (n_1 <= 104). Frame capacity bounds only
>   DISTINCT coverage per chart. #5811 / #6030 credit cov(2,1) >= 9618 > 4992, and #5907 mapped to type counts is INFEASIBLE in the FLOOR2 LP
>   (min violation 118: n1 needs ~200 lines). So 742.9 (FRAMELP), 736.28, 752.85, 794.53 and 813.31 are not valid floors. Toy T12 shows the mechanism.
> - **Sound row (PROVED):** distinct level-d coverage by crossings whose last-effective chart has dim u is <= 48 n_u
>   (rectangle P(c) x J(g) lies in P(c) x J(c)). **Corrected PROVED floor 754.14 R0 = 9.44% of 7990** (9.73% of 7748.63), exact recheck True.
>   Same rows without R+ (ORBITLP config): 734.96. MODEL tiers: lbt 1551.73, notie 1576.08.
>   **Swarm test passed:** #5907 and #6030, mapped to type counts, are feasible in the corrected LP (violation 0). Every future floor must pass this test.
> - **Chart-orbit LP not built (ceiling first).** In the corrected LP every tie/token row has dual 0. What binds is credited cover (668) and
>   line/Q integrality (165). In general networks the five chart-level laws (private-content, junk-split, P2x, X-split, skeleton condition)
>   reduce to JR (i)/(iv) and Theorem LC, which are already rows. Their extra force is SCOPE (#6030's skeleton class).
>   A G-symmetric orbit LP adds geometry only. Probe (MODEL): cover inflated x1.066 gives 798.3, x1.2 gives 889.6.
>   ESTIMATE ceiling about 10-11%, **not 20%**. Next lever: support presence on CREDITED coverage (the original lane notes (not shipped)).

---

## 8. Open problems

### 8.1 The skeleton class (the live frontier)
- The rules pin #6030 *given* its population and incidence. No generator yet produces that population from E.
- SKELGEN's oriented skeleton (from E -> tiling -> CP-SAT orientation) reaches residual 7774.8. With swarm-honest signal that is kappa .0031097 < bar (EXACT law arithmetic).
- The realised from-scratch word p1oF_r is kappa .0027748 (EXACT), 89% of the bar; its gap is the top.
- **TOPGEN ceiling (MODEL, provisional kill; scope: oriented p1o + hubs/markets as add-ons):** hubs cost about +12.7 each from scratch and eat the X climbs.
  - EXACT geometry: no T=384 tiling port frame h is orthogonal to a foreign octet frame (0 of 14 x 14), so an oriented X cannot both stop at O_r and climb.
  - Result: R0eq >= 8333 vs 8015.2.
- **The gap is the skeleton class, not the top:** #6030 without its O stops is ~7587 honest residual, about 200 below p1o at the same no-hub level (MODEL).
- Learnings for a class generator (RESKEL L1-L4, SURGERY2):
  - ties are inert;
  - one park per (source, reader octet), no sharing;
  - count a copy's F0 readers before re-orienting it;
  - price completion over the whole co-present set.
- **Open question:** which incidence (which octet climbs, which reads low; 99 multi-octet sources vs p1o's 18) is optimal, and can it be derived?

### 8.2 Global optimality
- No PROVED statement bounds R0 above 794.53. The rigidity results are local, scoped to fixed population and incidence.
- **Open:** a lower bound that knows the tiling (a per-octet LP using O_r reader-freeness and P2c per frame), or a proof that the rule-pinned family is optimal within the octet class.
- PRINCIPLES gap 3 notes that P2c is already per-frame. That is the hopeful sign for scaling the column solver to an octet, then to the word.
- Also open: the P2c placement form (gap 0); Theorem R9F outside F (escape E1); O2 (6.18 R0 per dual at 1031/117).

### 8.3 The 7 non-reducing regularities (PRINCIPLES sec 4)
> **Update (REGULAR7):** status column superseded by sec 10: R1t PROVED, K5 PROVED on all 13 candidate sites (not anti-P1: P1 + B3 + commutation), R3 dissolved (cf label), R1x reduced (not junk; nesting), ties free, up vectors pinned-or-gauge (EXACT flip), E MEASURED (skeleton class).

| # | regularity | why it does not reduce | status / best lead |
|---|---|---|---|
| 1 | **E / S4 exit:** the step out of Q_a adjoins q_a (the reader's own port) | any port with odd dot to q_a would exit; 5 counterexamples (sources 2, 347, 443) | MEASURED 166/171. Lead: the tiling (which ports a cross-octet piece absorbs next). R4 (orthogonal co-readers) follows from it |
| 2 | R1x read at the exit frame | a lower frame has the same content at 93/131 sites; nesting + junk pin it | MEASURED 237/238 |
| 3 | R1t read when settled | no time principle in P1-P4 | MEASURED 55/55; MODEL reason P2j |
| 4 | K5 never park at Q_Y | contradicts P1 (tax-cheaper); full-coordinate failure is junk | MEASURED; per-site 9/9 algebraic tests hold (PSOLVE6030) |
| 5 | R3 primary = max-exit octet | 21 exceptions at equal kappa | MEASURED 78/99 |
| 6 | tie-breaks (23 S2 ties, proxy identity, block order) | equal kappa | free (EXACT: RESKEL L1) |
| 7 | up vectors = octet characters; which octet climbs | pinned by the top, not derived | MEASURED; **partly reduced:** SIGPIN F1 pins 2 of the 4 up-departures at each 4-hub as root characters (27/28), so only 2 per hub remain unexplained |
- **Most promising extension (PRINCIPLES gap 2):** a time-resolved P2j (outflow-corank per time window) may derive 2, 3 and 4 together. Items 1 and 7 look like tiling (P4) facts. No candidate fifth principle covers them.
- "Lazy absorption" is the L-branch of S1 and does not single out q_a.

---

## 10. The seven regularities (REGULAR7, Oct 28; supersedes the status column of sec 8.3)
Details, censuses and code: the original lane notes (not shipped), `ext/REGULAR7/`. No CANDIDATE.

**The tool (PROVED, op semantics).** *Commutation lemma C.* `Y += c s` commutes with every op that neither writes s nor reads Y; a SCALE of Y
only rescales c. Hence a read can be moved from (t1, f1) to (t2, f2) with identical finals iff s is not written and Y is not read in between
(and s, Y meet at f2). This is the exact form of the "time-resolved P2j" of PRINCIPLES gap 2. It needs no new principle.

| # | regularity | status now | derivation sketch |
|---|---|---|---|
| 1 | E: the exit step adjoins q_a | **MEASURED 166/171, sharpened** | PROVED: every odd port (dot q_a odd) of the exit frame is newly absorbed (171/171). E = "the first odd pair s absorbs after a's read is a's own". Not a dual-cone fact (q_a in the dual at 0/59 cone exits; 107/166 exits at dim 3/4). Not content-forced (55/166). The exit frame is a kept completion stop, so E belongs to the skeleton class (8.1) |
| 2 | R1x read at the exit frame | **REDUCED** to S0-S2 + Y-chain nesting | At 163/170 reads with a lower completion frame, s is not written in between, so its value is the same and the old "junk" reason is wrong (at 135 Y is also unread, so finals agree by C). The read sits where the Y chain can meet s (lower frame nests at 1/93, YROUTE); that frame is the closure join/meet (S0-S2, PROVED). Residue: the Y chains (= incidence) |
| 3 | R1t read when settled | **PROVED** (normal form) | By C the read time is free within its commutation class; "settled" = its earliest point. kappa-inert (events free) |
| 4 | K5 never park at Q_Y | **PROVED on all 13 candidate sites**; general form MODEL for a pre-exit level <= 1 | By C a Q_Y read is admissible iff Y is not read afterwards. At 13/13 sites Y is read once later (12 by its D3-pair partner at the shared d7 frame, B3, where the d7 frame is the partner's only post-F0 meeting with s; 1 by helper 133, which carries it to an owned d8 read at t13486, long before its F9 meeting with s). Repair = a new stop (>= 2 ln 2 = 1.386) or a courier (>= 6.15); saving <= 1.116 (exact chain tax). Net >= +0.27 per site. The swarm's 2 Q_Y parks (into relay Y169) have no later read of Y, as predicted. **Corrects sec 3.1: K5 does not contradict P1; it is P1 + B3 + C.** |
| 5 | R3 primary = max-exit | **DISSOLVED** (accounting) | "Primary" is the courier counterfactual's label (YREADORIGIN), not part of the word; the max-exit octet is the one whose Q holds s's top frame (P3 ascent, true by definition). Design content = the incidence (8.1, open) |
| 6 | ties, proxy identity, block order | **FREE** (EXACT + PROVED) | RESKEL L1 (58 flips dk 0), M4 PP/NN LEGAL, 3P1Z (the G block exists iff dim ker C >= nb, whatever the born-ness) |
| 7 | up vectors = octet characters | **PINNED OR GAUGE** (PROVED + EXACT) | Of 112 registers leaving the 14 octet frames, 27 are read before F9 (9 by owned registers, 18 at dim-8 frames, root frames H_k by SKELCLASS I4): pinned by their readers (SIGPIN). 85 are read only at F9: by C, `u1 += lambda u2` at O_r undone at F9 changes the departure value and nothing else. EXACT flip at hub 235 (u35 += u107): LEGAL, kappa .003125811557911897 identical. "Characters" is the swarm's gauge |

**Count after REGULAR7.** Of the 7: 4 PROVED or free (R1t, K5 scoped, ties/identity, up vectors), 1 dissolved (R3), 1 reduced to closure + the
incidence (R1x), 1 MEASURED (E). Both remaining residues (E, and R1x's Y chains) are properties of the skeleton class / incidence, i.e. sec 8.1.

**Levers (task: is a free choice a CHOICE?).** The genuinely free choices (ties, proxy identity, the F9 gauge, read times) are kappa-neutral
by construction. The only non-neutral flip, anti-K5, loses by exact tax arithmetic at every site. No CANDIDATE.
