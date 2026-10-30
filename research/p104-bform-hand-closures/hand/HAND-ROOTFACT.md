# RootFact for P104 by hand

**Statement (RootFact).** Let `K` be a field of characteristic zero and `x ∈ K^8`, `x ≠ 0`. Then at least
**49** of the 104 ports `p` of P104 satisfy `p · x ≠ 0`. The bound is sharp: equality holds for `x = r`,
where `r` is any port.

Coordinates are the doubled D8 coordinates of `../data/p104_r8_d8.json`. E8 roots have norm 8, so inner products of
roots lie in `{0, ±4, ±8}`. P104 is the set of the 120 root lines of E8 with 16 lines removed.

The proof uses three standard facts about root systems (Humphreys, *Reflection Groups and Coxeter
Groups*, §1.3–1.10; Bourbaki, *Lie*, Ch. VI, Plate VII) and five finite facts. The finite facts are
checked exactly by [check_hand_rootfact.py](check_hand_rootfact.py), which runs in under 1 s and prints
`ALL PASS`. They are small enough to check on paper as well.

- **(A)** The 16 removed lines form two *frames* `F1`, `F2`, each made of 8 pairwise orthogonal lines.
- **(B)** Each root line is non-orthogonal to exactly 57 of the 120 lines, itself included.
- **(C)** A root `r` is non-orthogonal to exactly 4 lines of a frame `F` if `r ∉ F`, and to 1 line if
  `r ∈ F`. Proof by hand: `r = Σ_{f∈F} (r·f)/8 · f`, so `Σ_f (r·f)^2 = 8·|r|^2 = 64`, and each nonzero
  `r·f` is `±4` unless `f = ±r`.
- **(D)** Take the Bourbaki simple roots of E8. Delete one node `i`. The parabolic subsystem `Φ_{Δ∖i}`
  then has this many positive roots:

  | i         | 1  | 2  | 3     | 4        | 5     | 6     | 7     | 8  |
  |-----------|----|----|-------|----------|-------|-------|-------|----|
  | type      | D7 | A7 | A1 A6 | A1 A2 A4 | A4 A3 | D5 A2 | E6 A1 | E7 |
  | positive roots | 42 | 28 | 22 | 14 | 16 | 23 | 37 | 63 |

  The highest root `θ` is orthogonal to `α1,…,α7`.
- **(E)** Sharpness: `N(r) = 49` for every port `r`, and `N(r) = 52` for every removed line `r`.

Here `N(x)` is the number of ports `p` with `p·x ≠ 0`, and `Z(x)` is the set of root lines orthogonal
to `x`.

## Step 0: reduce to rational x

Let `V ⊆ Q^8` be the Q-span of the root lines in `Z(x)`. Rational vectors that are independent over
`Q` stay independent over `K`, because `K ⊇ Q`. The `K`-span of `V` lies in `x^⊥ ≠ K^8`, so
`dim_Q V ≤ 7`. Pick a nonzero `y ∈ Q^8` with `y ⊥ V`. Then `Z(x) ⊆ Z(y)`, so `N(x) ≥ N(y)`. It is
therefore enough to prove the claim for `y ∈ Q^8 ⊂ R^8`.

## Step 1: a hyperplane holds at most 42 root lines unless y is a root

Choose `z ∈ R^8` with `α·z ≠ 0` for every root `α`. Put

`Φ⁺ = {α : α·y > 0} ∪ {α : α·y = 0, α·z > 0}`.

This is the positive system of the lexicographic order given by `(y, z)` (Humphreys §1.3). Let `Δ` be
its simple system. Every positive root `α` is a combination `Σ_{β∈Δ} c_β β` with integers `c_β ≥ 0`, and
`β·y ≥ 0` for each `β ∈ Δ`. Hence

`α·y = Σ c_β (β·y)` is a sum of non-negative terms.

So `α·y = 0` exactly when `c_β = 0` for every `β` with `β·y > 0`. In other words, `Z(y) = Φ_J` with
`J = {β ∈ Δ : β·y = 0}`. Since `y ≠ 0` and `Δ` spans `R^8`, `J ≠ Δ`, so `J` lies inside some `Δ∖{i}`.

All simple systems are conjugate under `W(E8)` (Humphreys §1.8). So `(Φ, Δ)` is the standard E8 with
Bourbaki numbering, after a relabelling. By (D), `|Z(y)| ≤ 42` unless `J = Δ∖{α8}`. In that case
`y ⊥ α1,…,α7`. That orthogonal complement is one-dimensional and contains the highest root `θ` of `Φ⁺`,
again by (D). So `y` is proportional to a root.

## Step 2: y not proportional to a root

The ports in `y^⊥` are among the root lines of `Z(y)`, so there are at most 42 of them. Hence
`N(y) ≥ 104 − 42 = 62 ≥ 49`.

## Step 3: y proportional to a root r

By (B), 57 root lines are non-orthogonal to `r`. The lines removed from E8 to form P104 are `F1 ∪ F2`,
by (A).

- If `r` is a port, `r ∉ F1 ∪ F2`. By (C), exactly `4 + 4 = 8` removed lines are non-orthogonal to `r`, so
  `N(r) = 57 − 8 = 49`.
- If `r` is a removed line, the count is `1 + 4 = 5`, so `N(r) = 52`.

In both cases `N(y) ≥ 49`. ∎

## Remarks

- In E8 language, the worst hyperplanes are exactly `r^⊥` for a port `r`: their E7 has 63 lines, and 8
  of them are removed. Every other hyperplane holds at most 42 root lines (a D7).
- A random check agrees with the table in (D). For 20 000 hyperplanes spanned by random 7-tuples of roots,
  the number of root lines in each was always one of 14, 16, 22, 23, 28, 37, 42 or 63, and 63 occurred
  only for `y ∝ root`. The minimum of `N` was 49. This check is corroboration only; the proof does not
  depend on it.
- The Lean development (`../../lean/BForm/E8/`) proves RootFact without root-system theory, using the
  13-frame spread, a block bound, and kernel-checked tables. That route was chosen because Mathlib lacks
  the conjugacy of simple systems and the classification of parabolic subsystems that Step 1 uses.
