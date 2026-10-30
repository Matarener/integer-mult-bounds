# Exact dirty-connector cost with overlapping output windows

**Scoped recursive-interface result; no supplier or new kappa.** Allowing
output write windows to overlap can remove complete source/restoration calls.
For one immutable source and one arbitrary dirty connector, the exact query
optimum is a minimum-weight interval-hitting multiset with **even cardinality**.
A written all-word lower bound and an attaining schedule are in [PROOF.md](PROOF.md).

At uniform complete source-call price b, let tau be the minimum number of
slots hitting every output window. The exact bill is

```
2 sum_i a_i + 2b ceil(tau/2).
```

Here a_i is the complete price of reading the connector into output i.
Disjoint windows give tau=k, reproducing the one-source case of woklerx's
PR1442; a shared slot gives tau=1. A connected overlap chain can still need
more than two source calls. The parity rounding pays for restoring arbitrary
connector dirt. For varying source prices, the explicit last-hit/parity
recurrence gives the exact optimum; ordinary greedy interval stabbing does
not suffice.

This changes an observation/write-permission premise, not the scalar operation
alphabet. It does not reopen a closed search or assume that the selected
supplier grants early output writes. It complements PR1780's already solved
mutable-source, sequential-delivery contract rather than repeat it.

## A concrete comparison with the predecessor optimum

Use six outputs with windows [0,1], [1,2], ..., [5,6], one three-bit immutable
source, a three-bit dirty connector, and six three-bit dirty outputs. The
source map B=(3,6,7), written as binary row masks, is credited to PR1439.
Readers alternate the identity (1,2,4) and (3,2,4); they need not commute with B.
Every nonzero matrix entry is implemented as a literal scalar XOR.

The old disjoint windows are [1,1], ..., [6,6]. The new contract permits a
one-slot earlier write, with the same delivery cuts. The schedule pairs two
outputs around B at slots 1, 3 and 5 and closes the connector at slot 6.
There is no source change, extra data row, hidden copy, frame map or rounding.

| Exact local bill | Closed after each output | PR1442 disjoint persistence | Overlapping windows |
| --- | ---: | ---: | ---: |
| Complete B calls | 12 | 6 | 4 |
| Complete A calls | 12 | 12 | 12 |
| XORs / data writes | 126 | 84 | 70 |
| Data reads | 252 | 168 | 140 |
| Return-to-origin head steps | 1920 | 1572 | 1456 |
| Read-latch resets, including initialization | 127 | 85 | 71 |
| Equal-width 13-bit gate records | 1638 bits | 1092 bits | 910 bits |
| Arbitrarily dirty data bits | 24 | 24 | 24 |

Thus the new permission saves **14 XORs against the existing disjoint optimum**,
not all 56 XORs against the separately closed baseline. These are exact local
counts, not runtime measurements or unrestricted XOR-circuit optimality.

For the explicit head tariff, each XOR visits its source bit, visits its
target, and returns to position zero: 2 max(source,target) steps, two data
reads, one data write and one XOR. One common finite-control read latch is
initialized and reset after each gate; it is not an uncharged dirty tape row.
Each fixed instruction contains two five-bit addresses and a three-bit slot
label, for 13 bits. One dispatch per record and common fixed interpreter and
slot metadata are additional explicit charges. The immutable matrices are
compiled into the gate list; dynamic matrix multiplication is not free.
All three programs reserve the same data bank for the whole pilot.

## Complete recurrence and adoption boundary

For a compiled path c, the complete cost is

```
C(n,c) = P(n,c) + 2 sum_i C_Ai(n) + sum_t c_t C_B,t(n).
```

Each child cost includes its source access, helpers, frames, recursive work,
restoration and head return. P is all remaining caller preparation, program,
window control, lifetime/hosting, precision and storage work. The optimizer
minimizes the query part; it minimizes the whole expression only if P is
path-independent. Actual extra caller costs must be added, not assumed zero.
The finite binary pilot's costs are enumerated above, including restoration.

For the six-output comparison, extra physical caller work must cost less than
two complete B calls to retain a saving. Their saved cost vector is 14 XORs,
28 reads, 14 writes, 116 head steps, 14 latch resets, 14 dispatches and 182
bits of program storage; these components are not priced as zero. No selected native caller with these
permissions and tariffs is known from this contribution. No contracting
supplier recurrence, rank-profile improvement or numerical kappa follows.
Both suppliers and assembly constraints therefore remain unchanged.

## Reproduce

Python 3.12 and the standard library, from the repository root:

