# A connector must distinguish leaves in both directions

This is a theorem about finite matrices in characteristic two. It is not a
native multiplication theorem. No new kappa is established.

## 1. Contract

Let the main space be `W_0 + W_1 + ... + W_g`, with each block of dimension
`d > 0`. Block zero is the core. Stage j acts on the core and leaf j. On these
two blocks put

```text
E_j = diag(I,I),                 T_j = [[I,I],[I,I]].
```

Thus `T_j^2=0`. Stage j can have any finite number of full calls. Their
projectors `P_jh` form an orthogonal resolution of `E_j`, and commute with
`T_j`. Their query maps are `R_jh=P_jh T_j`. There is no bound on the number
of stages, the number of splits, the block dimension, or their call order.

In the normalized ring `F[e,D_1,...,D_g]/(e^2)`, a full call is

```text
(I+(D_j+1)P_jh)(I+e R_jh).
```

A thin call is `I+e Z`. The proof permits arbitrary matrices Z. In particular,
it does not impose a rank, a square-zero condition, or a count on thin calls.
The required word is `Q product_j (I+(D_j+1)E_j)`, where `Q=1+e`.
The main fields are independent. All D variables remain independent.

This is the star stage contract from PR5631/5649, with arbitrary stage splits
and a much larger connector class. It excludes no general complex or dyadic
caller. It also excludes no caller with a different grouped stage map, a
nonfull stage, a different output, or paid idle multipliers.

## 2. The one-sided theorem

**Theorem.** A successful word cannot have three distinct leaves whose block
columns are identical in every thin matrix Z. It also cannot have three
leaves whose block rows are identical in every thin matrix Z.

Only one of these two equalities is needed for exclusion. Thus changing the
forward split, adding more queries, increasing their rank, or adding more
stage splits cannot repair connectors which only see the sum of the leaves.

### Local form and chronology

Commutation with T and the local support give

```text
P_jh = [[A_jh+B_jh, B_jh], [B_jh, A_jh+B_jh]],
R_jh = [[A_jh, A_jh], [A_jh, A_jh]].
```

The A matrices form an orthogonal resolution of I. In particular,
`A_jh A_jk=0` for `h!=k`, `A_jh^2=A_jh`, and `sum_h A_jh=I`.
These statements do not require the A matrices of different stages to commute.
The orthogonal-resolution hypothesis also follows from full rank use: if the
projectors sum to E and their ranks sum to rank E, their images form a direct
sum. Each projector is then the corresponding coordinate projection on that
sum. Stages with a rank deficit are a different contract.

Set all D variables to one. The coefficient of e requires `sum R=I`, including
thin queries. The mixed coefficient of `e(D_j+1)` then requires

```text
sum_(full call i in stage j) [P_i, sum_(calls l later than i) R_l] = 0.   (1)
```

This necessary condition follows by expanding the literal ordered word.
No full-word converse is used.

For distinct selected stages j,k define

```text
S_jk = sum_(call (j,h) before call (k,l)) A_jh A_kl.                    (2)
```

In (1), add block rows zero and j, and read block column k. The contribution
of good calls is S_jk. The contribution of a later thin map Z is
`A_jh (Z_0k+Z_jk)`. If the three selected leaf columns of every Z are equal,
this thin contribution is the same for the two choices of k other than j.
Consequently

```text
S_jk = S_jl    for each permutation (j,k,l) of the three stages.        (3)
```

Other good stages do not contribute to these blocks. Thus the argument
restricts to any three selected leaves in a larger star.

### The prefix determinant argument

Read just the calls of the three selected stages in their original order.
Before a call with projection A from stage j, let P_k be the sum of the A
projections already read from stage k. Left multiplication of (2) by A and
orthogonality within stage j give

```text
A S_jk = A(I+P_k).
```

Equation (3) gives `A P_k=A P_l`. Also `A P_j=0`. Therefore, for the total
prefix `S=P_0+P_1+P_2`, every update satisfies

```text
A S=0.                                                               (4)
```

Introduce an independent central variable x. Equation (4) implies

```text
(I+xA)(I+xS) = I+x(S+A).
```

Starting at S=0, the product of all these factors is `I+xS_final`.
At the end, `S_final=I+I+I=I`. On the other hand, an idempotent of rank r
has determinant `det(I+xA)=(1+x)^r`. Each stage is a resolution of I,
so its ranks sum to d. Taking determinants now gives

```text
(1+x)^(3d) = det(product(I+xA)) = det((1+x)I) = (1+x)^d.
```

This is impossible for positive d. This proves the column statement for
all finite dimensions and all finite split counts. It uses no list of orders.
Transpose all matrices and reverse the order to obtain the row statement.

