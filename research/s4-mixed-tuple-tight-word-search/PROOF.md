# Window lemma and the four-role exclusion for the mixed S4 tuple

Prepared by Sagar Thakrar (thakrarsagar) with substantial AI assistance from
Claude (Anthropic, Claude Opus 5.5). Apache-2.0. This is a written reduction
plus an exhaustive finite search. It has not been formally verified, and no
human has reviewed it independently.

## 0. Model (inherited unchanged)

This is the formal `F2[S4]` register model of Nick Petalas's PR2583 and of
Arham Tahir's PR2998. Permutations are written in one-line notation, and `ab`
means `a after b`. The adjacent labels are `s1=2134`, `s2=1324` and
`s3=1243`, with prices `(2,1,2)`. There are r scalar roles over `F2`, and
every role starts arbitrary (dirty). A paid call is

    D_N(s) = I + ([s]+1) N,

where N is a binary rank-one idempotent `u v^T`, with `u,v` in `F2^r`
nonzero and `v^T u = 1`. Scalar `GL_r(F2)` maps are free. The endpoint must
equal the full group-algebra matrix

    T = diag([2143],[3142],[4231],[2143],1,...,1)        (r >= 4),

so spectator roles are restored exactly. The direct word costs
`4+5+8+4 = 21` (verify.py multiplies an explicit one in exact arithmetic).
PR2998 proves that coordinate cuts give exactly 20.

## 1. Normal form (inherited: Ross Richardson's PR1989 argument, reused in PR2583)

For `G` in `GL_r(F2)`, `G D_N(s) = D_{G N G^-1}(s) G`, and `G N G^-1` is again a
binary rank-one idempotent. All free maps can therefore be pushed to the
right, so a circuit with m paid calls equals `D_1 ... D_m G`. The
augmentation `F2[S4] -> F2` sends each `D_j` to `I` and T to `I`, so `G = I`.
Hence **a circuit with m paid calls realizes T if and only if some product of
exactly m paid gates equals T.** The search below enumerates every such
product, with every idempotent allowed at every position.

## 2. Cut potentials (inherited cut-rank lemma)

Let `Omega` be a finite permutation S4-set and `H` a subset of it. The
representation `rho(g) e_x = e_{gx}` is a ring homomorphism, and it extends
entrywise to `M_r(F2[S4])`. For a matrix M, define two potentials:

* `phi->_H(M)` is the F2 rank of the block of `rho(M)` from `H x [r]` to
  `H^c x [r]`;
* `phi<-_H(M)` is the rank of the block from `H^c x [r]` to `H x [r]`.

Each potential satisfies three facts.

1. It is subadditive: `(AB)_{21} = A_{21}B_{11} + A_{22}B_{21}`.
2. A gate has value `c_s(H) = #{x in H : s x notin H}`. The identity has no
   off-diagonal block, and `rank(X tensor N) = rank X` when N has rank one.
3. The target has value `Phi_H(T) = sum_i c_{t_i}(H)`.

This is the cut method of Adam Gall (PR1941) and Ross Richardson
(PR1966/PR1989). Two blocks are used here only because each one is a valid
potential with the same charge profile.

## 3. Window lemma (new pruning device)

**Lemma.** Let `W = L_1 ... L_m = T`, and let the label counts be
`n = (n1,n2,n3)`. Let `P_j = L_1 ... L_j` have counts `m_j`, and write
`c = (c_s1(H),c_s2(H),c_s3(H))`. Then for every j and either block,

    Phi_H(T) - c.(n - m_j)  <=  phi_H(P_j)  <=  c.m_j .

*Proof.* The upper bound is subadditivity over the first j letters. For the
lower bound, `Phi_H(T) <= phi(P_j) + phi(L_{j+1}...L_m)`, and the second term
is at most `c.(n-m_j)`. QED.

**Corollary (prefix tightness).** If `c.n = Phi_H(T)`, then
`phi_H(P_j) = c.m_j` for every prefix. Every letter changes the potential by
exactly its charge, both from the identity end and from the target end. This
is sound for every word with counts n. It assumes nothing about optimality
beyond the counts themselves.

