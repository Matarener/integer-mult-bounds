# Exact sign-dependent tariffs for every signed 3x3 connector target

produced by Nick Petalas

This is a **scoped proof with finite corroboration**, answering open question 1
of [#4241](https://github.com/CrocSwap/integer-mult-bounds/pull/4241).
The exact query bill for all 19,683 matrices in `{-1,0,1}^{3x3}`, over every
nonzero unital coefficient ring, depends only on the active operators and
membership in Ross Richardson's 288-member obstruction orbit. Forward and
inverse additive calls may have arbitrary different positive complete prices.
There is no new kappa or multiplication theorem.

The new result is the transport of the sign-dependent envelope through the
entire orbit, its combination with the support-attaining class, and the
resulting all-target constructor. The integer classification, six integer
repairs, canonical ring theorem and canonical sign-dependent theorem remain
credited predecessor results, used as lemmas rather than offered as an audit.

## Interface and exact formula

There are seven distinct dirty arrays `x0,x1,x2,y0,y1,y2,z` over a finite free
module over a nonzero unital ring R. The maps Ai and Bj are arbitrary R-linear
maps and need not commute. The only operations are

```text
Bj^s: z  += s Bj(xj)
Ai^s: yi += s Ai(z)             s in {-1,+1}.
```

Sources remain immutable, outputs are never read, and z must restore. For a
specified M in `{-1,0,1}^{3x3}`, require `yi += sum_j Mij Ai(Bj(xj))` for every
choice of maps and initial data. Each call restores private scratch and obeys
its complete port and head-return contract. A negative call subtracts the
increment, rather than inverting Ai or Bj.

Let S(M) contain Bj for each nonzero column and Ai for each nonzero row.
Let delta(M) be one on the signed/permuted orbit of

```text
C = [[1,1,1], [1,1,-1], [1,-1,0]],
```

and zero otherwise. Let `sigma_F = p_F^+ + p_F^-` and
`mu_F = min(p_F^+, p_F^-)`, for arbitrary positive complete call prices.
For characteristic c, define

```text
c = 0:   b_F = sigma_F;               u_F = 2 sigma_F
c >= 2:  b_F = min(sigma_F, c mu_F);   u_F = min(2 sigma_F, c mu_F).
```

**Theorem.** The exact minimum query bill is

```text
M = 0:    0
M != 0:   sum_{F in S(M)} b_F + delta(M) min_{F in S(M)} (u_F - b_F).
```

Every orbit member has all six operators active. In characteristic two,
`u_F = b_F = 2 mu_F`, so membership in the integer orbit incurs no surcharge.
The formula is uniform in composite characteristic and rings with zero
divisors. Preparation, admission and word-dependent control costs must be
charged separately unless already included in the fixed call prices.

## Proof

**Active-operator lower bound.** Write `(a_F,d_F)` for the positive/negative
occurrence counts of F. Restoring z and eliminating the initial dirt in each
y imply `a_F-d_F = 0` in the prime subring. Each active operator must occur,
and cannot occur just once. Thus in characteristic zero its counts dominate
`(1,1)`; in characteristic c >= 2 they dominate `(1,1)`, `(c,0)` or `(0,c)`.
Every active operator therefore costs at least b_F. These necessary conditions
follow by isolating one input and taking identity maps. Inactive operators
have positive costs and cannot lower this sum.

**Support-attaining targets.** Ross Richardson's
[#944](https://github.com/CrocSwap/integer-mult-bounds/pull/944) proves that every
M outside the orbit has an integer word with exactly one positive and one
negative call of each active operator, with inactive operators omitted.
Its coefficient identities hold over every ring. In characteristic c,
replace a call of sign -s by c-1 consecutive calls of sign s whenever the
unary profile has a lower price. The replacement acts identically at every
other query boundary since `(c-1)s = -s` in R. Apply this independently to each
active operator. The resulting word costs exactly sum b_F, attaining the lower
bound. This also covers zero rows or columns and the empty word for M = 0.

**Cost-preserving transport, the new orbit step.** Suppose

```text
M[i,j] = r_i s_j C[pi(i),rho(j)],       r_i,s_j in {-1,+1}.
```

In a word for C, replace an old A[pi(i)] call of sign t by Ai of sign r_i t,
and an old B[rho(j)] call of sign t by Bj of sign s_j t. Prefix source
coefficients and read coefficients acquire the indicated signs, giving M;
restoration identities remain zero. Inverse signed permutations give a
bijection of all valid words, in both directions, over every R.

Pull back the actual prices along this bijection. A negative r_i or s_j swaps
the corresponding two sign prices; permutations relabel them. Both sigma_F
and mu_F survive a sign swap, and the displayed sum and minimum survive the
operator permutation. Consequently the canonical-target theorem of
[#4241](https://github.com/CrocSwap/integer-mult-bounds/pull/4241), namely
`sum b_F + min(u_F-b_F)`, gives precisely the same expression for M. This proves
the lower bound and attainability throughout the orbit, completing the proof.
The transport is a compilation rule for the emitted queries at fixed ports;
it requires no runtime array permutation or free frame conversion.

For explicit construction, #4241 supplies an anchored word for every operator
F with F at `(c,0)` and the other five at `(1,1)`, in characteristic c. Global
sign reversal preserves the target and selects `(0,c)` when cheaper. Its
integer branch uses martinxxx9's six `(2,2)` repairs from
[#1088](https://github.com/CrocSwap/integer-mult-bounds/pull/1088).
`optimal_word` transports the anchor for the desired physical operator and
then makes the independent cheaper-sign conversions. These predecessor
constructions are retained with attribution; the transported family is new.

## Finite evidence and reproduction

From the repository root, with CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/signed-matrix-price-classification/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/signed-matrix-price-classification/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/signed-matrix-price-classification
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/signed-matrix-price-classification --check-source-history
```

The first two commands print `PASS_SIGNED_MATRIX_PRICE_CLASSIFICATION`.
The registered replay checks:

- All 19,683 targets in characteristics 0,2,3,4,5,8, at four exact integer price
  vectors. Each of the 472,392 words has its full dirty-action coefficients and
  actual signed bill checked against the closed formula.
- Every orbit target, every repeated operator, both global signs, and
  characteristics 0,2,3,4,5,8,12,16: 27,648 transported anchors. Both action and
  exact signed occurrence profile are checked.
- 6,912 additional orbit words at seeded rational prices in eight
  characteristics; 768 finite count-profile dynamic programs; 2,304 dense
  two-coordinate dirty-array executions using noncommuting maps; and 744
  single-query deletion controls.

The support-word table instantiates #944's existing recipe so that the new
constructor can serve the entire target domain. Its 19,395/288 partition is
inherited, and is not claimed as a new classification or independent audit.
The hash-pinned certificates from #944 and #1088 are the only live external
inputs. No pending executable or source-history object is imported.

Every run prints a generated receipt digest bound to all package files and
both live inputs. To retain the generated JSON, use `--receipt /path/outside`
with a destination outside the checkout. No receipt is handwritten or committed.

Python uses managed allocation. The evidence domains fix capacity at 19,683
support/target keys, 288 transformations and at most 1,536 queries per word.
All loops have finite bounds; there is no recursion or subprocess. Explicit
exceptions keep checks enabled under optimized Python. Warnings are errors.

## Limits and obligations

The all-ring result is a written scoped proof using the cited predecessor
lemmas, including the unmerged canonical theorem #4241 at head
`ec573175d36cb016661f37293dd9ee2aefb737bb`. The new proof does not independently
establish that theorem's lemmas. Finite executions do not enumerate every ring,
price vector or characteristic. Independent human and formal proof-kernel
review are unclaimed. A physical consumer, complete fixed prices, routing,
preparation, precision, supplier admission and outer multiplication transfer
remain uninstantiated. No selected cold replay or formal build was run.

## Open next questions

1. Can a concrete caller use one of these optimal words with a smaller complete
   bill than its current schedule? Pin the caller, its demanded M and the actual
   forward/inverse prices, then charge routing and admission as well as calls.
2. Which signed rectangular targets admit both an integer `(2,2)` repair and a
   characteristic-c unary anchor at every operator? A first step is a 3x4
   obstruction with those two properties; without them the same count-profile
   lower bound need not be attainable.

## Credit and provenance

Ross Richardson's #944 supplies the signed interface, 19,395 support-attaining
targets and 288-member obstruction orbit, building on #943/#934 and the
PR889/PR628 lineage. martinxxx9's #1088 supplies six arbitrary-operator integer
repairs. Sagar Thakrar's #1349 supplies the characteristic-three predecessor.
Nick Petalas's #4233 supplies the characteristic transfer and #4241 the
canonical sign-dependent envelope and six unary anchors. This contribution
proves sign-price invariance under signed permutations and the combined
all-target theorem, with a constructor for all targets.

Base `12fa8c5c844be21bfefb38a19503fbd867a11244`, priority revision 7.
[Claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19082890).
Exact source pins are in [SOURCES.json](SOURCES.json); structured next steps are
in [TASK.json](TASK.json). Apache-2.0.
