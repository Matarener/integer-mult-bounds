# B02 independent owner and moment review

Status: **PASS within the fixed contracts below. No new supplier or κ.**
Reviewed 2026-10-20. This review imports or executes no producer module.
`check_owner_accounting.py` independently reconstructs the actual chronological
windows, selected slots, physical owner rows, complements and complete
histograms. Its regenerated receipt is `OWNER-REVIEW.json`.

The source scientific base remains
`20ecf2891d80b5acf18d980b2164fb44ea7faa90`; the current checkout is used only
for byte-identical pinned predecessor files. The three file hashes in
`BIT-OWNER-PRUNE.json` still match, as do all consumed PR2653 source inputs.
The source word is PR2423's R438 word, gzip SHA256
`a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022`.
The independently rebuilt old slot digest matches
`1ef76bb87f1cfac7b4281c308bd71064c1fb1b6b4b267cfe9f3290212a5de11e`;
the restricted slot digest matches
`5b2189e714523b5fa8b01e5aee52f332511920fa4620104b2a894907b57cc238`.

## Fixed physical contract and returned rank

There are 111 ordinary ports, nine local stages, 32 replicas, ambient rank
64 and 28,416 live data families. The physical family formula is

```
replica*888 + (2*pair+side)*111 + port.
```

The allocation has ten pending children per physical port/side, including
one zero-rank child. It retains all 71,040 physical deadlines. Each hosted
helper is a complete width-eight slice in its original pending child;
there is no repacking, changed offset or borrowing-window relaxation.

The helper numbers 249 through 257 correspond to old physical registers
471 through 479. Exactly nine such helpers are deleted at each of nine
stages: 81 deleted occurrences per replica, each width eight. The actual
remaining set at every deadline is the old remaining set disjointly united
with the deleted slices. Consequently

```
returned idle rank per replica = 81*8 = 648.
```

The remaining 3,861 roles per replica give 123,552 roles over all replicas.
The independent owner and factorization digests agree with the historical
receipt for both the old and restricted allocations.

The complete idle profiles, including rank zero, are:

```
old: {0:222, 2:433, 4:444, 6:444, 7:666, 34:1, 42:10}
new: {0:222, 2:420, 4:435, 6:435, 7:666, 10:2, 14:9,
      18:2, 26:2, 28:9, 34:3, 42:15}
```

The source projector chart consists of the root line, all seven root-
orthogonal axes, and exterior coordinates. Every retained slice and every
new remainder contains either all seven root-orthogonal axes or none.
The set partition therefore is a partition into actual orthogonal
projectors, rather than only a dimension sum. For
`D(P)=[[I-P,P],[P,I-P]]`, orthogonal `P_i` satisfy
`product_i D(P_i)=D(sum_i P_i)`. This identity holds on arbitrary head and
tail vectors; no zero-helper premise is used. The finite set/owner
reconstruction binds that algebraic identity to this fixed allocation.
The inherited whole-call realization and early-preload/late-X code-window
arguments remain distinct from the projector identity.

## Complete histogram and the two baselines

The old local rank mass is 5,121 and the pruned mass is 4,989. The apparent
132-unit saving consists of 72 deleted-helper units plus 60 COPY units
(nine rank-seven copies replaced by three rank-one copies). The first
72 units return to the idle invoice. The complete net saving is therefore
60 per local call, or `288*60=17,280` globally.

The complete local-plus-idle histogram is reconstructed directly as
288 local histograms plus 32 idle histograms:

```
H = {1:373824, 2:399936, 3:22752, 4:26592, 5:26784,
     6:17088, 7:23904, 10:64, 14:288, 18:64, 26:64,
     28:288, 34:96, 42:480}.
```

Its mass is **1,791,072**. The known two-N terminal adds
`2*4*111=888` rank-one children per replica, hence 28,416 globally.
The completed histogram differs only at rank one, which becomes 402,240;
its mass is **1,819,488**.

| Comparison | Exact quantity |
| --- | ---: |
| Old complete candidate mass | 1,808,352 |
| Pruned prefix mass | 1,791,072 |
| Pruned prefix plus known terminal mass | 1,819,488 |
| Available rank budget `64*28416` | 1,818,624 |
| Terminal excess over old candidate | 11,136 |
| Terminal excess over available budget | 864 |

The receipt field `zero_exponent_two_N_excess_over_baseline=11136` uses
the old candidate as its baseline. It is not the excess over stock.
Both numbers are correct; publication prose should explicitly distinguish them.

For the stated moment convention

```
M(a) = sum_r H[r]*(r/64)^(1-a),  with acceptance M(a)<28416,
C(a) = 64*M(a) = sum_r H[r]*r*(64/r)^a,
```

every retained child has `0<r<=42<64`. Thus for every real `a>=0`,
each tariff is at least its rank, and

```
C_completed(a) >= 1819488 > 1818624.
```

This is a direct lower bound on the true moment, not failure of a sufficient
upper estimate. Additional nonnegative fallback, precision or routing
charges cannot reverse it at the same stock. A changed stock or child-rank
contract requires a different argument. Rank-zero census entries are
excluded before taking powers, including at `a>=1`.

## Useful sharpening: a uniform prefix price comparison

The signed histogram `H_pruned-H_old` is

```
{1:-6912, 2:-416, 3:0, 4:-288, 5:-2592, 6:-288,
 7:-2592, 10:64, 14:288, 18:64, 26:64, 28:288,
 34:64, 42:160}.
```

Its rank-mass sum is -17,280. Every negative entry is at rank at most
seven, and every positive entry is at rank at least ten. For `a>=0`,
`(64/r)^a` is decreasing in `r`; using separating rank eight gives