The search uses three cuts, each with both blocks:

| cut | module | H | charges (s1,s2,s3) | Phi(T), four targets |
| --- | --- | --- | --- | ---: |
| inv | ordered pairs (12 points) | `{(a,b): a<b}` | (1,1,1) | 2+3+5+2 = 12 |
| c1 | natural (4 points) | `{1}` | (1,0,0) | 4 |
| c3 | natural (4 points) | `{1,2,3}` | (0,0,1) | 4 |

## 4. A cost-20 word has counts exactly (4,4,4)

This section is inherited and only made explicit. The bound
`cost >= sum_i L(t_i)` with `L = inv + c1 + c3` is PR2583's, and PR2998's open
question already observes that a cost-20 word has twelve paid letters and
eight exterior letters. The argument is restated for completeness.

Every word for T satisfies `n1+n2+n3 >= 12` (inv), `n1 >= 4` (c1) and
`n3 >= 4` (c3). Spectators contribute zero, so this holds for every r >= 4.
If `2n1+n2+2n3 = 20`, then `n1+n2+n3 = 20-(n1+n3) >= 12`, which forces
`n1+n3 <= 8` and hence `n = (4,4,4)`: twelve paid letters. All three cuts
are then tight, so the corollary fixes every prefix potential exactly. Costs
below 20 are excluded by the same bound (PR2583; PR2998's coordinate-cut
value), and costs are integers. **So
"cost <= 20" and "cost = 20 with counts (4,4,4)" are the same search.**

## 5. Exhaustive search from the target end

Words are enumerated backwards: `P_12 = T` and `P_{j-1} = P_j L_j`, since each
gate is an involution (`([s]+1)^2 = 0`). Each branch is kept only if all
six windows hold for `P_{j-1}`, with the remaining counts. A word is
reported only if it reaches depth 12 and `P_0 = I` holds exactly in
`F2[S4]`. Every word for T passes every window (section 3), so pruning
cannot discard a solution. The alphabet has `3 (2^r-1) 2^(r-1)` gates: 360
for r = 4 and 1488 for r = 5.

**Symmetry, used only for r = 5.** Conjugation by
`G` in `GL_2(F2)` acting on roles 1 and 4 fixes T, because both roles hold
`2143`. So does the automorphism `x -> w0 x w0` with `w0 = 4321`, applied to
every coefficient. Every target, including 1, is `w0`-invariant, and this map
swaps s1 and s3, which preserves the counts `(4,4,4)`. Both maps are ring
automorphisms of `M_r(F2[S4])`. They send gates to gates and words for T to
words for T, so a word exists only if one exists whose last letter `L_12`
(the first peeled letter) is an orbit representative. The 56 surviving first peeled letters fall into 7
orbits under this group of order 12.

Recorded node counts (nodes that pass all windows at each peeled depth):

| roles | depths 1..12 | survivors at depth 12 |
| --- | --- | ---: |
| r = 4 (no workspace), all 360 first letters | 56, 1904, 28562, 207168, 571536, 648720, 381816, 0, ... | 0 |
| r = 5 (one restored dirty spectator), 7 orbit representatives of the 56 depth-1 survivors | 7, 238, 3571, 25940, 72256, 85622, 52422, 0, ... | 0 |

Both trees die at depth 8. No 12-letter word passes the windows on its last
eight letters, so no word exists. The r = 4 tree has 1,839,762 window-feasible
nodes in total, and the r = 5 representative tree has 240,056.

## 6. Theorem (scoped finite exclusion)

**Theorem.** In the model of section 0:

1. On exactly four roles, no circuit of paid cost `<= 20` realizes
   `diag([2143],[3142],[4231],[2143])`. The direct word costs 21, so **the
   four-role optimum is exactly 21**.
2. On five roles (one dirty spectator, restored), no circuit of paid cost
   `<= 20` realizes `diag([2143],[3142],[4231],[2143],1)`. The direct word
   leaves the spectator untouched, so **the five-role optimum is also exactly
   21**.

**Corollary (three-target sub-tuples).** Exact rational LPs over all `2^24`
coordinate cuts of the regular S4-set give two gaps:

