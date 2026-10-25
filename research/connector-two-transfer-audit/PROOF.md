# Coverage proof for the independent two-phase audit

This is a new verification of conorholds' PR2208 exclusion, not a new claim to
its tariff theorem. The source head is `28480ef4fdb4caeab89765ea56595bf1f6f37688`.
The exact retained bytes are pinned in SOURCES.json. No predecessor code is
imported by the new census.

## Contract and finite reduction

There are five immutable source rows, two arbitrary dirty roots, and 31 distinct
arbitrary dirty outputs, over F2. The allowed complete operations are
`B_j(p): z_p += B_j x_j`, `A_m(p): y_m += A_m z_p`,
`C: z0 += z1`, and `D: z1 += z0`. Each map is an arbitrary compatible linear
map, including singular and noncommuting maps. One word must work for every
choice. Each child restores its disjoint private scratch and agreed heads and
frames. Roots restore; outputs are observed only at completion. No extra root,
frame, clean row, source mutation, output feedback, combined call or direct
product operation is allowed. Physical port prices are additional costs.

We check words with 73 A/B calls and exactly two C/D transfers. Each of the 36
active maps must occur at least twice. A single B call leaves a nonzero
transported source column in the restored roots; a single A call leaves a
nonzero dirt row in its output. This argument uses invertibility of the binary
root frame, not invertibility of A or B. Consequently exactly one map occurs
three times and every other map occurs twice. The two cases are 10 B calls
with one three-read output, or 11 B calls with one three-insertion source.

The root frame restores only for CC or DD among two transfers. Swapping root
names sends DD to CC. We cover both orientations in the small direct oracle.

## Rotate to the first transfer

Let E be the desired endpoint, which fixes sources and roots and adds the
prescribed source-dependent translations to outputs. E commutes with every
allowed elementary operation, because sources never change and outputs are
never read. If a full word PQ has endpoint E, its cyclic rotation QP has
endpoint `P^-1 E P = E`. Inverses exist for every elementary update, even when
the A/B maps themselves are singular.

Rotate a successful full word to a C, then remove its A events to obtain a
skeleton of the form

```text
C, k source events, C, s-k source events;  0 <= k <= s.
```

All cut observations, including those between adjacent transfers, are retained.
A calls do not affect roots. For each target, readers can be independently
inserted at their chosen cuts. Their order does not matter under the offline
output contract. Thus removing A events loses no necessary candidate.

Five source pairs have `(10-1)!! = 945` canonical words. For an exceptional
source, rename it 0, choose its three positions, and pair the remaining eight
positions. This gives `C(11,3) * 7!! = 17,325` words. Ordinary labels are assigned
by first occurrence. The target family is invariant under these source
permutations. The implementation constructs perfect matchings iteratively,
then inserts the exceptional positions. It uses neither the predecessor's
recursive source-prefix generator nor its source/transfer merge enumeration.

## Solve restoration before choosing ports

Start just before the first C. A source increment deposited at physical port 0
has final root coefficient `(1,0)`, in either phase. A port-1 increment before
the second C has coefficient `(1,1)`. A port-1 increment after the second C has
coefficient `(0,1)`. These are the three nonzero vectors of F2^2.

Two increments restore their source exactly when their vectors agree. Therefore
a paired source either uses port 0 twice, or uses port 1 twice with both events
in the same phase. Three nonzero vectors sum to zero exactly when all three
are distinct. Therefore the exceptional source has one port-0 occurrence and
two port-1 occurrences on opposite sides of the second C. Choosing the port-0
occurrence and the freely eligible ordinary pairs exhausts every restoring port
assignment. The code separately replays every generated assignment and checks
the literal dirty-root endpoint with always-enabled error checks.

## Test all possible readers

Represent a root observation by its five source bits and two incoming-dirt
bits. Every nonzero dirt row is one of 1, 2, 3. A paired read cancels dirt if
and only if both dirt rows agree. Its source mask is their XOR. The census
computes the complete union of these masks, including zero.

