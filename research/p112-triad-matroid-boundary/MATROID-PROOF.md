# Complete eight-point reduction for five-term triple replacements

This layer reduces every rational replacement of three canonical target terms
by at most five outer products to 135 explicit support families. It does not
price those remaining families. The separate geometric cost replay supplies
that obligation. The fixed triad geometry, tariff, rank-57 gauge, and four-term
triple theorem are as in PROOF.md.

The catalogue and field certificates are in MATROIDS.json. The selective
transfer witnesses and exact remaining families are in SUPPORT-TRANSFER.json.
The standalone, read-only command is:

```sh
python3 -I -O -Werror -B research/p112-triad-matroid-boundary/matroids.py
```

The replay uses only the standard library and the hash-bound inherited
seven-point generator already declared as a live package input. It regenerates
all catalogues and support classes; it does not search for representations or
use a solver, network service, cached executable, or scratch receipt.

## Why ranks three and four suffice

Let B have three disjoint nonzero indicator columns and let

    B B^T = U V^T

use at most five rational outer products. Append zero columns to reach five.
Both factor ranks are at least three. Sylvester's inequality gives
rank(U)+rank(V) <= 5+3 = 8. Transpose the target if needed so rank(U) is three
or four; this preserves the rectangular binary pairing tariff. The column
space of B is contained in that of U. Therefore the augmented column matroid
of the five queries and three marked columns B has eight indexed elements,
rank three or four, three independent marks, and a full-rank query complement.
Loops, parallel elements, zero queries and repetitions are retained.

## Exhaustive abstract catalogue

Nick Petalas' seven-point extension routine constructs every simple rank-three
line system through seven elements. When a point is added, the old lines it
extends are disjoint, including possible two-point lines; enumerating all such
choices is exhaustive. The all-collinear rank-two system is omitted when
forming rank-three bases. Positive multiplicities of every nonloop class,
together with every possible number of loops, give all rank-three matroids
on seven elements after simplification. Exact isomorphism deduplication leaves
108 bases. Taking their duals gives all rank-four seven-element bases.

Every rank-three or rank-four matroid on eight elements has a non-coloop,
because its rank is less than eight. Deleting that element preserves rank.
For any such deletion N, one-element rank-preserving extensions correspond
exactly to nonempty modular cuts of its lattice of flats. A modular cut is
upward closed and contains the intersection of every modular pair it contains.
For a cut C, the extension is determined by

    r_M(S union {e}) = r_N(S) + 1[closure_N(S) not in C].

The empty cut adds a coloop and raises rank, so is omitted. Matroids that have
other coloops are still covered by deleting a non-coloop. The all-flat cut
adds a loop, and principal rank-one cuts include parallel extensions.

The checker computes the least closure under the two cut rules. Its lectic
NextClosure traversal visits every closed family: for each missing flat,
in decreasing index order, close the retained prefix plus that flat, and
accept exactly when the lower prefix is unchanged. This is the exact successor
criterion; termination exhausts all closures. The replay visits 3,435 rank-three
and 33,982 rank-four extensions of the 108 bases.

For isomorphism deduplication, circuit-size incidence colors are refined by
pair incidence counts. These colors are isomorphism invariants. The complete
circuit list is minimized over every permutation within each color cell, so
the canonical form is exact. The shortcut for uniform circuit-size layers is
used only when every subset of every present circuit size is a circuit; then
all permutations are automorphisms.

The resulting complete rank tables equal every saved table in MATROIDS.json:
325 rank-three and 940 rank-four types. Every saved table also passes the
elementary rank increment and diminishing-returns axioms, which imply the
usual rank axioms. Counts alone are not the coverage test. Published counts
by Mayhew and Royle are a comparison only, not a runtime oracle or input.

## Exact minimal source and reader requests

Write Q for the five query elements and T for the three independent marks.
At a physical port belonging to target j, a source support S is feasible
precisely when

    r((Q\S) union T) > r((Q\S) union (T\{j})).             (S)

This is linear-functional separation: there exists a functional equal to one
on target j and zero on the other targets and inactive queries exactly under
this rank condition. A reader support R is feasible precisely when

    r(R union {j}) = r(R).                               (R)

This says the target has a query expansion supported on R. Retain all
inclusion-minimal query masks. Minimality makes every retained coordinate
nonzero, since an additional zero would provide a smaller feasible mask.

These conditions are simultaneously sufficient in any one representation
of the marked matroid. Independently choose a source functional f_p at each
source port, and coefficients beta_q expressing its mark at each reader
port. Their product is

    sum_t f_p(U_t) beta_(q,t) = f_p(b_owner(q))
                             = 1[owner(p)=owner(q)].

