# SpanFact for P104 by hand

**Statement (SpanFact, as in `BForm/CaseII.lean`).** Let `K` be a field of characteristic zero, `y ∈ K^8`,
`y ≠ 0`, `B` a set of at most 4 ports, and `z ∈ F2^9`, `z ≠ 0`. Suppose every port `t ∈ N(y) \ B` has
`lab(t)·z = 0`. Then either every `t ∈ N(y)` has `lab(t)·z = 0`, or `z = lab(w)` for some `w ∈ B`.

Notation:
- `N(y)` is the set of ports non-orthogonal to `y`, and `Z(y)` the ports orthogonal to it.
- `O(z) = {t : lab(t)·z = 1}`.
- `S = O(z) ∩ N(y)`.

The hypothesis says `S ⊆ B`. Taking `B = S` shows that SpanFact is equivalent to the following:

> **(★)** If `1 ≤ |S| ≤ 4`, then `z = lab(w)` for some `w ∈ S`.

We prove (★). It reuses [HAND-ROOTFACT.md](HAND-ROOTFACT.md): the parabolic lemma (Step 1 there), facts
(A)–(C) and the bound `N(y) ≥ 49`. Finite facts (D′), (F), (G) and (H) are checked exactly by
[check_hand_spanfact.py](check_hand_spanfact.py), which takes a few seconds and prints `ALL PASS`.

## The labels are E8 modulo 2

Let `E ⊂ F2^9` be the even-weight vectors, `dim E = 8`. Put `B(u,v) = u·v`, and `Q(u) = wt(u)/2 mod 2` on
`E`.

- **(G)** Ports have labels of weight 3 or 7. The 16 missing labels of weight 3 or 7 attach to the 16
  removed lines, one each. Put `u_r = lab(r) + 1` (the complement), a vector of weight 2 or 6, so
  `Q(u_r) = 1`. The 120 lines of E8 then correspond exactly to the 120 vectors `u ∈ E` with `Q(u) = 1`.
  Distinct lines are orthogonal if and only if `B(u_r, u_r') = 0`. In other words, `r·r' ≡ B(u_r, u_r')
  (mod 2)` with roots of norm 2. This is the usual `E8/2E8` picture.
- **Translation of `O(z)`.** Write `ε = wt(z) mod 2` and `a = z + ε·1 ∈ E`. Then
  `lab(t)·z = B(u_t, a) + ε`, so `O(z) = {t : B(u_t, a) ≠ ε}`. Here `z = 1` gives `a = 0, ε = 1`. And
  `z = lab(w)` exactly when `ε = 1` and `a = u_w`.
- **(F)** `|O(z)| ≥ 44` for every `z ≠ 0`.
- **Gauss sum.** `Σ_{u∈E} (-1)^{Q(u)} = 136 − 120 = 16`. Expanding `Q(u+b)` gives
  `Σ_u (-1)^{Q(u)+B(u,b)} = 16·(-1)^{Q(b)}`. For `b ∈ E∖{0}`, `Σ_u (-1)^{B(u,b)} = 0`, because
  `E^⊥ = ⟨1⟩` and `1 ∉ E`.

**Counting lemma.** Let `c ∈ E∖{0}` and `W_c = {u : Q(u) = 1, B(u,c) = 1}`, and let `a ∉ {0, c}`. Write
`(1 − (-1)^Q)/2 · (1 − (-1)^{B(u,c)})/2` for the indicator of `W_c` and apply the Gauss sums:

`Σ_{u∈W_c} (-1)^{B(u,a)} = 4·((-1)^{Q(a+c)} − (-1)^{Q(a)})`, with `Q(a+c) = Q(a) + Q(c) + B(a,c)`.

| type of `c`  | size of `W_c` | `B(a,c) = 0` | `B(a,c) = 1` |
|--------------|---------------|--------------|--------------|
| `Q(c) = 1` (a root) | 56 | split 24 / 32 | split 28 / 28 |
| `Q(c) = 0`   | 64            | split 32 / 32 | split 28 / 36 |

In every case each side of the split, `B(u,a) = 0` or `1`, has **at least 24** elements.