Three reads cancel dirt if and only if their dirt rows are 1, 2, 3, one each.
For source-value sets S1, S2, S3 at those rows, the target m is available exactly
when some `a in S1`, `b in S2` satisfy `m XOR a XOR b in S3`. The code tests that
condition, without a support or phase restriction on the target.

In the exceptional-output case, the 30 ordinary targets require paired reads.
Coverage below 31 including zero cannot suffice. Coverage 31 leaves one missing
nonzero target, which the exceptional triple must supply. Coverage 32 would be
a favorable acceptance even before checking whether some target has a triple.
There are no coverage-32 cases. Each of the 132 coverage-31 cases fails the
triple repair test. In the exceptional-source case, all 31 targets require
paired reads; again none has coverage 32.

| Exceptional map | Canonical source words | Phase cuts | Restoring assignments | Maximum paired coverage | Successful repairs |
| --- | ---: | ---: | ---: | ---: | ---: |
| One output, three reads | 945 | 10,395 | 145,080 | 31/32 | 0 |
| One source, three insertions | 17,325 | 207,900 | 1,401,120 | 31/32 | 0 |

These exact finite counts cover arbitrary linear-map dimension through the
formal source/dirt identity. They do not infer an all-size circuit theorem from
sampled dense matrices. The proof of exhaustive normalization and the complete
finite census together establish this scoped exclusion.

## Full-histogram counting identity

The predecessor enumerates linear skeletons with either CC or DD and every
source/transfer interleaving. Our census fixes the first transfer to C. Let
`ell = s+2`, namely 12 or 13. First work with fully labelled sources. Mark one
of the two transfers in a predecessor skeleton. There are two marks per word.
Rotate the marked transfer to the front and, if needed, exchange root names.
A normalized skeleton has ell choices of the old starting position and two
choices of old transfer orientation. Hence

```text
2 * old_count = 2 * ell * new_count.
```

The equality counts marked objects, so rotational stabilizers cause no
exception. Source relabelling acts freely, and dividing by 5! for the paired
case or 4! for the distinguished-source case preserves the identity. Every
cyclic shift changes observations by an invertible dirt-coordinate change and
a dirt-dependent source shift. Both two- and three-read zero-dirt sums preserve
their masks. Thus each individual paired-coverage histogram bin, as well as
successful triple repairs, scales by ell.

The new checker recomputes every bin and compares it with the pinned native
receipt after multiplication by 12 or 13. A fresh run of the predecessor's
unchanged C++ census matches every retained bin at 1,740,960 and 18,214,560
assignments. This is agreement between two separately structured implementations,
not merely agreement on their final zero-success totals. These are exact
combinatorial counts, not performance measurements.

## Independent controls and limits

A separate direct oracle enumerates every labelled small source word, filters
multiplicities and label symmetry afterward, then tries all port bitstrings.
It represents rows as sets and executes both CC and DD literally, without the
restoration shortcut. It agrees on all 116,400 attempted small assignments,
all 2,796 restoring cases, their full observation sets and every two- and
three-read mask. Its domains are two and three sources, for both multiplicities.

Actual two-source 13-call positive words include a three-read output and a
three-insertion source. They and the credited 74-call one-root and 78-call
six-transfer five-source witnesses pass 552 complete dirty-basis/mixed-state
forward/inverse pairs at widths 1, 2, 3. All 356 single-call omissions and
port/direction changes fail. The maps include explicit singular and
noncommuting fixtures. Three out-of-domain census requests fail.

The original 72-map/fewer-than-six-transfer exclusion, six-transfer attainment,
74-map one-root attainment and resulting equal-price formula
`min(74c, 72c+6sigma)` remain predecessor results. This package independently
checks only the 73-map/two-transfer implication needed there. It does not cover
unequal complete map/port prices, a real selected-supplier caller, complete
physical admission or hosting, precision/tape, both supplier moments, a new
kappa, a selected-frontier change, or formal proof-kernel review.
