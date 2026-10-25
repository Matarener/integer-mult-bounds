# Exact boundaries of the unary endpoint-debt argument

The dressed current-cut swap below disproves one proposed absorption step.
The chirped common-axis map disproves restricting all legal insertions to
orthogonal address maps. Neither contradicts the corrected unary
endpoint-debt theorem: that theorem uses exact telescoping and row support,
and permits the insertions exhibited here. A separate paired-decoder witness
shows why a valid finite operator identity cannot be assigned a constant
four-translation implementation at every chunk size.

The scientific snapshot is `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.
Original sources and notices are retained unchanged under `frozen/`;
`ORIGINS.json` gives exact byte pins and provenance. The insertion construction
comes from the historical complex lane; the paired complementary-vacancy
proposal and exact group-algebra decoder come from the historical algebra
lane, with the tensor-cost correction independently identified by the
recursive/complex lanes. The present portable audit, full-column controls,
generic normalization correction, and proof were prepared with substantial
OpenAI Codex assistance. Apache-2.0.

## 1. Exact operators and current-cut convention

Values are arbitrary complex arrays; all coefficients in the finite witnesses
are Gaussian dyadic rationals. For a nonzero binary direction a, let

```
C_a = ((1+i) I + (1-i) X_a)/2,
C_a^-1 = ((1-i) I + (1+i) X_a)/2,
C_a^2 = X_a,
```

where `X_a |x> = |x+a>` and addition of addresses is over GF(2). These are
actual phase-bearing operators, not their unsigned symplectic images.
The program's `A.then(B)` means matrix product `B A`.

Use four orthogonal address directions p,q,u,v, encoded as 1,2,4,8. The
first two form the common plane; u is a completed fresh direction and v an
uncompleted future direction. Put

```
G_past = C_u,
D_X = C_p G_past,        D_Y = C_q G_past,
K = D_Y D_X^-1 = C_q C_p^-1.
```

The common logical insertion corresponding to physical X-side monomial M is

```
H = D_X^-1 M D_X.
```

Its two physical pullbacks are exactly M and `K M K^-1`. It is admitted at
both cuts when both are monomial. The condition is on these actual products,
including their phases. It does not require H itself to be monomial in the
bare computational frame.

## 2. A nonorthogonal common-axis monomial

On p,q use address matrix and chirp matrix

```
G = [[0,1],[1,1]],       Q = [[1,1],[1,0]].
```

Both act as the identity on the fresh address coordinates except that Q is
zero there. Let `P_G |x> = |Gx>` and

```
D_Q |x> = i^(x_p + 2 x_p x_q) |x>,
M = D_Q P_G.
```

The matrix G has order three and is not orthogonal. Direct exact conjugation
by K gives a monomial. With the common two-bit input listed as 0,1,2,3, the
complete action is

| Input | M output | `K M K^-1` output |
| --- | --- | --- |
| 0 | `|0>` | `|3>` |
| 1 | `|2>` | `-i |0>` |
| 2 | `-i |3>` | `|2>` |
| 3 | `i |1>` | `i |1>` |

The fresh two bits are unchanged. Thus the table proves the one-column
phase identity on every basis vector; tensoring proves it for every chunk
parameter f and embedding it by identity preserves it on additional axes.
The checker reconstructs the literal products and tests all 16 columns,
both cut pullbacks, and every emitted native lowering. It also independently
evaluates every literal Gaussian gate rather than accepting a tableau alone.

Omitting the actual quadratic chirp leaves `P_G` on the X side but gives
native rank two on the Y side. Its zero-input column has four nonzero entries.
This is an executed monomial-admission failure. Consequently legality is not
equivalent to choosing an orthogonal common-plane address permutation, and
the chirp cannot be dropped from the physical bill.

## 3. Past/future transfer within the common intersection

Let S exchange fresh physical axes u and v, fixing p and q. It commutes
with K. The logical dressed insertion

```
H_swap = D_X^-1 S D_X = C_u^-1 S C_u
```

therefore has exact physical pullback S on both banks. There is no residual
global phase. In the Pauli convention `i^t X^x Z^z`, the completed-past
direction is the actual Hermitian operator

```
C_u^-1 Z_u C_u = i X_u Z_u.
```

Conjugation gives the phase-exact identities

```
H_swap (i X_u Z_u) H_swap^-1 = Z_v,
H_swap Z_v H_swap^-1 = i X_u Z_u.
```

Indeed the central `C_u C_u^-1` factors cancel; S exchanges `Z_u` and
`Z_v`, and `C_u` commutes with `Z_v`. The fresh portion of the common cut
Lagrangian is spanned by these two directions. Its whole space is preserved,
but its past and future summands are exchanged. In the minimal four-axis
example this is the entire dimension-two intersection; extra fresh axes add
identity spectators.

This invalidates the inference "preservation of the common intersection
forces every completed-past leakage component to remain in the past." It
does not produce an improved D4 endpoint, and does not invalidate a bound
proved without that inference. In particular, the companion endpoint-debt
proof retains every physical monomial between consecutive rank-limited
factors, without moving a monomial through a fresh Fourier factor. Its
row-support argument explicitly permits this swap.

Using the undressed logical S at this cut is a different operation: its X
pullback `D_X S D_X^-1` has native rank two. This is also an executed defect.
Replacing the inverse past C gate by its positive version changes the
actual pullback. A global i mutation preserves the complete signed tableau
but changes both exact pullbacks, and is rejected on ordinary address
columns. These controls distinguish phase-correct dressing from binary
containment or rank alone.

## 4. Native-zero operations have a paid array implementation

The inserted logical H expressions describe which physical operators to
execute at the current cut. The actual operations are the physical M on X
and `K M K^-1` on Y, or the fresh swap S on both; executing all the displayed
logical dressing C gates is not the proposed implementation.

For f tensor columns these physical monomials act on N=`2^(4f)` array
entries. Their addresses and phases are explicit functions of 4f address
bits. The common-axis address permutations have order three, with exactly
`2^(2f)` fixed addresses, including the affine permutation on the Y side.
They therefore have `(N-2^(2f))/3` cycles of length three. The fresh swap has
`2^(3f)` fixed addresses and `(N-2^(3f))/2` cycles of length two.

One concrete in-place array realization enumerates addresses, acts only on
the least address in each cycle, and realizes an l-cycle with l-1 raw value
swaps. A raw swap can be implemented by three signed unit ADDs and one
negation. The common-axis permutation consequently needs
`2*(N-2^(2f))/3` raw swaps; the fresh permutation needs
`(N-2^(3f))/2`. A separate phase pass multiplies each entry by its explicitly
computed unit in `{1,i,-1,-i}`. With arbitrary indexed cell access, the
cycle discovery uses O(f N) binary arithmetic and O(f) control storage,
because each cycle has length at most three. This is a paid array recipe,
not a physical finite-tape or head-return implementation. Cell routing and
the field's real/imaginary primitive lowering remain charged by the caller.
No ordinary or private auxiliary array is introduced.

Thus native rank zero means absence of a positive-rank native child in these
physical insertions. It does not mean free permutations, phases, address
arithmetic, or complete-field scans.

## 5. The paired decoder as an arbitrary-input identity

First give the correct general algebra. Let A be any invertible operator and
assume its square is a monomial admitted by the chosen alphabet. Put B=A^-1.
Starting with `(A u,A v)`, normalize the second field by `(A^2)^-1`, giving
`(A u,B v)`. Then execute

```
(x,y) <- (-y,x),
x <- x + B y,
y <- y - A x,
x <- x + B y.
```

After the signed exchange the pair is `(-Bv,Au)`. The three shears give
successively `(u-Bv,Au)`, `(u-Bv,v)`, and `(u,v)`. This is an all-input
operator identity. It uses no commutation between A and unrelated operators,
and no clean or zero promise for either original field.

The unqualified historical sentence "apply A^2 to the second field" needs
the further premise `A^4=I`. The original finite vacancy below has that
premise, so its finite tests remain valid. For arbitrary A with monomial
square, the inverse-square normalization is the correct general statement.
The historical normalization gives `(u,A^4 v)` in general, as direct
substitution into the same three shears shows.
The frozen original sentence is retained as provenance rather than silently
edited.

A cheap exact counterexample makes this distinction substantive. Take
A=`P_G` for the order-three GL(2,2) address matrix above, now acting on a
four-entry field without the chirp. A and A^2 are monomial, but A^2 is not
an involution. The historical normalization followed by the stated decoder
produces `(u,A v)`; inverse-square normalization produces `(u,v)`. Both are
computed on all eight independent ordinary input columns. No improved paid
implementation follows merely from the corrected algebra.

The signed exchange itself has the literal lowering

```
x <- x-y;    y <- y+x;    x <- x-y,
```

which gives `(-y_old,x_old)` in three signed unit ADDs. This is distinct from
a raw unsigned field swap. It uses no extra field and is freshly executed
as part of every finite decoder replay. The historical cost wording is
preserved; the new receipt states only the actual three-ADD lowering.

## 6. Why four translations do not remain four at general f

For f independent address-column pairs define

```
A_f = tensor_(j=1..f) (C_(q_j)^-1 C_(r_j)^-1),
B_f = A_f^-1.
```

The 2f directions are independent. Here
`A_f^2=X_(sum_j(q_j+r_j))` is an involutory translation, so the original
second-field normalization does equal its inverse. At f=1,

```
A_1 = (-i I + X_q + X_r + i X_(q+r))/2,
B_1 = ( i I + X_q + X_r - i X_(q+r))/2.
```

Every one of the four coefficients is nonzero with modulus 1/2. In the f-fold
tensor expansion, each choice of one term per tensor column has a distinct
translation address, since all 2f directions are independent. Its coefficient
is a product of nonzero Gaussian dyadics, hence is a nonzero unit times
`2^-f`. There are exactly `4^f` choices, with no collisions or cancellation.
The translations are linearly independent in their regular action: applying
their sum to the zero-address basis vector exposes every coefficient in a
different row. Thus no representation by only four translations can equal
this kernel when f>1. Its coefficient absolute sum is exactly `2^f`.

The three shears in this direct expansion require `3*4^f` weighted complex
translation ADDs, besides the three signed unit ADDs for the exchange and
the second-field normalization. One fully explicit source preparation uses
`X_w`, performs the weighted ADD, and restores with `X_w` for each nonzero
translation w. This adds `6*(4^f-1)` source permutation scans and one initial
second-field translation scan. These are counts within that specified
array/ADD expansion, not a complete physical instruction or precision bill.
Dyadic coefficient lowering, real/imaginary phases, actual scans and address
access are all separately paid. The growing coefficient absolute sum is
not by itself a rounded-error theorem.

The new checker executes the complete two-field word at f=1,2,3 on 8,32,128
independent ordinary columns respectively. It compares every retained
historical finite-case field, including kernels and final operator rows.
The fresh endpoint calculation uses literal three-ADD exchange and sparse
Gaussian matrices. Omitting normalization, exchange, or any of the three
operator shears fails the same all-column endpoint predicate. Replacing B_2
by the four-term B_1 embedded in the first two axes also fails that predicate,
with an actual address-column discrepancy.

This support theorem is confined to the direct translation expansion of
this two-coordinate vacancy. It is not a general circuit complexity lower
bound, a decoder for every D4 endpoint, or a proof that all alternative
factorizations are expensive. Sequential tensor-factor algorithms, native
operator calls, other bank topologies, and joint precision/stock bills need
their own all-size implementation and costs.

## 7. Reproduction and acceptance controls

Use an absolute, nonexistent output path outside the package and any
overridden input directory:

```
python3 -I -B check.py --output /absolute/external/new-checks.json
python3 -I -O -B check.py --output /absolute/external/new-optimized.json
```

The optional `.gz` output uses a deterministic gzip timestamp. Every listed
input is captured once and authenticated before use. The compiler and
retained pair-decoder module are executed from those captured buffers with
`optimize=0`; no bytecode cache, ambient Git query, or path module loader is
used. The old insertion main is reconstructed by the fresh audit; its named
lowering/event fields are reconciled with the preserved receipt. The old
pair main is not invoked: its original `vacancy` and `witness` functions,
including all their mathematical predicates, execute at f=1,2,3 and their
complete finite-case outputs are compared. Historical prose and unrelated
claims are not turned into fresh evidence.

The receipt stores complete signed tableaus, literal circuits, lowerings,
and all 16 independently evaluated ordinary columns for eleven n=4 operators;
the exact transported Pauli; all three finite pair kernels and complete
endpoint matrices; the non-involutory counterexample; and all controls.
Each of the 22 semantic defects must fail at its intended named production
predicate with a concrete discrepancy. The identical candidate then runs
with only that predicate disabled, outside the rejection catch, and must
be accepted. Global i defects specifically survive signed-tableau equality
but fail the phase-sensitive all-column comparison. The normal and optimized
receipts must match completely.

No 51-by-51 or 101-by-101 nominee search is repeated. Radical and P112 cautions
are not imported because they are unnecessary to this corrected theorem
boundary and their separate source obligations are not part of this closure.
Finite exhaustive checks, the written all-f tensor argument, native/physical
implementation admission, and the companion endpoint theorem remain distinct.
