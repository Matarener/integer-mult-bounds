# A chronological lower bound for star connectors

This is a finite-matrix theorem in characteristic two. It rules out the
31-leaf, five-rank-two target from PR5673 and the static maps in PR5681.
It does not rule out a different stage frame or a general native caller.
No new kappa is established.

## 1. Contract and statement

Use the full star contract of PR5673. The core and each of the g leaves
have dimension d. A stage j has orthogonal projectors P_jh which resolve
its core-plus-leaf support E_j. They commute with

```text
T_j = [[I,I],[I,I]].
```

The full call is `(I+x_j P_jh)(I+e R_jh)`, where `R_jh=P_jh T_j`,
`x_j=D_j+1`, and `e^2=0`. Thin calls are `I+e Z`. All x_j are independent.
The target is `(I+e I) product_j (I+x_j E_j)`. Thin maps can be arbitrary;
the proof needs no bound on their number and no square-zero condition.

The local form is

```text
P_jh = [[A_jh+B_jh,B_jh],[B_jh,A_jh+B_jh]],
R_jh = [[A_jh,A_jh],[A_jh,A_jh]].
```

Within a stage, the A_jh are orthogonal idempotents which resolve I.
Suppose every nonzero A_jh has rank at least r, and put
`L=floor(d/r)+1`. Let V be the span of all thin row spaces, and U the
span of all thin image spaces. For g>=3, write

```text
dim V = 2d+b,    dim U = 2d+a.
```

**Theorem.** Every successful word satisfies

```text
g <= L b+2,       g <= L a+2,
sum_thin rank Z >= 2d + 2 ceil((g-2)/L).                         (1)
```

This holds over every field of characteristic two. It does not use a finite
field count. For two equal query halves per stage, d=2q and r=q, so L=3.
Thus the extra row and image dimensions must each grow at least as
`ceil((g-2)/3)`. A large number of distinct static signatures is not enough.

## 2. The exact chronology relation

The coefficient of e gives `sum_full R + sum_thin Z = I`. The coefficient
of e*x_j then gives the necessary relation

```text
sum_(i in stage j) [P_i, sum_(l after i) R_l] = 0.               (2)
```

Here the sum includes full and thin queries. This is a necessary coefficient
of the literal ordered word, not an endpoint converse. The retained source
and PR5681 give separate derivations of (2).

For j!=k, let

```text
S_jk = sum_(jh before kl) A_jh A_kl.
```

In (2), add block rows core and j and read column block k. A later full
call in stage k contributes `A_jh A_kl`. Other full stages contribute zero.
A later thin map contributes `A_jh (Z_0k+Z_jk)`.

The thin sum is `K=I+sum T_j`. Its rank is 2d. Its row space is the core
plus the leaf-sum space; its image is the core plus the diagonal leaf space.
Choose b further row vectors which extend the row space of K to V. Let
M_k be their b-by-d restriction to leaf k. Every thin block column can be
written as a term constant in k plus a matrix times M_k. Therefore (2) gives
matrices L_j and C_j such that

```text
S_jk = L_j + C_j M_k,                  k!=j.                    (3)
```

For a particular full call A=A_jh, let P_k be the sum of the A projections
in stage k before that call. Orthogonality within stage j gives
`A S_jk=A(I+P_k)`. Multiply (3) by A and absorb its constant term. For each
call there are matrices H and C with

```text
A P_k = H+C M_k for every k!=j,        A P_j=0.                 (4)
```

This statement remains valid after selection of any subset of leaves.
Use the induced call order and omit the other stages. A removed stage has
no contribution to S_jk for retained j,k. This restriction property is
essential to the proof below.

## 3. A dimension drop forced by the first calls

For a nonempty leaf set J, define h(J) as the dimension of the span of
all columns of `M_k-M_l`, for k,l in J. This span is a subspace of F^b.
It is not the dimension of the vectorized matrix differences. Choose one
leaf as a reference and a basis for that column span. After absorption of
the reference matrix into H, equation (4) has signatures with h(J) rows.

Read the full calls on J in their induced order. Let `S=sum_(k in J) P_k`
be the total prefix. If `A S=0` at each of the first L calls, then

```text
(I+xA)(I+xS) = I+x(S+A)
```

