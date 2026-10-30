# A shared compensation basis, and a bounded factory screen

Status: locally checked finite construction and scoped negative screen. The
compensation word is exact and reduces a finite scalar bill. Its recursive
histogram is unchanged, so this work establishes no new conditional kappa.
No public action, repository edit, native replay or full release was performed.

## Pins and input contract

The immutable comparator is PR3605 head
`3efbb5de06a49ffeea6684482f2d3fe48cdca3fb`, scientific commit
`c006ddb034f5efcb0706a5d8207d38c367a99ace`, under canonical guidance
`20ecf2891d80b5acf18d980b2164fb44ea7faa90`. The two source blobs are
`research/staged-644-660-width-reduction/STAGED644-660-{base,extra}.json.gz`.
Their compressed SHA256 pins are respectively
`735c540b1fe29d0ceeb4d2f304ec941e5f2bd3bc92bafc8cce2b4f9a67a3b653` and
`886338fc32da14f3389a82c8120a1bcf9c5e2f0ec3e9b2d377fdae809e1d977f`.
The predecessor local package is `ac92a027c78b0c9bb0ada739b26959afda489d0e`;
its PR3133 word source is `51eb9c4ee9e4722010d308aa3309e039d3940cc2`.

All 632 live source, target and helper inputs are arbitrary independent module
elements over the dyadic rationals. No helper is initialized to zero by this
rewrite. The source's 91 private cleanup buffers retain their zero-input and
zero-output contract. There are 112 targets and 408 actual live helper roles;
the historical R=480 field includes 72 removed identities. The ordered ports,
centers, native charts, helper identities, entrances and ends are unchanged.

## Actual combined word and current compensation pullback

Let y be the 112 target coordinates and z the other raw live coordinates at
the existing frame-zero compensation interface. The old word is

    (y,z) -> (y+Cz,z).

Its 5736 literal additions aggregate to a rational matrix C of rank 56 on 207
nonzero helper columns, in both providers. A 14-block division into the actual
eight-consecutive-target address ranges has summed block ranks 104. That sum
does not equal the joint rank and cannot be used to price independent bases.

Choose 56 actual rows of C as a basis. For each remaining row write
`C_r = sum_s b_rs C_s`, where s runs over the chosen target rows. The producer
tries four fully specified row orders and selects the least literal gate
count among the dyadic bases obtained. Define E by

    y_r -= sum_s b_rs y_s       (nonbasis r),
    y_s unchanged              (basis s).

The support is bipartite: basis rows are never changed and nonbasis rows are
never read. Thus E is invertible and the inverse consists of the negated gates
in reverse order. Here E needs exactly 56 unit-coefficient additions. Every
one of these additions crosses two of the displayed eight-target ranges.
For example, the exact current rows satisfy

    C_125 = C_139 + C_190,       C_133 = -C_123.

Consequently the two beginning updates to target125 are
`125 -= 139; 125 -= 190`. Its correction is then supplied by the shared basis
rows and the final inverse updates. The already arbitrary dirt in targets
139 and 190 cancels exactly when E is reversed.

Replace only the compensation section by the chronological word

    y <- E y;
    y <- y+(E C)z;
    y <- E^-1 y.

The new correction is EC at this *current target-basis cut*. Using C there
would be a stale pullback. Direct multiplication gives

    E^-1(Ey+ECz) = y+Cz.

The other live coordinates are fixed throughout. This block identity is valid
on arbitrary inputs over every dyadic module. Every independent noncommuting
invertible warp in the surrounding supplier is retained literally; the changed
subword is already equal before any surrounding operator is composed. It does
not assume commuting or identical warp operators.

`SHARED-COMPENSATION-{base,extra}.json.gz` contains the entire new subword.
The replacement is identical in both providers, with decompressed SHA256
`9f242abd5d2ed46a2e95dad46449d1d77c6fec330b5e0db6b324ac93fe756e62`.
`SHARED-WORD-{base,extra}.json.gz` contains each complete changed supplier.
All other fields, including the 5222-gate literal inverse cleanup, are copied
unchanged from the pinned word. The target-only replacement has the same full
interface, so the old helper row/column identities, arbitrary entering dirt
restoration and 91 cleared private buffers remain exactly the same.

