# A four-call floor that uses only the single labels

**Scoped written theorem in the formal group-algebra model of #4089 / #6038; no
new κ.** It strengthens the length-three exclusion of
[PR #6038](https://github.com/CrocSwap/integer-mult-bounds/pull/6038)
(`research/conjugate-pair-every-group`, head
`0cee0e104b68ce6f06bf84af03f46ac30680e64c`) and replaces its eight-pattern case
analysis with two cases.

## Statement

Let `G` be a group, `F` a field and `r ≥ 2`. Let `a, b ∈ G` be distinct and
both different from `e`, and let

```text
T = diag([a], [b], [e], …, [e]) ∈ M_r(F[G]).
```

A paid call is `D_N(g) = [g] N + N̄` with `N̄ = I - N`, where `N` is a rank-one
idempotent of `M_r(F)` and `g ∈ L` for a label set `L ⊆ G`.

**Theorem S.** If no label equals `e`, `a` or `b`, then no product of at most
three paid calls equals `T`. This holds for every label set and whatever
coincidences hold among products of labels.

A call with label `e` is the identity matrix, so `e ∉ L` costs nothing: drop
such calls. The only hypothesis that matters is that no single label equals `a`
or `b`.

**Corollary (PR6038's length-three step).** Take `L = {x, y}` with `xy ≠ yx`,
`a = xy` and `b = yx`. Then `a ≠ b` and `a, b ≠ e`, and `x, y ∉ {e, xy, yx}`
by cancellation, which is #6038's (F1). Theorem S excludes every word of length
at most three. #6038's facts (F2) and (F3) and its pattern-by-pattern analysis
are not needed. With #6038's four-call direct word, the minimum is four.

## Proof

Expand `D_{N_1}(g_1) ⋯ D_{N_k}(g_k) = Σ_U [g_U] P_U` as in #6038, where
`P_U = X_1 ⋯ X_k`, `X_i = N_i` if `i ∈ U` and `N̄_i` otherwise. Group the
subsets by value into three classes: `𝔸 = {U : g_U = a}`, `𝔹 = {U : g_U = b}`
and `𝔼 = {U : g_U = e}`. Since `[w] E_ij` is a basis, the word realizes `T`
only if

```text
Σ_{U∈𝔸} P_U = E_00,    Σ_{U∈𝔹} P_U = E_11,    Σ_{U∈𝔼} P_U = T_e := I - E_00 - E_11.
```

The proof uses only these three equations. The equations at other group
elements are never used. By hypothesis, `∅ ∈ 𝔼`, and no singleton lies in
`𝔸`, `𝔹` or `𝔼`.

**k ≤ 2.** `𝔸` and `𝔹` are disjoint and nonempty, because `E_00, E_11 ≠ 0`.
They lie in the subsets of size at least two, and there is at most one such
subset. Contradiction.

**k = 3.** Write `N_i = u_i v_iᵀ` with `v_iᵀu_i = 1`. Then `𝔸, 𝔹 ⊆ S :=
{12, 13, 23, 123}`, and

```text
P_12 = u_1 (v_1ᵀu_2)(v_2ᵀN̄_3),        P_13 = u_1 (v_1ᵀN̄_2u_3) v_3ᵀ,
P_23 = (N̄_1u_2)(v_2ᵀu_3) v_3ᵀ,        P_123 = u_1 (v_1ᵀu_2)(v_2ᵀu_3) v_3ᵀ,
P_2  = (N̄_1u_2)(v_2ᵀN̄_3),             P_∅ + P_2 = N̄_1 N̄_3.
```

Corner rules (as in #6038): `N_1 P_U = P_U` if `1 ∈ U` and `0` otherwise;
`N̄_1 P_U` is the complement. The same holds on the right with `N_3` and
position 3.

*Step 1: `23 ∈ 𝔸 ∪ 𝔹` and `12 ∈ 𝔸 ∪ 𝔹`.* Every `P_U` with `U ∈ S \ {23}`
has column space in `span(u_1)`. If neither `𝔸` nor `𝔹` contained `23`, then
`E_00` and `E_11` would both have column space in `span(u_1)`. Then `u_1` would
be parallel to both `e_0` and `e_1`, which is impossible. The same argument
with row spaces and `v_3ᵀ` gives `12`. So the cases are (up to the symmetry
below): (1) `12, 23 ∈ 𝔸`, or (2) `23 ∈ 𝔸` and `12 ∈ 𝔹`.

*Symmetry.* Exchanging `a ↔ b` together with the coordinates `0 ↔ 1`
(conjugation by a permutation matrix maps rank-one idempotents to rank-one
idempotents) exchanges `𝔸` and `𝔹`. The hypotheses are symmetric, so the
other two placements reduce to these.

*Case 1: `12, 23 ∈ 𝔸`.* Then `𝔹 ⊆ {13, 123}`, so `E_11` is a multiple of
`u_1 v_3ᵀ`, and `u_1 ∥ e_1`, `v_3 ∥ e_1`. Within `S`, only `12` omits position
3, so `E_00 N̄_3 = P_12`. The left side has column space in `span(e_0)`. The
right side has column space in `span(u_1) = span(e_1)`. So `P_12 = 0`.
Likewise only `23` omits position 1, so `N̄_1 E_00 = P_23`. The left side has
row space `span(e_0ᵀ)` and the right side has row space `span(v_3ᵀ) =
span(e_1ᵀ)`, so `P_23 = 0`. Then `E_00 = N_1 E_00 N_3`, a multiple of
`u_1 v_3ᵀ ∥ e_1 e_1ᵀ`. Contradiction.

*Case 2: `23 ∈ 𝔸`, `12 ∈ 𝔹`.* `𝔸` omits `12`, so every member of `𝔸`
contains position 3. Hence `E_00 N̄_3 = 0`, and `E_00` has row space in
`span(v_3ᵀ)`, so `v_3 ∥ e_0`. `𝔹` omits `23`, so every member contains
position 1. Hence `N̄_1 E_11 = 0` and `u_1 ∥ e_1`.

* `P_12 ≠ 0`: within `𝔹` only `12` omits position 3, so `E_11 N̄_3 = P_12`.
  If this were zero, `E_11 = E_11 N_3` would be a multiple of
  `e_1 v_3ᵀ ∥ e_1 e_0ᵀ`, which is false.
* `P_23 ≠ 0`: within `𝔸` only `23` omits position 1, so `N̄_1 E_00 = P_23`.
  If this were zero, `E_00 = N_1 E_00` would be a multiple of
  `u_1 e_0ᵀ ∥ e_1 e_0ᵀ`, which is false.
* Hence `v_2ᵀN̄_3 ≠ 0` and `N̄_1 u_2 ≠ 0`, so `P_2 ≠ 0`.
* The corner `(N̄_1, N̄_3)` keeps `∅` and `{2}`. Only `∅` lies in `𝔼`, so
  `P_∅ = N̄_1 T_e N̄_3 = N̄_1 N̄_3 - N̄_1 E_00 N̄_3 - N̄_1 E_11 N̄_3 = N̄_1 N̄_3`,
  using `E_00 N̄_3 = 0` and `N̄_1 E_11 = 0`. With `P_∅ + P_2 = N̄_1 N̄_3`,
  this gives `P_2 = 0`. Contradiction. ∎

## What is used

The proof uses three things: the three class equations, `∅ ∈ 𝔼`, and the
fact that no singleton is in a target class. It uses no element of `L`, no
relation among labels, no field characteristic and no width beyond `r ≥ 2`.
It does not use the equations at the other group elements; dropping them only
enlarges the set of systems excluded. The verifier's `singleton` tier searches
exactly this relaxed system over small prime fields and widths and finds no
solution. Its controls show the search is not vacuous: it finds four-call
solutions, and a single label allowed to equal `xy` reopens length three.

## Scope

This is a statement in the formal group-algebra model. It prices no native
address operation, conversion, restoration or caller and changes no κ. No
proof-kernel check and no independent human review is claimed.
