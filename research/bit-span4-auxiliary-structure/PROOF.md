# Span four with dirty auxiliary registers

## Statement

Work in the abelian rank-one model of
[`research/bit-dirty-auxiliary-registers`](../bit-dirty-auxiliary-registers/README.md) §1.
The address group is `(M_3(Q), +)`. There are three data registers and any number
of dirty auxiliary scalar registers. A paid call is `D_N([A]) = I + ([A] - 1)N`
with `rank_Q A = 1` and `N = xy^T` a binary rank-one idempotent. A word succeeds
when the product is diagonal, the three data endpoints are invertible, and the
auxiliary endpoints are arbitrary. Exact restoration is allowed. Clean
zero-initialized ancillas are not in this statement.

Let `s` be the number of nonzero paid calls and let `d` be the rational dimension
of their frames.

**Proposition.** Suppose `d = 4`.

1. If the normalized generator below has every coordinate of both vectors nonzero,
   then `s ≥ 9`.
2. Otherwise a simultaneous row and column permutation makes the span
   block-upper-triangular, with diagonal address blocks of sizes `1+1+1` or `1+2`.
   The `1+1+1` partition needs `s ≥ 9`. The `1+2` partition needs `s ≥ 8`, and
   equality holds only when the `1×1` block uses exactly three calls, the `2×2`
   block uses exactly five calls, no call is strictly block-upper, and the
   projected `2×2` word has frame span exactly 3.
3. Every successful span-four word with `s < 8` is impossible. An eight-call
   span-four word can exist only in the `1+2` shape of (2). No such word is
   constructed or excluded here.

Spans 5 and 6 at eight calls stay open. Nothing here changes κ or the selected
record. The selected value remains `0.001672660197076918`.

## Cited dependencies

These are not re-proved.

- **Lemma 1 and its corollary**, dirty-auxiliary README §2, for any register
  count. At most one integral relation among the frames gives disjoint subset
  sums for the diagonal endpoints, and therefore
  `rank C_0 + rank C_1 + rank C_2 ≤ s`. Invertible `m×m` targets force `s ≥ mW`.
- **Lemma 2**, dirty-auxiliary README §3, for any register count. Frame span at
  most `m` forces `s ≥ mW`.
- Together, a successful word with `s < mW` has `m+1 ≤ d ≤ s-2`. For
  `(m, W, s) = (3, 3, 8)` the only surviving dimensions are 4, 5 and 6. That is
  the handoff in dirty-auxiliary README §6.
- The three-register span-four normalization in
  [`research/bit-three-register-lower-bound`](../bit-three-register-lower-bound/README.md) §3
  and [`research/three-register-no-target-flag`](../three-register-no-target-flag/README.md) §6.
  Section 6 of the no-target-flag note then prices a `2×2` block at six calls by
  its §5. That section is stated for exactly three scalar registers. This note
  does not import that six-call step. Open PR #3537 prices nine coordinate
  projectors beside one idle dirty auxiliary and leaves general spans 4, 5 and 6
  open. The argument below is the general span-four case, for any number of
  dirty auxiliaries.

`verify.py` checks the arithmetic consequence of the two cited lemmas: the only
pair `(s, d)` with `m = 2`, `W = 3` and `s < 6` that they do not exclude is
`(s, d) = (5, 3)`.

## Normalization

The determinant of `Σ_{i=1}^3 a_i u_i v_i^T` equals `(Π a_i) det(U) det(V)`,
where the columns of `U` and `V` are the `u_i` and `v_i`. A sum of two rank-one
`3×3` matrices has determinant 0. Consequently, on any span of rank-one matrices,
the cubic `det(Σ x_j B_j)` has no term `x_i^3` or `x_i^2 x_j`: each such term is
the determinant of a combination of at most two rank-one matrices. The cubic is
the sum of its square-free triple coefficients. An invertible matrix in the span
produces a nonzero triple. The corresponding left vectors are independent, and so
are the right vectors, because that coefficient is `det(U) det(V)`.

