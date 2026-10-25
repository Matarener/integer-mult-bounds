# V4, scalar decoders with even denominators — theory notes (2026-10-25)

Setting. 112 ports, 56 planes `E_i` (each nondegenerate: Gram rank 2 over F2). A scalar decoder is
`K = sum_k u_k v_k^T` over Q, with mask `K_pp = 1`, `K_pq = 0` when `p != q` and the planes of `p, q` are equal or
non-orthogonal; entries on orthogonal plane pairs are free. Term `k` costs
`tariff_k = rank_F2( pairing( span_F2 planes(supp u_k), span_F2 planes(supp v_k) ) )` — it depends only on supports.

## Known (prior art)
* 2-integral decoders (all coefficients with odd denominators): `sum tariff >= 224`, tight. Reduction mod 2 keeps the
  mask and only shrinks supports, then the block-Gram rank argument over F2 applies
  (philippeVV, Discussion 1587 c.18927273; #2532 review). Our Lean: `lean/V4Rank.lean`, `V4.decoder_cost_ge`.
* Minimum scalar rank of the mask is 49 over every field (PR2484, PR2541).

## New results of this session
### R1. Field-free lower bound 139.113 (exact certificate)
The clique-dual LP uses only (a) on a clique `Q` of pairwise non-orthogonal planes the mask forces `K|_Q = I`, so at
least `2|Q|` terms touch `Q` on both sides (rank argument, any field), and (b) tariffs, which depend only on supports.
Hence every plane-port decoder over ANY field, including even denominators, satisfies
`sum tariff >= 18233853/131072 = 139.113...`.
Certificate: 443 cliques with integer weights / 2^20, inequality checked for all 39087^2 ordered span pairs in exact
integer arithmetic (`kaggle-exact/v4_exact_certificate.json`). Lean (any field): `identity_block_needs_terms`,
`weak_duality` in `lean/V4Duality.lean`. Previously only 49 was known for the dyadic case; 139 > 128 excludes the
kappa-doubling target even for scalar decoders. The clique method itself cannot exceed 167.02 (Farley bound).

### R2. Pairs cost >= 8 over every field
Let `D = {i, j}` be two non-orthogonal planes, so the mask on their 4 ports is `I_4`. Split the terms into
"diagonal" ones (some plane in `A_k ∩ R_k`; tariff >= 2 because the pairing restricted to that plane already has rank 2)
and "cross" ones (`A_k ∩ R_k = ∅`; tariff >= 1 because the planes are non-orthogonal). Let `N` be the sum of the cross
terms restricted to `D`. Its diagonal 2x2 blocks vanish, so `N = [[0, X], [Y, 0]]`, which is similar to `-N`
(conjugate by `diag(I, -I)`): eigenvalues come in pairs `±λ`. Hence `dim ker(I - N) = dim ker(I + N) =: m` and
`2m <= rank N <= c` (number of cross terms). The diagonal terms sum to `I - N`, of rank `>= 4 - m`, so there are at
least `4 - m` of them and
`cost >= 2(4 - m) + c >= 8 - 2m + 2m = 8`.  This uses char != 2 (so that `1 != -1` and the two eigenspaces are
independent inside `range N`); in characteristic 2 the F2 block-Gram theorem gives the same 8 (and CP-SAT confirmed it).

### R3. Where an escape must live
Tariffs depend only on supports. If a support pattern (the multiset of `(planes(supp u_k), planes(supp v_k))`) can be
realized over F2, its cost is `>= 2 * #ports` by the F2 theorem. Therefore a scalar decoder cheaper than 224 must use a
pattern that is realizable over Q but NOT over F2 — and, by the 2-integral theorem, it must use even denominators in an
essential way (no per-term rescaling `u -> 2^a u, v -> 2^-a v` makes all terms 2-integral).

### R4. 2-adic leveling (structure of an escape)
Rescale every term so that `u_k` is primitive (min 2-adic valuation 0). Let `-e < 0` be the smallest valuation among
all `v_k` and `L` the set of terms reaching it. On every FIXED mask entry the left side `K_pq` is an integer, so the
leading parts must cancel:
`sum_{k in L} (u_k mod 2)(2^e v_k mod 2)^T = 0` on all fixed entries (over F2).
So the most fractional layer is an F2 decomposition of the ZERO mask (free entries arbitrary). Such layers are not free:
each term still pays its full tariff. An escape must buy, with these "zero-mask" layers, a saving on the integral
layer that the F2 argument cannot see. Closing the dyadic case = bounding what zero-mask layers can buy.
This is the same mechanism as the known escape in `research/bit-full-borel-2adic-floor` (PR288 model), so it is a
genuine obstacle, not a technicality.

## Next steps
1. Extend R2 to triples (bound `dim ker(I - N)` by the cost of the cross part when the cross graph is a triangle);
   compare with the numerical search `v4-real-triples` (real-valued, 38 classes).
2. Turn R4 into an induction on `e`: lower-bound the tariff of a zero-mask layer by what it changes in the next layer.
3. If 1 succeeds with `c(D) = 12` over Q for triples, add triple blocks to the field-free LP (expected gain small).

## R5. Necessary conditions for an escape on a clique group (any field)
Let `S` be a set of pairwise non-orthogonal planes (so the mask on its `2|S|` ports is the identity). Split the terms
touching `S` into *diagonal* terms (some plane in `A ∩ R`; tariff `>= 2`) and *cross* terms (`A ∩ R ∩ S = ∅`; tariff
`t_j >= 1`). With `N` = sum of the cross terms on `S` (zero diagonal 2x2 blocks) and `m = dim ker(I - N)`:
`cost_S >= 2 (2|S| - m) + sum_j t_j = 4|S| - 2m + sum_j t_j`.
So a saving needs **`2m > sum_j t_j`**: the cross part must have eigenvalue 1 with multiplicity above half its tariff.
* Bipartite cross structure (planes split in two sides, every cross term goes between the sides): `N ~ -N`, so
  `2m <= rank N <= sum t_j` — no saving (this is R2 for pairs, and it holds for every bipartite pattern).
* Hence an escape needs **odd cycles** of cross terms, and in characteristic 0 the trace condition `tr N = 0` must be met
  by compensating eigenvalues (e.g. `1,1,...,-m`).
* The extreme case `m = 2|S| - 2` forces the diagonal part to be rank 2: `I - N = W Z^T`, i.e. two terms on the whole
  group (cost `2·GR(S)`) plus two cross terms `({i}, S \ {i})` per plane. Cost `2·GR(S) + 2·sum_i t({i}, S\{i})`.
  This construction works over F2 as well, so by the F2 theorem it can never beat `4|S|`; the geometry must make those
  tariffs large. (Checked consistent: no such cheap triple exists.)

## R6. Data: cheap cross interactions are plentiful
Single-plane cross terms `({i},{j})` on non-orthogonal pairs: 1758 of tariff 1, 1104 of tariff 2. The tariff-1 graph has
879 edges on all 56 planes, 5136 triangles, and is not bipartite; `({i},{j,k})` has tariff 1 in 9026 of 71768 cases.
So odd cycles of cheap cross terms are everywhere — R5's combinatorial conditions alone do NOT rule escapes out.

## R7. What actually blocks escapes, and where one could hide
* Any support pattern realizable over F2 costs `>= 2 · #ports` (F2 theorem; tariffs see only supports). Every
  "eigenvalue-1" construction built from 0/1 data (like `I - N = J ⊗ I_2`) is realizable over F2, hence excluded.
* So an escape must use a pattern whose mask equations are solvable over Q but **not over F2**: the equations must force
  a coefficient `1/2` (e.g. two symmetric contributions summing to an odd target) somewhere — R4's zero-mask top layer.
* On clique groups this is tested numerically: all 38 triple classes have exact real minimum 12 (= F2 value);
  60 most degenerate quadruples running. A real-valued solution space contains all rational ones, so if the true real
  minimum on a group is `4|S|`, no denominator helps there; but the search is heuristic (local optimisation from random
  starts), so "none found" is evidence, not proof.
* For groups with **orthogonal pairs** (free mask entries), the mask has scalar rank below `2|S|` over every field
  (C5 holes: rank 5 vs clique bound 4; global 49 vs 48). Over F2 the Gram lift kills free entries, which is why the F2
  floor survives these rank savings. Over Q there is no such lift — **this is the most plausible home of an escape**:
  odd holes (C5, 5 planes) combined with dyadic coefficients. Next test: the sparse real search on the 23 C5 holes and on
  C5 + adjacent planes (groups of 5-7), baseline `4|S|`.
