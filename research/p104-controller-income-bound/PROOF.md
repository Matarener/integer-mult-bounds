# Proof: twisted outputs are at most paid odd shears minus one

## Setting

One central port. The caller word of `research/p104-productive-controller/caller.py` acts on `n = 32` banks
(16 pairs). A bank holds an element of `R = K[Q, Q⁻¹] ⊗ K[D_0, …, D_32]`, `K = ℚ`; the banks start as the rows of
the constant right boundary matrix (invertible), and the constant left boundary matrix is applied at the end. The
alphabet is replayed literally:

| event | action on the rows | kind |
|---|---|---|
| `ADD y x c` | `y += c·x`, `c ∈ K` | free |
| `SWAP`, `SIGNED_SWAP` | exchange two rows, one sign | free |
| `Q_POWER r ±2` | `r *= Q^{±2}` | free (even central powers are translations) |
| `IDLE pair S` | both rows of the pair `*= ∏_{s∈S} D_s` | free in this count (its rank-`8|S|` price is a lift, cancelled by the target rank) |
| `LOCAL s pair back` | `y += Q^{-1}·x` (or `x += −Q·y` backward), then both rows `*= D_s` | **paid odd shear** (one full call) |
| `QUERY_SHEAR s pair back` | `y += Q^{-1}·x` (or `x += −Q·y`) | **paid odd shear** (one rank-one request per port) |

Write every row as `a + Q·b` with `a, b ∈ R_even = K[Q^{±2}] ⊗ K[D]`; `a` is the **even part**. Let `E` be the
`n × n` matrix over `R_even` whose rows are the even parts, and `rank E` its rank over the fraction field of
`R_even`.

## Lemma

1. Every free event is an invertible row operation of `(E | odd parts)` with coefficients in `R_even` (constants,
   `Q^{±2}`, monomials in `D`); it preserves `rank E`.
2. A paid shear `y += Q^{±1}·x` changes exactly one row of `E`: `E_y += Q^{±1}·(odd part of x)`, which lies in
   `R_even`. So `rank E` changes by at most one.
3. Before the first paid shear every odd part is zero (the right boundary is constant), so the first paid shear
   does not change `E` at all.
4. The outputs are the rows of `L·M_final`, `L` the constant left boundary. The even part of `L·M_final` is
   `L·E_final`, so an output `ℓ_i·M_final` that is an odd monomial `Q^{±1}·D^{S_i}·e_i` (every declared diagonal
   output) puts the row `ℓ_i` of `L` in the left kernel of `E_final`.

**Theorem.** With `s` paid shears and `n_odd` outputs that are odd (zero even part),

    n_odd ≤ n − rank E_final ≤ n − (n − (s − 1)) = s − 1 .

Proof: `rank E` starts at `n` (invertible right boundary), stays `n` through free events and the first paid
shear, drops by at most one at each of the other `s − 1` paid shears, so `rank E_final ≥ n − (s − 1)`. For the
other inequality let `T` be the set of twisted outputs and `L_T` the matching rows of `L`. By (4), `L_T·E_final = 0`.
The outputs `Q^{±1}D^{S_i}e_i`, `i ∈ T`, are linearly independent, so `rank L_T ≥ rank(L_T·M_final) = n_odd`, and
the left kernel of `E_final` has dimension at least `n_odd`: `rank E_final ≤ n − n_odd`. This does not need `L`
to be invertible (on the three literal controllers it is; the verifier records its rank, 32). ∎

