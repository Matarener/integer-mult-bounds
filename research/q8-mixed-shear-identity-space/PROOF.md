# Call-space identities for mixed positive-Q8 words

## Model

The model is the one in `research/q8-mixed-boundary-rank/PROOF.md` and
`research/q8-square-iblock-obstruction/PROOF.md`. Work in the full formal
group algebra `F2[Q8]`. Every role starts with independent arbitrary dirty
input, and binary scalar GL mixing is free. A paid call is

```text
D_l = I + x_l u_l v_l^T,   x_l = 1 + [g_l],   g_l in {i, j},   v_l^T u_l = 1.
```

Call 0 acts first. The endpoint is diagonal: `t_i` roles carry `[zi]`,
`t_j` roles carry `[zj]`, and every other role is restored to the identity.
Any finite number of restored roles is allowed. After conjugating the free
mixing through the calls (the PR3517 normal form), let `X` be the `t × n`
active rows of the `u_l` columns and `Y` the `n × t` active columns of the
`v_l^T` rows. Let `L` be the strictly lower part of the full-role Gram matrix
`(v_l^T u_a)`. Dirty coordinates contribute to `L`. Let `E_i` and `E_j` be
the diagonal projectors onto i-calls and j-calls, and let `P_i` and `P_j` be
the active target projectors.

For a label word `w = w_0 w_1 ... w_d`, define the block monomial

```text
M_w = E_{w_0} L E_{w_1} L ... L E_{w_d}.
```

The left label is the latest call. The calculus `C_3` consists of the 30
monomials with `d <= 3`, together with `P_i` and `P_j`. An *identity* of
`C_3` is a coefficient vector `c` in `F2^32` such that

```text
sum_w c_w X M_w Y + c_i P_i + c_j P_j = 0
```

holds for every exact word of every shape and every finite workspace.

## The coefficient equations

Put `a = 1+[i]` and `b = 1+[j]`. Then `a^2 = b^2 = 1+[z]`, and every product
of five factors from `{a, b}` is zero. The eight elements

```text
1, a, b, aa, ab, aaa, aab, aaab
```

form a basis of `F2[Q8]`; the verifier checks this and every coordinate used
below. Expanding the product in chronological order gives

```text
W = I + sum over chains l_0 > l_1 > ... > l_d of
        x_{l_0} ... x_{l_d} u_{l_0}(v_{l_0}^T u_{l_1}) ... (v_{l_{d-1}}^T u_{l_d}) v_{l_d}^T.
```

Scalar matrices commute with group-algebra coefficients, and chains with
`d >= 4` vanish. The active block of the label-`w` chains is `X M_w Y`.
Equating each basis coordinate of the active block with the target
coordinates gives seven equations. The coordinates of `[zi]` are
`1, a, aa, aaa` and those of `[zj]` are `1, b, aa, aab`.

```text
a    : i + Pi = 0
b    : j + Pj = 0
aa   : ii + ji + jj + Pi + Pj = 0
ab   : ij + ji = 0
aaa  : ji + iii + iji + ijj + jij + jji + Pi = 0
aab  : ji + iij + iji + jii + jij + jjj + Pj = 0
aaab : ji + iji + jij + iiij + iiji + ijii + ijij + ijjj
       + jiii + jiji + jijj + jjij + jjji = 0
```

Here a word `w` stands for `X M_w Y`. The quadratic pair is the
`X(I+H)Y = 0` identity and its orientation-swapped partner from the
mixed-boundary proof (Nick Petalas/PR3570). It is restated here, not claimed
as new.

## Theorem A: the identity space of `C_3`

**The identities of `C_3` are exactly the span of the seven coefficient
equations, a 7-dimensional subspace of `F2^32`.**

*Proof.* Each coefficient equation holds for every exact word, so the span
consists of identities. Conversely, `WITNESS.json` lists 25 exact words, on
one or two roles, of lengths 3 to 8. Each active entry `(p, q)` of each word
gives a row vector in `F2^32` that every identity annihilates. The verifier
recomputes each endpoint exactly, forms these rows, and finds rank 25. The
annihilator of the rows therefore has dimension 7. It contains the span of
the seven independent equations, so the two spaces are equal. ∎

