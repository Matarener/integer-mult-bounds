# Audit of PR6114: controller income bound

Audited: PR #6114 (Matarener), head `3183c6553e5559df8807fde4fec27e2403f3040a`,
`research/p104-controller-income-bound/PROOF.md`, against the literal alphabet of
`research/p104-productive-controller/caller.py` on main `721c03822`.

**Verdict.** The theorem is correct as stated for the literal alphabet: with a constant invertible right
boundary, `s` paid odd shears and `n_odd` outputs with zero even part, `n_odd ≤ s − 1`. The three retained
controllers attain it (33 shears, 32 twisted outputs, income 17 = 18 − 1); an independent engine reproduces every
number. There are two gaps in the written argument, both closable (A1, A2), and a cosmetic error (A3). The scope sentence
"a paid primitive that touches several banks or ports at once ... is the only way to escape the bound" is
overstated: one-bank paid primitives and non-constant boundaries also escape, while multi-source jobs that write
a single row do not (A4).

Notation as in PR6114: every bank row is `a + Q·b` with `a, b ∈ R_even^n`, `R_even = ℚ[Q^{±2}] ⊗ ℚ[D_0, …, D_32]`;
`E` is the matrix of even parts and `B` the matrix of odd coefficients, so the state is `M = E + Q·B`.

## A1. The left boundary (gap in step 4 / the theorem's last inequality)

PR6114's PROOF.md says that the left boundary is applied at the end. It then uses "the `n_odd` zero rows give
`rank E_final ≤ n − n_odd`". But the zero rows belong to `L·M`, not to `M`. The repair below does not need `L`
to be invertible. Let `T` be the set of twisted outputs and `L_T` the corresponding rows of the constant matrix
`L`. The even part of `L_T·M` is `L_T·E = 0`, so the rows of `L_T` lie in the left kernel of `E`. The outputs
`Q^{±1}D^{S_i}e_i` (`i ∈ T`) are linearly independent, so `rank L_T ≥ rank(L_T M) = |T|`. Hence
`n − rank E ≥ |T|`. On the literal words `L` is invertible anyway (checked).

## A2. Lift cancellation (unproved step of the invoice consequence)

The consequence `income = Σ_i (1 + d|S_i|) − d·lifts − n_thin = n_out − n_thin` needs `Σ_i |S_i| = lifts`.
PR6114 asserts this ("every stage that appears in an output was paid once as a lift"). That assertion is
true, and it follows from the determinant for every word whose outputs form the full monomial diagonal.
Scalar `ADD`, swaps and shears have determinant `±1`, `Q_POWER` multiplies the determinant by `Q^{±2}`, and a
lift of row `r` by `D_s` multiplies it by `D_s`. So `det(L·M_final) = c·Q^{2k}·∏_s D_s^{ℓ_s}`, with `c ∈ ℚ^×` and
`ℓ_s` the number of row-lifts at stage `s`. For each output `i`, `S_i` is its stage set. The diagonal
`diag(Q^{q_i}D^{S_i})` has determinant `∏ Q^{q_i} ∏_s D_s^{#{i : s ∈ S_i}}`, and `ℚ[Q^{±1}, D]` is a UFD. Hence
`#{i : s ∈ S_i} = ℓ_s` for every stage `s`, and `Σ_i q_i = 2k`. The verifier checks both identities stage by
stage on all three controllers (`Σ|S_i| = 194` lifts, net `Q_POWER` = `Σ q_i`). If a word twists only some of its
outputs, this argument does not apply, and the consequence needs the untwisted outputs' targets to be stated.
The physical cost model in `caller.py` accepts only odd diagonal outputs.

## A3. Cosmetic

The stage markers are `D_0, …, D_32` (33 of them; `caller.py` exponent tuples have 1 + 33 entries). They are not
`D_0, …, D_33`.

## A4. Which paid primitives escape

Write a paid job as `M ← A·M` with `A = A_e + Q·A_o` (`A_e, A_o` over `R_even`). Then the new even part is
`E' = A_e·E + Q²·A_o·B`. Sylvester's rank inequality gives

    rank E' ≥ rank E − (n − rank A_e) − rank A_o ,     and, if B = 0,   rank E' ≥ rank E − (n − rank A_e).

Free events have `A_o = 0` and invertible `A_e`, so they preserve `rank E` and keep `B = 0` before the first paid
job. With a constant invertible entry this gives

    n_odd ≤ (n − rank A_e^(1)) + Σ_{k ≥ 2} [(n − rank A_e^(k)) + rank A_o^(k)] .

PR6114's open question 1 asks for this bound ("twisted ≤ sum over paid jobs of their even-rank change"), and the
formula above computes it from the job matrices alone. Consequences:

* **Positive (generalization).** A paid job that writes one row, `y ← u·y + Σ_{j≠y} f_j·x_j`, has `A_e`
  invertible and `rank A_o ≤ 1` when `u ∈ R_even` is nonzero. This holds for any number of source banks and any
  Laurent coefficients `f_j`. Such jobs obey PR6114's bound exactly, including the `− 1`. Touching several banks is
  therefore not by itself an escape.
* **Escape 1: an odd one-bank job.** A paid odd translation `y ← Q·y` has `rank A_e = n − 1` and twists one output
  even as the first job. So `s` such jobs can twist `s` outputs, which is one more than the bound. Control:
  one job, one odd row.
* **Escape 2: a non-constant boundary.** If the entry rows already carry odd content, step 3 fails. Control
  (2 banks): entry `x = e1 − Q·e2`, `y = e2`, then `y += Q^{-1}x` and `x += −Q·y` give the odd rows `−Q·e2`
  and `Q^{-1}·e1`. That is 2 twisted outputs from 2 shears. The entry is one backward shear of the identity, so
  a Laurent boundary can hide a paid shear. With a general entry the bound is `n_odd ≤ (n − rank E_entry) + s`.
* **Escape 3: a job that writes several rows.** This is the case PR6114 names. Control: the 2×2 composite of the
  three Whitehead shears, taken as one paid job, drops the even rank by 2 from a constant entry.

Within the literal alphabet (rational boundary programs, `Q_POWER ∈ {±2}`, one-pair shears with coefficient
`Q^{-1}` or `−Q`) none of these escapes is available, so PR6114's theorem and its 17 = 18 − 1 conclusion stand.

## Not audited

The surplus formula `M = v·income − n_thick·c` and the value `c = 56` on the PR5907 word (`760`) were not
rechecked against an invoice. The choice of rank mass rather than the moment as the objective was not audited
either; PR6114 itself defers the moment to PR5554 and `research/fragmentation-ceiling`. The random one-destination
test supports the A4 positive case, and the A4 proof is the evidence for it.