at each step, for an independent central variable x. The product of the
first L factors is `I+xS_L`. Its determinant has degree at most d.
Each A is idempotent, so `det(I+xA)=(1+x)^rank(A)`. The product determinant
has degree at least L*r>d. This is impossible. Consequently one of these
first L calls has `A S!=0`.

Let U be the leaves not yet called at that point, after exclusion of the
current stage. At most L leaves have been removed from J. If U is nonempty,
choose u in U. For every k in U, `P_k=0`, so (4) gives

```text
H=-C M_u,          C(M_k-M_u)=0.
```

The map C cannot vanish on the column-difference span of J. If it did,
(4) would give `A P_k=0` for every k!=j; the own-stage product is also zero.
That would give `A S=0`. Thus C is nonzero on that span, but it kills the
column-difference span of U. We have proved

```text
|J minus U| <= L,             h(U) <= h(J)-1.                  (5)
```

Only the stage ranks and equation (4) were used. No connector placement,
matrix-size search, or pure higher stage coefficient was assumed.

## 4. Induction and the paid-rank bound

If h(J)=0, all signatures on J are equal. The one-sided theorem from
PR5673 gives |J|<=2. Its short proof also follows from (4): for any three
stages, `A P_k=A P_l` at every update, so `A S=0`. At the end S=I in
characteristic two. The determinant would be both `(1+x)^(3d)` and
`(1+x)^d`, which is impossible.

We now prove `|J|<=L h(J)+2` by induction on h(J). If |J|<=L+2 and h(J)>0,
the bound holds. Otherwise (5) supplies a nonempty U. Equation (4) is
preserved on U, and the induction hypothesis gives

```text
|J| <= L+|U| <= L+L(h(J)-1)+2 = L h(J)+2.
```

For the full leaf set, h(J)<=b. This proves the row-space bound in (1).
Transpose every matrix and reverse the complete word for the image-space
bound. The target is unchanged, since its full stage supports commute.

Factor each thin map at its rank and concatenate the factors. If R is the
sum of those ranks, Sylvester's inequality gives

```text
rank K >= dim U+dim V-R,
R >= 2d+a+b.
```

Combining the two dimension bounds proves (1).

## 5. The two previously open targets

For g=31 and q=2, d=4 and L=3. Equation (1) gives a>=10, b>=10 and
**R>=28**. Five rank-two thin connectors have R=10. Thus no choice of their
matrices, call order, or compatible paired stage projections can give the
required endpoint. The PR5681 static maps remain valid static maps; they
cannot be completed to this chronological word.

Allowing arbitrarily many nonzero stage splits does not repair this target.
At d=4, every nonzero query has rank at least one, so L<=5. Even this weaker
contract requires `R>=8+2 ceil(29/5)=20`, still more than ten. The bound 28
uses the requested paired rank-two full queries; the bound 20 does not.

For g=127 and q=1, the bound is a,b>=42 and **R>=88**, instead of the ten
rank-one connectors in the earlier target. It is excluded for the same reason.

For g=31 with five rank-q connectors, the necessary inequality is
`5q>=4q+20`, or q>=20. A paired-port block with q=26 divides the 104 native
ports and passes this new necessary test. It still has no supplied word.
The q=8, g=13, five-rank-eight target also passes. Passing (1) is not a
construction and does not supply a native lift.

## 6. Scope and attribution

The result concerns independent stage variables, the fixed star support,
full orthogonal stage resolutions, the stated query map, and the exact
normalized target. Nonfull stages, paid idle stage maps, different graph
frames, and general complex or dyadic callers are outside this proof.
Arbitrary thin maps are included. Square-zero thin maps are a special case.

The argument uses elementary determinant degree, subspace dimension and
Sylvester rank. The new step is the recursive restriction in (5). It changes
the old logarithmic static signature bound into a linear chronological bound.
The exact tariff consequence is in COST.md. Finite checks support the written
proof; they do not constitute human review or proof-assistant acceptance.

Credit PR5673 for the one-sided proof and rank framework, PR5681 for the
static witnesses and separate coefficient audit, Cinna Davis for the
controller/simplex source, and the retained P104/helper/native/compiler line.
Prepared by Ali Romman with substantial OpenAI Codex assistance; no subagents.
Apache-2.0.
