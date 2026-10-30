# Exact fixed-cubic coframe frontier

This is a scoped rank-graph theorem with a concrete Clifford realization. It
does not optimize an unrestricted circuit or change the selected supplier.

## Contract and result

For an integer m >= 1 let V = F2^m plus F2^m, with

```
omega((x,z),(y,w)) = x.w + z.y
S(x,z) = (z,x+z)
L0 = {(0,z): z in F2^m}
d(A,B) = m - dim(A intersect B), for Lagrangians A,B.
```

Fix one internal Lagrangian L. Both its entrance from L0 and its exit to L0
are paid. Every internal occurrence of the prescribed transport S must use
this same L. Write

```
a = d(L0,L), b = d(L,S L).
```

The exact componentwise minimal attainable pairs are

```
(a,b) = (j,m-2j),  j = 0,...,floor(m/2).                 (1)
```

In particular, all charts satisfy 2a+b >= m and b = m modulo 2. Every
feasible pair is dominated by a pair in (1), and every pair in (1) is
attained. This characterizes the Pareto frontier, not every attainable pair.

Let phi be increasing and concave on [0,m], with phi(0)=0, and let k>0.
The exact minimum complete graph bill is

```
min_L [2 phi(a) + k phi(b)]
  = min(k phi(m), 2 phi(floor(m/2)) + k phi(m mod 2)).   (2)
```

For the power tariff phi(r)=r^t, 0<t<=1, and even m, division by m^t gives

```
normalized optimum = min(k, 2^(1-t)).                  (3)
```

For odd m the exact unnormalized value is

```
min(k m^t, 2 ((m-1)/2)^t + k).                         (4)
```

Thus two copies and two prescribed native occurrences have normalized bill
2^(1-t), strictly below the one-copy value 2 for every t>0. Both boundary
transitions are included. At t=1 the values are respectively 1 and 2.

The contract requires a common internal coframe. Different coframes at
different occurrences and replacement of the prescribed word by another
word are excluded. In particular S^3=I permits cancellations in unrestricted
synthesis. The theorem makes no lower-bound claim for that larger problem.

## Lower bound and parity

The distance d is invariant under symplectic transport and satisfies the
triangle inequality. Indeed dim(A intersect C) is at least
dim(A intersect B)+dim(B intersect C)-m, by applying the dimension formula
inside B. Since L0 and S L0 are complementary, d(L0,S L0)=m. Hence

```
m <= d(L0,L) + d(L,S L) + d(S L,S L0) = 2a+b.          (5)
```

Put W=L intersect S L. The polynomial identity S^2+S+I=0 implies
S^-1=I+S. If v is in W, then v is in L and S^-1 v is in L. Consequently
S v = v+S^-1 v is in L. Also S v is in S L. Thus W is S-invariant.

The polynomial X^2+X+1 is irreducible over F2. On W, multiplication by its
class X can therefore be defined as S, making W a vector space over F4.
Its binary dimension m-b is even. This proves b=m modulo 2. No estimate
from a finite search is used here.

For any attainable pair, put j=(m-b)/2. Parity makes j an integer in
[0,floor(m/2)], and (5) gives j<=a. Once attainment below is proved,
(j,m-2j)=(j,b) dominates the original pair. The displayed pairs are mutually
incomparable, which establishes exactly the frontier (1).

## Attainment

Use the coordinate symplectic planes with bases e_i,f_i. On each of j
disjoint pairs of planes use the two-dimensional subspace

```
span(e_(2i-1)+e_(2i), f_(2i-1)+f_(2i)).
```

The displayed generators pair to zero because 1+1=0 in F2. Their span is
Lagrangian in its four-dimensional block and is S-invariant. Its
intersection with L0 has dimension one. On each remaining plane use the
original line span(f_i). Its intersection with its S-image is zero.

Taking their direct sum gives a Lagrangian with a=j and b=m-2j. Every
rank in (1) is therefore attained for every positive m.

After restriction to (1), the objective is
f(j)=2 phi(j)+k phi(m-2j). It is concave as a function of real j on
[0,floor(m/2)]. A concave function is at least the smaller of its two
endpoint values. Both endpoints are attainable. This proves (2), and
(3)-(4) follow by substitution. No numerical root calculation is needed.

## A phase-exact Gaussian-dyadic witness

Let H_g=(1+i)[[1,1],[1,-1]]/2, P=diag(1,i), and U=-P H_g. These are
Gaussian-dyadic Clifford matrices. Direct multiplication gives U^3=I,
U X U*=Z, and U Z U*=Y. Thus U induces exactly S on Pauli labels.
Put

```
B = CNOT (H_g tensor I), M = B* (U tensor U) B.
```

B takes the standard Z chart to the paired-plane chart above. It has
Fourier rank one; U tensor U has rank two; M is monomial and has rank zero.
The exact monomial phases and its four columns are generated in RESULT.json.
The full forward and inverse identities are

```
B M B* = U tensor U
B M* B* = (U tensor U)*.
```

They hold on every input, by equality of the full matrices. For any positive
integer k, B M^k B*=(U tensor U)^k. The graph invoice is therefore two
rank-one boundary children and k rank-zero internal occurrences, compared
with k rank-two occurrences in the original common chart. Tensoring these
blocks and adding an unpaired U supplies the general attaining recipe.
No relative or global phase is discarded. A monomial internal operator
still has ordinary arithmetic, routing and precision costs; zero Fourier
rank is not zero machine cost.

## Relation to earlier work

Ali Romman's PR6171 proves tensor reduction for a fixed scalar contact
graph with fixed repeated canonical boundaries and no prescribed native
transport equation. That theorem is a cited predecessor, not an object of
verification here. Its projection inequality is credited to Cinna Davis /
PR5140, and the canonical subspace-frame construction to icekylinx.

The present positive-cost graph prescribes S on a loop at its internal
chart. It therefore changes the native-transport hypothesis excluded by
PR6171. The invariant paired chart demonstrates why that excluded
hypothesis matters, with both boundary costs paid. PR6172's signed graph
instead varies productive boundaries and has negative edges; it supplies
neither this transported model nor this optimum. Classical symplectic
distance, F4 linear algebra and Bell-basis facts are background. The new
contribution is the exact paid rank frontier and all-width tariff formula
for this specified common-coframe native contract.

Ross Richardson / PR4081 supplies an earlier Gaussian order-three tensor
family and its distinct whole-bank quadratic-response restriction. No new
gate family or quadratic-response theorem is claimed here. The present
objective prices a conjugated native map rather than requiring every
tensor power to satisfy U_m^2+U_m+I=0.

This contribution was produced by Nick Petalas. Independent human and
formal proof-kernel review are unclaimed. Apache-2.0.