## Reduction to rational y with the same zero set

Let `V` be the Q-span of the roots orthogonal to `y`. A root `r` not orthogonal to `y` is not in `V`. The
reason: `V ⊗ K ⊆ y^⊥`, and rational vectors independent over `Q` stay independent over `K`. So `r` is not
orthogonal to all of `V^⊥ ∩ Q^8`. Choose `y' ∈ V^⊥ ∩ Q^8` off finitely many proper subspaces. Then
`Z(y') = Z(y)` exactly, and `S` does not change. So assume `y ∈ Q^8`.

By Step 1 of HAND-ROOTFACT, the roots orthogonal to `y` form a parabolic `Φ_J`. By **(D′)**,
`|Φ_J| ≤ 37` unless `Φ_J` is an E7 or a D7.
- An **E7** means `y ∝ r` for a root `r`.
- A **D7** means `y ∝ v` for a lattice vector `v` of norm 4, with `v = r1 + r2`, `r1 ⊥ r2`.

## Case 1: |Z(y)| ≤ 37

`O(z) \ S ⊆ Z(y)`, so `|S| ≥ |O(z)| − 37 ≥ 44 − 37 = 7` by (F).

## Case 2: y = r is a root (E7)

Let `c = u_r`. Then `N(r)` consists of `r` (if `r` is a port) and the ports in `W_c`. By (C), at most
`4 + 4 = 8` removed lines lie in `W_c`.

- **`a ∉ {0, c}`.** By the counting lemma, `|S| ≥ |O(z) ∩ W_c ∩ ports| ≥ 24 − 8 = 16`.
- **`a = 0`, so `z = 1`.** Then `O = ` all ports and `S = N(r)`, with `|S| ≥ 49` by RootFact.
- **`a = c`, `ε = 0`.** Every `u ∈ W_c` has `B(u,c) = 1 ≠ ε`, so `|S| ≥ 56 − 8 = 48`.
- **`a = c`, `ε = 1`, so `z = lab(r)`.** No `u ∈ W_c` is in `O`, while `r ∈ O` because `B(c,c) = 0`. So
  `S = {r}` if `r` is a port, and (★) holds with `w = r`. If `r` is a removed line, `S = ∅`.

## Case 3: y = v of norm 4 (D7)

Let `s = u_{r1} + u_{r2}`. Then `Q(s) = 0` and `s ≠ 0`, and for every root `r`,
`r·v ≡ B(u_r, s) (mod 2)` by (G). So the ports with `B(u,s) = 1` lie in `N(v)`, and at most 16 removed
lines lie in `W_s`.

- **`a ∉ {0, s}`.** By the counting lemma, `|S| ≥ 28 − 16 = 12`.
- **`a = 0`.** `|S| = |N(v)| ≥ 49`.
- **`a = s`, `ε = 0`.** `S ⊇ W_s ∩ ports`, so `|S| ≥ 64 − 16 = 48`.
- **`a = s`, `ε = 1`.** `O` is the set of ports with `r·v` even, that is `r·v ∈ {0, ±2}`. So `S` is the set
  of ports with `r·v = ±2`. There are 14 such lines in E8, and by **(H)** at most 4 of them are removed. So
  `|S| ≥ 10`. The hand reason for (H): in a frame `F`, `v = Σ_{f∈F} (v·f/2) f` with `Σ (v·f)^2 = 8`, so at
  most two `f ∈ F` have `v·f = ±2`.

In every case where `S ≠ ∅` and `z` is not `lab(w)` for some `w ∈ S`, we get `|S| ≥ 7`. This proves (★)
and therefore SpanFact. ∎

## Remarks

- The margins are wide. In the special cases the true minimum of `|S|` is 18 for root normals and 11 for
  norm-4 normals, by brute force.
- The script also brute-forces SpanFact on all 120 root and 1080 norm-4 normals as corroboration.
- Fact (F) is the only finite fact here that is not one line of hand counting. By hand one gets
  `|O(z)| ≥ 40`: the E8 count is 56, 64 or 120, minus at most 16 removed lines. The extra 4 come from how
  the two removed frames sit relative to each other.
