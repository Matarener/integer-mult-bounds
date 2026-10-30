# Exact signed subspace triangle

This is a scoped theorem in a rank-distance relaxation. It does not assert
that the graph below is the contact graph of a legal scalar word. In
particular, its three negative edges are variable productive credits, not
three already implemented independent recursive targets.

## Contract

Let K be any field, let H=K^m with m a positive integer, and let S1,S2,S3
be arbitrary subspaces. Write

```math
d(A,B)=\dim A+\dim B-2\dim(A\cap B).
```

There are four vertices, 0,S1,S2,S3. Three positive edges join 0 to Si;
three negative edges join every pair Si,Sj. For 0<t<=1 define

```math
J_t(S_1,S_2,S_3)
=\sum_i (\dim S_i)^t-\sum_{i<j} d(S_i,S_j)^t,
\qquad 0^t=0.
```

This uses the canonical subspace charts and Fourier-rank convention of
Ali Romman's [PR6171](https://github.com/CrocSwap/integer-mult-bounds/pull/6171),
at `343232cdf5273d1f77569de390f0977b46916644`, sections 1 and 2.
The distance identification is inherited, not a new native-operator lemma.
The normalization at m copies is J_t/m^t. All six graph terms are included;
physical realization costs have not been supplied by this relaxation.

## Linear optimum and every equality case

For every field and m>=1,

```math
\min J_1=-\lfloor3m/2\rfloor.
```

The minimizers are exactly the pairwise-disjoint triples with dimensions
(k,k,k) for m=2k, and a permutation of (k,k,k+1) for m=2k+1.
Pairwise-disjoint means each pair intersects only at zero. The sum of all
three spaces need not be direct.

Put x_i=dim Si, D=x1+x2+x3, and
I=sum_(i<j) dim(Si intersect Sj), a nonnegative integer. Directly,

```math
J_1=-D+2I.
```

Each pair has sum dimension at most m. Summing those three inequalities,

```math
2D-I\leq3m,
\qquad D-2I\leq\frac{3m}{2}-\frac{3I}{2}.
```

The integral left side is at most floor(3m/2). This proves the lower bound.
If I>=1, the right side is at most 3m/2-3/2, strictly smaller than
floor(3m/2). Thus equality forces I=0 and D=floor(3m/2).
Now xi+xj<=m implies each xi>=D-m. For m=2k this forces all three
dimensions to be k. For m=2k+1 it forces all three to be at least k and
their sum to be 3k+1, hence the claimed permutation. Conversely those
dimensions and zero pairwise intersections give equality in J1.

For attainment, split H=U plus W with dimensions k and m-k. Choose an
injective linear map f:U->W. Set S1=U, S2=W, and S3=graph(f).
The three intersections are zero, and their dimensions are k,m-k,k.
This works over every field, including characteristic two and k=0.

Consequently the normalized linear optimum is
-floor(3m/2)/m. It is -1 at one copy, -3/2 at every positive even width,
and -3/2+1/(2m) at odd width. The advantage is established in the signed
graph model; a supplier or exponent improvement does not follow.

## Exact two-copy power optimum

For m=2 let a=2^t, so 1<a<=2. Every nonzero proper subspace is a line.
Two distinct lines have distance two; a line and the full plane have
distance one. The following table exhausts unordered triples. A repeated
letter means the same subspace; L,M,N are distinct lines, and H is the
full plane.

| Triple | J_t |
|---|---:|
| 0,0,0 | 0 |
| 0,0,L | -1 |
| 0,0,H | -a |
| 0,L,L | 0 |
| 0,L,M | -a |
| 0,L,H | -1 |
| 0,H,H | 0 |
| L,L,L | 3 |
| L,L,M | 3-2a |
| L,M,N | 3-3a |
| L,L,H | a |
| L,M,H | 0 |
| L,H,H | 2a-1 |
| H,H,H | 3a |

Every field has at least three lines in K^2, so all rows exist. Comparing
these affine functions on 1<a<=2 gives

```math
\min J_t=\min(-a,3-3a),
\qquad \min J_t/2^t=\min(-1,3/2^t-3).
```

At one copy the only spaces are zero and K. If exactly h of the three
spaces are K, the signed cost is h-h(3-h)=h(h-2), independent of t.
Its minimum is -1. Thus two copies beat the best one-copy assignment
exactly when 2^t>3/2, equivalently t>log_2(3/2). Equality holds at the
threshold. The threshold lies below 3/4 because 2^3>(3/2)^4.

## What changes relative to fixed-boundary reduction

PR6171 fixes each productive endpoint to a repeated space U^m. Here all
three productive pairs vary. At m=2, the attaining linear triple consists
of the three distinct lines of F2^2. No line is a repeated scalar boundary:
the repeated one-dimensional scalar choices are only zero and F2^2.
The coupled triple has three full-distance productive pairs. A one-copy
assignment has at most two nonzero pair distances. Their negative credits
therefore cannot be held constant during the common-copy choice.

This gives an exact optimality gap and threshold, beyond the predecessor's
arithmetic control that negative terms can reverse an averaging inequality.
It neither contradicts that theorem nor extends the graph into a physical
construction. In particular, pairwise graph edges do not establish three
independent targets on arbitrary dirty inputs. Producing such a caller,
or proving that its legal graph constraints forbid this configuration,
is a separate question.

## Verification boundary

The written dimension argument and exhaustive two-dimensional table give
the all-field statements. The checker enumerates actual small subspaces,
checks every ordered triple, and compares all equality cases. Its binary
RREF inventory is independently checked by closure under adjoining vectors.
It also constructs the attaining binary triples at widths 1 through 64.
These are finite corroboration, not a proof-kernel formalization.

The code uses finite, explicit bounds. Its managed-runtime allocations
are a Power of Ten deviation: finite calibration sizes bound the lists,
tables and loops. No recursion, external solver, network access, imported
predecessor executable or persistent mutable state is needed.

This proof and verifier were produced by Nick Petalas. Standard dimension
identities, graph subspaces and affine-envelope comparisons are background;
no literature-priority claim is made. PR6171 retains its tensor-reduction
credit; Cinna Davis retains the projection inequality, icekylinx retains
the canonical subspace-frame construction, and all retained P104/native/
helper/caller/compiler contributors retain their predecessor credit.
