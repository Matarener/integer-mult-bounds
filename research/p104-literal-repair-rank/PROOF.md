# Complete information rank at the literal P104 correction boundary

All ranks are over a characteristic-zero field containing `i`, for example
`Q(i)`. One array has dimension `d` over this field. The physical formulas
are ideal exact operators. No rounded implementation is inferred.

## 1. Credited boundary, new question

Chris R / Clear1nsight's PR3954 supplies the physical encoding and old
correction; unpaidmoon's PR4133 separates their dimension-free commutators.
We retain those operators, including the literal slot exchange:

```
J = I-H,  H^2=H,  T invertible,  K=T^-1,  HT=TH,
P = [ I 0; K I ],       L = [ D HT; 0 I ],
Pi = [ J H; H J ],      A = Pi L.
```

Both banks have dimension `n`. Neither `DT=TD` nor commutation between
different address blocks of T is assumed. The stated compatibility maps
act as identity on every borrowed helper. This is their mathematical
boundary extension, not an implementation of a helper's earlier native path.

The old operation on an encoded input gives `P A x`; the intended encoded
operation gives `A P x`. The existing first-bank defect is `-H K a`, of
rank `h=rank(H)`. The question here is the **complete two-bank** defect,
then the exact amount of linear information needed by an additive repair.

## 2. General rank and kernel

The credited block multiplication gives

```
E = P A - A P = [ -HK                 0  ]
                 [ KJ(D-I)-H         KH ].
```

Let `j=n-h`, and let `B0` be the endomorphism `J(D-I)J` restricted to
`im(J)`. Put `r=rank(B0)`. Then

```
ker(E) = { (a,b) : Ha=Hb=0 and J(D-I)J a=0 },
rank(E) = 2h+r.                                             (1)
```

To prove this, the top equation `HK a=0` gives `Ha=0`, since K is
invertible and commutes with H. Apply H to the bottom equation: its first
term vanishes because `HKJ=0`, and `Ha=0` leaves `KHb=0`. Hence `Hb=0`.
The remaining bottom equation is exactly `KJ(D-I)Ja=0`, equivalent to
`B0 a=0`. Conversely these three conditions make both blocks zero.
The kernel dimension is `(j-r)+j`; subtracting it from `2n` proves (1).
Invertibility of D is unnecessary for this defect statement.

For a one-port check, take `H=T=I` and `D=-I`. Then
`A=[0 1;-1 1]`, `E=[-1 0;-1 1]` and the eventual repair is
`R=[3 -1;1 0]`. The first-bank error has rank one, while E and R-I
have rank two. This is the smallest instance of the two-bank distinction.

This also explains a boundary on the specialization below. If the pivot
block differs from identity by rank one, the complete defect rank increases
by one. A zero first-bank response on a pivot input alone is insufficient.

## 3. Actual P104 specialization

Use the ordered ports J followed by N, with original pivot indices
`(0,1,3,6,22,31,93,103)`, `|J|=8`, `|N|=96`. Here J denotes both the
pivot set and its projection, according to context. PR3954's scalar block is

```
D = [ I8       B       ],       H = diag(0_8,I_96),
    [ B^t    B^t B-I96  ]
D^-1 = [ -11 I8   B   ],        BB^t = 12 I8.
       [   B^t   -I96  ]
```

The checker reconstructs the roots and Gram matrix from the pinned P104
fixture and verifies these premises. Thus `J(D-I)J=0`. For arbitrary
invertible physical T preserving J/N, including the port-dependent native
charts, (1) gives

```
rank(E) = 192d,
ker(E) = { (a_J,0_N,b_J,0_N) },     dim ker(E)=16d.           (2)
```

The 72 unchanged helper arrays add `72d` to the kernel and zero to the
rank: the complete 280-array boundary has kernel dimension `88d`.

A concrete minor makes the lower bound especially transparent. Project
the two output banks onto their N ports and restrict the inputs to their
two N banks. The resulting `192d` square matrix is

```
[ -K_N    0   ]
[  -I    K_N  ].                                            (3)
```

It is invertible. The 16 pivot input arrays are annihilated, establishing
the matching upper bound without any numerical rank tolerance. The lower
pivot output still contains `K_J B a_N`; it is not omitted from the replay.

The kernel in (2) uses the input *before* A. It must not be confused with
the coordinates already stored in the literal encoded banks. For an
encoded input `z=A x`, unchanged P is correct exactly when

```
z_first,N=0,     z_second,N=B^t z_first,J.
```

The second pivot bank and all borrowed helpers are arbitrary. This follows
by applying A to (2). The same conditions hold after P, because its added
term on the N bank is zero on this subspace.

Removing Pi gives the ordered commutator `[-H 0; K(D-I) H]`.
For this D its kernel instead has `a_N=0` and `b_N=-K_N B^t a_J`,
with both pivot inputs free. It has the same rank 192d but a different
kernel. Thus a successful rank comparison alone cannot bind the literal
slot convention; the checker also compares every endpoint coefficient.

## 4. Changed consumer: arbitrary linear summaries

Now allow a much more permissive repair than a uniform bank multiplier.
After the old operation, let `s=P A x`. Require the repaired state to be
`A P x`, with every physical bank and helper returned at this boundary.
Since D is invertible, the unique full-state linear repair is

