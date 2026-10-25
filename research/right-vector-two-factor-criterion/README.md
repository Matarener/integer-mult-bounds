# Exact two-factor criterion for right-vector targets

**Scoped proofs with finite certificates. No new κ.** Selected κ stays
`0.001672660197076918`.

Paid factors are `I + u y^T` with `u` in `R^n` and `y` in `K^n`; free maps are
`GL_n(K)` changes of basis anywhere in a word (#4099, #4243). #4243 proved
`cost(M) >= delta(M) = min_T dim_K (M T - I) K^n` and equality on diagonal
targets. #4265 showed equality fails over `M2(F2)` at `n = 2` (72 targets cost
3 against `delta = 2`) and asked what the exact cost is over noncommutative
algebras, whether the failure lifts to `F2[S3]`, and whether `delta` is exact
over commutative or local algebras.

## Result

Proofs are in [PROOF.md](PROOF.md).

1. **One factor, every `n` and every algebra:** `cost(M) <= 1` exactly when
   `delta(M) <= 1`, and then the two are equal.
2. **Two factors at `n = 2`, every algebra:** `cost(M) <= 2` exactly when some
   `G, H` in `GL_2(K)` give `N = G M H` with `N12` in the right ideal `N11 R`.
   With item 1, this decides `cost(M)` in {0, 1, 2, ≥3} for every target.
3. **Matrix algebras.** Over `R = M_m(K)` the condition reads: some nonzero
   `phi`, `t` in `K^2` give
   `rank (phi ⊗ I_m) M = rank (phi ⊗ I_m) M (t ⊗ I_m)`. This answers #4265's
   question 3 at `n = 2`.
4. **Local algebras.** If the non-units of `R` form an ideal `J`, every target
   with an entry outside `J`, in particular every invertible target, costs
   exactly `delta(M)`. This answers #4265's question 1 at `n = 2` for local
   algebras and invertible targets. It cannot be extended to every target:
   over the commutative local algebra `F2[x,y]/(x,y)^2`, 12 targets in
   `M_2(J)` are unreachable while `delta <= 2`, for example
   `[[x + y, y], [y, x]]`.
5. **`F2[S3]`.** The failure lifts. A unital surjection
   `F2[S3] -> M_2(F_2)` maps words to words, so every lift of a #4265
   failure costs at least 3 while `delta <= 2`. `verify.py` builds one target
   of cost exactly 3. Over all `2^24` targets at `n = 2`, exactly **120,060**
   fail the criterion, so they cost at least 3 against `delta <= 2`. Of these,
   18,432 = 72 · 4^4 are lifts of `M2(F2)` failures. The rest fail because one
   pair `(G, H)` must work in both blocks.
6. **A smaller noncommutative failure.** Over the 3-dimensional algebra
   `UT2(F2)` of upper triangular matrices, 12 of 4,096 targets cost 3 with
   `delta = 2`.

| Algebra `R` | Targets (n = 2) | Cost histogram 0/1/2/3 | Unreachable | Criterion failures |
|---|---:|---|---:|---:|
| `F2[x,y]/(x,y)^2` (local) | 4,096 | 6 / 549 / 3,529 / 0 | 12 | 12 |
| `F2 x F2` | 256 | 6 / 117 / 133 / 0 | 0 | 0 |
| `F2[C3]` | 4,096 | 6 / 549 / 3,541 / 0 | 0 | 0 |
| `UT2(F2)` | 4,096 | 6 / 549 / 3,529 / 12 | 0 | 12 |
| `M2(F2)` | 65,536 | 6 / 2,277 / 63,181 / 72 | 0 | 72 |
| `F2[S3]` (criterion only) | 16,777,216 | — | — | 120,060 |

In every exhaustively searched algebra, the criterion holds exactly on the
targets of cost at most 2, and every criterion failure costs 3 or is
unreachable. The 72 `M2(F2)` failures agree with #4265.

Claim types: items 1–4 and the lift in item 5 are proofs for every algebra in
scope. The counts in the table and items 5–6 are finite certificates. Cost 3 as
an upper bound is only checked by search on the listed algebras; no general
three-factor theorem is claimed.

## Method

`verify.py` builds each algebra from a structure table and checks that it is
associative with `K` central. It precomputes right-ideal membership `z ∈ a R`
by `F_p`-rank. Stage `main` computes the exact minimum on every target by
breadth-first search over words `Q S`, computes `delta` over every `T`, and
asserts: the criterion equals `cost <= 2`, Theorem A, the local statement on
`F2[x,y]/(x,y)^2` (non-units checked to form an ideal), the rank form over
`M2(F2)`, and the expected counts. It also checks that `rho` is a surjective
unital algebra map, lifts a three-factor `M2(F2)` word to `F2[S3]`, and
asserts that the lifted target fails the criterion. Stage `s3` evaluates the
criterion on all `2^24` targets over `F2[S3]`. The script writes nothing.

## Reproduce

From the repository root:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -B -W error research/right-vector-two-factor-criterion/verify.py --stage main
~/git/integer-mult-bounds/.venv/bin/python3.12 -B -W error research/right-vector-two-factor-criterion/verify.py --stage s3
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/right-vector-two-factor-criterion
```

Expected final lines:

```text
PASS_RIGHT_VECTOR_TWO_FACTOR_CRITERION F2[x,y]/(x,y)^2:4096:12 F2xF2:256:0 F2[C3]:4096:0 UT2(F2):4096:12 M2(F2):65536:72 m2_rank_form=ok f2s3_lift=cost3 no_new_kappa
PASS_RIGHT_VECTOR_TWO_FACTOR_S3 targets=16777216 three_or_more=120060 no_new_kappa
```

Each stage takes under 40 seconds on one core (CPython 3.12, NumPy 2.5.4,
macOS arm64). The asserts are the checks, so do not run with `-O`.

## Limits

This is a formal alphabet. Native frames, hosting, routing, precision and
recursive cost are not priced, and no supplier changes. Theorems B–D are for
`n = 2` only. Whether every reachable target at `n = 2` costs at most 3 is
not proved. The `F2[S3]` count gives cost at least 3; exact costs there are not
searched. Independent human and formal proof-kernel review are unclaimed.

## Open next questions

1. **Three factors.** Is every reachable target at `n = 2` reachable with
   three factors, over every algebra? Characterise the three-factor set as
   Theorem B does for two; with it, the cost at `n = 2` would be exact.
2. **Larger `n`.** With `y_1, ..., y_k` a basis, `k` factors are block column
   operations. Write the `n = 3`, `k = 2` condition as a flag of right
   ideals and test it by search over `F2[C2]` or `UT2(F2)`.
3. **Commutative non-local algebras.** Is `delta` exact for invertible
   targets over every commutative algebra at `n = 2`? A product of local
   algebras needs one `(G, H)` that works in every factor. Count criterion
   failures over `F3 x F3 x F3` first.

## Credit

Produced by Nick Petalas. The alphabet, normal form and lower bound come from
#4243 (`research/right-vector-diagonal-free-basis`); the open questions and the
`M2(F2)` counts come from #4265 (`research/right-vector-general-target`). The
column bound and right-vector alphabet are Wentao Li's
`research/f2-right-vector-diagonal-minimum` (#4099), building on
`research/bit-cyclic-root-barrier` (#2513). Apache-2.0.