The inverse of the new subword is obtained by reversing it and inverting every
addition; equivalently it is E, followed by `-(EC)z`, followed by E^-1. The
same-chronology inverse-transpose has block response `z <- z-C^T y`. The
independent checker executes every literal gate in both orientations on all
632 input columns. The producer also rejects a stale C pullback and a missing
inverse basis gate; the independent checker rejects a literal final-gate sign
defect in both orientations.

## Complete changed bill

All new operations are at the existing frame-zero compensation interface.
The source transport and normalized wrapper words are retained with their
original constant charges. This does not make those charges zero.

| Component | old additions | new additions |
| --- | ---: | ---: |
| Target basis E | 0 | 56 |
| Helper-to-target correction | 5736 | 3102 |
| Inverse target basis | 0 | 56 |
| Total | 5736 | 3214 |

There are no added scale gates, helper roles, zero buffers, source queries,
native warps, or recursive children. The local profile remains
`{1:2439,2:726,3:224,4:102,5:20,8:8}` and the ordered helper widths remain
`{4:26,5:2,6:18,7:52,8:97,9:213}`. Thus Delta H=0, every helper-width delta
is zero, and the complete recursive moment is unchanged for every exponent.

Under the stipulated cleared-work component price

    p(a/2^d) = 3 + floor(log2|a|) + popcount(|a|) + d

for a reduced nonzero dyadic coefficient, the exact bill in *each* forward
or inverse-transpose orientation is

| Component | primitive cost per real component |
| --- | ---: |
| Old compensation | 31214 |
| New basis | 224 |
| New correction | 16886 |
| New inverse basis | 224 |
| New total | 17334 |
| Difference | -13880 |

With two real components, old/new totals are 62428/34668 and the saving is
27760 cleared-work primitives. The 112 total basis additions cost 448 per
component, or 896 across both real components, and are included above. The
entire signed coefficient histograms are in `INDEPENDENT-SHARED.json`; no
coefficient-changing operation is priced by logical-gate count alone.

## Prefix bounds and remaining numerical gate

The following are exact maximum prefix matrix norms for this component, from
the identity on the 632 live coordinates, including E and its inverse.

| orientation | old max norm1 | new max norm1 | old/new max norm-infinity |
| --- | ---: | ---: | ---: |
| forward | 79 | 79 | 151/4 |
| inverse-transpose | 151/4 | 153/4 | 79 |

The literal reverse-inverse word has the same new bounds in the respective
orientations. Every exact prefix coefficient has denominator dividing 2^3;
the maximum reduced numerator bit length is three. These depth bounds match
the old component. The dual norm1 increase of 1/2 is real. The *whole supplier*
prefix, adjoint weights, rounded grid reserve and finite controller/tape bill
have not been rebound to the replacement. These component bounds alone do
not certify an existing whole-word precision reserve.

## Bounded factory and complement screens

These screens were chosen to test a premise beyond the prior fixed584/590
recovery and enlarged644/660 entrance routes. They do not imply a universal
source-factory obstruction.

First, the exact full non-target maps P and P^-1 were computed over the free
group algebra of all independent warp letters. For every selected low-frame
output pool I and protected input set J, scalar row/column annihilation is
expanded separately for every formal operator word before taking rational
kernels. This is not a scalar projection of noncommuting operators.

An equal-clean source/copy exchange whose row difference involves only cold
inputs preserves P[:,J], provided J protects true sources and entering helper
dirt and the suffix is fixed. A cold-only invertible input premix also preserves
that block. Hence these changes cannot enlarge L=leftker(P[I,J]). At the
current rank-four pools all 26 rows are already saturated. Every current pool
through rank seven has rank(LK)=dim L, so a swap-only change at those exact
pools cannot add a direction. A general changed complementary clean basis or
changed suffix falls outside this observation.

