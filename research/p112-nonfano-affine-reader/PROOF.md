# The complete non-Fano affine reader family does not save this literal bill

Let a,b,c be the indicators of three distinct alternating halves in the
retained Tekalign/PR3370 sixteen-group P112 partition. The halves are pairwise
disjoint, including the two halves of one group. Fix these four query rays,
up to separate nonzero rescalings:

    q12=a+b, q13=a+c, q23=b+c, q123=a+b+c.

The target is the exact unmasked scalar operator T=aa^T+bb^T+cc^T on all 112
ports. A reader may have arbitrary values, including values outside the three
target supports. For a scalar vector v, cl(v) contains both ports of every
retained plane touched by its support. The actual term tariff is

    C(u,q) = rank_F2 Gram(cl(q),cl(u)).

The coefficient field and this binary geometric rank are different objects.
All ranks in the tariff use the pinned binary labels, regardless of the
coefficient field.

**Scoped result.** Over every field of characteristic other than two, every
exact four-term factorization with these query rays has total actual-reader
tariff at least the original three-term tariff. This holds for all 4,960
retained target triples. Exactly six triples attain equality. This is a
computer-assisted finite geometric result with an algebraic reduction of
arbitrary coefficients, not a bound for other query rays or partitions.
The author proof and two separately implemented exact replays are complete;
independent human and formal proof-kernel review are unclaimed.

## Every reader belongs to one affine family

Because a,b,c have disjoint nonempty supports, they are linearly independent.
Comparing their coefficients in the query factor gives

    u12+u13+u123=a,
    u12+u23+u123=b,
    u13+u23+u123=c.

In characteristic other than two the solutions are exactly

    u12=(a+b-c-w)/2,
    u13=(a-b+c-w)/2,
    u23=(-a+b+c-w)/2,
    u123=w,                                                   (1)

where w is an arbitrary ambient vector. Substitution proves the target
identity, since the coefficient of w is
q123-(q12+q13+q23)/2=0. Thus this does not restrict the readers to the target
span. Independent query rescalings are absorbed into their readers and change
neither support nor tariff.

## Arbitrary coefficients reduce to three values per target port

At a port in A=supp(a), the first three doubled-reader entries are
(1-w,1-w,-1-w), while the fourth reader entry is w. The analogous triples
on B and C are (1-w,-1-w,1-w) and (-1-w,1-w,1-w). Hence each target port has
these support choices, with terms ordered 12,13,23,123:

| Port type | w=0 | w=1 | w=-1 |
|---|---|---|---|
| A | 1110 | 0011 | 1101 |
| B | 1110 | 0101 | 1011 |
| C | 1110 | 1001 | 0111 |

The symbols are support bits, not coefficient values. Since 0,1,-1 are distinct
in every field under consideration, this table is the same in every such
field. Every other value of w makes all four reader entries nonzero at that
port. Replacing it by zero deletes the fourth entry and preserves the other
three. Outside A union B union C, a nonzero w makes all four reader entries
nonzero, so replacing it by zero deletes all four.

Each replacement is still an exact identity by (1), and shrinks supports
term by term. Complete-plane closure preserves inclusion. Deleting rows or
columns of a matrix cannot increase its rank. Therefore every arbitrary
reader has a ternary specialization with no larger total tariff. Conversely,
every ternary assignment in the table is realized by (1). The exact minimum
over arbitrary ambient readers is consequently the minimum over
3^(|A|+|B|+|C|) assignments, with w zero outside the targets. This proves
that finite support minimization covers infinite coefficient fields and all
external reader directions. It does not transfer the identity to
characteristic two.

## Why 800 classes cover all 4,960 triples

Both alternating halves of an even group contain one port of each plane.
Switching a target to the other half moves each of its ports to its plane
mate. Its query closures do not change. Transporting the chosen w values
along those planes also preserves every reader closure, including when two
selected targets are the complementary halves of the same group. All four
term tariffs therefore remain identical.

