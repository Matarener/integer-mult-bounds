# A cubic obstruction at the cyclic half-call boundary

## Model and claim

Fix g=i or g=j in Q8. All paid labels are g. Work in the full formal
group algebra F2[Q8], with only binary scalar GL mixing free. Every role
contains arbitrary independent dirty input. A paid factor is

```text
D_l = I + x u_l v_l^T,   x=[g]+1,   v_l^T u_l=1.
```

Call zero acts first. The endpoint is `D_(n-1)...D_0`. The target has
`[g^-1]` on t>0 active roles and identity on every other role. Arbitrary
finite restored dirty workspace is allowed. As in PR3517, conjugating
interleaved binary scalar matrices absorbs them into the projectors.
Augmentation forces the residual scalar matrix to be identity.

**Theorem.** The exact minimum is 3t calls for every positive integer t,
with any finite number of restored arbitrary dirty roles. Every full word
also satisfies the independent determinant congruence

```text
n >= 3t,                    n = 3t mod 4.
```

In particular four inverse-generator targets cost exactly
twelve calls, even with arbitrary finite restored dirt, when every paid
label is that same positive generator.

There is also a structural statement at n=2t. If only the degree-one and
degree-two coefficient equations hold, the compressed cubic defect below
has rank t. Thus every saturated cyclic quadratic word fails at degree
three. PR3551's invertible cubic defect is an instance of this fact.

These are single-generator statements. They do not exclude eight-call
four-target words using both i and j. They supply neither a physical
caller nor a multiplication supplier or a new kappa.

## Ordered coefficients and the uniform 3t bound

The subgroup algebra F2[<g>] is F2[x]/(x^4). Its four powers of x are a
basis, since g has order four. Its inclusion in F2[Q8] is injective.
Also `[g^-1]=[g]^3=1+x+x^2+x^3`.

Let X have the n gate columns u_l, Y have the n covector rows v_l^T, and
`A=YX`. Let L be the strictly lower triangular part of A. Expanding in
chronological order gives

```text
W = I + x S1 + x^2 S2 + x^3 S3,
S1 = XY,          S2 = XLY,          S3 = XL^2Y.
```

For example the degree-three term for c>b>a is
`u_c (v_c^T u_b)(v_b^T u_a) v_a^T`; these are precisely the terms of
`XL^2Y`. No commutation of role matrices is used.

Let P be the active coordinate projector, of rank t. Quadratic target
equality says `XY=P` and `XLY=P`. These are all the endpoint equations
needed for the separate saturated-defect result below. For a full word,
also `XL^2Y=P`. Put `K=I+L`, which is invertible because L is strictly
triangular. In characteristic two these full equations imply

```text
XY=P,                 XKY=0,                 XK^2Y=0.
```

Restrict Y to the active input space and project X onto the active output
space. Denote the resulting maps by Y0 and X0. Then

```text
X0 Y0 = I_t,          X0 K Y0 = 0,           X0 K^2 Y0 = 0.
```

This is a statement in the n-dimensional call space, regardless of the
number of original roles. Set U=im(Y0), which has dimension t. Since X0
is injective on U and kills KU, `U intersect KU = {0}`. Invertibility of
K gives

```text
KU intersect K^2U = K(U intersect KU) = {0}.
```

Both KU and K^2U lie in ker(X0), which has dimension n-t. Their disjoint
sum has dimension 2t. Hence `2t<=n-t`, proving n>=3t for all t. This is
a standard finite-dimensional subspace argument applied to the full
ordered cubic equations. It needs no workspace reduction or census.

Three calls on each active coordinate give g^3=g^-1, use 3t calls and
never touch any spectator. They attain the bound for every t. Thus there
is no cyclic batching saving in this alphabet and restoration contract.

## The inherited half-call bound and quadratic equality

The quadratic equations alone give, by multiplication by Y and X,

```text
A^2 = YPX,          ALA = A^2,          AKA = 0.
```

The last identity implies `2 rank(A)<=n`: K maps im(A) injectively into
ker(A). This is the all-g specialization of Nick Petalas/PR3536's
sign-sensitive bound, restated here without its finite census premises.

Moreover `rank(A^2)=t`. Write `A^2=BC`, where B is Y restricted to the
active space and C is PX with codomain that space. Then `CB=I_t`, so B
is injective and C is surjective. Also
`A^3=Y(XY)^2X=YPX=A^2`. In particular rank(A)>=t and n>=2t.

