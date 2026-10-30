# The degree-two negative-Q8 bound is sharp

Let Q8 have generators i,j, with i^2=j^2=z, z^2=1 and ji=z ij.
Work over the full formal group algebra F2[Q8]. Binary scalar mixing is
free. A paid factor is

```text
D_g(u,v) = I + ([g]+1) u v^T,   g in {i,j},   v^T u=1.
```

Every role has independent arbitrary dirty input. Identity-target roles
must return unchanged. Call zero acts first. The normalized endpoint is
`D_(n-1)...D_0`; binary free mixing is absorbed by conjugation, and
augmentation forces its residual scalar matrix to be I.

Let B be the five-dimensional binary algebra with basis `1,x,y,tau,q`.
Its only nonzero products between positive-degree basis elements are

```text
x*x=tau, y*y=tau, x*y=q, y*x=q+tau.
```

All products of three positive-degree elements vanish. This is the
sign-sensitive quotient used in Nick Petalas's PR3536. The map
`[i] -> 1+x`, `[j] -> 1+y`, `[z] -> 1+tau` respects the Q8 relations;
in particular `[zi] -> 1+x+tau`, `[zj] -> 1+y+tau`.

**Theorem.** For each positive integer b, set t=4b. The exact minimum in B
for a diagonal endpoint with t copies of `[zi]` and any finite number of
restored dirty roles is 2t positive i/j calls. The same holds with all
`[zj]` targets. Thus complete equality in this degree-two quotient cannot
exclude the eight-call four-negative boundary, or give a universally
stronger lower bound than 2t on this family. The attaining words below
fail the full formal Q8 endpoint by an explicitly nonzero cubic term.

This is a theorem about the quotient relaxation. It is not an eight-call
construction in F2[Q8], a full-Q8 minimum, or a physical supplier.

## The inherited lower bound, restated in the quotient

Let X have the gate columns u_l, let Y have rows v_l^T and let A=YX.
For t negative-generator targets and restored identities, the sum of the
x and y coefficient matrices of the endpoint is the active coordinate
projector P of rank t. Thus `XY=P`. It follows that rank(A)>=t, because
`A Y e=Y e` on the active coordinate subspace and Y is injective there.

Set

```text
H[b,a] = A[b,a] c(g_b,g_a) for b>a, and zero otherwise,
c(i,i)=c(j,j)=c(j,i)=1, c(i,j)=0.
```

Chronological expansion gives the tau coefficient `XHY`. Each negative
generator has tau coefficient one, so `XHY=P=XY`. Multiplication by Y
and X gives `A(I+H)A=0`. Since H is strictly triangular, I+H is invertible.
The image of `(I+H)A` lies in ker(A) and has dimension rank(A). Hence
`2 rank(A)<=n`, and therefore `n>=2t`.

This argument already holds in B. It needs no full-Q8 finite exclusion,
no source-support theorem lost by projection, and no workspace bound.
PR3536 retains this lower-bound credit. Its proof and PR3517's scalar-core
proof are retained unchanged with exact origin identities in
`inputs/RETENTION.json`.

## An explicit eight-call attaining word

Coordinates are bits zero through three. Each row below gives the binary
vectors as decimal bit masks. Every label is i.

| Call | u | v | v^T u |
|---|---:|---:|---:|
| 0 | 1 | 1 | 1 |
| 1 | 7 | 15 | 1 |
| 2 | 2 | 10 | 1 |
| 3 | 15 | 2 | 1 |
| 4 | 8 | 14 | 1 |
| 5 | 9 | 8 | 1 |
| 6 | 11 | 12 | 1 |
| 7 | 7 | 9 | 1 |

Consequently every u v^T is a legal binary rank-one idempotent. Such a
projector is a scalar conjugate of a coordinate projector: choose u as
the first basis vector and the remaining basis vectors in ker(v^T).
No extra free address operation or initialized role has been introduced.

For an exact multiplication check, put `x=[i]+1`. The cyclic subalgebra
F2[<i>] is F2[x]/(x^4), since i has order four. Write

```text
W = I + x S1 + x^2 S2 + x^3 S3.
```

Starting with S0=I and S1=S2=S3=0, prepend each factor `I+xN` using the
simultaneous recurrence `S_d <- S_d + N S_(d-1)`, d=1,2,3. Direct exact
binary multiplication of the eight listed projectors gives

```text
S1=S2=I4,
S3 has binary row masks (15,3,7,12).
```

These are small explicit matrix identities, reproduced by `polynomial`.
The independent full Hamilton action checks the same word on every input
basis column without using this polynomial recurrence. In B the cubic
term vanishes, so W becomes `(1+x+tau) I4 = [zi] I4`, attaining the lower
bound with eight calls and four active roles.

For t=4b use b disjoint copies of the word. There are 8b=2t paid calls.
Each copy acts only on its own four coordinates. Appending any finite
number of dirty spectators leaves them untouched. The automorphism
interchanging i and j gives the all-zj result. This proves the theorem
for all b, independently of the executable's bounded direct-sum fixtures.

## The full endpoint has an invertible cubic defect

In the full cyclic subalgebra `[zi]=[i]^3=1+x+x^2+x^3`. Therefore

```text
W + [zi] I4 = x^3 D,
D = S3+I4 has binary row masks (14,1,3,4).
```

D is invertible. Its inverse has row masks `(2,6,8,15)`, and both binary
products are I4. Also `x^3=1+[i]+[z]+[zi]` is nonzero because these are
four distinct basis elements of the full group algebra. Thus the word
fails the full endpoint on every nonzero binary role direction.

More concretely, left multiplication by x^3 has rank two on the regular
Q8 module: the group splits into two right cosets of <i>, and on each
four-element coset multiplication is the nonzero all-ones map of rank
one. Since D has rank four, the full error has binary rank eight. Every
one of the 32 active role/group input columns has nonzero error. For b
disjoint copies the error rank is 8b=2t. Spectator inputs are restored.
The verifier checks these finite instances, and the direct-sum argument
proves the asserted all-b extension.

## What this changes and what remains open

PR3536's sign-sensitive bound is optimal for the complete degree-two
relaxation on an infinite family. The eight-call point is a legal
rank-one-projector word, not merely an abstract Gram matrix satisfying
one necessary equation. Any exclusion of eight calls for four zi targets
must use information absent from B or a different premise.

The full positive-i-only eight-call probe returned unknown at 120 seconds;
a QF_BV variant also returned unknown at 180 seconds. A quadratic mixed
three-zi/one-zj probe returned unknown at 90 seconds. All used Z3 4.13.4.
They are exploratory diagnostics, not exclusions, constructions, proof
certificates or performance comparisons. No all-label eight-call census
or mixed two-zi/two-zj solver run was performed. The full-Q8 four-negative
minimum, every mixed-shape minimum and a cubic invariant excluding all
words remain open.

The new contribution is the explicit saturated quotient word, its exact
invertible cubic defect and the all-multiplicity direct-sum consequence.
Nick Petalas/PR3536 retains the half-call invariant; PR3517 retains the
ordered-call scalar core; Tuafo/PR2900, ywz65/PR2587 and PR3487 retain the
image, coefficient-support and common-kernel lineage. Aaron Wang/PR2318,
Cinna Davis, steph4n-gh and the retained register-model predecessors keep
their source credit. Arham Tahir/PR3137 and PR3461 have separate physical
and scalar-cost obligations. Independent human and formal proof-kernel
review are unclaimed. No supplier, kappa or selected-frontier change follows.