The paid-tail screen protects all 91 existing ended helper inputs and excludes
their output rows, so it cannot re-count an existing end. Among the 100
distinct joins of two current rank-six last frames having rank at most seven,
every complete low-supported pool has L=0. No cold direction is available by
only changing the cold input basis and appending a tail at these joins.
`JOIN-SCREEN.json` contains every exact pool and pairing dimension.

The genuinely changed complement screen uses the 28 independent A-end
two-coordinate source pairs. Eight pairs have a native warp on a changed wire
and are excluded. For each of the other 20 pairs it inserts an invertible T
after A and conjugates *every* subsequent cut/B/restore read and producer by
T, retaining all warp letters on other wires. For an outside read the new
coefficient row is the old row times T^-1; for a producer it is T times the old
column. Mutable cells therefore remain in the current basis at every use.
Read combinations are merged only by checked commuting transpositions and
never across a warp sentinel. All old helper identities remain identities
under this change because the final non-target map is T P on the two source
rows only. Its cleanup is the reverse-inverse of the complete changed
non-target word, with the same ended-helper substitutions; an inherited old
cleanup is not asserted for a rejected candidate.

The finite domain consists of the 20 original-coordinate bases and, for each
pair, both triangular shears with coefficient in
`{-4,-2,-1,-1/2,1/2,1,2,4}`: 340 candidates per provider. All 680 complete
forward contact patterns fail monotone native frames with the old target
cuts, native charts, 91 helper ends and chronological order retained.
`FRAME-WITNESSES.json.gz` stores a concrete increasing contact path for every
case, including the forced direction and endpoint cap. An independent small
GF(2) verifier checks consecutive shared-register contacts and a separating
normal at the endpoint. `FRAME-WITNESS-SUMMARY.json` records the exact domain
and decompressed witness hash. An arbitrary larger GL basis, changed chart,
target endpoint, source assignment or whole consumer network is not excluded.
Rejected candidates have no admitted paid profile; unknown adapter/native
costs are not assigned zero.

## Reproduction and attribution

The positive construction and independent check use Python's standard library:

    python3 -B shared_compensation.py
    python3 -B check_shared.py

The source blobs must be present at the exact Git head above. The screen scripts
reuse the frozen source frame engine, with its exact path and source pins in
the preserved script imports, and the existing local venv only for mpmath.
`frame_witnesses.py` rechecks the literal path certificates without relying on
the optimizer's cost output. `MANIFEST.json` binds the local evidence files.

PR2857/Yiyang Lu's shared compensation-kernel method and PR2894/Jeremy Kothe's
preload composition are separate predecessor mechanisms. PR2696/Mason Hale and
PR2751/Tekalign supply the exact dirty source-recovery lessons. The historical
Gauge44 source/copy and complementary-basis construction is credited to
icekylinx with OpenAI GPT-6 Astra assistance, with its PR531/PR635/AtomScout and
native lineage retained. None of those historical results certifies this
changed word. The actual present source is dcharb78's PR3133 and Ross
Richardson's PR3605, with all credits and notices in their pinned packages.

The new local contribution is the emitted shared target-basis compensation
word, its exact cleared-work and prefix bill, and this bounded full-suffix
conjugation screen. Prepared with substantial OpenAI Codex assistance. Separate
AI checks do not constitute independent human review or formal-kernel proof.

Possible standalone publication requires checking the prior compensation
forest and two-sided target-basis literature against these exact words and
binding the whole finite scalar/numerical invoice. `PUBLICATION-OVERLAP-LEADS.json`
records cache leads, not novelty evidence. No publication is promised. Native
phase/compiler binding, whole-word precision, owner/physical admission, all-size
compiler/source access/hosting, SCALAR/COPY/CLEAR allocation, finite tape costs,
recursive rounding, bootstrap/PR559 recovery/analytic transfer and BIT H1-H5
remain at their inherited scope. This work does not alter the selected record.