There can be three distinct selected groups, or one group selected twice and
another selected once. Their respective class counts are
choose(16,3)=560 and 16*15=240. The primary solves these 800 classes. The first
kind represents eight half choices and the second two, giving
560*8+240*2=4,960 triples. In sorted target order, canonicalization replaces a
single target from group g by index 2g and a repeated group by 2g,2g+1.
Local port order is the retained plane order. This is an exact closure
symmetry, without any assumption that different groups are geometrically
interchangeable.

## Exact geometric minimization

The source labels are the pinned nine-bit q labels in DATA-PHASES.json. The
retained fixture supplies sixteen disjoint even groups, each with identity
binary Gram matrix. Both programs check that premise. The original target
from one half touches every plane in its own group, so its tariff is the
complete group size. Write m_A,m_B,m_C for those sizes. The original bill is
m_A+m_B+m_C, and the complete 32-indicator bill is 224.

For each query, the primary first takes a binary basis of its complete-plane
label span. Every possible reader plane contributes its two labels projected
by dot products against that basis. Incremental elimination builds a rank
lookup table for all subsets of at most twelve target ports. The lookup
entry is exactly the rectangular Gram rank. The primary enumerates the three
choices in the displayed table independently at every port, in value order
0,+1,-1. It retains the first minimum in that order.

The separate implementation imports no primary code. It uses the raw
rectangular Gram columns against all actual source ports, without reducing
the source to a nine-dimensional basis. It enumerates assignments in two
halves of the port list rather than three target blocks, and solves all
4,960 triples without the 800-class shortcut. Thus the second replay also
checks the symmetry used by the primary. For the selected minimum it checks
all 12,544 entries of the doubled integer operator identity on the full
112-port domain.

RESULT.json records every canonical minimum and one exact ternary minimizer.
The primary enumerates 185,031,864 assignments. The uncompressed all-triple
count is 1,084,757,832. Both programs agree on the SHA256 of the 4,960-row
stream
`0bbb26534e8d8b663647d16b2c063c0bed5a0305e6e4a1989f6e5292fdb8e160`.
Each row is the JSON array [a,b,c,original,minimum,w_0,...], with compact
separators and an ASCII newline; triples use lexicographic order and w follows
the concatenated local target-port order. The digest is a comparison aid;
the exact data and algorithms remain the evidence.

The minimum excess histogram is:

| Minimum minus original | Number of triples |
|---|---:|
| 0 | 6 |
| 1 | 324 |
| 2 | 4 |
| 3 | 1,392 |
| 4 | 14 |
| 5 | 1,180 |
| 7 | 1,568 |
| 8 | 64 |
| 9 | 408 |

The six equality triples are [6,24,25], [7,24,25], [18,24,25], [19,24,25],
[18,30,31], [19,30,31]. The first uses w=+1 throughout targets 6 and 24 and
w=-1 throughout target 25. Its bill is 16, the same as the original. The
retained per-class assignments provide attainment as well as exclusion.

## Relation to the earlier support-transfer failure

PR3515 proved that one nonconstant-reader specialization of (1) has no
same-target termwise support-shrinking completion in any characteristic-two
field. Its one-port switch census had best bill 20 versus original 16.
Here varying every port can lower that bill to 16, but cannot beat 16.
The previous support-transfer obstruction does not itself give a saving.
This package closes the full affine-reader question for these four query
rays and this literal partition; it does not republish that one-port census
or assert that every ternary specialization obstructs transfer.

The exact predecessor proof is retained unchanged, with its origin and hashes
in SOURCES.json, because (1) and the motivating support exception come from
that work. The identity and support reduction used here are proved above.
Tekalign's PR3370 partition bytes are also retained unchanged. No foreign Git
object or network request is needed for scientific replay.

Other rays, deformed coefficients in the queries, more terms, other target
blocks and other geometries remain open. Native acquisition, scalar execution,
frames, arbitrary dirty restoration, ownership, hosting, stock, precision,
physical consumers, all-size/compiler and outer multiplication implications
are unproved here. The selected frontier is unchanged.
