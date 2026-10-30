# E8 span lemmas over every field of odd characteristic

This contribution was produced by Nick Petalas. Apache-2.0.

## Statement

Let L be the 120 standard norm-two E8 root lines, with representatives in
Z[1/2]^8. For a line u write O_u for the root lines orthogonal to u. Evaluate
these representatives in a field K of characteristic different from two.
The ambient dot product is the ordinary nondegenerate form on K^8.

The following four facts hold over every such field, including characteristic
zero. There is no exceptional odd prime.

1. **S1.** The roots in O_f span f-perp, of dimension seven.
2. **S2.** For distinct root lines f,u, the roots in O_f intersect O_u span
   span(f,u)-perp, of dimension six.
3. **S3prime.** Suppose u,v are distinct root lines nonorthogonal to f, neither
   equal to f, and f,u,v are independent over Q. The roots in O_f intersect
   O_u intersect O_v span span(f,u,v)-perp, of dimension five. The three
   anchors remain independent over K.
4. **W2.** Project the 56 lines nonorthogonal to f, other than f itself, onto
   f-perp by w_u = r_u - (r_u dot r_f) r_f/2. Their projective images are
   exactly 28 distinct directions. Every three distinct directions are
   linearly independent over K. Consequently a two-dimensional subspace
   contains at most two of them.

The S3prime admissibility condition uses the rational root configuration.
The conclusion proves that its admissible triples remain independent after
reduction. It does not silently change the domain at a special prime.

These are the span inputs named in DreamingOfClouds's PR2819 and its PR2784
lineage. PR2819 establishes them in characteristic zero and explicitly leaves
positive characteristic outside its classification. This proof supplies the
new field range of those inputs. It does not assert the full rank-nine
classification in positive characteristic.

## Integer certificates

Use doubled roots R_u = 2 r_u. Their entries are integral, their squared norm
is eight, and distinct root-line products are 0 or +/-4. All those nonzero
products remain nonzero over every odd-characteristic field, so the
orthogonality pattern itself does not change.

For an integer matrix A, a k-by-k minor with determinant +/-2^a certifies
rank(A) >= k over every field of characteristic different from two. This
follows because its determinant is a unit in Z[1/2], hence is nonzero in K.
The same certificate also applies to characteristic zero. No extrapolation
from finitely many primes is involved.

The verifier fixes f = e_0+e_1. It constructs the entire root inventory
explicitly and generates one such minor for each of the following matrices.

| Matrix family | Matrices | Certified lower rank |
| --- | ---: | ---: |
| R[O_f] | 1 | 7 |
| Two anchors (f,u) | 119 | 2 |
| R[O_f intersect O_u] | 119 | 6 |
| Admissible three anchors (f,u,v) | 1512 | 3 |
| R[O_f intersect O_u intersect O_v] | 1512 | 5 |
| Three distinct projected directions | 3276 | 3 |

There are 6539 minors. Their absolute determinants are powers of two between
2 and 256. `select_minor` uses elimination modulo three only to choose row
and column indices. `determinant` then evaluates the selected original
integer square matrix by fraction-free elimination, checking every division.
Only that exact integer determinant establishes the all-field claim.

All rows of the first, third and fifth families are orthogonal to their
respective anchor rows. The certified anchor ranks and nondegeneracy of the
ambient dot product bound their ranks above by seven, six and five. Thus the
lower bounds give the exact spans in S1, S2 and S3prime.

For W2 the verifier forms integer projected rows

    D_u = 2 R_u - (R_u dot R_f)/4 R_f = 4 w_u.

It divides each by its positive coordinate gcd and chooses its sign by its
first nonzero coordinate. Every divisor is a power of two. These operations
remain invertible over every K in the statement. The 56 rows form 28 rational
directions with two rows per direction. Their 3276 triples have certified
rank three. This also proves nonvanishing and pairwise distinction after
reduction, since any pair belongs to such a triple. No extra direction can
arise by reducing two proportional vectors.

For the S3prime inventory, f,u,v are rationally dependent precisely when
the two nonzero projections have the same projective direction. The verifier
omits exactly those pairs and certifies every other anchor triple separately.
This accounts for every rationally admissible pair in its stated domain.

## Transport to every anchor

For a doubled root a, the reflection is

    H_a = I - a a^T/4.

Since a^T a = 8, direct multiplication gives H_a^T H_a = I and H_a^2 = I.
Its coefficients are in Z[1/2], so these identities hold over every K under
consideration. On a doubled root R its image is

    R - (a dot R)/4 a.

The verifier checks all 14400 root images, including divisibility by four
and membership in the signed root set. Each reflection gives a permutation
of the 120 root lines. A bounded traversal of these permutations proves
that the orbit of f contains all 120 lines. Each resulting product is an
invertible isometry over Z[1/2], hence over K.

These products transport root orthogonality, anchor independence, spans and
orthogonal projection. Therefore the complete fixed-anchor certificates
prove S1, S2, S3prime and W2 for every root line f. Multiplication by any
representative sign has no effect on these assertions.

## Scope and remaining obligations

This is a scoped algebraic proof supported by an exhaustive finite integer
certificate. The executable certificate and the written transport argument
jointly establish the quantified field statement. The executable is not a
formal proof-kernel check.

The rank-nine pinning/classification argument, its sign logic, SAT encodings,
refutations and other finite facts are inherited research and were not
replayed. Applying this new lemma to a positive-characteristic classification
still requires checking all remaining characteristic assumptions in that
argument. No decoder COPY floor, native operation, physical caller, signed
invoice, new kappa or complete multiplication theorem follows here.

Power-of-two minors and integral root-reflection transport are established
methods. CubeJerry's PR3095 and conorholds's PR3755 use them for different
root/character span statements. They retain that methodological credit.
The new result here is the complete all-odd-field S1/S2/S3prime/W2 input set
and its explicit bounded integer certificates.
