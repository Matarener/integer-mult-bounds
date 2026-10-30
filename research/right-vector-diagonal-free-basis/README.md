# Free basis changes do not shorten a right-vector diagonal

**Scoped proof, with finite controls. No new κ.** Selected κ stays
`0.001672660197076918`.

Factors are `I + u y^T` with `u` in `R^n` and `y` in `K^n`, over any field `K`
and any associative `K`-algebra `R`. Free maps are arbitrary `GL_n(K)` changes
of basis, placed anywhere in the word. The exact number of factors needed for
`diag(d_1, ..., d_n)` is

```text
t_K(d) = #{ i : d_i is not in K^x }.
```

For `K = F_2` this is the count `t` of entries different from 1. So free
`GL_n(F_2)` mixing never realizes a diagonal with fewer than `t` factors. That
answers open question 1 of
[`research/f2-right-vector-diagonal-minimum`](../f2-right-vector-diagonal-minimum/README.md),
which proved the count without free maps and named the missing invariant as
the blocker.

## Argument

The written proof is [PROOF.md](PROOF.md). It has three steps:

1. **Normal form.** Conjugating a factor by a free map gives a factor, so every
   word equals `Q S` with `Q` a product of the same number of factors and `S`
   one free map.
2. **Column bound** (from the predecessor). `Q - I` maps `K^n` onto a
   `K`-space spanned by `L` vectors.
3. **Kernel lemma** (new). For a diagonal `D` and any `T` in `GL_n(K)`, every
   kernel vector of `D T - I` on `K^n` vanishes at each `i` with `d_i` not in
   `K^x`. So the image of `D T - I` has dimension at least `t_K(d)`. Apply it
   with `Q = D S^{-1}`.

The coordinate factors, followed by one free diagonal map for the entries in
`K^x`, attain the bound.

Corollaries: every group algebra `F_2[G]`, abelian or not, has exact diagonal
minimum `t` in the full nonidentity-label alphabet `I + (g - 1) x y^T`, with
free scalar mixing allowed. Over `F_3`, `diag(2, 2)` costs nothing, because it
is a free map. Restricted label alphabets, such as `{i, j}` only in `F_2[Q8]`,
can need more factors. They are outside this statement.

## Finite controls

`verify.py` uses the standard library and writes nothing. It checks:

| Ring | n | Word length | Factors | Free maps | Diagonals reached, each first at length `t_K` |
|---|---:|---:|---:|---:|---:|
| `F_2[C_2 x C_2]` | 2 | ≤ 2 | 766 | 6 | 256 of 256 |
| `F_2[S_3]` (nonabelian) | 2 | ≤ 1 | 12,286 | 6 | 127 (all with `t ≤ 1`) |
| `F_3[x]/(x^2)` | 2 | ≤ 1 | 321 | 48 | 32 (all with `t_K ≤ 1`) |

It also checks:

- Every conjugate of every factor stays in the alphabet: 93,720 checks.
- The kernel lemma for every diagonal and every free map: 718,128 cases over
  the three rings at `n = 2` and the Klein ring at `n = 3`.
- Over `F_3`, `diag(2, 2)` is reached at length 0.
- Sharpness of the `K`-valued right vector: the predecessor's ring-valued factor
  is outside the alphabet and gives `t = 2` from one factor.

These are corroboration, not the proof.

## Reproduce

From the repository root:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -B -W error research/right-vector-diagonal-free-basis/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -O -B -W error research/right-vector-diagonal-free-basis/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/right-vector-diagonal-free-basis
```

Expected final line of `verify.py`:

```text
PASS_RIGHT_VECTOR_DIAGONAL_FREE_BASIS F2[C2xC2]:n2:L2=256 F2[S3]:n2:L1=127 F3[x]/(x^2):n2:L1=32 no_new_kappa
```

Each run takes about 20 seconds. The script prints a receipt digest bound to
its own bytes and to the declared input.

## Limits

This is an exact count in a formal alphabet. Native frames, hosting, routing,
precision and recursive cost are not priced, and no supplier changes.
Free maps must have entries in `K`. With `R`-valued free maps the statement is
not asserted. Independent human and formal proof-kernel review are unclaimed.

## Open next questions

1. **General targets.** For a non-diagonal target `M`, is the minimum
   `min_T dim_K (M T - I) K^n` over `T` in `GL_n(K)`? The lower bound follows
   from the same normal form. The upper bound needs a factorization
   `I + C Y^T` into factors whose prefixes stay invertible. A first step is a
   permutation target over `F_2[C_2]` at `n = 2`.
2. **Restricted labels with free mixing.** Which part of the Q8 `{i, j}` lower
   bounds survives when the alphabet adds one paid label outside `{i, j}`?
   This package shows that the full label set gives `t`. Start with a single
   `[zi]` target.
3. **Native price.** Bind one coordinate word to an existing supplier meter.
   This note has no physical schedule.

## Credit

Produced by Nick Petalas. The right-vector alphabet, the column expansion and
the ring-valued sharpness witness are Wentao Li's
`research/f2-right-vector-diagonal-minimum` (#4099), which builds on
`research/bit-cyclic-root-barrier` (#2513). The graded diagonal argument for
elementary abelian groups is `research/elementary-abelian-diagonal-minimum`
(#4098). Apache-2.0.