```
R = A P A^-1 P^-1,
R-I = -E A^-1 P^-1,          rank(R-I)=192d.                 (4)
```

The changed consumer receives an input-independent linear summary `U s`
in `k` arrays, and its *entire additive increment* is a linear function
`V U s`. The unchanged s is retained as the identity passthrough. Thus its
contract is `R(s)=s+VUs`. Rank submultiplicativity and (4) imply

```
192d = rank(R-I) <= rank(U) <= kd,     so k >= 192.          (5)
```

This bound even grants free formation and communication of U and ignores
scratch restoration costs. Requiring a real arbitrary-dirty implementation
cannot weaken it. It is a lower bound on the total linear information
factoring the increment, **not on simultaneous scratch storage**, native
child rank, scalar operations or native calls. Streaming with repeated
reads, a changed producer, changed output equivalence, or nonlinear coding
needs its own model. There is no claim that an arbitrary in-place algorithm
needs 192 live scratch arrays.

The information bound is sharp algebraically. Write the two current banks
as `(r,w)`, and form exactly two 96-array summaries

```
v = r_N,                  e = w_N-B^t r_J,
u = (K_N+T_N)v-e.
```

Then the complete repair is

```
r'_J = r_J,
r'_N = r_N + K_N u,
w'_J = w_J - K_J B u,
w'_N = w_N + u-K_N v,                                  (6)
helpers' = helpers.
```

Indeed, set `(a,b)=A^-1 P^-1(r,w)`. Direct inversion using the displayed
D^-1 gives `a_N=u` and `b_N=v`. The complete defect on these coordinates
is `(-K_N u, K_J B u, -u+K_N v)` on the respective nonzero output blocks.
Subtracting it proves (6). Operator order is retained throughout; in
particular `K_J B` is not changed to `B K_N`. Both summaries can range
independently over all 192 arrays (set `r_J=0`), and the increment map in
(6) is injective on them, consistent with (5).

Equations (4)--(6) are a factorization of a uniquely forced map, not an
affordable physical implementation. A borrowed summary register starts
with independent dirt eta: replacing `Us` by `Us+eta` adds `V eta`.
Here V is injective, so nonzero eta necessarily contaminates the endpoint.
Any dirty echo or cleanup must cancel that contribution and be priced.
The 72 existing helpers are untouched in (6), but they do not automatically
provide 192 clean summaries. No clean-scratch hypothesis is hidden in the
claim of arbitrary dirty *existing-helper* restoration.

## 5. Complete finite scope

The retained physical port label p has chart
`T_p=((1+i)I+(1-i)X_p)/2`. In the character basis its eigenvalue is
`i^(ell.p)` and K's is `i^(-ell.p)`. For a fixed nonzero row-fiber label q
in the 81-bit tensor address, the chart labels are `p tensor q`. Contraction
of a tensor character with q maps onto every `ell in F2^9`, each with
`2^72` preimages. To see surjectivity, choose a coordinate where q is one
and place ell in that column, with all other columns zero.

The checker therefore covers all distinct address-character blocks of one
full physical row fiber by the 512 nine-bit ell values, without materializing
`2^81` addresses. For each value it literally composes `P A` and `A P` on
all 208 data and 72 dirty basis inputs and applies (6) to the former. Basis
values are scaled by four to keep this exact finite calculation in Gaussian
integers; no rounding occurs. The written linear proof covers arbitrary
payloads, all address dimensions and arbitrary invertible T satisfying the
stated premise. It is not an inference from finitely many sampled payloads.

`algebra.py` imports no main checker. Dense rational multiplication and
Gaussian elimination test (1) for all 512 binary 3-by-3 D matrices and
all four coordinate projections H. A two-dimensional address fixture has
noncommuting T blocks and `DT != TD`; the literal defect and the full repair
both have rank eight. Altering one pivot entry raises the rank to nine.
Dropping `HT=TH` invalidates the simplified literal formula; dropping
idempotence invalidates the slot involution. These are corroborating finite
checks of the written proof, not independent human or formal-kernel review.

## 6. Cost decision

The complete boundary obligations are explicit:

| Obligation | Status |
| --- | --- |
| Literal action on both banks, including pivot outputs | Proved by (1)--(6); exact finite replay |
| Identity on 72 independently dirty existing helpers | Proved for this boundary extension and replayed |
| Minimum information for the linear-summary increment | Exactly 192 arrays in the relaxed algebraic model |
| Summary formation, a chronological producer and legal chart access | Unknown physical implementation |
| New scratch initialization, dirty compensation and eventual restoration | Unknown physical implementation |
| Native chart conversions, owners, scalar passes, routing, storage, precision | Additional unpriced obligations |
| Complete supplier moment and all-size admission | Not supplied |

The inherited PR3954 scaffold already fails its favorable rank-mass gate
by 44,096 before extra boundary costs; that predecessor rejection is not
new evidence here. We make no recursive invoice edit, so the signed-invoice
preflight has no new pair of complete invoices to compare. In particular,
192 information arrays cannot be entered as 192 native tariff units.
Stop after the information obligation. A future changed producer/consumer
must supply a new favorable complete bill before construction expansion.