(The first version of this file read the zero rows off `M_final` instead of `L·M_final`; the left-kernel step
above is the repair given in the independent audit
[PR #6120](https://github.com/CrocSwap/integer-mult-bounds/pull/6120), PROOF.md A1.)

The verifier evaluates the same argument after the ring homomorphism `D_s → 1`, `Q² → θ` (`θ = 7/3`, `11/5`):
items 1–4 hold verbatim in the image, so the per-event rank trace is a complete check on the given word.

## Consequence for the complete invoice

Let a caller use `n_thick` full calls and `n_thin` thin shears, all on one pair each, and let every one of its
`n_out` outputs be an odd monomial with stage set `S_i` (target rank `1 + d·|S_i|`, `d = 8`). Every stage that
appears in an output was paid once as a lift of that content (`d` per bank per full call or per idle stage).
This follows from the determinant, stage by stage (audit PR #6120, A2): scalar `ADD`, swaps and shears have
determinant `±1`, `Q_POWER` multiplies it by `Q^{±2}`, and a lift of one row by `D_s` multiplies it by `D_s`, so
`det(L·M_final) = c·Q^{2k}·∏_s D_s^{ℓ_s}` with `c ∈ K^×` and `ℓ_s` the number of row-lifts at stage `s`; the
diagonal `diag(Q^{q_i}D^{S_i})` has determinant `∏_i Q^{q_i}·∏_s D_s^{#{i : s ∈ S_i}}`, and `K[Q^{±1}, D]` is a
UFD, hence `#{i : s ∈ S_i} = ℓ_s` for every `s` and `Σ_i |S_i| = Σ_s ℓ_s`. The argument needs the outputs to form
the full monomial diagonal (the cost model of `caller.py` accepts only that); the verifier checks both identities
stage by stage on the three controllers (`Σ_s ℓ_s = 194`, `Σ_i q_i` = net `Q_POWER` = 0). Therefore

    income per port = Σ_i (1 + d|S_i|) − d·(lifts) − n_thin = n_out − n_thin ≤ (n_thick + n_thin − 1) − n_thin = n_thick − 1 .

The three retained p16 controllers have `n_out = 32`, `n_thin = 15`, `n_thick = 18`: income `17 = 18 − 1`, the
bound with equality (checked from the literal words in `RESULT.json`).

With `v` ports and a local word that loses `c` units of rank mass per full call outside the main lifts (the owned
centre: `c = 56` on the PR5907 word, `64` on #4610), the complete rank-mass surplus is

    M = v·(income) − n_thick·c ≤ n_thick·(v − c) − v ,

equal to `18·48 − 104 = 760` on PR5907. Each additional thick call can add at most `v − c` units of surplus, and
no change of the caller graph inside this alphabet (path or not, any prefix/suffix idle law, any pairing of thin
shears) can add more. The remaining complex-side levers are therefore the centre `c`, the fragmentation of the
local word (which enters the moment, not the mass; see `research/fragmentation-ceiling`), and the moment cost of
the target ranks that grows with `n_thick` (which is why `p = 16` is optimal for the retained local profile,
PR5554).

## Relation to the binary theorem

`research/productive-controller-basis-search/GLOBAL-PROOF.md` (Cinna Davis), Theorem B, proves the count
`queries ≥ 2p + 1` for `2p` independent monomial outputs over `F₂[Q]/(Q² − 1)` with constant binary boundaries
and without idle work, by the rank of `n` rank-one nilpotents summing to the identity. The lemma above is the same
count in the retained complex alphabet: `K = ℚ`, `Q` a Laurent variable with `Q² ≠ 1`, free idle markers, outputs
counted one by one (so partially twisted words are covered), and it is read off the even-part rank rather than
the derivative at `Q = 1`. The pruning remark of that package's `PROOF.md` ("a query changes the even part from
`E` to `E + NO`, so its rank can fall by at most one") is the step (2) of the lemma; here it is made the whole
argument, with the first-shear refinement (3) that gives the `− 1`.

## Scope

The alphabet is the literal one of the retained callers (constant boundaries, `Q_POWER ∈ {±2}`, one-pair shears
with coefficient `Q^{-1}` or `−Q`). Outside it the bound can fail, but touching several banks is not by itself an
escape. Writing a paid job as `M ← A·M`, `A = A_e + Q·A_o`, Sylvester's inequality bounds its drop of `rank E` by
`(n − rank A_e) + rank A_o`, and by `n − rank A_e` while no odd content exists yet (audit PR #6120, PROOF.md A4,
with exact controls). So a paid job that writes one row, `y ← u·y + Σ_j f_j·x_j` with `u` even and nonzero, obeys
the bound including the `− 1`, for any number of source banks and any Laurent `f_j`. The known escapes are: a job
that writes several rows (for example the three Whitehead shears of one pair taken as one paid job, which drops
`rank E` by two from a constant entry); a paid odd
one-bank translation `y ← Q^{±1}·y` (it twists one output even as the first paid job); and a boundary that already
carries odd `Q` content (step 3 fails; with a general entry the bound is `n_odd ≤ (n − rank E_entry) + s`). None
of these is in the literal alphabet. The bound is on rank mass; it says nothing new about the moment at `t < 1`, where
PR5554's convexity argument and the fragmentation ceiling apply.
