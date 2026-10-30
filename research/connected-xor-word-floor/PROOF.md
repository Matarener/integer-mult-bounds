# Proof: connected restored XOR words need 2(n-1) calls

Produced by Nick Petalas. Apache-2.0.

## Model

Labels form a finite set `V` with `|V| = n`. Each label holds a value in a
vector space over F2; write `x` for the column of all values. The only call is

    X_(s,t):  x_t += x_s,   s != t,

whose matrix is `I + e_t e_s^T`. A word `w = g_1 ... g_L` applies `g_1`
first, so its matrix is `M(w) = G_L ... G_1`. It is **restored** when
`M(w) = I`. Its **interaction graph** `G(w)` is the undirected multigraph on
`V` with one edge `{s,t}` for every call, including calls whose effect later
cancels. Write `c(w)` for its number of components, counting isolated labels.
Call `t` a target and `s` a source of the call. Let `T(w)` and `S(w)` be the
sets of labels that occur as a target and as a source respectively.

This is the source-XOR projection used by PR #2455: Q and R calls never change
sources, so every restored connector word has a restored X-only projection.

## Lemma 1 (rank-one product identity)

Over any field, let `u_k, v_k` be column vectors and suppose

    (I + u_L v_L^T) ... (I + u_1 v_1^T) = I.

Then `L >= rank U + rank V`, where `U = [u_1 ... u_L]` and
`V = [v_1 ... v_L]`.

*Proof.* Let `P_k` be the product of the first `k` factors. By induction,
`P_k = I + U_k N_k V_k^T`, where `U_k` and `V_k` hold the first `k` columns
and `N_k` is `k`-by-`k` lower triangular with unit diagonal. The case `k=0`
is empty. For the step,

    P_k = P_(k-1) + u_k v_k^T P_(k-1)
        = I + U_(k-1) N_(k-1) V_(k-1)^T + u_k (v_k^T + v_k^T U_(k-1) N_(k-1) V_(k-1)^T),

so `N_k` is `N_(k-1)` bordered by the row `v_k^T U_(k-1) N_(k-1)`, a zero
column and a final diagonal entry one. Hence `N = N_L` is invertible and
`U N V^T = 0`. Sylvester's rank inequality for the `L`-column `U` and the
`L`-row `N V^T` gives

    0 = rank(U N V^T) >= rank U + rank(N V^T) - L = rank U + rank V - L.  □

For a restored XOR word, `u_k = e_(t_k)` and `v_k = e_(s_k)`, so

    L >= |T(w)| + |S(w)|.                                             (1)

## Theorem

Every restored word satisfies `L >= 2(n - c(w))`. In particular, a restored
word whose interaction graph is connected has at least `2(n-1)` calls.

*Proof.* Strong induction on `n`. For `n=1` there is no call and the bound is
`0`.

**Disconnected graphs.** If `c(w) >= 2`, each call acts inside one component.
Calls in different components act on disjoint coordinates and commute, so
`M(w)` is block diagonal with block `M(w_i)`, where `w_i` is the subword of
calls inside component `C_i`. Restoration of `w` is restoration of every
`w_i`. Each `w_i` is connected on `n_i < n` labels, so by induction
`L = sum_i |w_i| >= sum_i 2(n_i - 1) = 2(n - c(w))`.

**Connected graphs, n >= 2.** Every label is an endpoint of some call, so
`T ∪ S = V`. There are three cases.

*Case A: T = S = V.* Inequality (1) gives `L >= 2n > 2(n-1)`.

*Case B: some label v is not a source.* Then `v` is a target only. No call
reads `x_v`, so deleting every call into `v` leaves a word `w'` on `V \ {v}`
whose action on those labels equals that of `w`. Thus `w'` is restored. Let
`C_1, ..., C_m` be the components of `G(w') = G(w) - v`. By the disconnected
case and induction, `|w'| >= 2(n - 1 - m)`.