## 3. A paid-rank and finite-field cut

Assume g is at least three. The sum of the good queries is
`sum T_j`. Hence the thin sum must be

```text
K = I+sum T_j = epsilon E_core + F+G,
epsilon = (g+1) mod 2,
F: each leaf -> core by I,       G: core -> each leaf by I.
```

The rank of K is `2d`. Its column space is the core plus the diagonal leaf
space, and its row space is the core plus the leaf-sum space.

Let U be the span of all thin images, and V the span of all thin row spaces.
Write `dim U=2d+a`, `dim V=2d+b`, and let R be the sum of thin ranks.
Factor each thin map at its actual rank, then concatenate those factors.
Sylvester's rank inequality gives

```text
R >= dim U + dim V - rank K = 2d+a+b.                                 (5)
```

Both a and b must be positive. Otherwise one side of the one-sided theorem
applies to all leaves. In particular **R >= 2d+2**, over any field of
characteristic two.

For a finite field of size s, choose b additional row basis vectors beyond
the row space of K. Their restriction to one leaf is a `b by d` matrix.
There are at most `s^(bd)` such signatures. Equal signatures imply equal
leaf columns for every thin map. Each signature can occur at most twice.
The column-space argument is the same. Therefore

```text
g <= 2 s^(bd),     g <= 2 s^(ad),
R >= 2d + 2 h,     h = min {z >= 0 : g <= 2 s^(dz)}.                   (6)
```

This is a necessary condition, not a construction or a sufficient test.
It concerns a common field and a fixed block basis. For one-port binary
copies, d=2. It gives R>=6 for g=3..8, R>=8 for g=9..32, and R>=10 for
g=33..128. For coupled ports, use the actual larger d. Do not apply the
one-port bound per port after ports have been coupled.

At g=31, five rank-one connectors fail this cut. Five rank-two connectors
with d=4 meet it exactly: `2d+2=10`. Thus coupled pairs of ports are a precise
remaining target. The cut does not prove that such a word exists.

## 4. Constructive escape and its price

`ESCAPE-WORD.json` contains a complete eight-field binary word. It has three
paired stages, six full calls with rank-one queries, and eight rank-one thin calls.
Every local projector, query rank and compatibility relation is checked.
The verifier retains every exponent of each independent D variable and
checks every coefficient of the full word. It also checks that the thin
maps distinguish all three leaves in both directions.

Thus the changed connector contract has a real positive operator. It does
not give a profitable supplier. At the pinned PR5599 tariff, 104 copies have
complete optimistic moment coefficients

```text
208 H25 + 624 H9 + 6 helpers - 6 paid - 832 H1.
```

Its linear margin is -336. After common ranks are cancelled, all positive
terms have rank at least eight and all negative terms have rank at most
seven. For every `0<=t<=1`, the margin is at most `8^(t-1)*(-336)<0`.
Additional physical adapters cannot repair that price.

The new cut still leaves a useful target. At g=127, ten thin queries are
allowed by (6) for one-port binary copies. The optimistic PR5599 profile
has a positive exact margin at saving `7/2000=.0035`, and its numerical
crossing is about .00364156. **No 127-leaf word is supplied.** This screen
also does not establish a characteristic-zero lift, native frame adapters,
compiler admission, an outer transfer, or a new kappa.

A smaller coupled target is g=31 with five rank-two connectors per two-port
block. Its optimistic bill, scaled to 104 ports, also has positive exact
margin at .0035. It needs only 62 full calls. No such word is supplied either.
Coupling physical ports can require new frame maps; their costs must be
charged before this screen can become a supplier claim.

## 5. Evidence and limits

The main result is a written finite-dimensional matrix proof. The checker
also verifies fifteen exact free-algebra certificates for the paired-stage
case, without a solver or the discovery implementation. Matrix and formal
polynomial controls test the chronology extraction, restriction to three
leaves, prefix factorization and determinant formula. They support the
proof; finite tests alone do not prove its unbounded statements.

The discovery archive retains changed C,D splits, arbitrary aggregate maps,
extra thin queries, a different cycle frame, and three-/four-way splits.
Timeouts remain unknown. Passing first mixed coefficients is not passing the
full word. No proof assistant or independent human acceptance is claimed.

Credit Cinna Davis's controller and simplex work; PR5617/5631/5649 for the
query-frame and fixed-star line; and the complete P104/native/helper/compiler
lineage for the tariff. This proof, cut, search and escape word were prepared
for Ali Romman with substantial OpenAI Codex assistance. No subagents.
New work is Apache-2.0.
