# A smaller query interface from fewer full frames

The selected label set admits a plane matching whose strict scalar fitting rank
is exactly **32 over every field**. For equal d-dimensional port payloads it is
exactly **32d**, including directed, nonsymmetric and noncommuting free blocks.
This lowers the exhibited scalar rank from PR3335/PR3356's 34. It does not change
the selected conditional exponent or establish the minimum across all matchings.

## Construction and the objective mismatch

Read the 112 actual nine-bit labels q_i from the pinned selected DATA-PHASES
payload. Use the pairing `<q_i,q_j> = popcount(q_i & q_j) mod 2`.
The certificate partitions all ports into eleven orthonormal groups of size
eight, two of size six and three of size four. Every group's complete Gram
matrix is an identity; this is binary-label orthonormality, not a claim about
Euclidean E8 roots.

PR3356 has thirteen size-eight groups and four pairs, hence seventeen groups.
Keep eleven of its size-eight groups. Replace its zero-based frames 1 and 7
and all four residual pairs, on exactly these 24 ports:

```
9,10,16,21,24,26,29,35,36,49,54,57,63,65,68,69,70,74,80,93,94,103,106,108.
```

The five replacement groups are

```
[9,57,68,69,93,94]       [10,29,65,74]
[16,35,54,108]          [21,36,49,63,70,103]
[24,26,80,106].
```

Thus six old groups become five new groups. The full-frame count drops from
13 to 11 while the total number of even groups drops from 17 to 16. Maximizing
the first objective need not minimize the second. The source hash, preserved
predecessor certificate and full partition make this a literal repair, not a
comparison of unrelated numerical summaries.

## Strict scalar mask and all-field upper bound

Pair consecutive ports in each group. Each pair spans a Gram-I2 binary plane;
write E(i) for the plane containing port i. The scalar interface requires

    K_ii = 1,
    K_ij = 0 when i != j and E(i) is not orthogonal to E(j).

In particular, the two ports within one plane must not share a scalar total.
For each even group, make two supports by taking its even-position and
odd-position ports. Let v_s be the corresponding 0/1 indicator vector and put

    K = sum_(s=1)^32 v_s v_s^T.

The supports partition all 112 ports. Therefore K has identity diagonal and
rank at most 32 over any field. Distinct ports in one support are in distinct
planes in the same orthonormal group. Their full planes are orthogonal, so each
off-diagonal nonzero is permitted. The 112-by-112 matrix satisfies the entire
ordered mask, including all 11,392 forced entries.

Choosing one representative from each disjoint support gives a principal I32
in this constructed matrix. Its rank is consequently 32 in every characteristic.
The query map can be implemented algebraically by computing each support total,
adding it to the corresponding target coordinates and uncomputing it from the
preserved sources. The independent checker runs that field program on all 112
source columns and 112 arbitrary dirty-target columns. It is not a native
implementation or a complete physical cost analysis.

## Matching-specific lower bound, including block payloads

The certificate gives these sixteen pairwise nonorthogonal planes, indexed
after the consecutive pairing above:

```
54,53,50,48,46,43,38,34,30,27,23,18,15,10,7,3.
```

Take both ports from each. Every off-diagonal entry of their 32-by-32 principal
submatrix is forced zero by the mask, and its diagonal is forced one. Hence
**every fitting matrix for this matching** contains a forced I32, proving rank
at least 32. This applies to arbitrary nonsymmetric coefficients, not just
disjoint-support or Gram factorizations.

For uniform d-dimensional payloads, the same principal submatrix is I_(32d),
even when free blocks are arbitrary noncommuting matrices. K tensor I_d attains
rank 32d and satisfies all block constraints. This proves the exact uniform
block result for every field and every positive integer d. The proof does not
infer a universal lower bound over different matchings from this clique.

The disjoint even-group construction class has a separate counting lower bound
of 28 scalar queries: a binary orthonormal group is linearly independent in
F2^9, so an even group has size at most eight; covering 112 ports needs at least
14 groups, each yielding two supports. This is only a construction-class floor.
No arbitrary-matching rank-28 lower theorem, optimal grouping, or fourteen-frame
nonexistence theorem is supplied here.

## Full-plane copied-information charge

The plane contract reads both coordinate directions of every participating
plane, not just its named representative port. For a support in a group of size
k, closing its k/2 representatives to their complete planes gives all k labels
of the group. The source/reader binary pairing matrix is I_k, of rank k.
There are two supports per group. The exact one-total complete-plane tariff is

    22 * 8 + 4 * 6 + 6 * 4 = 224.

This agrees with an independently formed dense binary Gram invoice. Charging
only the representative labels would give 112, omitting the other plane port;
the checker includes this undercharge as a control. The full-plane tariff
boundary is inherited from ctoth, Philippe Van Velzen and the retained native
lineage; the present work applies it to the new matching. This is not a complete
source-access, frame, restoration, hosting, precision or recursive supplier bill.

The rank reduction therefore does not, by itself, supply a cheaper native
decoder or a new κ. A useful physical follow-up must change or realize that
copied-information contract and price the complete producer/consumer path.

## Search versus proof

Discovery used exact-cover SAT on even orthonormal subsets of a 24-port repair,
with OS assignment seed 40 used to order the 78 choices of two predecessor
frames. All 78 four-group instances returned UNSAT; the first five-group
instance, removing frames 1 and 7, returned this construction. Those solver
UNSAT reports were not proof-checked and are not used for any impossibility
claim. Every positive mathematical assertion replays from the compact certificate
using only the standard library, independent of the discovery solver.

The earlier order-seven orbit idea found no complementary pair among its 105
transversal orbit masks (910 frames); that is not a general fourteen-frame
obstruction. A 120-second unrestricted exact-cover run stopped after 29,200,000
nodes; a 180-second SAT run also timed out. A separate 180-second three-frame
repair attempt completed at least 21 logged instances without a witness and
was interrupted on the next part of its domain. These attempts do not prove
optimality. They are included to delimit the completed search, not as theorem
evidence. The positive 24-port repair is the contribution.

Credit Nick Petalas/PR3356, Matarener/Mark/PR3335, ywz65/PR2471,
thakrarsagar/PR2484, Cinna Davis/PR1825/PR2118/PR2126, Adam Gall/PR1889,
ctoth, Philippe Van Velzen, Jeremy Diviney and the selected E8/P112 lineage.
The exact-clique and disjoint-support arguments are established tools from that
lineage, applied here to a newly constructed matching. Tekalign, with substantial
OpenAI Codex assistance. Apache-2.0; no independent human or formal review claimed.