Thus no cross-port coefficient compatibility condition is missing. Rows
outside the three target supports may be zeroed on both sides, preserving
the exact target and shrinking both supports. Full-group tariff is monotone
under such shrinkage. Rational representability of an abstract table is the
only relaxation here; the support optimizer itself is exact for each fixed
represented matroid.

The checker enumerates every independent target triple whose query complement
has full rank: 9,554 markings in rank three and 41,386 in rank four. It derives
both families directly from all subset ranks and checks circuit/cocircuit
orthogonality. It then quotients by all 120 common query permutations, all
target permutations, and a common transpose. The result is exactly 9,377
paired support classes. A target permutation must also permute the physical
target roles when the separate cost verifier applies the family.

## Field transfer and all-field exclusions

For 1,150 tables the certificate gives a literal matrix over a characteristic-
two field: 19 over GF(4), 101 over GF(8), 1,024 over GF(16), and six over GF(32).
Polynomial residue arithmetic is checked to be a field by existence of a
unique inverse for every nonzero residue. All 256 indexed-subset ranks are
recomputed for each matrix, giving 294,400 exact rank comparisons.

For 39 other tables the saved four set masks violate Ingleton's linear-rank
inequality strictly. The checker recomputes both sides, so those tables cannot
be represented over the rationals or any other field. The remaining 76 tables
are explicitly unresolved by these two tests; a failed representation search
is never used as nonrepresentability evidence.

A support class with any verified characteristic-two provenance can transfer
all its admissible source and reader choices to that field with supports
unchanged or shrunk. The expanded-identity argument then gives the original
three-target tariff. This closes 8,329 support classes. A further 347 classes
have only Ingleton-violating provenance and cannot arise over the rationals.

## Universal query merges: every actual provenance is checked

Of the remaining 701 classes, exactly 22 are universally reducible to at most
four terms. This is not inferred from one conveniently reducible abstract
representative: every marking on every non-Ingleton provenance is checked.
All 186 marked instances have either a parallel query pair or a series query
pair. The replay recomputes this universal quantifier, not just a saved flag.

For parallel source queries, their two columns have rank at most one. Merge
the proportional source factors and add their scaled readers. The new reader
support is contained in the union of the old ones. Rectangular pairing rank
is subadditive under this union, so the cost cannot increase. Zero factors
are included in this argument.

For a series query pair, its rank in the augmented source dual is at most one.
The rows of [V|B] lie in the kernel of [U|-B], by the exact endpoint identity.
They may be a proper subspace of that kernel; nevertheless, restriction to
the two query coordinates still has rank at most one. Hence the actual reader
columns are proportional, and the transposed merge applies. The already
verified four-term triple theorem then supplies the original tariff floor.
This leaves 679 classes.

## Selective support transfer

Full matroid representability is more than is needed. For each old minimal
source or reader mask, it suffices to contain a feasible safe mask for the
same target, after one common query permutation, target permutation and
optional transpose. Choosing the safe supports independently at physical
ports remains exact by the construction above and cannot increase any tariff.

SUPPORT-TRANSFER.json contains 544 such transfers. Each safe class is bound
directly to an independent target marking of a literal matrix among the
verified field certificates. The replay derives these 228 marked safe
signatures from those matrices' actual subset ranks and verifies all 10,433
source/reader containment checks. It does not rely merely on another abstract
matroid sharing a class label. The matching operation is subset containment,
not intersection, support cardinality, or an unverified equality of hashes.

After these exclusions, exactly 135 classes from 61 unmarked tables remain.
Their exact canonical minimal families are exposed in remaining_classes of
SUPPORT-TRANSFER.json, with stable index, source_minimal_masks and
reader_minimal_masks fields. matroids.load_frontier() is a convenience reader;
the full registered matroid replay is still required before pricing them.
No absence-of-transfer claim is needed: replaying the supplied successful
transfers and retaining every other class is sufficient for coverage.

## Provenance and limits

The seven-point extension method and characteristic-two support-transfer
argument retain Nick Petalas' predecessor credit. The four-term merge endpoint
uses this package's separately verified triad result and its PR3513/PR3538
classification credit. Mayhew and Royle's published enumeration provides
external context only. The eight-point extension catalogue, exact marked
support reduction, field certificate search and replay, provenance repair,
and selective transfer integration were produced by flyingviper with
substantial OpenAI Codex assistance and separate-agent implementation audits.

This layer proves combinatorial coverage and exact transfer statements. The
135 residual cost problems must still be verified by the cost layer. No claim
about six-term triples, larger target blocks, arbitrary higher-rank fitting
matrices, native implementation, complete suppliers, or a new selected bound
follows from this matroid layer alone.
