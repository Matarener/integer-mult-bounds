# The right-vector column bound is not exact for every target

**Finite certificate with a sharp counterexample. No new κ.** Selected κ stays
`0.001672660197076918`.

Paid factors are `I + u y^T` with `u` in `R^n` and `y` in `K^n`. Free maps are
`GL_n(K)` changes of basis anywhere in a word. #4243 proved that a diagonal
target costs exactly `t_K(d)` factors, and asked in its open question 1 whether
every target `M` costs

```text
delta(M) = min over T in GL_n(K) of dim_K (M T - I) K^n.
```

`delta(M)` is always a lower bound: that is #4243's normal form plus the column
bound of #4099. This package tests the upper bound on every target of eleven
small domains.

## Result

| Algebra `R` over `K` | n | Targets | Max cost | Formula failures | Gaps with no free map |
|---|---:|---:|---:|---:|---:|
| `F2` | 2 | 16 | 2 | 0 | 0 |
| `F3` | 2 | 81 | 2 | 0 | 0 |
| `F2` | 3 | 512 | 3 | 0 | 0 |
| `F4` over `F2` | 2 | 256 | 2 | 0 | 0 |
| `F2[C2]` | 2 | 256 | 2 | 0 | 0 |
| `F2 x F2` | 2 | 256 | 2 | 0 | **2** |
| `F3 x F3` | 2 | 6,561 | 2 | 0 | 0 |
| `F2[C3]` | 2 | 4,096 | 2 | 0 | **6** |
| `F2[x]/(x^3)` | 2 | 4,096 | 2 | 0 | 0 |
| `M2(F2)` (noncommutative) | 2 | 65,536 | 3 | **72** | **684** |
| `F2[C2]` | 3 | 262,144 | 3 | 0 | 0 |

1. **The answer to #4243's question is no in general.** Over the matrix
   algebra `M2(F2)` at `n = 2`, exactly 72 of 65,536 targets cost 3 factors
   while `delta = 2`. One is the target `[[E11, E01], [E10, E00]]`. In
   `M_2(M_2(F_2)) = M_4(F_2)` it is the transposition of coordinates 0 and 3.
   A separate enumeration in `M_4(F_2)` confirms that no two-factor word
   reaches it, that a three-factor word does, and that `T = I` already gives
   image dimension 2.
2. **The formula holds on all ten commutative domains checked**: 278,274
   targets, local and non-local, including `F2[C3] = F2 x F4` and
   `F3 x F3 = F3[C2]`.
3. **The minimum over `T` cannot be dropped.** Without any free map, the cost
   of `M` exceeds `dim_K (M - I) K^n` on 2 targets over `F2 x F2`, 6 over
   `F2[C3]` and 684 over `M2(F2)`; each such target costs 3 against dimension 2.
   Over `F2 x F2` the two targets are `(A, A^{-1})` and its swap, with `A` of
   order three in `GL_2(F_2)`. The fields and local algebras in the table have
   no such gap.

All counts are enumerated. Statement 1 is a counterexample to the proposed
formula; statements 2 and 3 are finite certificates on the listed domains, not
theorems for every algebra.

## Method

`verify.py` builds each algebra from a structure table and checks that it is
associative with `K` central. It computes the exact minimum by breadth-first
search over words in #4243's normal form `Q S`: products of paid factors
followed by one free map. It computes `delta` by enumerating every `T` in
`GL_n(K)` and taking `F_p`-ranks. It asserts `cost >= delta` everywhere and
records every target with `cost != delta`. A second search from `I` alone
gives the no-free-map cost, compared with `dim_K (M - I) K^n`. The script
writes nothing and prints a digest bound to its own bytes and results.

## Reproduce

From the repository root:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -B -W error research/right-vector-general-target/verify.py --stage main
~/git/integer-mult-bounds/.venv/bin/python3.12 -B -W error research/right-vector-general-target/verify.py --stage large
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/right-vector-general-target
```

Expected final lines:

```text
PASS_RIGHT_VECTOR_GENERAL_TARGET F2:n2:16 F3:n2:81 F2:n3:512 F4:n2:256 F2[C2]:n2:256 F2xF2:n2:256 F3xF3:n2:6561 F2[C3]:n2:4096 F2[x]/(x^3):n2:4096 M2(F2):n2:65536 formula_failures=M2(F2):72 no_free_map_gaps=F2xF2:2,F2[C3]:6,M2(F2):684 no_new_kappa
PASS_RIGHT_VECTOR_GENERAL_TARGET_LARGE F2[C2]:n3:262144 formula_failures=0 no_free_map_gaps=0 no_new_kappa
```

Each stage takes about 100 seconds on one core (CPython 3.12, NumPy 2.5.4,
macOS arm64). The asserts are the checks, so do not run with `-O`.

## Limits

This is an exact count in a formal alphabet. Native frames, hosting, routing,
precision and recursive cost are not priced, and no supplier changes. The
commutative agreement is checked only on the listed domains; no general proof
of the upper bound is claimed. Whether the `M2(F2)` failure transfers to a
nonabelian group algebra is not checked. Independent human and formal
proof-kernel review are unclaimed.

## Open next questions

1. **Commutative algebras.** Is `delta(M)` exact for every commutative
   `K`-algebra, or every local one with residue field `K`? A one-factor peel
   `A = A' (I + u y^T)` with `dim_K (A' - I) K^n = d - 1` exists exactly when
   some `y` vanishing on the `K`-kernel of `A - I` and some `x1` with
   `y . x1 = 1` give `A x1` in `A (ker y ⊗ R) + x1 R`. Proving this for a
   minimizing `T` would settle the question.
2. **Group algebras.** Does the failure lift to `F2[S3]`, which has `M2(F2)` as
   a block? Fix an explicit isomorphism and project words onto that block.
3. **Exact noncommutative cost.** What replaces `delta` over `M2(K)`? Compare
   the cost with ranks in `M_n(M_2(K)) = M_2n(K)`.

## Credit

Produced by Nick Petalas. The alphabet, normal form and lower bound come from
#4243 (`research/right-vector-diagonal-free-basis`), which asked this question.
The column bound and right-vector alphabet are Wentao Li's
`research/f2-right-vector-diagonal-minimum` (#4099), building on
`research/bit-cyclic-root-barrier` (#2513). Apache-2.0.