Every call of `w'` stays inside one `C_i`, so at all times the value of any
label in `C_i` is a linear form in the initial values of `C_i` alone. Since
the prefix matrices are invertible, that form is nonzero. The final value of
`x_v` is `x_v + sum_k l_k`, where `l_k` is the value of the source of the
`k`-th call into `v` when it is made. Restoration requires `sum_k l_k = 0`.
The coordinate spaces of distinct `C_i` are independent, so the sum over calls
whose source lies in `C_i` vanishes for each `i`. Since `G(w)` is connected,
each `C_i` sends at least one call into `v`. One nonzero form cannot sum to
zero, so each `C_i` sends at least two. The degree of `v` is at least `2m`
and

    L = |w'| + deg(v) >= 2(n - 1 - m) + 2m = 2(n-1).

*Case C: some label v is not a target.* Then `x_v` never changes. Order the
coordinates as `(V \ {v}, v)`. Every call matrix has the block form
`[[A_k, b_k], [0, 1]]`. A call `X_(v,t)` has `A_k = I` and `b_k = e_t`; every
other call has `b_k = 0` and `A_k` equal to its matrix on `V \ {v}`. The
product is `[[A_L ... A_1, b], [0, 1]]` with

    b = sum over calls X_(v,t_k) of (A_L ... A_(k+1)) e_(t_k).

Restoration therefore forces `A_L ... A_1 = I` and `b = 0`. The first
equation says the word `w'` obtained by deleting the calls out of `v` is
restored, so `|w'| >= 2(n - 1 - m)` as in Case B, with `C_1, ..., C_m` the
components of `G(w) - v`. Every `A_j` is block diagonal over these components
and `e_(t_k)` lies in the block of the component containing `t_k`. So the
`C_i` block of `b` is a sum of the vectors `(A_L ... A_(k+1)) e_(t_k)` over
calls with `t_k ∈ C_i`. Each such vector is nonzero, because the matrix is
invertible. Connectivity gives at least one call from `v` into each `C_i`,
and a vanishing block needs at least two. Again `deg(v) >= 2m` and
`L >= 2(n-1)`.

If Case A fails, some label lies outside `S` or outside `T`, so Cases A–C are
exhaustive.  □

## Sharpness and consequences

The bound is attained for every `n`. The star word that applies each
`X_(0,i)` twice, and the path word that applies each `X_(i,i+1)` twice, are
restored, connected, and of length `2(n-1)`. Doubling the edges of any forest
with `k <= n-1` edges gives a restored word of length `2k` with exactly
`n - k` components, so `c >= n - floor(L/2)` is attained at every even
`L <= 2(n-1)`.

The theorem covers overlapping interactions and odd lengths. For example,
`X_(1,0) X_(2,1) X_(1,0) X_(2,1) X_(2,0)` is the commutator identity
`[E_01, E_12] = E_02` read as a restored connected word of length five on
three labels. It satisfies the bound `5 >= 4`. No parity argument is used.

**Corollary (connector source-XOR floor).** Assume the component inequality
`Q >= n + c` of PR #2455 for a restored `n`-source common-B mutable-source
connector word with `Q` queries, where `c` is the number of components of its
source interaction graph. PR #2455 states and proves that inequality for five
sources; it is cited here, not re-proved or audited. Then the word's source-XOR
count satisfies

    X >= 2(n - c) >= 2(2n - Q),   for n + 1 <= Q <= 2n.

At `n = 5` this gives `X >= 8` at `Q = 6`, matching the census theorem of
PR #2455, and `X >= 6` at `Q = 7`, matching the sharp floor of PR #2643. It
also gives `X >= 4` at `Q = 8` and `X >= 2` at `Q = 9`. At the minimum query
count `Q = n + 1`, the interaction graph is connected and `X >= 2(n-1)`.

**Remark (other fields).** Lemma 1 is stated over any field. The induction
uses only that the call coefficient is nonzero and that prefix matrices are
invertible, so the theorem holds verbatim for calls `x_t += a x_s` with
`a != 0` over any field. The finite verifier checks only F2.
