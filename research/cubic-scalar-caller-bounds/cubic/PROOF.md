# Cubic scalar caller bounds with constant rational bank directions

This contribution proves lower bounds for scalar bank words in the full
algebra `R=Q[N]/(N^3-1)`. It establishes no positive caller or native
implementation. In three banks at least five paid queries are necessary,
even under a larger scalar-polynomial query alphabet. In n banks the mixed
first/second-power alphabet requires

```
3 divides n,
k >= n + ceil((n+1)/3),
a,b <= 2(k-n),
```

where a,b count the two powers. A homogeneous alphabet requires `k>=2n`.
Three matching layers cannot suffice, and four layers cannot suffice when
each layer is pure in one power. Four internally mixed layers are not
excluded by the last argument.

The scientific snapshot is `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.
The unchanged historical proofs, scripts and receipts are under `frozen/`;
`ORIGINS.json` supplies their exact byte pins. The original scalar algebra
lane supplied these proofs and finite witnesses, with the historical
independent review strengthening the exact interaction rank and checking
the three-bank and three-layer arguments. This version completes the
four-pure-layer review, spells out the equality case, supplies fresh
defect-sensitive gates and independent regular-action checks, and records
the query-balance corollary. Prepared with substantial OpenAI Codex
assistance; Apache-2.0 ancestry. Historical quadratic references are retained
as provenance only and are outside this contribution.

## 1. Full algebra, paid alphabet, and augmentation

Every one of the n bank inputs is independent. The desired operator is
`N I_n`, optionally preceded by a final constant bank permutation. The paid
alphabet is

```
E_ij(s N^e) = I + s N^e e_i e_j^T,
i != j, s in {1,-1}, e in {1,2}.
```

Arbitrary constant `GL_n(Q)` bridges may occur between paid queries and are
free in this lower-bound relaxation. Thus the result also applies to the
smaller constant integral ADD/swap/sign bridge model. Allowing free bridges
in the proof is not permission to omit their physical cost from a supplier.
The target includes all n fields; additional fields with a different restored
endpoint would change this model and are not silently included.

The assertion is an identity in the full algebra R. Its regular action on
the basis `(1,N,N^2)` is injective: the first column of multiplication by a
polynomial gives its three coefficients. A faithful action merely on the
three group elements would not by itself guarantee injectivity of the
whole algebra. In particular, a fixed native operator satisfying
`N^2+N+I=0` has lost the augmentation component and is not automatically
covered by a full-ring lower bound for universal words.

Let W(N) be a complete word and `B=W(1)` its augmentation. If the word has
the stated target, `B^-1 W(N)=N I_n`, including when the original target has
a final constant bank permutation. To justify normalization with arbitrary
bridges, suppose the current augmentation is B_0. A paid query updates it
to `E_ij(s) B_0`. Since `(e_i e_j^T)^2=0`,

```
E_ij(s)^-1 E_ij(sN^e) = I+s(N^e-1)e_i e_j^T.
```

Consequently the new normalized factor is

```
I+(N^e-1) u v^T,
u v^T = s B_0^-1 e_i e_j^T B_0,
u,v rational, v^T u=0.
```

A free constant bridge changes W and B on the same left side and leaves
`B^-1 W` unchanged. This proves the normal form by induction without moving
noncommuting paid factors past each other. Each normalized factor has
determinant one and inverse obtained by negating its perturbation. Therefore
`det(N I_n)=N^n=1` in the full ring is necessary, which is exactly `3 | n`.

Specializing to a primitive cube root `zeta`, with
`zeta^2+zeta+1=0`, gives a necessary condition for a full-ring identity.
The obstruction proofs may use this condition. A positive identity at
zeta alone would not establish the full-ring target.

## 2. Three banks require five queries, even with polynomial coefficients

Consider four invertible factors

```
C_i=I+alpha_i u_i v_i^T,
alpha_i in Q(zeta), u_i,v_i in Q^3, v_i^T u_i=0,
C_4 C_3 C_2 C_1=zeta I_3.
```

This is a relaxation of the mixed alphabet and permits arbitrary
scalar-polynomial coefficients. The image of the product minus identity is
contained in the span of the four u_i. Since `(zeta-1)I_3` has rank three,
some three u_i are rationally independent. Every three-subset of four
cyclic positions is consecutive. A central invertible product is unchanged
by cyclic rotation: `AB=zeta I` implies `BA=A^-1(AB)A=zeta I`.
Rotate so that the independent directions occur first in application order,
then apply a constant rational change of basis sending them to e_1,e_2,e_3.

For `P=C_3 C_2 C_1`, the first three factors change only rows one, two,
three respectively. Each individual C_i has its own diagonal entry one
because the corresponding v_i has zero entry there; later row updates can
change accumulated diagonal entries. The resulting identities are

```
P_11=1,       det P[{1,2},{1,2}]=1.
```

Indeed, before the third row changes the leading two-square block is
`[[1,a],[b,1+ba]]`, of determinant one. But
`P=zeta C_4^-1=zeta(I-alpha_4 u v^T)`. With rational `c_i=u_i v_i`, the
one- and two-dimensional principal determinants give

```
alpha_4 c_1       = 1-zeta^-1,
alpha_4(c_1+c_2) = 1-zeta^-2.
```

The first right side is nonzero, so division is legitimate. The resulting
ratio is

`(c_1+c_2)/c_1 = (1-zeta^-2)/(1-zeta^-1) = -zeta`,

contradicting rationality. Three factors are covered by padding an identity;
fewer than three already fail the image-rank requirement. Hence at least
five are necessary in the stated larger constant-direction alphabet.

The rational-direction premise is essential. The retained source exhibits
four factors whose directions depend on N and whose product really is
`N I_3` in the full ring. This audit replays that excluded word and its
literal inverse independently as nine-dimensional rational matrices.
Every factor's perturbation has coefficient-span dimension greater than
one, and the actual constant-direction admission predicate rejects it.
It is an exact scope counterexample, not a four-query construction in the
allowed alphabet.

## 3. Exact interaction rank for the mixed alphabet

Let k normalized factors act on n banks. Put
`t=zeta-1`, `t_2=zeta^2-1` and `alpha_i in {t,t_2}`. Write

```
U=[u_1 ... u_k],       V=[v_1^T; ...; v_k^T],
B=VU=L_0+U_0,         D=diag(alpha_1,...,alpha_k),
G=(D^-1-L_0)^-1.
```

Here L_0 and U_0 are the strict lower and strict upper parts of B. Its
diagonal vanishes by `v_i^T u_i=0`. Since D is invertible and L_0 strictly
lower triangular, G exists. Expanding the finite lower-triangular resolvent
orders exactly the chronological chains of queries and yields

`W=I+U G V`.

For the central target, `U G V=t I_n`; hence U and V have rank n and k>=n.
The k-square matrix `E=G V U/t` satisfies `E^2=E` and has image `im(GV)`,
of dimension n. Therefore

```
C=B-tG^-1=tG^-1(E-I)
```

has rank exactly `r=k-n`, not merely an upper bound. The identities
`t/t=1` and `t/t_2=-zeta` give the rational split

```
C=A+zeta H,
A=U_0-diag(1 on first-power positions),
H=L_0+diag(1 on second-power positions).
```

A is upper triangular and H lower triangular. Their nonzero diagonal
supports partition all k query positions. Conjugating the cyclotomic field
preserves rank. Since A and H are linear combinations of C and its
conjugate, both have rank at most 2r. If a,b count the two powers, the
principal triangular submatrices on their respective diagonal supports
have nonzero determinant, so

```
a <= rank A <= 2r,
b <= rank H <= 2r,
k=a+b <= 4r.
```

The target assumption matters. For an arbitrary noncentral fixture the
correct identity is

`U G C = (W-zeta I) U`.

The finite certificate retains this entire defect and checks it exactly.
Dropping it on that actual fixture fails the production predicate; the
checker does not pretend its fixture solves the central target.

## 4. The equality k=4r is impossible

Suppose equality held. It would force `a=b=2r` and
`rank A=rank H=2r`. Let S be the sum of the column spaces of C and its
conjugate, and T the sum of their row spaces. Both have dimension at most
2r. A and H have column spaces contained in S and row spaces contained in T;
their ranks force equality in all four inclusions. Thus A and H have the
same image and the same kernel over Q(zeta).

It remains to justify the projectors rather than assume diagonalizability.
The only eigenvalues of the upper triangular A are -1 and 0. The algebraic
multiplicity of -1 is a, while `rank A=a`; therefore its zero eigenspace has
dimension `k-a`, equal to the algebraic multiplicity of zero. All Jordan
blocks at zero have size one. Jordan blocks at -1 may be nontrivial. On
those blocks `(I+A)^k` vanishes; on the zero eigenspace it is identity.
Consequently

`P_A=I-(I+A)^k`

is exactly the projection onto `im A` along `ker A`. The exponent k suffices
for every Jordan block. In the same way the lower triangular H has only
eigenvalues 1 and 0, zero is semisimple, and

`P_H=I-(I-H)^k`

projects onto `im H` along `ker H`. The common image and kernel force the
unique projections to be equal. But taking diagonals in these triangular
polynomials makes diag(P_A) the first-power indicator and diag(P_H) its
complement. They cannot be equal in characteristic zero for k>0.

Thus `k<4(k-n)`, equivalently `3(k-n)>=n+1`, so

`k >= n+ceil((n+1)/3)`.

The fresh finite projector fixtures include nontrivial size-two Jordan
blocks at -1 and 1. Their zero eigenspaces remain semisimple. Replacing the
fourth power by the first really fails the same image/kernel projection
predicate. These fixtures validate the polynomial formulas; they do not
purport to realize the contradictory common-image/common-kernel premise.

The separate type bounds give a useful immediate screening corollary:

```
max(0,2n-k) <= a,b <= min(k,2(k-n)).
```

For a homogeneous word this yields `k>=2n`. At n=3 and k=5 both powers must
occur; at n=6 and k=9 each power must occur between three and six times.
These are necessary composition constraints, not syntheses. The wide proof
uses the special two-coefficient split and does not extend to unrelated
polynomial coefficients merely because the three-bank proof does.

## 5. Three square-zero matching layers cannot suffice

In a matching layer, disjoint pair-query perturbations annihilate one
another in both orders. After full augmentation normalization its combined
perturbation A satisfies `A^2=0`, including a layer mixing t and t_2.
Constant bridges between complete layers only conjugate these matrices and
preserve square-zero. Arbitrary mixing inside a declared layer is outside
this premise unless square-zero is separately established.

For two such perturbations define `P=(I+A_2)(I+A_1)`. Its inverse is
`(I-A_1)(I-A_2)`. Square-zero matrices have zero trace, and cyclicity of
trace gives

`tr P=n+tr(A_2 A_1)=tr P^-1`.

If `(I+A_3)P=zeta I`, then `P=zeta(I-A_3)` and
`P^-1=zeta^-1(I+A_3)`. The two traces would be `n zeta` and
`n zeta^-1`, a contradiction for positive n in characteristic zero.
This argument even allows operator-dependent square-zero matrices. Its
strength comes from the layer condition, not rationality of individual
query directions.

## 6. Four pure layers cannot suffice

Assume four square-zero normalized layers have central product zeta I.
For any adjacent two-layer product P, write the complementary product as
`Q=zeta P^-1`. Both P and Q have trace equal to that of their inverses.
Thus `(zeta-zeta^-1) tr P=0`, and every adjacent pair must have trace zero.
Cyclic rotations preserve the central target and justify applying this to
every adjacent pair in the four-cycle.

If two neighbors are both of type `I+t A`, their pair trace is
`n+t^2 tr(BA)=n-3 zeta s` for rational s. It cannot vanish. The analogous
second-power trace is `n-3 zeta^2 s`, also nonzero. Hence pure types must
alternate. Cyclic rotation alone puts the product in the form

```
(I+t_2 D)(I+t C)(I+t_2 B)(I+t A)=zeta I,
A^2=B^2=C^2=D^2=0,
```

with rational A,B,C,D. No change of generator or conjugation of the central
target is required. Split the equality
`(I+t_2D)(I+tC)=zeta(I-tA)(I-t_2B)` into rational and zeta coefficients.
Using `t t_2=3` gives

```
C-D = I+2A+B+3AB,
I-C-2D+3DC = A-B.
```

Set `G=2A+B+3AB`, substitute `C=D+I+G`, and use `D^2=0`. The second
equation becomes `D G=A+AB`. Right multiplication by B and `B^2=0` give
`2DAB=AB`. Left multiplication by D and `D^2=0` force `DAB=0`, then `AB=0`.
The first pair would therefore have trace
`n+3 tr(BA)=n`, contradicting its required zero trace. This holds for every
positive n, with no rank assumption on the square-zero rational matrices.

The finite check carries the target defect explicitly. Writing the two
coefficient defects as

```
e = I-C-2D+3DC-(A-B),
f = C-D-(I+2A+B+3AB),
```

the identity valid for arbitrary square-zero fixture matrices is

`D(2A+B+3AB)-(A+AB) = (e+f-3Df)/3`.

Only under the hypothetical central target may e=f=0 be substituted. The
fresh fixture has a nonzero target defect and nonzero DC; omitting the
defect or changing the coefficient sign fails the actual production gate.
An internally mixed layer has additional independent coefficient matrices,
so this proof does not exclude four such layers.

## 7. Complete conditional optimistic invoice

Consider n banks of twelve independent fields, k OPEN calls arranged in s
legal matching layers. The source-bound optimistic profile stipulated for
this scalar screen is

```
W=12n, m=2+5s,
H_1=8k, H_2=40k, H_3=16k,
H_5=12(ns-2k).
```

Every inactive bank in every layer pays its rank-five idle progress. This
per-layer expression requires an actual matching arrangement, in particular
`k<=s floor(n/2)`. It does not assert that arbitrary constant bridges have
native admission. The complete mass and zero-exponent deficit are

```
mass = 60ns+16k,
D=mW-mass=24n-16k.
```

At n=3 the five-query lower bound yields D<=-8 for every legal layering.
The sequential five-call fixture has `m=27,W=36`,
`H={1:40,2:200,3:80,5:60}`, mass 980 versus stock mass 972. At n=6 the
nine-query lower bound gives D<=0. For positive exponent beta and strict
child contraction, each normalized child contribution
`r*(m/r)^beta` is greater than its rank r. Thus both cases fail every
positive supplier exponent even with the omitted costs treated favorably.
The chosen idle granularity is explicitly per layer; a more detailed
schedule is not inferred from this aggregate count.

For larger n a positive value of this optimistic D does not establish a
positive exponent or any caller. For example, n=9,k=13 gives D=8 while
leaving source-code transport, native gauges, scalar bridges, all additional
ordinary/private roles, owner stock, precision, address/tape work, and full
arbitrary-input endpoints unpaid. These obligations remain separate.

## 8. Finite replay, controls, and evidence limits

Run with Python 3.12 and a fresh absolute output path outside the package and
any overridden input directory:

```
python3.12 -I -B check.py --output /absolute/external/new.json.gz
python3.12 -I -O -B check.py --output /absolute/external/new-optimized.json.gz
```

Only the standard library is used. Both historical scripts are captured and
authenticated, then compiled unchanged with `optimize=0`. Their complete
`receipt()` functions execute, preserving every original mathematical guard,
and every typed output field is compared with its original frozen receipt.
The old `main()` path I/O is not used. No bytecode cache, ambient Git access,
numerical package, nominee search, or sibling import is required. Output
creation is exclusive and never overwrites an existing path.

The fresh independent regular-action stage uses ordinary rational matrix
arithmetic, distinct from the source's cyclic polynomial convolution. It
checks all nine rational input columns of every three-bank normalization
fixture, the excluded four-factor word, and its literal inverse. The receipt
stores the entire rational matrices. A polynomial that agrees with N at
primitive roots but augments to four is rejected by this full-ring gate.

Fresh cyclotomic fixtures retain all interaction matrices, coefficient
splits and target defects, the nontrivial Jordan projector fixtures, the
four-pure-layer coefficient remainders, and the literal two-layer inverse.
They are exact diagnostics for the written arguments, not solutions of
the impossible central factorizations and not an exhaustive search.

The 27 executed semantic defects comprise eight augmentation/power changes,
four omitted factors, four inadmissible operator-dependent directions, one
augmentation-component omission, one fake identity direction, two interaction
defects, two truncated projector powers, two pure-layer coefficient/defect
changes, one reversed inverse order, one invalid square-zero layer, and one
omitted idle invoice. Each must fail at its named production predicate with
a concrete matrix or rank witness. The identical defective candidate then
runs with only that predicate deleted, outside the rejection catch, and
must be accepted. Historical inequality-only controls are preserved but
are not counted as these new rejection/deletion checks.

Normal and optimized Python 3.12 receipts are compared completely. These
finite certificates support the stated algebraic identities and sensitivity;
the universal query and layer bounds are the written proofs above. There is
no formal-kernel claim, positive scalar synthesis, native Clifford admission,
or new multiplication bound. The separate primitive-only Clifford response,
quartic caller, and quadratic positive-caller models are not republished.
