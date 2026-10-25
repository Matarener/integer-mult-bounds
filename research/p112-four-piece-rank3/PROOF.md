# A sharp four-site P112 representation boundary

Let R be the 120 doubled E8 root lines, F the fixed orthogonal frame of eight
lines, and P=R\F the literal P112. Use the source's leading-one nine-bit
labels ell(r). Over a characteristic-zero field K, put

    C = {c_h=(r dot h)_(r in P) : h in K^8},
    w(q) = rank_F2 {ell(r) : q(r) != 0}.

Theorem, conditional only on the standard finite E8 Weyl-chamber theorem.
If q0 has at most four nonzero sites and w(q1),w(q2),w(q3)<=5,6,6, then

    C intersect span_K(q0,q1,q2,q3) = {0}.

Thus the same conclusion holds for support-rank bounds **3,5,6,6**. A
leading-one set in a binary three-space has at most four points. The pieces
may overlap and have arbitrary coefficients and cancellations. Independence
of the four pieces is not required.

The four-site allowance is sharp as a cardinality condition. The receipt gives
a literal rational root-code representation by disjoint pieces of sizes
5,10,20,18 and binary ranks 5,5,6,6. This does not settle the distinct question
with first-piece binary rank four.

## Reduce a hypothetical word to a root normal

The complete binary-flat censuses below reprove full-root support capacities
12 and 20 for dimensions five and six. A hypothetical nonzero word therefore
has support at most

    4+12+20+20=56.

The pinned root-simplex proof supplies the Weyl-chamber argument, whose finite
quantities are rechecked here. A codeword with support below 70 has at least
43 live perpendicular root lines. Every six-node parabolic has at most 36
root lines. The eight seven-node faces have line counts

    42,28,22,14,16,23,37,63.

The chamber theorem therefore puts its normal in a root direction. The
source replay verifies simple-root positivity, all 960 simple-reflection
root identities and the qualifying root ray. A root normal has live support
53 when it is live and 56 when it belongs to the removed frame.

For arbitrary K, the rational perpendicular roots have rational rank at most
seven. If that rank were at most six, a generic real normal to their rational
span would contradict the rank-six cap 36. Their rational rank is consequently
seven. Its one-dimensional rational kernel generates the field-valued normal
after scalar extension. Apply the real argument to that rational generator.
The live roots span eight dimensions, so no nonzero normal gives the zero word.
The standard Weyl-chamber theorem itself is an explicit mathematical premise,
not a theorem checked by this Python program or a proof kernel.

## The complete necessary cover problem

Let E be the support of this root word, of size N in {53,56}. A representation
requires E to be covered by the actual four supports. Intersect the supports
with E, and extend each large piece's binary support span to a five- or
six-dimensional binary flat. Let S5,S6,T6 be their intersections with E.
The small support contributes at most four sites. Capacities give

    |S5|>=12-(56-N),
    |S6|,|T6|>=20-(56-N).

For example, at N=53 a six-section of size at most 16 leaves total capacity
at most 4+12+16+20=52. Thus both six-sections have size at least 17 and the
five-section has size at least nine. At N=56 the thresholds are 20 and 12.
These are necessary bounds even if the actual pieces cancel outside E.

Enumerating distinct section masks loses no possible cover. If S6=T6,
the total cover has size at most 4+12+20=36, already impossible. Distinct
sections can be treated as unordered pairs.

For each such pair U=S6 union T6, if |E\U|>=17 then a five-section of size
at most twelve leaves at least five sites. Only pairs with |E\U|<=16 need
a complete comparison against every eligible five-section. The replay does
that comparison with exact integer masks.

For each of the two live-normal representatives, the results are:

- There are 320 distinct eligible six-sections and 10,562 eligible five-sections.
- All 51,040 distinct six-section pairs have union at most 38.
- There are 64 pairs with union 37. Each leaves at least six sites after the
  best five-section.
