# Invertible targets over products of fields in the right-vector model

## Model, statements, and predecessor

Let `K` be a field and let `R` be a commutative unital `K`-algebra. We use
exactly the retained source's model at `n = 2`:

```text
P(u,y) = I + u y^T,       u in R^2, y in K^2,
free factors: GL_2(K), usable anywhere in the word,
cost(M): minimum number of paid P factors in a word equal to M,
delta(M) = min_{T in GL_2(K)} dim_K ((M T - I) K^2).
```

The `K^2` in the definition of `delta` is the common two-dimensional input
space, not an independently chosen input in each product component. The
embedding of `K` into a product is diagonal. A free matrix and each right
vector `y` must therefore be common to all components. In contrast, the two
entries of `u` are arbitrary elements of `R`, so they may vary by component.

The predecessor is Nick Petalas's PR #4276,
`research/right-vector-two-factor-criterion`, at source head
`59c7bac0122ef2b80793c30a3d52329db6bdf17d`. Its retained
[PROOF.md](source/PROOF.md), Theorems A and B, supplies the one-factor and
two-factor criteria. Its [README.md](source/README.md) asks whether `delta`
is exact for invertible targets over commutative algebras. We rederive the
needed criteria below to make this argument self-contained.

For an invertible `M` over `R = K^k`, with `k >= 1` and components
`M_i in GL_2(K)`, we prove:

1. `cost(M) <= 2` if and only if there are nonzero
   `phi in (K^2)^*` and `t in K^2` such that `phi M_i t != 0` for every `i`.
2. Every invertible target over any finite product of fields that are
   unital `K`-algebras has an explicit word with at most three paid factors,
   using the fixed right-vector sequence `e1, e2, e1`.
3. If `K` is finite of size `q`, every invertible target over `K^k` costs at
   most two when `k <= q`. For every `k >= q+1` there is an invertible target
   of cost exactly three and `delta = 2`.

Thus commutativity alone does not make `cost = delta` on invertible targets
in this model. The smallest field-size instance proved here is `F2^3`.
No assertion is made that it is the smallest commutative algebra with this
property among all algebras.

## 1. Elementary one-factor and two-factor criteria

Conjugation by a free matrix preserves the paid alphabet:

```text
S P(u,y) S^{-1} = P(Su, S^{-T}y).
```

Moving free factors to the right therefore rewrites a word as a product of
the same number of paid factors followed by one `S in GL_2(K)`. Also, paid
factors with proportional nonzero right vectors merge:

```text
P(u,y) P(v,c y) = P(u + c v + c u (y^T v), y),   c in K.
```

This follows by expansion. A zero right vector or zero left vector gives
the identity.

For later use, `cost(M) <= 1` holds exactly when `delta(M) <= 1`. A word
`M = P(u,y) S` gives `(M S^{-1} - I) K^2` contained in `K u`.
Conversely, if the image of `M T - I` has dimension one, choose a spanning
vector `u` and write its two columns as `y_1 u, y_2 u`, with `y_j in K`.
Then `M T = P(u,y)` and `M = P(u,y) T^{-1}`. If the image has dimension
zero, `M = T^{-1}` is free. This also shows that `delta = 0` exactly when
`cost = 0`, and hence that cost and delta agree whenever cost is at most one.

We next prove the retained two-factor criterion:

```text
cost(M) <= 2
iff some G,H in GL_2(K) give N = G M H with N12 in N11 R.
```

For sufficiency, write `N12 = A C`, where `A = N11`, and put
`B = N21`, `D = N22 - B C`. Then

```text
N = [[A,0],[B,1]] [[1,C],[0,D]]
  = P((A-1,B)^T,e1) P((C,D-1)^T,e2).
```

Consequently `M = G^{-1} N H^{-1}` has a word with two paid factors and
free factors. This uses the explicit permission to place free maps anywhere.

For necessity, normalize a word with at most two paid factors to
`M = P(u1,y1) P(u2,y2) S`. If its right vectors are dependent, merge the
factors, handle any identity factors, and pad with an identity paid factor
whose right vector is independent of the remaining nonzero right vector.
For a completely free word, pad with identities in any two independent
directions. Thus we may arrange that `y1,y2` are a basis of `K^2`.
Choose `G in GL_2(K)` with `G^{-T} y_j = e_j` and set
`H = S^{-1} G^{-1}`. Then

