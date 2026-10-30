# P104 lemmas: local laws of the productive-controller word, with proofs

Scope tag: THEORY / exposition. A consolidation of the PROVED statements from the lane notes, in one self-contained form.
Nothing here is new computation. Every EXACT number is copied from the original lane notes (not shipped).
Each claim carries a label. Where a note's proof had a gap, the gap is flagged (marked **GAP**) and, where a short rigorous proof exists, that proof replaces the note's.
Labels: **SPEC** (verifier or pricing), **PROVED** (proof given here), **EXACT** (certified computation on a stated instance), **MEASURED** (census regularity),
**SCOPE** (proved, but resting on a measured constant), **ARGUED** (reasoning without full proof), **MODEL**, **OPEN**, **REFUTED**.

---

## 0. Setting

### 0.1 The verifier (SPEC)
`local.py` = `research/p104-productive-controller/local.py` (line numbers below). Ambient space F2^9. A *frame* is a subspace (F0 = {0}, F9 = everything).
- **Rows.** Every register r starts holding its unit row e_r (l.117). Public registers are r < 735 (packages retarget this to <= 770); owned registers are 735..742.
- **MOVE** (l.123-128). Ownership must match. A public MOVE goes strictly *up* (a < b), an owned MOVE strictly *down*. Every MOVE, public or owned, adds one unit to `paid[|dim b - dim a|]`.
- **INIT / CLEAR** (l.129-141). These apply to owned registers only. INIT sets the row to 0 at a frame. CLEAR erases the row at the frame where the register currently is.
- **ADD / SCALE / COPY** (l.143-161). The coefficient is nonzero and dyadic (l.144-146). SCALE multiplies by a dyadic *unit* (l.149).
  ADD r += q s needs s != r and **both registers at the same frame** (l.154, "Common scalar chart"). COPY writes only into a cleared owned field (l.156).
- **Exits** (l.162-168). No owned register is left live. Each public r ends at its declared final frame with row e_r, except Y = r with r - 112 live, which ends at e_r + e_{r-112} (= y_j + x_j). Owned rows end at 0.
  The capsule enforces owned peak == 1 at l.162; packages patch this to <= 13.
- **Helpers** (l.169-171). Each non-main public register is counted once, in `helpers[dim final - dim initial]`, and that span must be > 0.
- **Literals.** Fewer than 26000 events (l.115). A scalar/route budget below 10^7. The public inventory (735 in the capsule, 770 in current profiles).
- **Price** (package pricing; reimplemented in `infra/price_exact.py` l.18-24). kappa is the root of
  **F(k) = sum_r (T_r - P_r) r^(1-k)**, where T = 18 * helpers + T_out and P = 18 * paid + P_out, and T_out, P_out are word-independent constants.

Notation. x(v) is the projection of a row onto the 104 X-unit coordinates (the "x-content"). Every other public unit is a *junk* coordinate.
A register's *chain* is its sequence of frame dims. tax(chain) = D ln D - sum_i j_i ln j_i, where D = span and the j_i are the jumps.
mu(a,d,b) = (b-a)ln(b-a) - (d-a)ln(d-a) - (b-d)ln(b-d) is the tax of one stop at d inside a jump a -> b.
The lane-wide linearisation 1/kappa = 130.27 + .02364 (R0 + 380 (paid - 56)) is used only to convert numbers into R0. Its constants are fitted, not derived here.

### 0.2 Three accountings
- **Real values.** The values the verifier computes.
- **P'.** Every public read of an owned register is replaced by a fresh formal symbol. Sym_g is the span of the symbols created at chart g.
- **P_M.** Owned values are tracked exactly *within* a chart. Each owned MOVE arrival at g is replaced by a fresh symbol sigma_mu, with rho(sigma_mu) = its real value.
  There are m_g such arrivals at g. Sym_g is their span, and rho maps the symbols back to real values (identity on public coordinates).
A helper is **clean** in an accounting if its final there is exactly e_h. A helper is **dirty** if its final is e_h + z with z != 0. In every accounting, real finals are clean.
In each accounting, A_g is the list of values *arriving* at chart g: MOVE arrivals, plus the initial values e_r of registers whose initial frame is g.

---

## 1. Foundations

**Lemma 0 (local block, PROVED).** Let the n registers present at a frame phi perform ADD/SCALE only among themselves, with no arrival, departure or owned event in between.
Then their values satisfy V_after = T V_before, where T is an invertible n x n matrix.
*Proof.* ADD r += q s with s != r is an elementary matrix (l.154). SCALE multiplies by a nonzero unit (l.149). []

**Lemma 1 (local span; JR(i), PROVED).** Every value held at chart g, by any register at any time, lies in span(A_g) + Sym_g. This holds in P' and in P_M.
*Proof.* Induct over the events at g. A MOVE in adds a vector of A_g, or a symbol in P_M. An initial value is in A_g. ADD, SCALE and COPY combine values present at g (l.154, l.157).
INIT gives 0 (l.133), and CLEAR gives 0 (l.138). In P', an owned read adds a symbol of Sym_g. []

**Lemma 2 (owned registers add rank only by MOVE, PROVED).** In real values, every value held at g lies in span(public arrivals at g, initial values at g, owned MOVE arrival values at g).
The number M of owned MOVEs satisfies M <= sum_r r * paid_owned[r]: owned MOVEs strictly descend (l.126), so each one has rank >= 1 (l.127).
*Proof.* This is Lemma 1 with the owned arrivals kept as vectors rather than symbols. []
Corollary: an owned lifetime that never moves adds nothing at any chart.

**Lemma 3 (junk bookkeeping, PROVED).** Fix a public helper h. Let c_h(v) be the e_h-coefficient of a row.
If a register r != h has c_h(V_r) != 0 at some time, then r must later execute an ADD r += q s with c_h(V_s) != 0.
*Proof.* Only ADDs into r with c_h(V_s) != 0 change c_h(V_r): SCALE rescales a nonzero value, and COPY targets owned fields. The final c_h of r is 0 (l.164-168). []
*Instance (EXACT).* In the frontier word, every public hand-off of root content from a relay r carries r's junk e_r. Its receivers cancel that junk by reads that are paired to r.
Deleting any one of root 4's 9 hand-offs and offering a direct root read is UNSOLVABLE. Adding junk-partner reads for the deleted pair makes it solvable.
So a hand-off is specified by the pair (root content, junk content), not by the root content alone.

---

## 2. Cost lemmas

**Lemma 4 (additivity, PROVED from the price).** Let e = 1 - k. Then F(k) = const(k) + sum_r g_r(k), where
  **g_r(k) = 18 [r is a helper] s_r^e - 18 sum_{jumps j of r} j^e.**
