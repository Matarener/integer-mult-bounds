# Dynamic captures on the PR5708 G20 word: model and argument

## Word model

The local word is `research/g20-conjugation-admission/WORD.json.gz` with the
frames of its vendored G20 source. Wire i starts with the symbol x_i. A
payload is a finite F2 sum of terms M x_i, M an exact 8x8 rational matrix
(a product of frame reflections R_f = I - 2 P_f). `ADD d s f` adds the
payload of s to d; `Q d s t k` is a paid query of rank k and multiplies by
R_s R_t; `ZERO_Q` moves a zero payload for free; `ERASE`/`INIT` touch owned
wires only. The replay checks every frame, rank and zero move and reproduces
the published local paid profile {1:1281, 2:1338, 3:58, 4:57, 5:102, 6:10}.
Helpers are the 415 retained non-main wires; their target ranks are the
frame-dimension differences (413 rank 8, helpers 465 and 684 rank 4).

## Captures

Owning a set H of helpers debits sum over H of r_h^t. For h in H, h is
*dead-forward* before event i when its content then reaches no retained
output other than outputs of H (backward replay of the exact operators).
In each maximal dead interval [a, b] that contains no read of h, writes into
h are dropped and h is held zero, so its own queries in [a, b) become free
`ZERO_Q` moves. Just before event b, h receives an arbitrary payload w
(ERASE plus same-frame ADDs). Scalar costs of these changes are not charged,
which can only favour a capture.

## Exact kill condition

A forward replay injects a fresh symbol u into h before each b. Since the
operators act linearly, the true payload of every query is

    p_q = rest_q + sum M_(q,s) (w_s + snap_s),

where rest_q is the replayed payload with injected symbols removed and owned
input symbols set to zero, snap_s is the replayed content of h just before
the injection (owned inputs zeroed), and M_(q,s) is the coefficient of u_s.
The replay checks that every such coefficient is a single matrix and that no
injected symbol reaches a retained output outside H. A query is removed iff
p_q = 0.

*Single dependence.* If q depends on one injected symbol, it is removed iff
w_s = M^-1 (rest_q + M snap_s): one exact value. Queries are grouped by that
value; the best group of each epoch is the most a single injection removes.
For one helper every query depends on one symbol, so the single-helper census
is exact. On PR5708 every helper has two dead intervals (before its first
read and after its last) and so one injection; the leading interval never
contains a read of the helper.

*Parity classes.* Let parity(p) be the F2 sum of the symbol masks over all
matrices. It is F2-linear and parity(M p) = parity(p) for one invertible
matrix M. If q depends on a set D of injected symbols and p_q = 0, then

    parity(rest_q) + sum_(s in D) parity(snap_s) = sum_(s in D) parity(w_s).

The left side is a label computed from the word; all removed queries with the
same D share one label. Hence the removed mass of queries with dependence D
is at most the heaviest label class.

## Pairs

Individual schedule (each helper keeps its own dead intervals): for pair
(a, b) the gain is at most free(a) + free(b) + best(a) + best(b) + heaviest
class of the shared queries - 8^t(a) - 8^t(b). The 5638 pairs where this is
not positive are closed. When no single-dependence query is removed, the gain
is at most free + heaviest class - debits, which is negative for every pair
(checked). Otherwise w_a lies in the group values of a (or zero) and w_b is
in the group values of b, zero, or forced by one shared query; symmetrically.
All such candidates are evaluated exactly for the 392 remaining pairs; the
best gain is -1.957.

Joint schedule: a backward replay finds five pairs (h, p) where the content
of h at some time reaches only the outputs of h and p. Owning both lengthens
dead intervals. Each pair is reanalysed with joint deadness; four close by
the class bound and the pair (297, 684) by exact enumeration (-1.968).

## Joint token bound

Under the individual schedule, a removed query satisfies
parity(p_base) = sum over owned h it depends on of (e_h + b_h), where b_h
collects the parities of w_h and of the dropped writes. So every removed
base-word parity row lies in a d-dimensional space for d owned helpers. Give
each eligible query ceil(4 r^t) copies of its row (2213 queries, 15544
tokens) and greedily split them into N = 26 F2-independent sets. A
d-dimensional space meets each set in at most d vectors, so the removed
t-mass is at most 26 d / 4 = 6.5 d, plus at most one free own query per
helper (rank at most 2, checked). A helper with a free own query of rank 1 or
none therefore contributes at most -0.439; one with a free rank-2 query at
most +0.556. The greedy N is an upper bound; the true minimum may be smaller.

## Limits

The joint token bound uses individual dead intervals; joint deadness is
checked for pairs only. Sets of three or more helpers containing several
helpers with a free rank-2 query are not decided. All decisions use
double-precision moments with margins above 1e-3, except the exact neutral
case of helper 684 (one H4 removed for one H4 target).