```
sum_r (H_pruned[r]-H_old[r])*r*(64/r)^a
    <= (64/8)^a * sum_r (H_pruned[r]-H_old[r])*r
     = -17280*8^a < 0.
```

This proves a strict uniform price comparison for every nonnegative real
exponent. It does not compare two suppliers satisfying the same endpoint
contract: the new prefix still has a coded endpoint requiring repair.
In particular it does not contradict the completed-word obstruction.
No numerical root search or formal-kernel proof is claimed.

At exponent zero the available terminal rank budget is
`(1818624-1791072)/32=861` per replica. Strict acceptance requires an
integer terminal bill at most **860**, before any further charges.
Therefore an alternative to the 888-call construction must save at least
**28 rank-one units per replica** merely to pass this necessary first gate.
Saving 27 leaves equality and is insufficient.

## All odd-stage accounting identity

Under the specified ordinary-coverage ledger, let `B>=1`, `L=2B+1`,
and let `n` be the port count. Before the three rank-one local repairs per
stage, the deficit is `(L-1)n`. After those repairs and the stipulated two
endpoint normalizations on every one of the `Bn` hole fields, it is

```
D = (L-1)n - 3L - 2Bn
  = 2Bn - 3L - 2Bn
  = -3L < 0.
```

With `T` replicas the mass excess is `3LT`. At `B=4,L=9,T=32` this is
864. The general necessary integer terminal budget for strict passage,
before other charges, is `2Bn-3L-1`, whenever that number is nonnegative.

This is a written all-parameter implication from the given coverage,
repair and terminal costs. It does not construct or admit a hosted
controller for every B. The inherited generator itself only emits the
fully banked layout at L=9. The checker includes 2,048 finite arithmetic
sanity cases; those cases do not replace the displayed algebraic proof.
The all-nonnegative-exponent conclusion additionally requires every
counted child to have positive rank at most its ambient rank, as verified
for the fixed nine-stage histogram.

## Original-input gauge and source-access boundaries

The actual terminal expression is `N E^-1 N`, where the diagonal fieldwise
operator `N` uses `D(P_q)` and `P_q=q q^T/4`. These rank-one projectors
come from the pinned 111 root lines. The checker verifies the involution
on all 1,776 rational basis columns and constructs 111 one-gauge omission
witnesses: for `E=I`, the correct two-gauge map is identity, while one
gauge sends `(q/2,0)` to `(0,q/2)`.

More generally, for every invertible E and nonidentity N, removing only
the left N changes the map: `(N-I)E^-1 N` is nonzero. Removing only the
right N also changes it. This is an arbitrary-input algebraic statement,
independent of coefficient estimates. Removing both gauges can succeed
when E commutes with N; no universal obstruction to that separate
possibility is claimed. An actual commutation or joint-decoder word must
be supplied before charging such a cancellation.

The number **888 is the bill of the known complete construction**. It is
not a lower bound for every terminal decoder. The number **444** is the
source ascent cost of the specified all-bank FULL gather: four banks,
111 rank-seven caps each, each lifted to FULL by one rank-one child.
It is not a universal observer lower bound. A different observer, copied
query or legal shared cut needs its own ordered arbitrary-input access,
dirty-workspace and restoration contract.

In particular the proposed 288-unit descent assumes a nine-channel native
factorization inferred only from scalar augmentation. The actual ordered
word currently supplies an 81-channel factor. This review does not prove
that 81 channels are necessary; it records that the nine-channel native
factor and its readout are unbuilt. Even granting that factor, the stated
FULL-gather construction would add at least its own 444 ascents to the
288 descent, before output alignment and cleanup.

## Validation, provenance and remaining obligations

Run from any directory, with Python 3.12 or later:

```
python3 -I -B /absolute/path/to/b02-review/check_owner_accounting.py
python3 -I -O -B /absolute/path/to/b02-review/check_owner_accounting.py
```

The receipt contains every fixed histogram, deleted slot, source hash and
owner digest. Four injected accounting faults reject the missing physical
idle complement, false 132-unit net saving, missing second gauge charge,
and a child rank above ambient. The native gauge omission witnesses are
separate exact operator controls.

The established 651-column integer/F2 local operator identity is inherited
from published [PR3645](https://github.com/CrocSwap/integer-mult-bounds/pull/3645)
and is not re-executed by this package. This independent checker consumes
the pinned local receipt, whose forward and inverse paid profiles agree.
The separate parent-owned `native_remainders.py` binds the actual published
`WORD.json.gz` to all local frame events, paid ranks and COPY lifecycle, and
checks the changed owner remainder operators. Its
`NATIVE-REMAINDERS.json` records 326,784 exact ADDRESS basis columns; this
is not a full integer/value replay of the local operator identity.
The recursive/owner specialists retain the whole native code-window
realization and terminal owner-allocation
obligations; rounded-network/machine specialists own child-error,
precision and physical tape interfaces if a future construction survives
the cost gate.

No defect was found in the supplied B02 numerical claims. The most useful
presentation corrections are the two explicit excess baselines, the
conditional nature of the all-B ledger, and the construction-versus-lower-
bound distinctions for 888 and 444. The uniform prefix comparison and
860 strict terminal budget are safe additional deductions.

Credit: Ali Romman's PR1043 R438 word, Sagar Thakrar's PR2423 transport and
rehosting, commdata2338's PR2653 pending-projector audit and its PR1307
geometry predecessors; the local source-code, support-pruning and
recursive audit lanes identified in the preserved source handoff.
Prepared for Ross with substantial OpenAI Codex assistance. No human
independent review or formal-kernel proof is asserted.