## The invertible block lemma

Suppose n=2t. The preceding inequalities force rank(A)=rank(A^2)=t.
Since im(A)=im(A^2) and `A^3=A^2`, A acts as identity on im(A).
Therefore `A^2=A`.

Here is the needed linear algebra fact over F2, in every finite dimension.
Let A be a projection of rank t on a space of dimension 2t, and let K be
invertible with `AKA=0`. Set U=im(A) and V=ker(A). They form a direct
sum, with both dimensions t. K maps U injectively into V, hence onto V.
In the decomposition U direct_sum V, the two matrices have block form

```text
A = [ I  0 ],          K = [ 0  B ].
    [ 0  0 ]              [ C  D ]
```

C is invertible by `K(U)=V`. Invertibility of K forces B invertible:
if Bv=0, then Kv belongs to V=K(U); injectivity gives v in U, and also
v in V, so v=0. Hence

```text
AK^2A = [ BC  0 ]
        [  0  0 ]
```

has rank t. In particular its restriction to U is invertible.
Triangularity of K is not needed for this block lemma; the application
uses triangularity only to establish its invertibility.

## The compressed cubic defect at quadratic equality

Let `E3=S3+P` be the cubic coefficient error of a quadratically correct
word. Since the characteristic is two, `K^2=I+L^2`, and

```text
Y E3 X = A L^2 A + A^2 = A K^2 A.
```

At n=2t the block lemma gives rank(Y E3 X)=t. Thus rank(E3)>=t and E3
cannot vanish. This independently excludes n=2t without bounding
the number of original roles or assuming clean workspace. It proves
the stated compressed cubic-defect theorem for every quadratically
correct saturated cyclic word. The ordered-call/core lineage is PR3517;
the argument here works directly in call space and needs no finite core
enumeration or inherited finite exclusion.

For the retained PR3551 eight-call witness, A is an eight-by-eight
projection of rank four and K is invertible. Its cubic coefficient error
has row masks `(14,1,3,4)` and rank four, while the compressed error also
has rank four. The full regular Q8 action error has rank eight because
multiplication by x^3 has rank one on each of the two right cosets of
<g>. This fixture corroborates the general proof; it is not its premise.

## Independent determinant congruence

The cyclic coefficient ring is commutative, so the ordinary determinant
applies, even with arbitrarily many restored roles. Each rank-one factor
has determinant `1+x`: the determinant lemma gives
`det(I+xuv^T)=1+x v^T u=1+x`. Every free binary GL matrix has determinant
one. The target determinant is `(1+x)^(3t)`. The element 1+x has exact
order four in F2[x]/(x^4). Therefore `n=3t mod 4`.

The congruence is a separate necessary condition, not the proof of the
3t floor. Interchanging i and j preserves all arguments and constructions.
No census, solver timeout, positivity heuristic, proof-kernel acceptance
or human review is used as evidence for the universal statement.

## Credit and remaining obligations

Nick Petalas/PR3536 retains the sign-sensitive half-call bound; PR3517
retains the ordered Gram/scalar-core formulation; PR3551 retains the
explicit saturated quadratic word. Exact unchanged proof and witness
bytes, origin paths, commits, blobs and SHA256 are in inputs/RETENTION.json.
The new result is the uniform exact cyclic 3t tariff, the block-lemma
compressed full-rank defect at quadratic equality, and the independent
cyclic determinant congruence. The scalar linear-algebra facts are
standard; their application closes the cyclic handoff left by PR3551.

Tuafo/PR2900, ywz65/PR2587, PR3487, Aaron Wang/PR2318, Cinna Davis,
steph4n-gh and the retained register-model lineage keep their prior
coefficient-support, reduction and operation-model credit. Arham
Tahir/PR3137's physical contract and PR3461's scalar preparation have
separate costs. Caller, scalar, routing, hosting, precision, recursive
composition and complete supplier invoices remain unresolved. Independent
human and formal proof-kernel review are unclaimed.

## Open next questions

- Does a mixed positive-i/j eight-call word realize four inverse targets?
  Its degree-three algebra is noncommutative, so the single L and cyclic
  determinant step here do not apply. Start by deriving the exact mixed
  cubic equations rather than importing the cyclic conclusion.
- Which real caller could use a complete Q8 construction at a lower
  physical recursive bill? Begin with the contiguous layout contract of
  PR3137. The mathematical word alone does not settle that question.
