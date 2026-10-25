# The rank-three half of the P8 exterior-family theorem

For the fixed target indicators c0,c1,c2 on `[0,67]`, `[7,64]`, `[1,75]`,
let h be any rational vector in their span. Use the six prescribed queries

```
q0=h, q1=c1+c2+2h, q2=c0+c2+h,
q3=c0+c1+h, q4=2c0+c1+c2, q5=c0+h.
```

Every rational reader matrix that reconstructs the exact endpoint
`c0*c0^t+c1*c1^t+c2*c2^t` has full-group invoice at least **18**. Equality
holds at h=0. Combined with the rank-four theorem in [PROOF.md](PROOF.md),
this covers every rational h on all 112 ports: adjoining a single column to
the independent c0,c1,c2 gives rank three or four, with no other case.

This result fixes the dictionary, marking, physical embedding and exact
endpoint. It does not establish a floor for other dictionaries, other
embeddings, changed allowed-free strict-fit entries or unrestricted decoders.

## An exact affine arrangement covers all rational coefficients

Write h=x*c0+y*c1+z*c2. Relative to c0,c1,c2, the effective query matrix is
`A(h)=A0+h*b^t`, with columns and update row

```
A0: (0,0,0), (0,1,1), (1,0,1), (1,1,0), (2,1,1), (1,0,0)
b:   1,       2,       1,       1,       0,       1.
```

Append the target basis to obtain `B(h)=[I3|A(h)]`. Every 3x3 minor is affine
in x,y,z: any determinant term using two update columns vanishes because
both columns are multiples of h. The primary verifier expands all 84
determinants as exact multivariate polynomials and checks that every term
of degree two or three cancels. There are three identically zero minors,
four constant nonzero minors and 77 nonconstant affine minors. Normalizing
nonconstant forms up to nonzero scalar gives 25 distinct hyperplanes.

Their complete lattice of nonempty affine intersections has 443 flats:

| Dimension | Flats |
|---|---:|
| 3 | 1 |
| 2 | 25 |
| 1 | 167 |
| 0 | 250 |

The primary enumeration begins with the ambient flat. Adding each plane in
turn to every existing flat enumerates all intersections by induction on
the processed planes. Exact rational RREF gives a canonical representative;
a pivot in the augmented constant column rejects inconsistent intersections.
The independent checker instead intersects all subsets of at most three
planes. This is complete because a consistent affine system in three
variables has a defining row basis of at most three equations.

For each flat F, delete the hyperplanes that do not contain F. This stratum
is nonempty over Q: an affine rational space over an infinite field cannot
be covered by finitely many proper affine subspaces. In dimension zero none
of the excluded planes contains its point. Every rational h belongs to
exactly one stratum, obtained by intersecting all planes containing h.
Therefore these are complete algebraic zero patterns, not coefficient
samples or a bounded search box.

## The arrangement determines actual readers and source supports

The surviving maximal minors are constant on a stratum. Since the target
identity basis survives, they specify the complete rank-three matroid of
the nine augmented columns, including all loops and parallel elements.

For any column subset S, its rank equals the maximum of `|S intersect B|`
over the surviving three-element bases B. A maximum independent subset of
S extends to a basis of the whole matroid, which proves this formula. The
primary verifier regenerates all 512 ranks for each of the 443 strata.
A query coordinate is, up to sign, the minor using that query and the
other two target basis columns. Thus all source coefficient supports also
follow from the same bases, without choosing a sample point.

A query subset T recovers target j precisely when
`rank(T)=rank(T union {j})`. Testing all 64 query subsets gives all
inclusion-minimal recovering sets. Such a set is independent: if its
queries were dependent, deleting a redundant query would leave the same
span. Its unique recovery uses every selected query, because a zero
coefficient would contradict minimality. Conversely every arbitrary
recovery contains a minimal recovering set and can be replaced by its
unique recovery without enlarging any support.

Reader columns outside the six marked target ports reconstruct zero and
may be set to zero individually. The two physical copies of each mark
are optimized independently, so no reader symmetry is imposed. There is
one marked output port in each of physical groups 17,18,29,30,31,32.
Each nonzero source coefficient occupies both copies of its mark. A
coefficient support bit j therefore becomes physical source group bits
`3 << (2*j)` in this order. This accounts for all source and reader group
supports relevant to the invoice.

Crucially, the reader equations here are the actual three-coordinate
equations `A(h)r=e_j`. The inherited four-coordinate equations used in the
rank-four reduction are not imposed. For example, at h=0, `c0=q5` is valid
although its old fourth-coordinate value is one.

## Complete threshold pricing

Both checkers independently authenticate the two scientific inputs and
rebuild every one of the 64x64 physical tariffs. For group sets S,T, the
tariff is the GF(2) rank of the binary Gram matrix on **all three ports of
each selected physical group**. Source and reader union monotonicity is
checked in both arguments of every table entry.

For a fixed stratum, choose a minimal recovering query set independently
for each of the six physical output groups. The invoice is the sum, over
the six queries, of the tariff of its fixed source groups and the union
of groups whose chosen reader set uses it. The preceding reductions show
that a cheaper arbitrary reader would yield a cell in this finite product.
Across all 443 strata these products contain 2,785,849,439 cells.

The primary replay decides whether any cell costs less than 18. At a
partial assignment its already incurred invoice is a lower bound by
monotonicity. For each single unassigned group, the minimum invoice after
adding that group alone is another lower bound for every completion. If
any such bound is at least 18, the entire branch closes. These bounds are
**not added together**: the same future rank increase can be shared.
Every branch not pruned is visited. The complete replay closes all 443
strata in 28,206 branch nodes. This is a threshold certificate; it does
not assert that each individual stratum has exact minimum 18.

The independent replay splits the output groups into two triples. It
enumerates their support profiles, discards profiles whose partial invoice
already reaches 18, then prices every remaining pair with exact packed
integer arithmetic. Each per-cell total is below the byte radix, so no
carry can mix cells. All 2,785,849,439 cells are either monotonically
excluded or included in this second complete check. Its surviving product
has 123,990 pairs. It likewise finds no cost at most 17. See
[INDEPENDENT-RANK3-PROOF.md](INDEPENDENT-RANK3-PROOF.md) for its precise
independence and coverage argument.

## Equality and reviewable receipts

Set h=0 and use

```
c0=q5, c1=q3-q5, c2=q2-q5.
```

The six query charges are `[0,0,6,6,0,6]`, totaling 18. Both checkers verify
the exact rational endpoint on all 112x112 entries and reprice its actual
full-group supports. Thus 18 is the exact minimum of the rank-three
family, and also of the combined rank-three/rank-four family.

`rank3_verify.py` regenerates the affine minors, flats, subset ranks,
minimal readers, full physical tariffs and complete threshold coverage.
`independent_rank3.py` uses independent determinant/intersection/reader
reconstruction and the separate meet-in-the-middle pricing method.
Their compact receipts store coverage counts, deterministic digests of
the regenerated complete data and the attaining endpoint witness. Neither
checker reads discovery logs or relies on the other's code or receipt.
Default runs compare receipts without writing; `--write-receipt` explicitly
regenerates the corresponding receipt. No network, Git metadata, packages
outside the Python standard library or additional scientific inputs are
required.

The algebraic completeness argument is a written proof reviewed by
separate AI agents. The finite steps use exact arithmetic; they are not a
proof-assistant formalization or an independent human review. Attribution
for the classical P8 representation and the P112 data remains in
[README.md](README.md). No new representation or global multiplication
bound is claimed.