- There are 96 pairs with union 38. Each leaves at least five sites after the
  best five-section.
- The other pairs leave at least five sites by the twelve-site capacity.

Thus no four-site small piece can finish a live-root cover. For the frame-root
representative there are 336 eligible six-sections. Every pair has union at
most 38, so even a full five-section and four small sites cover at most
38+12+4=54<56. This excludes the frame case as well.

## Why three representatives cover every root normal

Use signed coordinate permutations preserving the four coordinate pairs of
F. The replay constructs fourteen generators: four swaps within a pair,
three adjacent pair-block swaps, and seven even sign flips at positions
{0,j}, for j=1,...,7. Each generator preserves both R and the literal live set.

For each generator, transform the eight simple roots and solve for their
integral simple-root coordinates. Reduction modulo two gives its linear
label action, with the leading coordinate fixed. All 1,680 root/label images
are checked. The 120 distinct labels span binary dimension nine. These
invertible coordinate transformations therefore preserve the support-rank
conditions as well as support cardinality and codeword supports. Canonical
root signs only rescale the corresponding coordinates by minus one, preserving
all support conditions.

The generated root-normal orbits have sizes 48,64,8 and cover all 120 lines.
The first orbit is the live two-coordinate roots, the second the live
half-integral roots in the undoubled convention, and the third the frame.
Orbit transport does preserve the fixed frame here, unlike an arbitrary Weyl
transformation. The census representatives and every finite quantity are
recorded in RESULT.json.

## Exact enumeration and separate reconstruction

The primary enumerates all 3,309,747 binary five-spaces and 788,035 binary
six-spaces in F2^9 as kernels of unique reverse-echelon annihilators. For each
of the three normal cases it records the full section-size histogram, maximum
full-root capacity, every eligible-section set digest, all pair-union counts,
and the minimum residual-site count for every exceptional pair.

The separate implementation enumerates affine four- and five-spaces on the
leading-one hyperplane using forward generator bases and complementary coset
representatives. It reconstructs 3,212,592 and 777,240 affine sections per
normal. Adding 97,155 and 10,795 leading-zero binary spaces accounts exactly
for the primary totals. It compares every histogram and eligible-section
set digest, then separately maximizes intersections with each pair's residual.
The complete per-pair minimum-residual digests agree.

The programs share authenticated geometry, digest serialization and the written
chamber/transport argument. This is internal computational corroboration,
not independent human review or proof-kernel verification. The new finite
cover result is checked from the canonical geometry. PR3397's pending
four-piece theorem is predecessor context, not a mathematical dependency.

## Five sites suffice

A mask has bit i set for root i in the sorted canonical full120-root list.
For each live representative the receipt records four disjoint masks covering
its 53-site support. Give the piece at site r the value r dot a when its mask
contains r, and zero otherwise. The sum is literally c_a on every live site.
The independent replay checks all coordinates and binary ranks. The sizes are
5,10,20,18 and the ranks are 5,5,6,6. Each piece is nonzero and disjointness
also makes the four pieces linearly independent. This establishes sharpness
of four versus five sites for the first piece. It supplies no rank-four
counterexample and no complete decoder.

## Scope and credit

The result is one conditional support theorem and its exact cardinality
boundary. It improves the first support-rank allowance from PR3397's two to
three. It does not prove full C5, a ten-piece caller exclusion, C(P112)>=64,
a native decoder, restoration/hosting/consumer costs, supplier admission,
a multiplication theorem, a new kappa or a selected-frontier update.
Lean, Docker, the selected cold replay and human/proof-kernel review are unrun.

Credit Nick Petalas/PR3397 for the prior four-piece boundary and its kernel and
separate affine methods, PR3405 for the completed distinct-endpoint caller,
PR3161/3162 and the retained root-simplex geometry, DreamingOfClouds/PR3154,
joaqcoo and the E8/P112 lineage. New work is Apache-2.0.
