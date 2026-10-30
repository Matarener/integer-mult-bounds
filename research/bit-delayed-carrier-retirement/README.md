# A paid query saved by delayed carrier retirement

Changing the downstream compensation of the PR4068 shared-source packet gives
a strict saving in its **complete local recursive-query bill**. The Boolean
word uses **2912 queries instead of 2913**, and **35947 unit ADDs instead of
36005**. Every source, arbitrary dirty helper, terminal frame and private COPY
contract is preserved.

The mechanism bypasses helper469, a source50 carrier feeding helper413.
It retains both original rank-two queries on helpers413/444. This is a changed
consumer and compensation construction, not a joint-query implementation of
those two independent inputs and not a counterexample to the fixed-join result
in [PR4179](https://github.com/CrocSwap/integer-mult-bounds/pull/4179).

## The complete saving

Helper469 formerly followed `0 -> 52 -> 517 -> FULL`, with query ranks
`1,6,1`. Its replacement follows `0 -> 517 -> FULL`, with ranks `7,1`.
The rank-one terminal completion remains paid. No helper, source round trip,
private field or address operation is free by assumption.

For \(\Phi_m(r)=m^b r^{1-b}\), the full forward saving is

\[
\Phi_m(1)+\Phi_m(6)-\Phi_m(7)>0 \qquad (m>0,\ 0<b<1).
\]

At \(m=64,\ b=1/500\) it is between
`0.005774999958471154074171` and `0.005774999958471154074172`.
This is a small concavity gain; rank mass stays **5101**. All child ranks
are at most seven, strictly below the local dimension eight. The positivity
also holds with \(m=8\); it does not rely on interpreting the local dimension
as 64.

| Complete forward word | Queries | Rank mass | Unit ADDs | COPY/ERASE pairs |
|---|---:|---:|---:|---:|
| Frozen comparator | 2913 | 5101 | 36005 | 9 |
| Boolean candidate | 2912 | 5101 | 35947 | 9 |
| Same-integer-endpoint control | 2912 | 5101 | 36049 | 9 |

The candidate histogram is
`{1:1321,2:1342,3:79,4:39,5:102,6:10,7:19}`;
its change is `e7-e6-e1`. A separate execution of a complete inverse has the
same query bill; it is not counted as another saving inside the forward word.

## Construction and restoration

Target178 has its last private-port read at original record23865. Moving its
existing source50 read just after that COPY closes at23889 lets source50 make its
already-paid arrival at frame509 earlier. Helper413 waits there, reads source50
directly, then completes its original rank-two/rank-one tail and delivers to
478 before that helper's COPY begins at23947. The private port is zero throughout
the inserted packet; no recursive MOVE is introduced inside a live COPY.

Removing helper469's old entrance subtraction changes three dirty rows.
Their exact pullback shows that deleting **55 existing frame-zero
compensation reads of469** cancels the public Boolean error. Removing the old
source50 load/delivery/cleanup and adding the direct read saves another three
ADDs. Helper469's arbitrary input still takes the fully paid `7,1` terminal
route. It is retained as a width-eight helper.

[PROOF.md](PROOF.md) gives the literal edit recipe, the compensation table,
the exact chronology, and the framed-function proof. The candidate has exact
integer source/helper restoration and the same Boolean public map. Its public
integer lift differs from the comparator by `-2 h469` on 51 targets; this is
not hidden. A second executable variant replaces the old 55 compensation
reads with 102 literal unit reads and preserves **all 660 integer output
rows**, with the same query saving.

## Verification and scope

Two implementations reconstruct both candidate words directly from pinned
archives. The primary checker uses sparse integer rows and orthogonalized
frame bases; the independent checker uses dense columns and inverse Gram
matrices. They agree on the full literal-word hashes and invoices.
They check all 660 independent inputs, exact restored non-target rows, Boolean
public outputs, COPY guards, both inverse orders, and exact dyadic geometry.
There are 636 frame projectors and 2393 nested frame pairs in the candidate
(2394 in the union with the baseline). Eight controls detect missing source
delivery, missing terminal queries, stale dirt compensation, illegal timing,
dirty private storage and an underpriced query.

The Boolean candidate's signed row-l1 peaks are `1300/1444` forward/inverse,
versus `1302/1446` for the comparator. Positive majorant peaks are
`8401795/630740`, versus `8402567/630744`.
These are finite coefficient diagnostics, not new precision admission.

The exact stream identity holds for arbitrary Boolean-valued functions on
pair-address space over any odd-characteristic field. The framed induction
is a written proof supported by finite rational certificates; there is no
formal-kernel proof or fresh physical compiler run. In particular helper469
has its original **physical full-swap residual**, while its decoded dirt is
restored. It is not physically reset to the identity.

The parent tariff and legal unary-query alphabet are explicit. The changed
word has a smaller complete recursive-query contribution at the same parent
size and boundary. Chronological owner admission of the retimed local events,
physical routing, rounded-child errors, all-size dispatch/storage and joint
outer assembly remain separate. The frozen five-terminal comparator itself
does not have complete physical supplier admission. **No new kappa or selected
frontier change is claimed.**

## Reproduce

From the repository root, with Python 3.12 and its standard library:

```sh
python3.12 -B scripts/research_package.py --package research/bit-delayed-carrier-retirement
```

The registered hook checks both ordinary and optimized Python. A standalone
read-only export also works without Git or predecessor checkouts:

```sh
python3.12 -I -B /absolute/path/to/bit-delayed-carrier-retirement/verify.py
python3.12 -I -O -B /absolute/path/to/bit-delayed-carrier-retirement/verify.py
```

The expected marker is
`PASS_BIT_DELAYED_CARRIER queries=2913->2912 adds=36005->35947 no_new_kappa`.
[RESULT.json](RESULT.json) and [INDEPENDENT.json](INDEPENDENT.json) contain
complete deterministic receipts; the wrapper authenticates all package files
and compares complete typed JSON values.

## Open next questions

1. Can a chronological owner/controller admit the retimed source50 and
   target178 events with the unchanged width inventory? Start by binding the
   eight moved/inserted events to one actual caller. Endpoint equality alone
   does not settle caller access.
2. Can the shared source92 carrier470 be bypassed without extra paid access?
   The analogous direct retiming has a cycle through target128 and the
   helper478 COPY. A source92 out-and-back tour costs two additional rank-two
   queries and loses. A changed COPY reader is a different, unresolved route.

The structured questions and precise assignment change are in [TASK.json](TASK.json).
The original two dirty-input query floor remains intact.

## Sources and credit

The scientific base is `12fa8c5c844be21bfefb38a19503fbd867a11244`.
Both frozen archives are byte-identical to
[PR4068](https://github.com/CrocSwap/integer-mult-bounds/pull/4068) at
`5a34918402ae2c0c683d8820ad832970e77f6382`, and the public five-terminal source
in [PR4021](https://github.com/CrocSwap/integer-mult-bounds/pull/4021) at
`c01f97ecfc7fa64847f6abd8f7b231e1df8c7b70`. Exact source paths and hashes are
in [INPUT-SOURCES.json](INPUT-SOURCES.json).

Credit Ali Romman's R438/PR1043 source substitution, Sagar Thakrar's transported
word and window analysis, the PR540 frame semantics, PR589 hosting and PR1023
width conventions, and the five-terminal source contribution. Retained
controller credit includes DreamingOfClouds, Zhihao Chen, eumemic and chafreaky.
The generic source-bypass and framed-replay mechanisms are prior work.
The contribution here is this literal delayed-read window, its corrected dirt
compensation, and the complete strictly smaller query bill.

The earlier helper444/470 kernel entrance (Adam Gall, PR1179; later independent
native boundary work) changes a different entrance contract and requires its
own owner bill. Chris R / Clear1nsight's R437 carrier quotient and two-window
constructions use different source roles and contracts. Their helper numbers
do not identify this R438 source50 carrier. [OVERLAP.json](OVERLAP.json)
records the bounded live search; it is not a novelty certificate.

Ross Richardson, with substantial OpenAI Codex assistance in construction,
implementation, writing and separate AI review. Apache-2.0. No independent
human review is claimed.