```text
G M H = P(v1,e1) P(v2,e2)
      = [[A,0],[B,1]] [[1,C],[0,D]]
      = [[A,A C],[B,B C+D]]
```

for suitable entries in `R`. Its `(1,2)` entry belongs to `N11 R`, as
required. This argument is the predecessor's criterion, not a new claim
about the alphabet.

## 2. The common row and column criterion

First allow `R = F_1 x ... x F_k`, where each `F_i` is a field containing
the given copy of `K`. An element `A = (A_i)` of `R` is a unit exactly when
every `A_i` is nonzero. Also,

```text
Z in A R  iff  A_i = 0 implies Z_i = 0 for every i.
```

Let `M` be invertible. Its components `M_i` are invertible, and the same is
true of every component of `N = G M H`, for `G,H in GL_2(K)`.
If `N12 in N11 R` and a component `N11_i` were zero, then `N12_i` would
also be zero. That component matrix would have a zero first row, which is
impossible. Thus `N11` is a unit. Conversely, if `N11` is a unit, then
`N12 in N11 R` automatically.

Write `phi` for the first row of `G` and `t` for the first column of `H`.
They are nonzero and

```text
N11_i = phi M_i t.
```

Every nonzero `K` row extends to a basis of the row space, and every nonzero
`K` column extends to a basis of the column space. Thus every such pair
`phi,t` occurs for some `G,H`. The preceding section now proves

```text
cost(M) <= 2  iff  there exist common nonzero K row phi and K column t
                        with phi M_i t != 0 for every i.
```

In particular this holds for `R = K^k`. Invertibility matters: for a
singular component, a zero first row need not give a contradiction, so the
unit-entry reduction above is not asserted for arbitrary targets.

## 3. A constructive three-factor word

Let again `R = F_1 x ... x F_k`, and write an invertible target as

```text
M = [[a,b],[c,d]].
```

The second column `(b_i,d_i)^T` is nonzero in each field component. Define
an allowed coefficient `r in R` componentwise by

```text
r_i = 0 if d_i != 0, and r_i = 1 if d_i = 0.
D = d - r b.
```

If `d_i != 0`, then `D_i = d_i != 0`. If `d_i = 0`, then `b_i != 0` and
`D_i = -b_i != 0`, including in characteristic two. Therefore `D` is a
unit. Put

```text
f = D^{-1} (c - r a),
e = a - b f.
```

Because `R` is commutative,

```text
e D = a(d-rb) - b(c-ra) = ad-bc = det(M).
```

The determinant of `M` and `D` are units, so `e` is a unit as well. Direct
multiplication gives the promised word:

```text
M = [[1,0],[r,1]] [[1,b],[0,D]] [[e,0],[f,1]]
  = P((0,r)^T,e1) P((b,D-1)^T,e2) P((e-1,f)^T,e1).
```

Indeed the right-hand product has entries `e+bf = a`, `b`,
`r(e+bf)+Df = ra+(c-ra) = c`, and `rb+D = d`.
All three factors are invertible, although the paid alphabet does not
require this separately. An identity factor can be omitted, so the result
is a bound of at most three paid factors. No free map is needed for this
construction. The componentwise choice of `r` is placed in a left vector
over `R`; it does not introduce componentwise free maps or right vectors.

## 4. Finite-field threshold and sharp examples

Suppose `K` has `q` elements and `R = K^k`. The projective line `P^1(K)`
has `(q^2-1)/(q-1) = q+1` points: its points are the one-dimensional
subspaces of `K^2`, each with `q-1` nonzero vectors. The dual row space has
the same number of projective points.

Fix any nonzero `t in K^2`. Each `M_i t` is nonzero. Exactly one projective
row `phi` annihilates it, since its annihilator has dimension one. There
are at most `k` forbidden projective rows. If `k <= q`, at least one of the
`q+1` projective rows is not forbidden, and it gives `phi M_i t != 0` for
every component. Section 2 proves `cost(M) <= 2`.

This also gives `cost(M) = delta(M)` in this range. Section 1 decides the
cases `delta <= 1`. If the cost is two, `delta` cannot be at most one, and
the map defining delta has domain `K^2`, so delta is exactly two.

To prove sharpness for every finite field, first construct a quadratic
field extension. There are `q^2` monic quadratic polynomials over `K`.
A reducible monic quadratic is determined uniquely by its unordered pair
of roots, allowing a repeated root. There are