After those two changes of basis the three rank-one matrices are `E_00`, `E_11`
and `E_22`. At dimension exactly 4 the fourth basis matrix is `B = uv^T`, and
the span is

```text
{ D + t uv^T : D diagonal, t rational }.
```

The verifier expands these identities over `Z`. It also checks the minor formula
used next: the minor of `D + t uv^T` on rows `(i, k)` and columns `(i, l)`, for
distinct `i, k, l`, equals `D_ii t u_k v_l`. The quadratic terms cancel.

## Full support

Suppose every coordinate of `u` and of `v` is nonzero. For `t ≠ 0`, the minor
formula forces every diagonal entry of `D` to vanish whenever the matrix is
rank one. Every paid frame therefore lies on one of the four lines `E_00`,
`E_11`, `E_22` and `uv^T`. Those four matrices are linearly independent, so the
line coordinates of a frame are unique. The verifier checks this for
`u = v = (1, 1, 1)` and checks that every pair of the four lines is singular,
while `E_00 + E_11 + E_22 = I`.

An invertible target is a sum of its four line coefficients. At most two nonzero
coefficients would make it a sum of two rank-one matrices, hence singular. Each
invertible target uses at least three lines.

Projection onto one line's coefficient is a homomorphism from the additive group
of the span to `(Q, +)`. Subset sums of frames remain in the span, so the
homomorphism sends the group algebra of the word to a group algebra `F_2[H]`
with `H ⊆ (Q, +)` torsion-free. A factor whose frame lies on another line maps
to `I`. A product of the `q` surviving factors has the form `I + XTY^T` with `T`
of size `q`. The two-factor identity

```text
(I + a xy^T)(I + b uv^T) = I + [x u] [[a, ab (y·u)], [0, b]] [y v]^T
```

and the inductive step that absorbs one more rank-one update are polynomial
identities over `Z`. They hold in the group algebra. Every `(q+1)×(q+1)` minor
of `XTY^T` vanishes, so the update has rank at most `q` over the fraction field.
The same domain property used in Lemma 1 makes `F_2[H]` a domain. The projected
endpoint is diagonal. Each data target with a nonzero coefficient on the line
contributes a nonzero diagonal entry `g - 1`. The principal minor on those data
coordinates is a product of nonzero elements, hence nonzero, whether or not an
auxiliary coefficient is nonzero. Thus `q` is at least the number of data targets
that use the line.

Summing over the four lines counts at least three uses per target. The verifier
enumerates the `4^3` ways to give each of three targets three or four lines; the
minimum total is 9. Therefore `s ≥ 9`.

## A zero coordinate

Now suppose some coordinate of `u` or of `v` is zero. In the directed graph of
`B = uv^T` there is an edge `i → j` exactly when `u_i` and `v_j` are nonzero.
Every vertex of a directed cycle lies in `supp(u) ∩ supp(v)`. A vertex outside
that intersection has no self-loop and is missing either all outgoing edges or
all incoming edges, so it is a trivial strong component. The verifier checks all
64 zero-patterns on three coordinates: full support is the single pattern with
one component of size 3, and every other pattern has strong components of size
at most 2. A topological order of the components is a simultaneous row and
column permutation making `B` block-upper-triangular. Diagonal matrices stay
block-diagonal under that permutation, so the whole span is block-upper-triangular.
The only possible diagonal block sizes on three coordinates are `1+1+1` and `1+2`.

For a block-upper-triangular matrix the determinant is the product of the
diagonal-block determinants. The verifier checks the `1+2` and `1+1+1` shapes.
An invertible target therefore has invertible diagonal blocks.

