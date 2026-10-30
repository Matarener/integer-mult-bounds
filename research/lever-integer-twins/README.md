# Integer twins of three ideal lever combinations

**All three minimal reaching cells in PR3874 still clear its stated target after
integer rounding in the declared models.** This resolves its first open question
as an arithmetic screen. No physical realization, supplier or new kappa is
claimed. The selected conditional result remains 0.001672660197076918.

The most restrictive row tested preserves one identical integer paid profile in
every call and pools idle mass across nine calls. For selected-centre/rank8/u2,
its root is strictly between **0.010351600977 and 0.010351600978**, giving a
balanced-transfer kappa cap between **0.010245543201980** and
**0.010245543202961** (outward rounded here). Thus integer rounding does not
remove this cell's planning margin. However its remaining allowance at the
target is only **16 additional rank-one children per nine-call pool**; 17 fail.
This is an additive recursive-work budget, not a scalar-ADD tariff or permission
to ignore restoration and other costs.

## Exact question and source boundary

This takes Nick Petalas's [PR3874](https://github.com/CrocSwap/integer-mult-bounds/pull/3874)
Open next question 1 at `fb86b078a53042974d88b9758fe36622571349d0`, following the
[handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19028179).
The canonical claim/result lives in [Discussion2278](https://github.com/CrocSwap/integer-mult-bounds/discussions/2278#discussioncomment-19029577).
The original card is `complex-new-helper-inventory`, explicitly **changed** to
this requested pricing subproblem, not its physically-realizable-contract gate.

Keep width 73, 896 live families per nine calls, rank guard 51 and the following
three parent cells. Shared centre products stay rank 8, just as in PR3874.

| Cell | Variable paid mass per call | Variable rank cap | Fixed rank-8 children per call | Centre charge | Unpaid coordinates |
|---|---:|---:|---:|---:|---:|
| selected-r8-u2 | 5586 | 8 | 0 | 64 | 2 |
| shared-r32-u1 | 5522 | 32 | 4 | 32 | 1 |
| free-r16-u1 | 5522 | 16 | 0 | 0 | 1 |

The declared target is **kappa = 1/99**, following PR3874's explicit table.
Since kappa = a/(1+a), the correct moment test is **a = 1/98**.
Testing a = 1/99 would instead test kappa = 1/100. This package does not change
the repository's separate kappa > .01 planning objective.

For N calls, W = 896 N/9 and total rank mass is `(73-u)W + C N`.
Subtract the full paid mass to obtain idle mass. For u2 the per-call idle
average is `13918/9`; for the other two cells it is `1646`. Integral families
and the u2 mass require N divisible by nine. We test N=9 and N=144; neither is
asserted to be a legal physical pooling group for a future changed construction.

The integer twin allows variable ranks **at most** the named cap, including a
remainder child. Requiring every child to have exactly that rank is a different
model and can fail divisibility. This is the rank-cap interpretation requested
by the predecessor's proposed integer DP.

Two paid restrictions are kept separate:

* **uniform:** partition the variable mass into integer children inside each
  call, then repeat that exact profile N times;
* **pooled:** partition N times the variable mass with no call boundaries.
  This is a further relaxation, not a repeated local word.

Idle is independently pooled across all N calls in both models. Integrality is
imposed **before** dividing by W. In particular, nonintegral per-call averages
are not an aggregate impossibility. This follows the boundary correction in
PR3747 and the two-unpaid mass observations of PR3754/PR3757.

## Results

All rows have certified `moment(a_lo) < 1 < moment(a_hi)` with
`a_hi = a_lo + 10^-12`. Every target moment is strictly below one, checked by
both arithmetic engines. The kappa column is the lower endpoint of the
**model root's** transformed bracket, rounded for display; it is not an achieved
multiplication exponent. Exact fractions, full paid/idle histograms and target
moment intervals are in `RESULT.json`.

| Cell / calls / paid restriction | a lower endpoint | kappa bracket lower (approx.) | Extra rank-one children: maximum passing integer |
|---|---:|---:|---:|
| selected-r8-u2/9/uniform | 0.010351600977 | 0.010245543202 | 16 |
| selected-r8-u2/9/pooled | 0.010353593558 | 0.010247495158 | 16 |
| selected-r8-u2/144/uniform | 0.010351914854 | 0.010245850680 | 268 |
| selected-r8-u2/144/pooled | 0.010354156699 | 0.010248046816 | 272 |
| shared-r32-u1/9/uniform | 0.012857118397 | 0.012693911277 | 120 |
| shared-r32-u1/9/pooled | 0.012881196799 | 0.012717381703 | 121 |
| shared-r32-u1/144/uniform | 0.012861767247 | 0.012698442831 | 1931 |
| shared-r32-u1/144/pooled | 0.012887413706 | 0.012723441452 | 1946 |
| free-r16-u1/9/uniform | 0.011000817562 | 0.010881116386 | 62 |
| free-r16-u1/9/pooled | 0.011005405074 | 0.010885604586 | 62 |
| free-r16-u1/144/uniform | 0.011003116946 | 0.010883365997 | 1003 |
| free-r16-u1/144/pooled | 0.011008280352 | 0.010888417598 | 1009 |

The last column adds work to the complete base histogram with unchanged W and
**no compensating mass credit**. Both signs are certified at a=1/98: the listed
integer k passes and k+1 fails. Any combined realization charges must fit the
same moment slack; different-rank work must be priced at its own child cost. The surcharge is
aggregate and need not preserve the base paid word's per-call uniformity. If the
extra rank-one work must itself be identical in every call, the tight row allows
only one extra child per call (nine total); two per call exceed its limit.
These numbers do not price a complete producer, consumer, dirty restoration,
frame transport, precision or the bit supplier.

For the tight nine-call uniform row, paid `{8:6282,2:9}` and idle
`{51:272,46:1}` have masses 50274 and 13918, totalling
`64192 = 71*896 + 64*9`. Independent integer powers give the strict bound

    moment(1/98) < 111970002856773289113 / 112000000000000000000 < 1.

The other nine-call uniform paid profiles are
`{32:1548,18:9,8:36}` and `{16:3105,2:9}`. Both have idle
`{51:290,24:1}`. The pooled alternatives are printed in the exact receipt.
No all-24-cell integer lattice or antichain classification is claimed.

## Why the histograms are optimal in these models

Reuse the strict-concavity argument of
[PR1685's retained proof](../idle-packing-stability/README.md#proof-2-exact-integer-optimum),
credited to Penguin (OpenAI) for Maximus Putnam. For 0<a<1,
f(r)=(r/73)^(1-a) is strictly concave and f(0)=0. With two positive parts
x<=y<R, transfer delta=min(x,R-y) from x to y. The sum of their costs strictly
decreases; one noncap part disappears or becomes R. Repetition leaves only
floor(M/R) cap parts and, when nonzero, one remainder M mod R. Conservation of
mass uniquely determines this optimal histogram. At a=0 all partitions tie;
no endpoint uniqueness claim is made.

Apply this separately to each variable paid pool and each idle pool. The shared
cell's fixed rank-8 centre copies are excluded from optimization. In uniform
mode optimize one call then repeat; in pooled mode optimize the total. Thus
all root brackets describe exact optima of the declared integer partition
classes, not merely sampled candidate histograms. Strict monotonicity in a
holds because every child rank is below width 73. A moment below one at the
lower bracket and above one at the upper bracket enclose the unique root.
The physical restrictions absent from these classes can only worsen the optimum.

## Evidence and reproduction

Python 3.12, standard library only:

```sh
python3 -I -B research/lever-integer-twins/verify.py
python3 -I -B research/lever-integer-twins/independent_check.py
python3 -I -B scripts/research_package.py --package research/lever-integer-twins
```

`verify.py --write` regenerates the deterministic receipt. The primary verifier
reuses the pinned Colkitt/Claude atanh-log/Taylor-exp rational enclosures,
checks all 12 root brackets and surcharge boundaries, source constants,
fractional-ceiling domination and both pooling monotonicities. An independent
small mass-axis DP checks 224 cases (masses 1..32, caps 2..8) against the exchange
histogram. Nine malformed-domain controls reject fractional counts/mass,
wrong mass, rank 52, invalid pooling and out-of-range savings. These finite
controls support the implementation; the proof above supplies general optimality.

`independent_check.py` imports neither primary nor predecessor code. At a=1/98,
the cost is `(r/73)^(97/98)`. On the 10^-18 grid, L/10^18 is at or below that cost
exactly when `L^98 * 73^97 <= r^97 * 10^(18*98)`. Integer binary search gives
rigorous enclosures, then sums integer counts and divides by W. It independently
certifies all 12 target signs and both sides of each additive surcharge boundary.
Exact and irrational-square calibrations, actual failing moments, wrong target,
malformed receipts and off-by-one surcharge controls are included. It does
**not** independently certify the root brackets or derive the histograms.
All controls use explicit exceptions and remain active under Python -O.

`predecessor/grid.py` is a byte-identical retained PR3874 file, read only for AST
constants and never imported/executed. Its exact head, original path, Git blob
and SHA256 are recorded in SOURCES.json; the blob was matched to the GitHub
file response at that head. This external pending source is retained in-package
so replay does not need a foreign Git commit. Generic source-history checks bind
the base inputs; predecessor binding is the verifier's explicit byte check, not
an assertion that the foreign commit is in local history. No frozen predecessor
file is changed.

## Decision and limits

**Decision: narrow to realization pricing; no family expansion is justified by
this result alone.** Integer histograms and their model moments are proved and
checked as above. Realization, legal owner groups, source/consumer frames,
dirty compensation, restoration and precision costs are **unknown**, not zero.
The completed budget could fail once those are charged. No full selected cold
replay, Lean proof, supplier admission or bit-side improvement was attempted.
Independent AI arithmetic/review is not independent human or formal acceptance.

## Open next questions

1. Can a physical rank-8/u2 producer and consumer fit the tight cell's remaining
   moment slack? Name the source/consumer contract first, then charge every
   extra operation at its rank. The 16-per-nine-call rank-one boundary is a
   concrete stop test for an additive realization bill. Stop without a priced
   contract; another ideal ceiling calculation does not supply one.
2. Which idle pooling groups are legal for that actual changed construction?
   Extract owner/chronology restrictions before citing either unrestricted
   9-call or 144-call optimum as physically achievable. A pool size chosen only
   to clear denominators is not a hosting theorem.

## Scope, overlap and credit

Base `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority revision 6.
The entry overlap scan covered all 592 open PR bodies including drafts; the
repository helper used that complete paginated snapshot. Manual live checks
covered #1163, recent #1166, the active board, lever search and #2278. There was
no complete Discussion cache and sparse local package coverage; no-match is
not a novelty guarantee. Exact checkpoints and limitations are in TASK.json.

* Nick Petalas: PR3874's grid and requested integer continuation, PR3811's
  joint integer cap study, PR3754's pooled two-unpaid model. Exact heads:
  `fb86b078a53042974d88b9758fe36622571349d0`,
  `2205148748bbce47256e916d7485fc0219b8427f`,
  `4bde35c0200e83fe27a08ec408a2ae59b490a03f`.
* Arham Tahir: PR3747 aggregation boundary audit,
  `98847f9aba65ba835a15725c9f173c04a98788b3`.
* jwr404: PR3757 two-unpaid mass accounting,
  `f8c1754ad593ca1379d44c71722a9e9421caed3c`.
* Penguin (OpenAI) for Maximus Putnam: PR1685's integer optimum proof.
* Douglas Colkitt with Claude assistance: ceiling model and primary exact
  arithmetic; PR1012 coverage identity; Ali Romman and retained selected
  Rohan Arun/Jeremy Kothe/Hao Yan supplier lineage. Philippe Van Velzen's
  lever-map thread provides the canonical coordination context.

New contribution by ToikY with substantial OpenAI Codex assistance, Apache-2.0.
The new result is the integer continuation and surcharge boundaries for these
three cells, with independent target arithmetic; it does not claim the parent
grid, concavity theorem or aggregation correction as new.