```text
q + q(q-1)/2 = q(q+1)/2
```

such pairs. Thus there are `q(q-1)/2 > 0` irreducible monic quadratics.
Choose one, `h`, and form the field `L = K[X]/(h)`, which has dimension two
over `K`. Fix a `K` basis of `L` and choose a nonzero representative
`alpha_l` of each of its `q+1` one-dimensional `K` subspaces `l`.
Let `A_l in GL_2(K)` be the matrix of multiplication by `alpha_l`.
It is invertible because `alpha_l` is nonzero in a field.

For a fixed nonzero `t in K^2`, let `beta` be the corresponding nonzero
element of `L`. The vectors `A_l t` correspond to `alpha_l beta`.
Multiplication by `beta` is a `K`-linear bijection, so it permutes the
one-dimensional `K` subspaces of `L`. Hence these `q+1` outputs meet every
projective line exactly once. For every nonzero row `phi`, one of the
outputs therefore lies in the line `ker(phi)`.

The target with components `(A_l)_l` has no common pair `phi,t` satisfying
Section 2. It costs more than two. Section 3 supplies a word with at most
three factors, so its cost is exactly three. For any `k > q+1`, append
identity components. The original `q+1` components still prevent a common
pair, and the three-factor construction still applies.

Finally, these examples have `delta = 2`. Delta is at most two because its
defining map has a two-dimensional domain. If delta were at most one,
Section 1 would give a word with at most one paid factor, contradicting
the proved cost of three. This proves the stated threshold with no search
or asymptotic assumption.

## 5. The explicit F2^3 target

Take `h(X) = X^2+X+1` over `F2`, with basis `(1,theta)` of its quotient
field, and use the line representatives `1,theta,1+theta`. The target has
components

```text
M1 = [[1,0],[0,1]],
M2 = [[0,1],[1,1]],
M3 = [[1,1],[1,0]].
```

For each of the three possible nonzero input columns, the outputs are:

| `t` | `M1 t` | `M2 t` | `M3 t` |
|---|---|---|---|
| `(1,0)^T` | `(1,0)^T` | `(0,1)^T` | `(1,1)^T` |
| `(0,1)^T` | `(0,1)^T` | `(1,1)^T` | `(1,0)^T` |
| `(1,1)^T` | `(1,1)^T` | `(1,0)^T` | `(0,1)^T` |

Every row of this table contains every nonzero vector, so each nonzero
row `phi` annihilates at least one output. The target therefore costs
more than two. Here is a three-factor word, written entirely in `R=F2^3`:

```text
zero = (0,0,0),  one = (1,1,1),
r = (0,0,1),    b = (0,1,1),    f = (0,1,0),
M = P((zero,r)^T,e1) P((b,zero)^T,e2) P((zero,f)^T,e1).
```

Its first component is the identity. Its second component is
`[[1,1],[0,1]] [[1,0],[1,1]] = M2`, and its third component is
`[[1,0],[1,1]] [[1,1],[0,1]] = M3`. Thus this target has cost exactly three
and delta exactly two. These identities and the three-line table are
mathematical checks, not claims that a computational replay was run here.

## Scope, credit, and remaining trust

The model and column bound originate in Wentao Li's #4099, building on
#2513; #4243 supplies the diagonal/free-basis development. The general-target
question and earlier noncommutative failures are from #4265. Nick Petalas's
#4276 supplies the retained criteria and the explicit commutative-product
question. Those contributions retain their credit. The scoped deductions
here are the product-field reduction, constructive three-factor bound, and
sharp finite-field component threshold. Projective-line counting, quadratic
extensions, determinant algebra, and rank-one factor manipulations are
classical facts and are not claimed as new general mathematics.

This is a proof in the stated formal alphabet. It assumes that arbitrary
left vectors over the whole product algebra are permitted at one paid
factor and that `GL_2(K)` maps are free anywhere. No physical implementation,
component-selection cost, routing, storage, precision, restoration, native
supplier invoice, or recursive multiplication cost has been supplied;
those costs remain UNKNOWN. The argument does not classify singular targets
or general commutative algebras, and does not change selected kappa.

The proof was prepared with substantial OpenAI Codex assistance, including
separate AI mathematical assessment. It is not independent human acceptance
or formal proof-kernel verification. Finite enumerations, if supplied
elsewhere in this package, remain separate evidence and do not substitute
for the quantified argument above. No source files were changed for it.