A rank-one matrix `xy^T` that is block-upper-triangular has at most one nonzero
diagonal block. If two diagonal blocks were nonzero, the later block would meet
`supp(x)` and the earlier block would meet `supp(y)`, so the strictly lower
block `x_later y_earlier^T` would be nonzero. The verifier checks this
implication on every ordered partition of `{0,1,2}` and every zero-pattern.
Paid frames lie in the span, so they are block-upper-triangular, and the calls
with a nonzero diagonal block partition across the blocks. A strictly
block-upper call projects to zero on every diagonal block.

Block projection is an additive map on address space, so it induces a ring
homomorphism of the group algebra. It sends `D_N([A])` to `D_N([π(A)])` with the
same register idempotent `N`. A zero projection deletes the call. A nonzero
projection of a rank-one block-upper-triangular matrix is rank one. The image of
a successful word is a successful word for the projected invertible targets, in
the same dirty-auxiliary model, at address size 1 or 2.

A `1×1` block has frame span at most 1. Lemma 2 with `(m, W) = (1, 3)` gives at
least three calls. Three blocks of size 1 are disjoint and need at least nine
calls.

A `2×2` block is a word for three invertible `2×2` targets. Lemma 2 excludes
span at most 2 unless there are at least six calls. The corollary of Lemma 1
excludes relation rank at most 1 unless there are at least six calls. The only
remaining possibility with fewer than six calls is exactly five calls and frame
span exactly 3. In particular the block uses at least five calls. At five calls
the projected generator on that block is nonzero and is not diagonal: otherwise
the projected span would have dimension at most 2.

The `1×1` calls, the `2×2` calls and the strictly upper calls are disjoint. For
total length 8 the only solution of `s_1 ≥ 3`, `s_2 ≥ 5` and `s_2 = 5` or
`s_2 ≥ 6` is `s_1 = 3`, `s_2 = 5`, `s_upper = 0`. Every shorter total has no
solution. That is the equality case in the proposition. The five-call `2×2`
word is not ruled out by Lemmas 1 and 2, and the three-register six-call
argument does not apply once an auxiliary register is present.

## Why a degree-1 count does not close the gap

A cancelling pair `D_N([B]) D_N([-B])` equals `I` whenever `N` is idempotent,
because `(I + (g - 1)N)(I + (g^{-1} - 1)N) = I`. The two frames sum to 0, so the
pair does not change the degree-1 tensor `Σ frame ⊗ projector`. The verifier
checks this for a non-coordinate idempotent and checks the characteristic-2
splitting identity `D_N([A/2])^2 = D_N([A])`. Padding three coordinate calls by
such a pair preserves both the diagonal endpoint and the degree-1 sum, while the
length grows from 3 to 5. Those three targets are rank one, so this is not a
successful invertible word. It shows that a degree-1 balance against a diagonal
endpoint does not forbid five calls. The open case needs a two-relation argument
or a genuine normal-form search, not a degree-1 enumeration.

## Nine calls still suffice

Nine coordinate-projector calls realize three invertible targets and restore one
auxiliary. For

```text
C0 = I,
C1 = [[1, 0, 0], [1, 1, 0], [0, 0, 1]],
C2 = [[1, 0, 0], [0, 1, 0], [0, 1, 1]],
```

each column frame `(C e_r) e_r^T` is placed on projector `E_ww` of its data
register. The frames on a register sum to that target, and the formal product in
`F_2[(M_3(Q), +)]` equals `diag([C0], [C1], [C2], 1)`. Deleting any one of the
nine factors, or changing one entry of the first frame, breaks the equality.
This shows that nine calls are achievable in the model with a restored dirty
auxiliary. It is the coordinate-projector construction already distinguished
from the general span-four question. It does not produce a span-four word, and
it does not decide the remaining `1+2` case.

## What was not run

No enumeration of the 120 four-register idempotents at length five or eight.
No replay of the three-register census. No proof-assistant check. The polynomial
checks are identities and exhaustive pattern checks; they are not a substitute
for the cited lemmas.