```sh
python3.12 -I -B scripts/research_package.py --package research/connector-overlapping-windows
```

Expected markers include:

```
PASS_CONNECTOR_OVERLAPPING_WINDOWS cases=5336 matrices=4096 controls=7 XORs=126/84->70 kappa=unchanged
PASS_INDEPENDENT_WINDOW_QUERIES cases=5336 settled=618645 dirty_inputs=1024
PASS_WINDOW_PACKAGE_CONTROLS
PASS_REGISTERED_RESEARCH_PACKAGE
```

The independent marker continues with its exact cost digest. Direct entry
points are `verify.py`, `independent.py` and `test_package.py` in this package.
Ordinary replay is read-only. `verify.py --write-receipt` creates an absent
RESULT.json exclusively and refuses to replace one.

Checked coverage:

- All 5,336 window/tariff instances: 1..4 slots, 0..3 outputs, every multiset
  of nonempty closed intervals, source prices in {1,3}, alternating reader
  prices 1,2. The scan recurrence and direct enumeration of slot
  multiplicities 0..2 agree; the attaining word passes every deadline.
- A separate full-query Dijkstra explores arbitrary A/B ordering and
  multiplicity without assuming paired readouts, interval hitting, or a
  two-call-per-slot cap. It agrees on every cost, settling 618,645 states.
- 4,096 two-bit matrix cases with arbitrary B and two arbitrary readers,
  including zero/singular/noncommuting maps, checked on every dirty column.
  The 24-bit pilot and both comparators also pass exact full-column replay.
- The independent bit-value interpreter checks all 1,024 dirty assignments
  of a ten-bit example at each deadline. Exact rational-price checks,
  chronology-neutral illegal writes, missing restoration, wrong outputs,
  invalid tariffs and actual source/receipt/algorithm corruption are covered.

The Dijkstra code imports neither the primary implementation nor predecessor
code. Both implementations have the same AI-assisted author; this is not
independent human review. Finite replay supports the written theorem, not a
formal proof of the full multiplication theorem.

## Provenance and scope

Exact base: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`. OS-random recorded
assignment seed **58** selects recursive interfaces. The six-output pilot
uses k=4+(58 mod 4)=6; the exhaustive domain is fixed independently of the
seed. Task selection, three candidates, stopping rule and local claim are
recorded in [TASK.json](TASK.json). No pinned coordination issue existed.

The selected record at this base is PR1094, kappa
`836330098538459/500000000000000000`. Its actual ASSEMBLY.json digest was
checked against the selected pointer; the current review, retained construction,
source manifest and review ledger were read. This is source-bound orientation,
not a cold supplier replay. `upstream/`, selected files and all frozen inputs
are unchanged.

Live predecessor text is pinned by Git blob and SHA256 in [SOURCES.json](SOURCES.json),
and every such input is declared in VERIFY.json. Catalogue and selected-record
pins are historical provenance. The entry overlap snapshot covered 476 open
PRs and 2,508 Discussion records with complete reported pagination, plus local
READMEs and the ledger. Specific window/interval queries found no equivalent
scope; that is not a novelty guarantee. See TASK.json for final refresh.

## Open next questions

Find one actual recursive caller whose output rows may be written in overlapping
windows while its source and connector chart stay fixed. This would determine
whether the abstract saving can alter a paid profile. First extract its literal
read/write/observation cuts and complete child tariffs, then apply the recurrence
and price additional reservation and dispatch. The blocker is a verified caller
and favorable complete invoice, not the finite window optimizer. Do not expand
this into a larger search without that caller. Structured details are in TASK.json.

## Credit

Credit **woklerx** for PR1442 (`7c573bc769798ce4e336fd5be630060bd9d69a71`),
the sequential-delivery lower bound and dirty-query construction, and PR1439
(`3852c2d03044895cebdc9b31b0c7131a617774d2`), the source matrix and mutable
correction pilot. Credit **Ross Richardson** for PR934/943's dirty connector
lineage and PR1780's exact mutable sequential optimum. Interval stabbing,
parity arguments and dynamic programming are standard methods, not new inventions.
The new result is their precise connection to this changed write-window contract,
its complete-query price and independently implemented evidence.

Prepared by **Yuzhou Wang (@yzhouwang)** with substantial **OpenAI Codex assistance**
in research, proof, programming, verification and writing. No subagents,
independent human review, hosted CI success or native supplier admission are
claimed. New files are Apache-2.0 under the repository LICENSE; predecessor
sources and notices remain intact.