* `(4231,2143,2143)`: LP 15 against a direct cost of 16;
* `(2143,3142,4231)`: LP 16 against a direct cost of 17.

The LP is `max sum_H a_H Phi_H(T')` subject to `sum_H a_H c(H) <= (2,1,2)`.
Its optimal dual solution is a vector of fractional label counts n,
`n = (3,3,3)` and `(3,4,3)` respectively (`(4,4,4)` for the full tuple). It is
feasible for every one of the `2^24` cuts (`n.c(H) >= Phi_H(T')`), so
`(2,1,2).n` bounds the LP from above, and the simplex supplies cut weights
attaining it. The integer lower bounds for words, 15 and 16, come from
`inv + c1 + c3`, which is tight only at those counts.

The regular set carries every permutation module's cuts, as in PR2998. Both
three-target sub-tuples have exact optimum equal to their direct cost on
three roles. A cheaper three-role word, placed next to the missing target's
direct word on a fourth role, would give a four-role word of cost 20 after a
free role permutation, contradicting part 1. The same argument with one more role transfers part 2
to the three-target sub-tuples with one spectator.

Direct checks agree. The separate engine `independent.py`, run at r = 3,
finds no word for either sub-tuple at its only cost-tight counts:
`(4231,2143,2143)` at (3,3,3) dies at depth 5 after 12, 84, 216 and 216
nodes, and `(2143,3142,4231)` at (3,4,3) dies at depth 6 after 12, 84, 218,
248 and 200 nodes. The two two-target sub-tuples have no integer gap,
because their LP values 23/2 and 25/2 round up to the direct costs 12 and 13.
For context, Ross Richardson's two-cut theorem (archive
`s4-permutation-cut-cone`, retained under PR2998's `predecessor/`) makes the
sum tariff exact, with arbitrary dirty roles, for every tuple from 20 of the
24 targets. It excludes 2143, 2413, 3142 and
3412, and every gapped tuple here contains an excluded target.

## 7. Scope and what is not proved

* Six or more roles are not searched. Two or more dirty spectators might
  still realize cost 20. This is **not** a theorem that the optimum is 21
  with arbitrary workspace.
* Each exclusion (r = 4 and r = 5) rests on a finite computation run by two
  separately written in-package engines that agree node-for-node
  (section 8). No formal-kernel proof is given.
* The model is formal only: no native realization, routing, ownership or
  precision invoice, no bit supplier and no kappa.

## 8. Cross-checks

* A second engine (`indep.cpp`) reproduces both trees node-for-node: the
  full r = 4 tree over all 360 first letters, and the r = 5 tree over the
  same 7 orbit representatives (same gate indexing). It multiplies explicit
  F2 matrices in the natural and ordered-pair representations and uses no
  group-algebra bit masks.
* A Python implementation (`independent.py`) of the same pruned search
  reproduces three sets of node counts: the r = 3 tree, the first three
  r = 4 depths (56, 1904, 28562) and the 56 depth-1 survivors at r = 5.
* A brute-force meet-in-the-middle counter (`brute.py`) uses exact
  frozenset group-algebra arithmetic and no cuts. On
  `diag([4231],[2143])`, r = 2, counts (3,2,2), it counts 146 words, and
  the pruned primary engine also finds 146. `independent.py` leaves 150
  full-depth window survivors (it does not check the endpoint), of which
  exactly 146 equal T in exact arithmetic; 104 of these 146 words contain a
  mixing gate. On this instance, pruning loses no solution, including
  mixing ones.
* Positive control at r = 4: replacing 4231 by 4312 gives a tuple whose
  direct words cost 20 with counts (4,4,4). The same engine and cuts find a
  word. The word found is block-diagonal (a direct word), so this control
  shows only that the windows keep direct words at full scale.
* Negative control: scalar 4231 at counts (1,3,1) passes the cut count test
  but returns no word, as PR2998's precedence argument requires.

All of these were prepared in the same AI-assisted session. They are several
implementations by one author, not independent human review. AI review passes
in the same loop (also not human review) reproduced the r = 4 and r = 5 trees
node-for-node with a further engine that is not part of this package; see the
README.
