# Joint full-guard header law for orthogonal requests of any rank

This scoped counting proof gives the exact fraction of a complete header cover
on which every request of a pairwise orthogonal idempotent family passes its
full leading-minor guard. It extends Nick Petalas's single-request law in
[#4228](https://github.com/CrocSwap/integer-mult-bounds/pull/4228) and joint
rank-one law in [#4239](https://github.com/CrocSwap/integer-mult-bounds/pull/4239)
to families of arbitrary ranks. Both predecessors are used as cited steps and
are not rechecked here. No new kappa, supplier admission or multiplication
theorem is claimed.

## Result

Let F be a finite field of order q. Let P_1,...,P_k be idempotents on F^m with
ranks r_i >= 1, `P_i P_j = 0` for i != j, and `r_1+...+r_k <= m`. Request i
passes header G in GL_m(F) when the leading principal minors of sizes
1,...,r_i of `G P_i G^-1` are all nonzero. This is the guard counted by #4228;
for r_i = 1 it is the first-pivot guard of #4239.

For positive ranks s_1,...,s_k in dimension n, with `e = n - (s_1+...+s_k)`,
define the first-stage factor

```text
F(q,n; s) = (q^s_1 - 1)...(q^s_k - 1) [(q-1)^k q^e - (-1)^k] / [q^k (q^n - 1)],
```

with F = 1 for the empty family. The exact fraction of headers passing every
request is the stage product

```text
J(q,m; r) = prod_{t=0}^{R-1} F(q, m-t; (r_i - t : r_i > t)),   R = max r_i.
```

At stage t the active requests are those with r_i > t, and the free dimension
is `e_t = (m-t) - sum_{r_i>t} (r_i-t)`. For k = 1 this is #4228's product; when
every rank is one it is #4239's J(q,m,k).

Examples, all checked by the complete enumerators below:

| q | m | ranks | joint fraction | product of marginals |
|---:|---:|---|---:|---:|
| 3 | 3 | (2,1) | 14/117 | 49/117 · 19/39 |
| 3 | 4 | (2,2) | 88/1755 | (361/1170)^2 |
| 2 | 4 | (2,1) | 1/56 | 5/28 · 3/10 |
| 2 | 6 | (2,2,2) | 15/6944 | — |
| 2 | 6 | (2,1,2,1) | 0 | — |

The guards are dependent: at q=3, m=4, two orthogonal rank-two requests pass
together on 5.0% of headers, against 9.5% under independence.

**Zero locus and header cover.** J = 0 exactly when q = 2, the family is
complete (`sum r_i = m`) and k is even. Otherwise one header serves the whole
family. In the exceptional case exactly two headers suffice. This extends
#4239's cover theorem from rank one to arbitrary ranks with the full guard
chain. These are existence counts; they do not price finding, emitting,
dispatching or returning a header.

## Proof

**1. Normal form.** The images of the P_i are independent and the common
kernel `K = ker(P_1+...+P_k)` complements their sum, because `P_i (sum P_j) = P_i`.
In a basis made of bases of the images followed by a basis of K, each P_i is
the coordinate projector on a block B_i of r_i consecutive coordinates.
Right translation permutes the complete GL cover, so all fractions are
unchanged. The stabilizer of the ordered family is block diagonal, so ordered
orthogonal families with fixed ranks form a single GL_m-conjugacy orbit.

**2. First stage.** Put `a = e_0^T G` and `b = G^-1 e_0`. As in #4228 and
#4239, every pair with `a.b = 1` has the same number of completions G, so the
pair (a,b) is uniform among the `D = (q^m-1)q^(m-1)` such pairs. The first
pivot of request i is the block sum `x_i = sum_{j in B_i} a_j b_j`. #4228
counts the pairs of d-vectors with dot product t as
`N_d(t) = (q^d-1)q^(d-1) + [t=0]q^d`, with `N_0(t) = [t=0]`. Disjoint blocks
make the block sums independent coordinates, so the all-pivots-nonzero count is

```text
prod_i (q^r_i - 1) q^(r_i-1) · sum_{x_1..x_k != 0} N_e(1 - x_1 - ... - x_k).
```

There are `(q-1)^k` nonzero tuples and `T_k = [(q-1)^k - (-1)^k]/q` of them
sum to one (#4239, step 2). The inner sum is therefore
`q^(e-1)[(q-1)^k q^e - (-1)^k]`, also when e = 0. Dividing by D, and using
`sum r_i + e = m`, gives F(q,m; r).

**3. Schur deletion keeps the family orthogonal.** Write `Q_i = G P_i G^-1`
as `[[a_i, b_i], [c_i, D_i]]` with `a_i != 0`, and put
`S_i = D_i - c_i a_i^-1 b_i`. By #4228, S_i is an idempotent of rank r_i - 1
and `Delta_k(Q_i) = a_i Delta_{k-1}(S_i)` for k >= 2. The new step is
orthogonality. For i != j, the blocks of `Q_i Q_j = 0` give

```text
a_i a_j + b_i c_j = 0,  a_i b_j + b_i D_j = 0,
c_i a_j + D_i c_j = 0,  c_i b_j + D_i D_j = 0.
```

Expanding and substituting these four identities,

```text
S_i S_j = D_i D_j - D_i c_j b_j/a_j - c_i b_i D_j/a_i + c_i (b_i c_j) b_j/(a_i a_j)
        = -c_i b_j + c_i b_j + c_i b_j - c_i b_j = 0.
```

So (S_1,...,S_k) is an ordered orthogonal family in dimension m-1 with ranks
r_i - 1; zero ranks are allowed and carry no further guard.

**4. Uniformity.** Replacing G by `diag(1,K) G` permutes the complete cover,
preserves every a_i, and conjugates every S_i by K. Hence, conditional on all
first pivots being nonzero, the law of the S-tuple is invariant under
GL_{m-1} conjugation. It is supported on one orbit by step 1, so it is uniform
on that orbit, which is the law of a fixed family under a uniform header in
dimension m-1. Request i's remaining guards depend only on S_i. Induction on
the maximum rank gives the stage product.

**5. Zero locus and cover.** F(q,n; s) vanishes exactly when
`(q-1)^k q^e = (-1)^k`. For q >= 3 the left side has absolute value at least
2^k > 1; for q = 2 it needs e = 0 and even k. If k >= 2 at stage 0, then
`e_t = e_0 + sum_{u<t}(k_u - 1) >= 1` for every t >= 1. If k = 1, every later
stage also has at most one request, and `(q-1)q^e + 1 > 0`. So J = 0 exactly
at q = 2, complete family and even k. In that case the first k-1 requests
form a family with `e = r_k >= 1`, and the last request alone has k = 1.
Both fractions are positive, so two headers suffice and one does not.

## Evidence and reproduction

[verify.py](verify.py) has two independent enumerators with separate field
arithmetic paths. F4 uses `F2[x]/(x^2+x+1)`, not integers modulo four.

- A complete GL census over F2 (m=3,4) and F3 (m=3), 31,560 headers, checks
  every rank composition (29 tuples), not just the all-pass entry. For each
  tuple it compares the full law of the passing set with inclusion-exclusion
  over subfamily stage products. It also checks the Schur lemma on every
  header with all first pivots nonzero: idempotent, rank r_i - 1, pairwise
  orthogonal. It also checks that the conditional S-tuple is uniform on an
  orbit of the exact size, and that the cover number is 1 or 2 as stated.
- A row/column-pair census enumerates every `(X, Y)` with `XY = I_R` from the
  top R rows of G and left R columns of G^-1: 1,937,856 pairs over F3 (m=4),
  F5 (m=3), F4 (m=3) and F2 (m=6), 11 rank tuples with R = 2, each checked
  against the full passing-set law.
- A formula grid of 3,514 tuples (q in {2,3,4,5,7,8,9}, m <= 8) checks the
  zero locus and the two-header argument. 180 specializations reproduce
  #4228's closed form at k = 1 and #4239's J at all-rank-one.
- Four controls are rejected or differ from the law: the independence product,
  a recursion that holds the free dimension fixed as in the single-request
  law, a nonorthogonal pair sharing an image, and an altered count.

From the repository root, with any CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/orthogonal-chain-header-law
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/orthogonal-chain-header-law --check-source-history
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/orthogonal-chain-header-law/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/orthogonal-chain-header-law/verify.py
```

Expected marker:

```text
PASS_ORTHOGONAL_CHAIN_HEADER_LAW {"controls": 4, "formula_grid": 3514, "gl_headers": 31560, "gl_rank_tuples": 29, "pair_rank_tuples": 11, "pairs": 1937856, "specializations": 180}
```

Each direct run takes about 100 seconds on one core. The verifier has fixed
case lists, no recursion and no subprocesses. Every scan is capped at
1,100,000 candidates. Checks raise explicit exceptions, so they stay active
under `-O`. Python allocates during the bounded scans, a documented Power of
Ten rule 3 deviation for a finite verifier.

## Limitations

The universal claim is the written proof; the enumerations are finite
corroboration. It is not a proof-kernel result or a multiplication theorem.
Orthogonality, fixed idempotents and complete equally weighted headers are
essential premises. The census does not reach m = 64 or rank 42, and no
prime-power lift, actual request stream, physical selection/emission/dispatch
or dirty-return cost, stock, fallback repricing or selected replay is supplied.
Nonorthogonal families are outside this package and claimed separately.
Independent human and formal proof-kernel review are unclaimed.

## Open next questions

1. Does the stage product extend to commuting but nonorthogonal idempotents,
   or to families with prescribed image/kernel intersections? Only step 3 used
   `P_i P_j = 0`. Start by computing the Schur complements of two idempotents
   with `P_i P_j != 0` and find which pair invariant survives one stage.
2. Can an actual orthogonal BIT request family use a fully charged
   shared-header caller? Pin one producer family with its ranks, then charge
   header selection, emission, dispatch, dirty return and stock. The joint law
   and cover theorem supply none of those prices.

## Credit

Produced by Nick Petalas. It builds on Nick Petalas's #4228 (single-request
Schur deletion and dot-product counts) and #4239 (rank-one joint law and
nonzero-sum count). Cinna Davis's #4100 BIT.md poses the per-request guard
accounting. Apache-2.0.