So g_r depends only on r's own dim sequence. Consequences:
- (A1) Frames of equal dim, events, their order and their number never enter kappa. Events meet only the literals.
- (A2) Edits that change disjoint sets of chains satisfy Delta F = sum_i Delta F_i, at every k.
  *Hypothesis:* F has a single sign change, from + to -, in the pricing bracket. Under it, if every edit alone has Delta F_i(kappa0) <= 0, then the combination has kappa <= kappa0.
  Edits interact only through feasibility, or through edits to the same chain. (**GAP, minor:** the single sign change is a property of the invoice, assumed by the pricer's bisection, and not proved here.)
- (A3) A helper with one jump has g = 18 s^e - 18 s^e = 0. More generally the jumps of a helper sum to its span, so g_r = -18 k tax_r + O(k^2). This is where "R0 = sum of taxes" comes from.
*Proof.* T gains 18 at s_r for each helper (l.170). P gains 18 at |gap| for every MOVE (l.127). []
*Tightness (EXACT).* Three predecessor words differ from #6030 on 6, 11 and 12 chains. Their kappa, computed from the per-chain differences alone, matches the exact kappa bit for bit.

**Lemma 5 (swap gauge, PROVED).** Let a and b be public registers that are both at frame f at time t1 and both at a frame g at a later time t2.
Construct a new word as follows:
- at t1, swap the values of a and b (a += b; b -= a; a += b; b *= -1);
- in the window (t1, t2), relabel a <-> b in every event (MOVEs included);
- at t2, swap the values back.
The result is legal, it has the same final rows, and its kappa is identical.
*Proof.* Within the window each relabelled register holds exactly the value its partner held in the original, and it sits at the partner's frame. So every ADD is still at a common chart (l.154), and every MOVE still starts from the current frame (l.125).
The swaps use coefficients +-1 and the unit SCALE -1 (l.144-149). The jump multiset over all registers is unchanged: segments are exchanged between the same pair of frames f and g.
Initial and final frames are unchanged, so the helper spans are too. By Lemma 4, kappa is unchanged. The cost is 8 events. []
*Tightness (EXACT).* An X main and a 0-born helper exchange futures at dk = 0, LEGAL. Whole octets can be relabelled: one octet with 0 done-at-O X, another with 7 of 8.
So "which X are done at the octet frame and which climb" is a gauge choice, not a cost fact.

**Lemma 6 (shadow-relay fold, PROVED identity; realisation EXACT per site).** Let an owned root rho have consecutive stays a -> b with d_a > d_b. Let a public helper H, born at dim d_b - beta, read rho at b and then climb a nested chain b < f_1 < ... < f_{m-1} < a, and end at a.
Replace this by: rho descends a -> f_{m-1} -> ... -> f_1 -> b, and H becomes a single jump. Then, with D = d_a - d_b and e = 1 - k,
  **Delta F(k) = 18 ( beta^e + D^e - (beta + D)^e ) > 0 for 0 < e < 1.**
The linearised gain is mu(0, beta, beta + D) R0, which is the tax of H's first stop.
*Proof.* H's jumps after b are exactly the reversed jumps of the deep descent, because both visit the same frames between b and a. Removing H gives
-18[(beta+D)^e - beta^e - sum_deep j^e] by Lemma 4 and A3. Rho's P-terms change by -18[sum_deep j^e - D^e]. The sum_deep terms cancel. Positivity is strict subadditivity of x^e for 0 < e < 1. []
- On #6030 beta = 1 and D = 6, so the gain is 7 ln 7 - 6 ln 6 = **2.871** per relay. On the older families beta = 1 and D = 7, giving 8 ln 8 - 7 ln 7 = **3.014**.
- **GAP (corrected statement).** The notes give the saving as "staging(a -> b)". That equals mu(0, beta, beta + D) only because the root's top jump (8 -> 7) and beta are both 1. The general form is the one above.
- **Realisability is not implied.** Each site still needs an exact re-solve of H's receivers: re-read rho or its junk partners, and relocate rho's landing lifetime.
  This is EXACT on #6030: roots 4 and 5 give +6.663e-7 and +6.666e-7 kappa; root 2 succeeded only after the reader MOVEs were hoisted.
  It fails on older-geometry words: no common chart exists for the re-read, and one word sits 26008 events above the cap.

**Lemma 7 (commutation, PROVED, "if" direction).** An event p += c h at (t0, f0) can be moved to (t', f) with the same values everywhere if four conditions hold:
h is not written in between, p is not read in between, p is not SCALEd in between, and p and h are both at f at t'. *Proof.* Addition commutes with the other writes into p, and no other register sees p's value in between. []
(The notes state "iff". The "only if" direction is not proved.)
*Application (EXACT census).* Consider all 464 0-born helpers of the frontier word. For 461 of them, moving the birth off F0 leaves some F0 event with no meeting at a later common frame. The other 3 are single jumps with ceiling 0.
So F0 births are geometrically forced wherever they cost anything. This is scoped to one moved event per F0 event, with partners taking at most one new stop.

---

## 3. Rank and content at one frame

**Lemma 8 (merge-sink, PROVED).** Take a block at phi as in Lemma 0. For each register k, let sigma_k(j) be the scalar coefficient of V_k in Y_j's final.
The rest of the program is row-linear (l.150-160), so this coefficient is well defined. Let X and S be the n x 104 matrices of x-rows and of sensitivities, and Delta = S^T X.
Then Delta_arr = Delta_dep, and
  **n - rank S_dep >= rank X_arr - rank Delta.**
*Proof.* V_dep = T V_arr, so S_arr = T^T S_dep, and Delta_arr = S_dep^T T X_arr = Delta_dep. Sylvester's inequality gives rank(S^T X) >= rank S + rank X - n, and rank S_arr = rank S_dep. []

**Lemma 8b (dual content-in-frame, PROVED).** Suppose k departs phi to a next frame F', and every register on a read path from k to Y_j is public.
Then sigma_k(j) != 0 implies F' is inside Q_j, i.e. q_j is in F'^perp.
*Proof.* A path k -> r_1 -> ... -> Y_j consists of ADDs at common frames. Public frames only ascend (l.126), so every register on the path is, at its read, at a frame containing F'. Y_j's frames lie inside its final frame Q_j. []
The hypothesis excludes owned registers, which descend.

*Application (EXACT inputs, pair model).* At a cycle hyperplane hp where two rank-1 blocks (g1,h) and (g2,h) merge, four facts hold:
(a) the blocks share the reader factor rho_h; (b) the x-arrivals pi_g1 and pi_g2 are independent; (c) |supp rho_h| >= 3; (d) every next frame of a departure reaches at most 2 of h's readers (by 8b, dim F'^perp <= 2 gives at most 3 readers; parity cuts this to 2, because readers have odd weight and the sum of two readers is even).
Then rho_h lies in the row space of S_dep, and by (c) and (d) rank S_dep >= 2. Lemma 8 then gives **n >= 3**. At n = 3, S_dep has a nonzero left-kernel vector, so after an invertible change of the block one departure has sigma = 0: a *sink*.
(a)-(d) hold EXACTLY on all 168 cycle hp's. Two continuing dual registers can therefore never deliver a merge with any number of ADDs. One explicit 4-ADD construction with a third register Z works, with det = 1:
Z += D2; D1 += D2; D2 -= Z; D2 += D1.
*Tightness (EXACT).* All 109 merge hp's of #6030 have exactly 3 registers, one of which is a zero-sensitivity sink. In the pair model the cheapest generic sink is a fresh 0-born (0,6,9) register at 6 ln(3/2) + 3 ln 3 = 5.7286 R0.

**Lemma 9 (frame conservation and local end, PROVED).** Suppose there is no owned CLEAR at frame E after time t0. Then every value present at E at t0, together with every later arrival, lies in
  span(values departing E after t0) + span(finals of registers that end at E).
*Proof.* The invariant "span(arrivals so far) is inside span(present) + span(departed)" survives each event: arrivals and departures move one vector, and ADD/SCALE/COPY/INIT do not shrink span(present) (Lemma 0). Only CLEAR can. At the end, "present" = finals. []
- **Local-end corollary.** Let a helper m end at E, below F9, and let t_a be its last arrival. Then x(V_m(t_a)) lies in X(departures from E after t_a) + span{x_y : Y_y ends at E}, because helper finals have x = 0.
- **Closed frame.** If nothing departs E after the arrivals, then span(arrivals) = span(finals).
  *Instance.* On market dual 116 of #6030, each dim-8 delivery frame is visited only by its Y and by members that would end there. So every arriving member's x-part would be a multiple of x_y, but the members carry independent read-frame content.
  So no plan in which members end low on 116 exists, structure aside.
- **GAP.** The notes' form ("span of the *other non-Y* registers", with a Y returning "total coefficient 0 on e_y") assumes that no register other than Y holds e_y. That need not hold. The corollary above is the rigorous replacement.

**Lemma 10 (leavers, PROVED in scope).** Let O be a frame with no reader (no Y ends or stops there), no X ending there, and no owned CLEAR or owned departure. Then
  **#public departures from O >= dim xspan(arrivals at O).**
*Proof.* Apply Lemma 9 over the whole history of O, then project with x. The only finals at O are helper finals, which are x-free. []
*Instance.* Octet frames O_r are reader-free (EXACT, 14/14). On the 13 root-feeding full octet hubs the arrivals have x-rank 8 (MEASURED: every up character uses all 8 port directions), so **#leavers >= 8**.
The swarm's 4-ender hubs use exactly 8. **GAP (scope):** the source note does not exclude an owned register present at O_r, and owned hub ends exist in the word family. With an owned CLEAR or owned departure at O_r, the bound applies to public plus owned departures, not to public leavers alone.

**Lemma 11 (hub/market separation, PROVED; geometry EXACT).** After a public register has stopped at O_r, it visits only frames containing O_r (l.126). From its first stop on, a market member visits only frames containing G_r = O_r^perp. A 0-born member also sits at F0, but no register that has been at O_r is ever at F0.
So the two can share a frame only if that frame contains O_r + G_r = (O_r cap G_r)^perp. Since dim(O_r cap G_r) = 2 (EXACT, 14/14), that sum has dim 7.
*Instance (EXACT, r245g).* No dim-7 frame contains O_r + G_r. The only frames containing it are 2-3 dim-8 relay frames per octet, and no market member or served Y visits them.
With the slot defined as "registers that stop at O_r, plus market members" and everything else frozen, the joint optimum is the sum of the two separate optima.
*Scope (independent audit).* On every octet, 4-14 Ys and other registers stop at frames inside O_r (dims 1-3) that hub registers also use, and later reach frames containing G_r.
That bottom-to-market coupling lies outside the slot and is untested.

---

## 4. Ties, custody, and dirt

Setting for this section. At a chart g, E is a set of clean helper enders and C = A_g \ E. N_s is the arrival value of s with the e_E coordinates and the symbols deleted. C_h is the set of s in C whose arrival holds some e_h with h in E.
q_E = dim(xspan A_g / xspan C) counts the x-directions that only the enders' arrivals bring: the *tie*.

**Lemma 12 (JF, PROVED).** Let W = span V_C + Sym_g. Then
  **q_E <= delta := dim(W cap span e_E) <= |C_h| - rank(N_{C_h} mod span N_{C \ C_h}).**
*Proof.* Let U = span A_g + Sym_g. It contains every value at g (Lemma 1), so in particular e_E, since those finals are clean. Let pi delete the e_E coordinates.
Then ker pi cap U = span e_E, so dim pi(U) = dim U - |E| <= dim W, because U = span V_E + W. Hence dim pi(U)/pi(W) <= dim W - dim pi(W) = delta.
x factors through pi and kills Sym, so q_E = dim X(U)/X(W) <= delta.
For the second inequality: sum_C c_s V_s + sigma lies in span e_E if and only if sum c_s N_s = 0, with sigma absorbing the symbol part. Its e_E-part depends only on c restricted to C_h. []
- R+ (delta <= |C_h|) is the special case.
- **Count corollary (PROVED).** Call a tie (q >= 1) *non-degenerate* if rank(N_{C_h} mod ...) >= 1. A non-degenerate tie has |C_h| >= 2 holders.
  The containment of C_h in the LP's token set (prev >= beta) is cited from the earlier proof of R+ and not re-verified here.
- *Tightness (EXACT).* On the frontier word, q = delta in 33 of 35 (chart, beta) checks, and JF beats R+ strictly in 20 of 35. There are 0 violations on three words and their transposes.
  The toys U1 (degenerate) and U2 (non-degenerate, 2 holders) realise q = delta = 1 (sec 5).

**Lemma 13 (custody, PROVED in P' only).** Work in P', mod Sym.
(This fails in P_M and in real values: COPY o <- d (l.157) followed by d -= o (l.160) legally zeroes a public row.)
In P', public values are linearly independent at all times:
- they start as units (l.117);
- ADD and SCALE are invertible;
- an owned read changes a value only by an element of Sym.
So a vector u in W cap span e_E, u != 0 (it exists when delta >= 1), has a unique expansion u = sum_r a_r(t) V_r(t). Let K(t) = {r : a_r(t) != 0}.
- (i) An op d += q s changes exactly one coefficient, a_s <- a_s - q a_d, and only if d is in K. SCALE rescales one coefficient. Owned reads change nothing.
- (ii) *Scope:* suppose no op at g precedes the last arrival t_g of supp(c), where u = sum_C c_s V_s. Then K(t_g) = supp(c), which is inside C.
- (iii) **Second meeting.** A register enters K only by being read by a K member. If it is not a survivor in C at g, it leaves K only by being read again by a K member.
  So a tied ender h is read by a member of its custody set after h acquires the tied content.
*Proof.* (i): rewrite a_d V_d + a_s V_s after V_d <- V_d + q V_s. (ii): uniqueness of the expansion. (iii) follows from (i) and (ii). []
- This gives no per-chart LP row. The toys U1 and U2 satisfy (iii) at a single chart, with partners reading X0 at the ender's prev chart.
- (The notes' further gloss, "the source of h's content is read twice", is ARGUED, not proved.)

**Lemma 14 (SEP, x-balance of custody, PROVED in P', inheriting Lemma 13's expansion).** For every t, sum_{r in K(t)} a_r(t) x(V_r(t)) = 0.
*Proof.* Apply x to u: x(u) = 0 because u lies in span e_E, and x(Sym) = 0. []
*Consequence (ARGUED, single-holder chains only).* Custody of a carrier must be taken while the carrier is x-free, unless an x-copy is also in custody.
So in a uniform single-holder ladder brigade (b, b+1, b+2) the depth is 1. Realisable chains are *stars*, where every holder swaps with its carrier at one pure chart. General holder sets: OPEN.

**Lemma 15 (DR: dirt enters as a rank, PROVED).** Work in P_M at g. Let:
- D = the P_M-dirty helper enders, with finals f_d = e_d + z_d;
- E* = E u D and C' = A_g \ E*;
- S = span e_{E*}, K0 = span V_{C'} + Sym_g, and T = span{z_d};
- tau_g = dim (T + K0)/K0 and q* = dim(xspan A_g / xspan C').
Then
  **q* <= dim(K0 cap S) + tau_g <= |H| - rank(N_H mod span N_{C' \ H}) + tau_g,** where H = C' arrivals holding some e_{E*}.
*Proof.* Let K = K0 + T. Each e_d equals f_d - z_d, so S is inside U + T = span V_{E*} + K, and dim(U + T) <= |E*| + dim K. Deleting the S coordinates (pi) gives dim pi(U+T)/pi(K) <= dim(K cap S), and x factors through pi.
x maps K/K0 onto X(K)/X(K0), and its kernel contains (K cap S + K0)/K0, so dim X(K)/X(K0) <= dim K/K0 - dim(K cap S) + dim(K0 cap S).
Add the two bounds, use X(U) inside X(U+T) and X(K0) = xspan C', and apply Lemma 12's second inequality to K0. []
tau_g <= dim T <= the number of dirty enders at g, so the count form is a special case.

**Lemma 16 (TAINT, PROVED; proof replaced).** tau_g <= dim T <= m_g + #(tainted arrivals at g). An arrival is *tainted* if its P_M value holds a symbol.
*Proof.* Each real final is clean, so rho(f_d) = e_d and z_d = f_d - rho(f_d). Write f_d (in U, by Lemma 1) as sum_{a in A_g} b_a V_a + sum_mu c_mu sigma_mu. Then
  z_d = sum_a b_a (V_a - rho V_a) + sum_mu c_mu (sigma_mu - rho sigma_mu).
Untainted arrivals satisfy rho V_a = V_a, so T lies in the span of m_g + #tainted vectors. []
**GAP (in the source).** The note decomposes z over span V_{E*} + K0, which holds only mod S. In toy D2, U = span{e_i + x0 + sigma} while z = x0 + sigma is not in U. The direct proof above has no such step.
*Tightness.* Toy D2(k) has tau = 1 at each of its k charts, with m_g = 0 and 1 tainted arrival per chart (sec 5).

---

## 5. Toys and refuted claims

All toys pass the per-event verifier (contract literals off), and every real final is clean. Frames: <p> (dim 1), a plane (dim 2), dim-3 charts above it, F9.

**U1 (degenerate late-born tie).** Registers: X0 (1,2,9), helper h (1,2,3), helper s (2,3,9). h is born at <p>; s is born at the plane.
- Plane: h += X0; h += s; s += X0; s -= h, which leaves s = -e_h.
- g (dim 3): s += h; h -= s, which leaves h = e_h and s = x0 + e_s.
- F9: s -= X0.
At g with beta = 1: q = delta = 1, the single holder is s, and N_s = 0.

**U2.** As U1, plus a second plane-born partner s2 (2,3,9). At the plane the two partners become s1 = -e_h + e2 and s2 = e_h + e2. The tie is then non-degenerate, with 2 holders and q = delta = 1.

| claim (status before) | verdict | witness (EXACT) |
|---|---|---|
| NODEG: no degenerate tie charts (SCOPE in the 901.33 floor) | **not a law** | U1 and U1p are legal degenerate late-born ties. Real words have 0 late-born ties on all 6 sides, so measuring NODEG there says nothing about the LP's regime |
| supply row SUP: late-born ties at dim v <= content-carrying interior stops at v - 1 | **REFUTED** | U6: a non-degenerate tie at (4,2) with 0 supply stops |
| SUP': each tie consumes one supplier meeting | **REFUTED** | U5: 3 ties, 1 supply stop (a single X0 read feeds the whole star chain, cancelled once at F9) |
| own (P'-dirty ends) bounded by SPEC | **REFUTED** | D1(k): one owned lifetime, never moved, peak 1, owned paid 0, k P'-dirty ends (k = 5 and 40 built). It is P_M-clean (tau = 0) |
| dirty tokens <= owned MOVEs <= paid, in count or rank form (MODEL floors 642.06 and 1143.80) | **REFUTED** | D2(k): one owned MOVE (paid 1) gives tau = 1 at k distinct dim-3 charts (k = 1 and 4 built). Each ender is a (1,2,3) helper at 2 ln 2 |
| A1: the owned-delivery matrix C has rank 8, so all 4992 orthogonal pairs carry public demand | **FALSE on the frontier** | r245g: rank C = 10 in P_M (4972 pairs) and 9 in P' (4982); #6030: 9 in P'. Only #5907 has rank 8 |
| the second dual register delivers with one ADD | **REFUTED** | Lemma 8 application, 168/168 hp's |
| done-at-O versus climbing X is a cost choice | **REFUTED (gauge)** | Lemma 5, whole-octet relabellings at dk = 0 |
| the 901.33 floor's scope is "worth < 9 R0" | **wrong** | with the degenerate budget free the floor is 754.14: all +147.2 is the NODEG scope |

D2(k): o INIT at <e1,e2>; o -= X0; MOVE o -> <e2> (owned, rank 1). Each h_i is born at <e2> and reads o (in P_M, the symbol sigma). Each h_i then climbs to <e1,e2>, reads X0, and ends at its own dim-3 chart.
Real final: e_i. P_M final: e_i + x0 + sigma.

On A1: rank C <= M is PROVED, because C = sum_mu (Y-coefficient of sigma_mu) (x) x(rho sigma_mu). C = delta on non-orthogonal pairs (EXACT).
rank C = 8 implies C = D M0 D^-1 (by rank-8 uniqueness, prior art #1212), and that implies every orthogonal pair has demand. **GAP:** the converse (NEED = 4992 implies rank 8), stated in the notes, is not proved.

Star ladder (EXACT for k <= 3; rows for k >= 4 extrapolate the op pattern, unbuilt). One pure chart P carries h (1,2,3), carriers (2, j+1, j+2), and a last holder (2, k+2, 9). Helper tax: degenerate 4.26, 6.96, 9.46 for k = 1, 2, 3; non-degenerate (twin holders) 5.64, 12.54, 17.54.
Against the floor LP's duals, a chain sits about 2.9-3.1 R0 above its optimum, nearly independent of depth for k <= 4.

---

## 6. Certified floor table (public R0; exact rational certificates, independently rechecked)

Common rows, proved in the earlier floor notes:
- cover/rectangle rows, with the corrected distinct-coverage cap;
- JR, Theorem LC, R+ and JF (degenerate budget free);
- capfix, mains and cpres.
Column bounds assume R0 <= 8000.
Every row passes the swarm test (r245g, #6030, #5907 feasible at violation 0).
The owned layer adds 380 (P - 56) + (8 * 7 ln 7 - sum r ln r) >= -11.1 R0-eq at P = 56.

| scope | own / owns / ownc | NEED | floor | % of r245g (7953.3) |
|---|---|---|---|---|
| SPEC + paid <= 56 (taint rows, Lemmas 15-16) | taint | 4972 | 0.00 | 0 |
| **SPEC + paid <= 56 + package literals (events < 26000, public <= 770)** | taint (free gives the same) | 4972 | **444.88** | 5.59 |
| measured owned scope (P' counts), A1-corrected | 22 / 18 / 64 | 4972 | **751.46** | 9.45 |
| same + literals | 22 / 18 / 64 | 4972 | **1327.08** | 16.69 |
| measured P_M rank scope (sum tau <= 7, owns 18 P', 26 owned MOVE visits) | 7 / 18 / 26 | 4972 | 781.16 | 9.82 |
| same + literals | 7 / 18 / 26 | 4972 | **1371.98** | 17.25 |

Scopes that every row carries (read before quoting):
- **NEED = 4972 is SCOPE in every row, the 444.88 row included.** It is the minimum over three words in P_M (Z = 20 zero-demand orthogonal pairs, from r245g). A paid-aware bound on Z is OPEN. So 444.88 is "SPEC + paid + literals + Z <= 20", not SPEC + literals alone.
- Literals are retargetable. The precedent is public 735 -> 770; 968 was requested once, and the analogous older row moved by 241 R0 under it.
- own = 22, owns = 18 and ownc = 64 are measured constants (P'). owns = 18 was measured on #5907 only: the swarm test leaves dirty births free, so it never checks owns on r245g or #6030.
- In P_M the D-side (transpose) rows are used by symmetry; the P_M transpose was not built.
- The rank-form reading of the non-tie rows (dirty, ncont, Q, rank_F) and the coverage corollary with the per-chart bound |H| + tau are ARGUED, not re-audited. These certificates postdate the independent audit.
- 0.00 with own/owns/ownc unbounded: the owned scope carries every floor above 444.88.

Superseded (do not quote):
- 742.9, 736.28, 752.85, 794.53 and 813.31 are INVALID (the old cap48 row).
- 754.14 becomes 751.46 and 502.37 becomes 444.88, and 1342.25 becomes 1327.08, after the A1 correction.
- 901.33 holds only under SCOPE NODEG.
- 642.06 and 1143.80 are refuted (D2).

---

## 7. Other EXACT, scoped results (censuses, not lemmas)

| result | scope |
|---|---|
| Root staging is load-bearing: 10/10 staging-drop variants are UNSOLVABLE | reads re-solved; feeds, other roots and public chains fixed; new stops only on the root's own frames |
| Market birth level is forced: on all 14 duals every pair of members' next frames meets exactly in G | geometry of the frontier frame table |
| Single-source X-Y incidence flips: exact ceiling 0 (1/131 is a tie). The read order is content-forced at 80/131 services; the relaxed MODEL ceiling is 72.8 R0 | Y chains fixed, nesting exact; 4/4 mechanism rebuilds UNSOLVABLE |
| Hub-end conversions (ceiling 7.46 R0): 12/12 UNSOLVABLE. The residual lies on the F9 exchange partner's coordinate (Lemma 9: span{e_R + c, e_C} does not contain e_R) | rest frozen; unknowns into R at its end frame |
| No sub-2.70 leaver window on any of the 14 hubs | one-hop windows; two-hop windows need re-framing a copy's hp frame |
| D3 pair read by a Y at dim 2 is pinned by content: 19/19 single moves and 4/4 joint moves infeasible | X chains fixed, existing co-presences only |
| Y read level: the 6 sites with a cheaper dim-3 read are geometrically blocked (the meet with the partner is the pair frame itself) | partners' plans fixed |
| B3 dim-7 Y-Y butterflies are load-bearing: 48/48 deletions infeasible | chains fixed |
| R-FOLD sites: #6030 has 3, r245g has 0 (exhausted); the corpus has 201 sites (a sum of ceilings, not a gain) | Lemma 6 precondition only |

---

## 8. Gaps found (collected)

1. **TAINT (Lemma 16):** the note's decomposition of z over V_{E*} + K0 is invalid (z need not be in U). Replaced by a two-line proof from rho(z) = 0.
2. **End-low (Lemma 9):** the "non-Y registers, Y returns coefficient 0" form assumes that only Y holds e_y. Replaced by the conservation form.
3. **Leavers >= 8 (Lemma 10):** owned CLEARs or departures at O_r are not excluded in the source. The statement is scoped to hubs with no owned visitor.
4. **R-FOLD (Lemma 6):** the saving is mu(0, beta, beta + D), not "staging(a -> b)". They agree only when beta and the root's top jump are both 1. Realisation is not implied by the precondition.
5. **Additivity A2:** combining edits needs a single sign change of F (an invoice property, assumed).
6. **Commutation (Lemma 7):** only the "if" direction is proved; the notes say "iff".
7. **CUST (Lemma 13):** (ii) needs "no op at g before t_g" as a hypothesis. "Source read twice" is ARGUED.
8. **SEP chains (Lemma 14):** depth 1 for uniform brigades is ARGUED for single holders; general holder sets are OPEN.
9. **JF count corollary:** the token containment relies on the earlier R+ holder argument (cited, not re-checked).
10. **A1:** "NEED = 4992 implies rank 8" is unproved. NEED = 4972 is a hidden SCOPE in the 444.88 floor.
11. **Floors:** the rank-form non-tie rows and the coverage corollary with tau are ARGUED. owns = 18 was measured on #5907 only. The P_M transpose is by symmetry.
12. **Lemma 8b** excludes owned paths. The source's escape note ("no spare owned lifetime exists") is a price argument, not part of the proof.
13. **Floor sensitivity:** the source's "< 9 R0" reading of the NODEG scope is wrong (the true value is 147.2 R0).
14. **CUST / SEP (Lemmas 13-14)** hold in P' only. In P_M or in real values a public row can be zeroed by an owned copy, so uniqueness of the expansion fails.

---

## 9. Gap status (GAPCLOSE, Oct 28)

Ranked by impact: G1 (whether any floor above 0 is free of measured constants) > G2 > G5 > G4 > the rest. Code: ext/GAPCLOSE/.
Verdicts: CLOSED (proof), REFUTED (exact witness), NARROWED (precise remaining assumption). Nothing argued is promoted to proved.

### G1. NEED is measured; is there a SPEC-level floor? -> NARROWED

**Lemma G1a (NEED from SPEC + paid, PROVED).** Work in P_M. Let C be the owned-delivery matrix of sec 5 (FLOORDIRTY cmat.py) and M the number of owned MOVEs. Then
  **NEED >= 104^2 / rank C - 104 >= 104^2 / M - 104**, so under the scope paid <= 56 (M <= 56): **NEED >= 90.**
*Proof.*
1. (C = delta off the orthogonal pairs.) Real finals give x(Y_j) = e_j (l.164-168). rho is the identity on public coordinates, so PUB + C = I, where PUB is the
   x-part of the P_M public (non-symbol) part. P3a holds for P_M public parts (owned values at a chart are combinations of values at that chart plus that chart's
   symbols; a MOVE re-symbolises). So PUB_ji != 0 needs p_i in a frame of Y_j, which lies inside Q_j = q_j^perp: p_i.q_j = 0. Hence C_ji = delta_ij on
   non-orthogonal pairs, and C_jj = 1 because every port has odd weight.
2. (rank C <= M.) C = sum over symbols of (Y-coefficients) x (x(rho sigma)); there is one symbol per owned MOVE (Lemma 2); each owned MOVE adds >= 1 to paid (l.127).
3. (Acyclic sets.) Let D be the digraph on the 104 indices with an arc j -> i iff i != j and C_ji != 0; it has NEED arcs, all on orthogonal pairs (step 1).
   If D[S] is acyclic, C[S,S] is permutation-similar to a triangular matrix with unit diagonal, so rank C >= |S|. Take a uniformly random order and keep j when it
   precedes all its out-neighbours: the kept set is acyclic and has expected size sum_j 1/(d+(j)+1) >= 104^2/(104 + NEED) (Jensen). So 104^2/(104+NEED) <= rank C. []
*Tightness (abstract).* 48 disjoint 2x2 rank-1 orthogonal blocks plus 8 singletons give rank 56 with 96 orthogonal entries. So rank-and-paid counting alone
cannot exceed about 96. The geometry is needed. (Such a block costs owned gap >= 2 per pair: p_j + p_k lies in no frame inside Q_j cap Q_k, since (p_j+p_k).q_j = 1.)
*Checks (EXACT, cmat.py).* r245g: rank 10, M 26, NEED 4972. #6030 and #5907: rank 8, M 20, NEED 4992. All three are far above the bound.

**What NEED >= 90 buys (LP, exact certificate).** The scope is the 444.88 row's (tzinv flags, taint=56, ev=26000, hinv=562), with needz = 4902.
It gives **0.00**: CERTIFIED, RECHECK True, and the swarm test r245g / #6030 / #5907 at violation 0/0/0 (cert gc90, jobs/GC_chain1.log).
The toys (D1, D2, U1-U6) have no 104-port cover, so they are not LP objects. Lemma G1a is a 104-port statement, and the toys do not test it.

*NEED threshold probes (same scope, exact certificates, solve only):*

| NEED | floor |
|---|---|
| 4972 (measured) | 444.88 |
| 4500 | 269.48 |
| 4000 | 120.30 |
| 3000 | 0.00 |

needz enters the right-hand sides only, and affinely, so the floor is convex in NEED. The chord through 4000 and 4500 therefore gives **floor > 0 for every NEED >= 3597**.

**Status.** The SPEC + paid + literals floor is 0 at NEED = 3000 and provably positive from NEED >= 3597. Lemma G1a gives only 90.
- *Remaining assumption (precise):* **Z <= 4992 - N\*** with N\* >= 3597 (N\* = 4972 for the quoted 444.88), a paid-aware bound on orthogonal entries with no owned delivery. Equivalently, at owned paid <= 56 the
  owned-delivery matrix has >= N\* nonzero orthogonal entries.
- The missing ingredient is geometric: the support of each symbol's b-side (x-content at the departure chart, recursively through earlier symbols). Rank and paid alone
  are tight at about 96 (abstract example above).
- So **no floor above 0 currently rests on SPEC + paid + literals alone.** The 444.88 row is "SPEC + paid + literals + Z <= 20".
- In P' the rank argument fails: there rank C is bounded only by the number of owned-to-public reads, not by paid. Lemma G1a is a P_M statement, which is the
  accounting FLOORDIRTY used for NEED.

### G2. "Leavers >= 8" (Lemma 10 / HUBMKT) with owned visitors -> unscoped claim REFUTED; corrected Lemma 10' PROVED

**Lemma 10' (PROVED).** Let O be a chart with no reader and no X ending there. Then
  **#public departures from O >= dim xspan(arrivals at O) - #(owned MOVEs out of O) - #(owned CLEARs at O).**
*Proof.* Lemma 9's invariant with each CLEAR treated as a departure of the erased value: span(arrivals) lies in span(public departures) + span(owned departures)
+ span(cleared values) + span(finals at O). Project with x. Helper finals are x-free, and owned lifetimes leave no finals. []

*Witness (EXACT, GAPCLOSE/hubown.py, real values).* On r245g, #6030 and #5907, octets 3 and 5 (charts 243 and 240) have arrivals of x-rank 8, but only
**7 public leavers**: each has 2 owned exits (1 owned MOVE out + 1 CLEAR). So "#leavers >= 8 per full octet hub", read as public leavers, is **false on the frontier**.
Lemma 10' holds with 0 violations on all 15 hub charts of all three words. Octet 4 (chart 1091) has 3 owned exits and 12 public leavers.
Octets 6, 11, 12 and 13 have arrival x-rank 7.
- Consequence: any per-hub "8 leavers" price must charge public + owned exits. The extra owned exits are owned MOVEs (paid) or CLEARs (events only).

### G4. A1 converse "NEED = 4992 implies rank C = 8" -> REFUTED (as stated); no floor uses it

*Witness (exact, by hand).* C = I + (1/100) O, where O is the 0/1 indicator of the 4992 orthogonal pairs. C = delta on non-orthogonal pairs, and every orthogonal
entry is nonzero, so NEED = 4992. Every row has off-diagonal mass 48/100 < 1, so C is strictly diagonally dominant (Levy-Desplanques): **rank 104.**
- Scope: this refutes the matrix statement. Whether a *legal word with paid <= 56* can have NEED = 4992 with rank C > 8 is open. It is part of G1's question, and
  #6030 in P' (rank 9, NEED 4982) comes close.
- Impact: none on the certificates. Floors use NEED directly. The proved direction (rank 8 implies C = D M0 D^-1, which implies NEED = 4992; Theorem U) is unaffected.

### G5. Rank-form reading of the non-tie rows -> NARROWED

*Monotonicity (EXACT, cert_freez.pkl).* Of the 995 incidences of the dirt columns oL and oD, 963 lie in lower-bound rows with a positive coefficient, so a larger oL
only relaxes them. The other 32 are the budget rows ownL/ownD (hi) and the SPEC rows ownTL/ownTD (oL[v] <= # helper enders at v).
- Hence the SPEC + literals number (444.88 = freez, owned budgets free; the taint rows add 0) **does not need the rank form.** Set oL = the COUNT of P_M-dirty enders
  (which is >= tau_g, and satisfies ownT). Then the certificate is valid as soon as each non-tie row holds in count form for P_M-dirty enders.
- *Remaining assumption:* dirtyL, ncont, Q and rankL_F hold in **count form in P_M**. Their source proofs are for P'-dirty counts, and the P' -> P_M transfer is not
  written. The rank form is needed only for the measured P_M-rank scopes (781.16, 1371.98), and stays ARGUED there.
- The tie rows are safe in either form. Declaring a clean ender dirty adds z = 0 to T, so Lemma DR still holds and count >= tau.

### Not reworked here
G3 (CUST/SEP in P' only; D1/U-toys in sec 5 already scope them), A2 single sign change, Lemma 7 "only if", the JF token containment, and the P_M transpose
are unchanged. Their sec 8 entries stand.

---

## 10. NEED from SPEC + owned paid (NEEDBOUND, Oct 28)

Goal: prove NEED >= 3597 (the point where the SPEC + paid + literals floor turns positive, sec 9 G1) from SPEC + owned paid <= 56.
**Verdict: NOT CLOSED.** NEED >= 3597 is not proved, and no witness of NEED < 3597 at owned paid <= 56 was found. The floor is unchanged
(0.00 without the Z scope; 444.88 with Z <= 20). Nothing new reached the floor's threshold, so no LP job was run. Code: ext/GAPCLOSE/needmove.py (read-only, exact).
What this section adds: the exact arena (10.1); the rank-8 frontier (10.2); a local Gram lemma that kills the cancellation-free half of the abstract
NEED ~ 96 example (10.3); and the precise remaining gap (10.4).

### 10.1 The arena REL (PROVED necessary conditions)
Readers are the ports themselves: q_j = p_j (FLOORDIRTY cmat.py `orth`). Q_j = p_j^perp. Work in P_M (sec 0.2). Each owned MOVE mu goes from a gather frame g_mu
to a landing L_mu, with L_mu strictly inside g_mu (l.126). It creates one symbol, and C = sum_mu u_mu v_mu^T (Lemma G1a step 2), where u_mu(j) is the coefficient of sigma_mu in Y_j's P_M final
and v_mu = x(rho sigma_mu). Then:
- (R1) **u_mu(j) != 0 implies L_mu is inside Q_j** (p_j is orthogonal to L_mu). *Proof.* sigma_mu enters P_M values only at L_mu. An owned holder that moves is re-symbolised,
  so sigma_mu reaches Y_j only through ADDs at frames containing L_mu: public frames ascend, and an owned holder that does not move stays at its frame. Y_j's frames lie in Q_j. []
- (R2) **v_mu lies in X(g_mu) + span{v_nu : nu earlier, L_nu inside g_mu}** (relays). *Proof.* By P3a for P_M public parts (G1a step 1), the non-symbol part of any value at g is supported on ports(g).
  A symbol present at g belongs to a move that landed in a subframe of g (same argument as R1). Apply rho and x. []
- (R3) C = delta on non-orthogonal pairs, diagonal included (G1a step 1). NEED = #{orthogonal (j,i) with C_ji != 0}.
- (R4) sum_mu (dim g_mu - dim L_mu) = **owned** paid. Note: the verifier's paid[] counts every MOVE (l.127), public ones included. The scope "paid <= 56" and the law's
  "paid - 56" mean the owned part (sec 9 G1a uses M <= owned paid).
REL drops everything public except R1-R2. In particular a relay (a public re-ascent carrying owned content) costs no paid in REL; it costs R0 in a real word.

### 10.2 The rank-8 frontier (PROVED, citing Theorem U)
**Lemma N1.** rank C >= 8, and rank C = 8 implies NEED = 4992. Hence **NEED < 4992 forces rank C >= 9, and so at least 9 owned MOVEs.**
*Proof.* An 8-clique K of non-orthogonal ports has C[K,K] = I_8 by R3, so rank C >= 8. If rank C = 8, then C is a rank-8 completion of the P104 pattern, so
C = D M0 D^-1 (Theorem U; prior art #1212). M0 is nonzero on every orthogonal pair (ROOTARCH sec 5: E_ij E_ji = 1/4 on all 2496 orthogonal edges). []
- So any NEED below 4992 at owned paid <= 56 comes from a rank >= 9 owned layer. r245g has rank 10, NEED 4972 and owned paid 56. Theorem R9F covers rank-9 family F only;
  ROOTARCH sec 6 (escape E1) lists rank >= 9 outside F as OPEN and unswept. That is exactly where any proof or witness at NEED < 3597 must live.

### 10.3 Local Gram lemma: cancellation-free layers cost >= 1 per diagonal
Say mu **serves** the diagonal set S_mu = {j : u_mu(j) v_mu(j) != 0}. Every j is served by some mu, because C_jj = 1. The move is **cancellation-free** if its rectangle supp u_mu x supp v_mu contains no non-orthogonal off-diagonal pair.
Otherwise its rank-1 term puts nonzeros on non-orthogonal pairs, and other moves must cancel them (R3). A non-orthogonal pair inside S_mu is the simplest case.

**Lemma N2 (local Gram, PROVED).** Let L be inside g, and let P be the set of ports in g that are orthogonal to L. For p, p' in P, the value p.p' depends only on the classes of p and p'
in g/L, and every p in P has a nonzero class. So the F2 Gram matrix of P has rank <= dim g - dim L, and an orthonormal subset of P has size <= dim g - dim L.
*Proof.* p.(p' + l) = p.p' for l in L, because p is orthogonal to L; by symmetry the same holds in the first slot. p.p = 1 (odd weight), so p is not in L. Orthonormal classes are independent. []
- (a) **Gap 1.** Any two ports of g that are orthogonal to a hyperplane L of g are non-orthogonal (both lie in the coset g \ L, so p + p' is in L, and p.p' = 1 + p.(p + p') = 1).
- (b) **Relay-free move.** If v_mu lies in X(g_mu), then S_mu is contained in P (by R1), so rank_F2 Gram(S_mu) <= gap_mu. A cancellation-free relay-free move has |S_mu| <= gap_mu.
- (c) **Ancestral form.** Let W_mu be the span of the gather frames of mu and of all its R2-ancestors. Then v_mu lies in X(W_mu), and **dim W_mu - dim L_mu <= sum of the gaps over mu and its ancestors** (each counted once).
  *Proof.* Add the gather frames in reverse topological order. Each ancestor nu lands inside the gather frame of a child that is already added, so adding g_nu raises the dimension by
  at most dim g_nu - dim L_nu. Then N2 applies to (W_mu, L_mu). []
- (d) **Single chain (PROVED).** Take one owned lineage with no resets (the scalar on the previous symbol's content is nonzero at every step), no relay from other moves and no public re-ascent, descending from g_top to L_bot, with every move
  cancellation-free. Then it serves at most dim g_top - dim L_bot = (its owned paid) distinct diagonals.
  *Proof.* Let j be served at some step, so p_j is orthogonal to that landing. Then p_j is outside every later frame of the chain, so e_j is never local again and stays in the content.
  A later move serving k has k in supp u and j in supp v, so cancellation-freeness makes k orthogonal to j. The served set is therefore orthonormal, it lies in ports(g_top), and every member is orthogonal to L_bot. Apply N2. []
- **Consequence.** The abstract tight example of sec 9 (48 orthonormal 2-blocks plus 8 singletons, NEED 96, rank 56) is cancellation-free. Any cancellation-free realisation of it
  (single chains or relay-free moves) costs owned paid >= 104 > 56. (Cancellation-freeness is a property of the decomposition, not of C.) **At owned paid <= 56 the owned layer must cancel (non-orthogonal pairs inside some S_mu) or share content (branching, relays).**
- *EXACT (needmove.py; r245g and #5907; not run on #6030 here):* every serving move has non-orthogonal pairs inside S.
  - r245g: 14 of 26 symbols serve. Their |S| is 2-28, and 198-324 ordered non-orthogonal pairs must be cancelled per large move.
  - #5907: 9 of 20 symbols serve.
  - Each large server has rank_F2 Gram(S) = 7 and lands at dim 1 (EXACT). Its lineage top is at dim 8, read from the table's chain structure rather than from a computed W, which is consistent with N2(c) at equality. The 8 relay-free moves serve nothing (0 violations of N2(b)).
  The frontier is purely the cancelling, content-sharing (E8) regime.

### 10.4 What is left (precise)
- **Proof side (OPEN).** No result here bounds NEED for layers that cancel. N1 handles rank 8. N2 handles cancellation-free single chains and relay-free moves.
  The remaining statement is: *in REL with owned paid <= 56, every rank >= 9 layer whose served sets carry cancelled non-orthogonal pairs has >= 3597 nonzero orthogonal entries.*
  Rank or count arguments alone stay near 96 (sec 9). The missing tool is a rigidity statement for partial E8-like layers: Theorem U extended to rank 8 + s with an owned-cost budget.
- **Witness side (OPEN).** Relays make REL more permissive than SPEC-with-R0. By-hand REL constructions:
  - Row service: gather at F9, land at Q_j, gap 1, any row.
  - Column service: gather at <p_k>, land at F0, gap 1, any column.
  - Relayed 2-block: inject r = sum over an orthonormal R of e_k at F0 with gap >= |R|, then gap-1 moves from Q_k to Q_j cap Q_k for orthogonal pairs (j,k). This breaks N2(b) for a single move.
  Every one of these still pays >= 1 per served diagonal (ARGUED, not proved for general relay networks). No REL layer with NEED < 3597 at owned paid <= 56 was built.
  ROOTARCH sec 6 rates rank >= 9 constructions as hard: no non-F completion converges.
- **If such a witness exists,** a SPEC-level NEED floor must charge what REL drops: the public re-ascents that carry owned content (relays) and the content reads at gather frames.
  Those are R0 (helper lifetimes), not paid. The floor would then come from a joint paid + R0 argument, not from paid alone.
- Remaining assumption for every floor > 0 (unchanged from sec 9): **Z <= 4992 - N\*, N\* >= 3597.** Nothing argued here is promoted.

---

## 11. Rigidity with cancellation, and the relay route (RIGIDITY, Oct 28)

Goal: lift NEED past 3597 at owned paid <= 56, by (a) a rigidity bound for cancelling layers or (b) charging relays in R0.
**Verdict: NARROWED.** Route (b) is obstructed EXACTLY: the frontier owned layers have no relays, so a relay term is 0 on them and (b) reduces to (a) on the relay-free class.
Route (a) is neither proved nor refuted. What is new: a served-set rigidity lemma that allows cancellation (N2(e), PROVED, tight on the frontier), a weak Hadamard identity (Lemma H), and exact local rigidity of the frontier skeleton.
No floor changed, so no LP job was run. The floor stays at 0.00 without the Z scope, and 444.88 with Z <= 20. Code: ext/RIGIDITY/ (all scripts read-only and exact).

### 11.1 N2(e): served-set rigidity with cancellation (PROVED)
Notation as in sec 10. U_mu = supp u_mu (rows), V_mu = supp v_mu (columns), and Gamma is the 0/1 indicator of non-orthogonal port pairs (diagonal included).
**Lemma N2(e).** rank_F2 Gamma[U_mu, V_mu] <= dim W_mu - dim L_mu <= lineage paid(mu) (the gaps of mu and its R2-ancestors, each counted once).
No cancellation-free hypothesis is needed. In particular rank_F2 Gram(S_mu) <= lineage paid.
*Proof.* By N2(c), v_mu lies in X(W_mu), so the ports of V_mu lie in W_mu. By R1, the ports of U_mu are orthogonal to L_mu, and L_mu lies inside W_mu.
Gamma[U,V] is a submatrix of the pairing W_mu x span(U-ports) -> F2. That pairing has rank dim W_mu - dim(W_mu cap U^perp), which is at most dim W_mu - dim L_mu. []
- Sec 10.3 used cancellation-freeness only to make S orthonormal (so |S| <= gap). N2(e) bounds the F2 Gram rank instead, and needs nothing about cancellation.
- **This bounds served-set geometry, not NEED.** Turning it into a NEED bound still needs the delta constraint (R3); see 11.3.
- *Tightness (EXACT, skel.py, all three words).* The script recomputes W_mu from the P_M ancestry (the symbols present in the mover's value at its MOVE).
  - Every move with |S| >= 20 has rank_F2 Gram(S) = 7 = dim W - dim L = lineage paid.
  - The single |S| = 8 move has rank 4 and lineage paid 5 (slack 1).
  - There are 0 violations on r245g (26 symbols), #6030 and #5907 (20 symbols each), and dim W = 8 for every move.

### 11.2 Lemma H (Hadamard rank, PROVED; weak)
R3 says C o Gamma = I_104. C = sum_mu u_mu v_mu^T, and (u v^T) o Gamma = D_u Gamma D_v. Hence
  **104 <= sum_mu rank_Q Gamma[U_mu, V_mu].**
*EXACT (hadamard.py).* On #6030 and r245g the sum is 416, with rank_Q Gamma[U,V] = |U| on every serving move. The F2 ranks are 7 against Q ranks of 44-52.
So the lemma is far from binding. Its value is diagnostic:
- cost tracks rank_F2 (N2(e)), while delta needs rank_Q;
- the gap between the two (about 45 per serving move) is where cancellation happens, and any NEED proof must bite there.
For a single relay-free move whose Gamma block is class-structured (rank_Q = rank_F2), Lemmas H and N2(e) together give cost >= the rank needed. Chains share cost, which breaks this additivity.

### 11.3 Route (a): exact local rigidity of the frontier skeleton (EXACT, scoped)
Fix a word's owned skeleton (gathers, landings, ancestry) and its v_mu. Free every u_mu(j) subject only to R1. Rows decouple: row j of C is a^T V_j, and delta must hold on the non-orthogonal columns.
- *Solution dimension per row:* d_j <= 3 on r245g (52 rows with d = 0) and d_j <= 2 on #6030 and #5907.
- *EXACT minimum NEED over this REL u-space (uexact.py).* It enumerates every flat cut out by <= d_j orthogonal-entry hyperplanes, in exact rationals.
  The minimum is **4962 on all three words**: 30 zeros in total, at most 10 in a row. These are REL witnesses (valid in REL, not in SPEC), and none comes near 3597.
- *Transpose probe (vfree.py; not a witness).* Fix u and free v_mu(i) whenever p_i is in W_mu. This is the N2(c) relaxation, a superset of R2.
  The greedy result is 4729 on r245g, also above 3597.
- *Scope.* This is local rigidity of one skeleton, not a bound over REL. Other skeletons (other landings and frames, branching trees, longer chains with more terms per unit of paid) are untested.

### 11.4 Route (b) obstruction (EXACT)
relays.py classifies every R2 ancestry edge nu -> mu as either:
- SAME: L_nu = g_mu, an owned hand-off at one chart, which costs no R0; or
- STRICT: L_nu is strictly inside g_mu, so the content must climb publicly (a relay).
**STRICT edges: 0 on r245g, 0 on #6030 and 0 on #5907.** Every frontier lineage is a disjoint path, and each mover has at most one ancestor.
- So a cost-aware relay term (stop tax per STRICT edge) is identically 0 on the swarm words. The swarm test passes trivially and the term adds nothing to the floor.
- It could lift the floor only if low-NEED layers were proven to need relays. That is the statement "relay-free layers (path or tree forests, SAME edges only) at owned paid <= 56 have NEED >= 3597", which is route (a) restricted to a subclass. **(b) is not shorter than (a).**
- Correction to an idea floated in this lane: "relay-free layers cannot satisfy delta at paid <= 56" is **false**. All three frontier words are counterexamples.

### 11.5 Small-case census and the block witness family (EXACT census; costs ARGUED)
The witness family that would kill (a): block-diagonal C = direct sum of restrictions of M0 to sub-root-system line groups (sec 10.2 / ROOTARCH C1).
Such a C is a valid pattern. Its rank is sum of r_k, and its NEED is the number of within-block 60-degree pairs. On the matrix side this is far below 3597 (a partition into A3 line groups, existence unchecked, would give about 416 at rank 52).
Whether these blocks can be realised in REL at owned paid <= 56 is the open question. **Not built.**
*Census (rich.py, grp4.py).*
- 3441 four-dim F2 subspaces have all 8 odd vectors as ports:
  - 759 are non-orthogonal 8-cliques (radical of dim 3), which force C_G = I_8;
  - 2682 are of two-clique type (radical of dim 2, two non-orthogonal 4-cliques that are mutually orthogonal), with C_G = [[I, X], [Y, I]] and minimum rank 4.
- No 5-dim subspace among the rich extensions holds more than 12 ports.
- For two-clique groups, every Gamma block is class-structured, so rank_Q = rank_F2. With single relay-free moves supported inside the group, Lemmas H and N2(e) give cost >= 8 per 8-port group, i.e. 1 per port, with no NEED/cost trade-off.
  For chains, or for moves reaching outside the group, this is **ARGUED** only. A trade-off can only come from Q/F2 rank-gap blocks (E8-like served sets), which is the frontier's own mechanism.

### 11.6 What is left (precise)
- **Open statement:** in REL, restricted to relay-free forests (SAME edges only, which covers the whole frontier) with owned paid <= 56, every layer has >= 3597 nonzero orthogonal entries of C.
  - N2(e) controls each move's served-set F2 geometry. Lemma H is the delta identity.
  - The missing link is a quantitative statement: cancelling the rank_Q - rank_F2 excess on the Gamma positions forces nonzeros on orthogonal positions.
- Charging relays adds nothing until that is proved. Because the frontier drops no relay cost, the only other public costs a joint paid + R0 argument could charge are the content reads at gather frames and the Y-side deliveries.
- **The witness that would kill (a)** is a REL realisation of a sub-root-system block C at owned paid <= 56 (11.5). It has not been attempted.
- Floors are unchanged: 0.00 at SPEC + paid + literals, and 444.88 with Z <= 20. Nothing argued here is promoted.