So no further degree-three call-space identity holds for active
compressions, whatever the shape and workspace. A cyclic-style identity
such as `X(I+L)^2 Y = 0` is outside the span. The verifier finds an
explicit witness row that refutes it.

## Theorem B: the four shears

Call `h` a *strict block polynomial* if it is a sum of monomials `M_w` with
`d` equal to 1 or 2. Then `I + h` is unitriangular and invertible.

**Exactly four strict block polynomials give an identity `X(I+h)Y = 0`:**

```text
K1 = I + ii + ji + jj
K2 = I + ii + ij + jj
Q1 = I + iii + iij + ijj + jii + jji + jjj
Q2 = Q1 + ij + ji
```

**No product of two of them whose degree stays at most three gives an
identity.** That covers 12 of the 16 ordered products. The four products
`Q_a Q_b` reach degree four and lie outside `C_3`.

*Proof.* By Theorem A, `X(I+h)Y = 0` is an identity exactly when its
coefficient vector lies in the 7-dimensional span. The verifier checks all
`2^12 - 1` nonempty strict block polynomials and all 12 products. ∎

`K1` and `K2` are the two quadratic shears of PR3570. `Q1` is the sum of the
`aaa` and `aab` equations. On a word that uses one label on each role,
`K1 = K2 = I + L` and `Q1 = Q2 = I + L^2`. These are the cyclic `K` and `K^2`
of `research/q8-cyclic-cubic-obstruction/PROOF.md`.

## Theorem C: every pair of shear images can meet

Let `U = im(Y)`, a `t`-dimensional subspace of the call space `F2^n`. Each
of `K1 U`, `K2 U`, `Q1 U` and `Q2 U` is `t`-dimensional and lies in
`ker(X)`, which has dimension `n - t`.

**For each of the six pairs of these images, some exact one-role
three-call word gives a nonzero intersection.**

*Proof.* Each witness has `u = v = 1` for all three calls. Listed in
chronological order (call 0 first), the label sequences are `ijj`, with
endpoint `[j][j][i] = [zi]`, and `iij` and `jii`, with endpoint `[zj]`.
Here `t = 1`, and for each pair the two images span only one dimension.
The verifier searches all eight one-role label sequences and records one
witness per pair. ∎

The cyclic theorem proves `n >= 3t` from the disjointness of `KU` and
`K^2 U`, which holds on every word. In the mixed model no pair of the four
images is disjoint on every word, even at `t = 1`. A two-image argument of
the PR3558 kind therefore cannot certify `n >= 3t` for mixed words. This
also explains why PR3570 only obtains rank inequalities with a defect term.

## Conjecture D: the four images together

**Conjecture.** For every exact word,

```text
dim(K1 U + K2 U + Q1 U + Q2 U) >= 2t.
```

The sum lies in `ker(X)`, so the conjecture implies `n >= 3t` for every
mixed shape. The direct word attains this bound. In particular, it would
give exact minima of 15 at shape `(4,1)` and 24 at shape `(7,1)`. On words
with one label per role the four images reduce to `KU + K^2 U`, so the
conjecture holds there by the cyclic theorem.

*Finite evidence, not a proof.* The verifier enumerates every exact word
in these classes by meet-in-the-middle. The classes are one role at
length 3, and two roles at lengths 5, 6 and 7, with every target in
`{zi, zj, 1}^r`. With `--full` it also covers two roles at length 8.
Every word meets the conjectured bound. The exact counts are in the
README. Here `t <= 2`, where `n >= 3t` is already known, so this evidence
decides no open length.

## What is not claimed

Theorem A is a statement about the degree-three compression calculus. It
does not exclude identities involving degree-four or higher monomials. On
words of length 8 those monomials are nonzero, even though their
coefficients vanish in `W`. It also does not exclude non-linear rank
arguments, arguments that use the dirty rows and columns of the endpoint,
or arguments outside call space. The (4,1) and (7,1) minima remain open.
Conjecture D is unproved. No physical caller, invoice, supplier or new
kappa is claimed, and the selected frontier is unchanged.
