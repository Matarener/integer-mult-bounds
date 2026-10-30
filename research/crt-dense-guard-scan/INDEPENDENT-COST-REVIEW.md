# Independent literal dense-guard machine review

Reviewer: independent OpenAI Codex agent, not human or formal-kernel review.
Scope: the admitted ordered-stencil transducer, its complete address counter,
owned mask and physical head/cleanup tariff. The semantic guard predicate,
good-set theorem, compact inverse/repair and reservoir descriptors are
predecessor work. This review adds no E evaluator, physical compact switch,
payload movement, precision or multiplication theorem.

## Quantified interface and constructive cost argument

Let a protected stencil have L>=1 data cells and explicit boundary markers.
Each data symbol comes from one fixed finite product alphabet. It describes
an untested bit, a bit of an active all-ones digit test, or a guard-comparison
bit with its two threshold bits; interval begin/end flags determine when the
finite comparison state resets or contributes to the final conjunction.
Assume this stencil is well formed, ordered and complete. Geometry parsing,
sorting, source-descriptor transport, threshold/stencil construction and
admission are dependencies unless the submitted machine literally executes
and charges them. Their host adapters cannot be silently included in this
transducer's invoice.

A private L-bit counter starts at zero. On each pass, scan its bits and the
stencil from most significant to least significant. One all-ones flag, two
three-state less/equal/greater flags, a running conjunction and a fixed
control mode suffice. They are finite state, independent of the number of
intervals and of L. This scan needs neither an interval-ID array nor a
numeric address register. The lower threshold accepts equality; the upper
threshold rejects equality. The target parity bit, inactive high compact
digits and dirty spectator bits remain untested by the source-bound stencil.

Append exactly one classification bit to one owned mask tape. Increment the
counter using a literal binary-carry walk, with tape-marker tests and all
head motions charged. Stop only on left-marker overflow after processing the
all-ones counter. Do not use a host loop through range(2^L), an uncharged
numeric address/position variable, or a test-fixture fuel counter as the
machine's termination criterion. The loop invariant is that its counter is
the next address and every previous address has been classified exactly once.
Therefore the owned mask has M=2^L bits in increasing address order.

One aligned scan and returns, one binary-carry increment and returns, and a
constant amount of finite state work per visited cell cost O(L) transitions
per emitted bit. Initialization and final erasure/returns cost O(L), and
returning the owned mask head costs O(M). Thus time is O(ML) and total visited
space, including protected input and owned mask, is O(M+L). The tape-role
inventory is fixed. No source-function or E-evaluator call is needed to
classify any address.

For the retained source family, L=Theta(p) and R=Theta(p), hence L=O(R) and
O(ML)=O(MR)=O(V). The final equality cannot be asserted for arbitrary positive
record width R. Mask classification also does not include payload reading,
exception extraction, key computation, sorting or reinsertion.

## Exact counter check independent of the implementation

Across x=0,...,M-1, the sum of trailing-one counts is

```
sum_(k=1)^L count{x: x has at least k trailing ones}
= sum_(k=1)^L M/2^k = M-1.
```

Every nonoverflow increment also reads/writes one terminating zero, and
there are M-1 such increments. Consequently a straightforward binary carry
routine changes exactly `2M-2` counter-bit cells across the entire run:
`M-1` one-to-zero changes and `M-1` zero-to-one changes. Marker reads, head
movement and final blank erasure are additional paid work. This is an exact
all-size identity, not an extrapolation from finite receipts.

Overflow restores all counter bits to zero. Zero is distinct from blank,
so this is not by itself private-work erasure. A claimed blank-return
contract must execute a final erase pass (including any owned boundary
marker) and return that private head. A weaker reusable-zero counter
contract must be named explicitly instead.

All successful-call protected inputs must be unchanged and their heads
returned. The final owned mask remains the output, with its head returned;
it must not be erased as private work. Repeated invocations reuse these
fixed physical tape roles only after their previous owned outputs have been
consumed/transferred and the relevant role has been prepared for reuse.

The exact submitted transition invoice and frozen file hashes are recorded
in the final section and accompanying receipt after stable-code review.

## Final stable kernel and written-proof review

I read the complete submitted `machine.py`, `verify.py`, `PROOF.md`,
`README.md`, `RESULT.json` and `SOURCE-PINS.json`. The program below the
emulator never reads `Tape.head`, allocated-cell arrays, action counts,
`len`, `L`, `M` or a host position counter. Its marker-driven helper calls
have fixed depth and can be inlined. Each stencil atom is one symbol of a
fixed finite product alphabet; tuple decoding and comparison-state updates
therefore have fixed finite-control implementations. Exact READ/WRITE/MOVE
totals are cell/head action counts. The extra finite-control transitions
introduce a uniform constant factor, not free unbounded arithmetic.

The normal program has these independently derived phase counts:

| Phase | Cell/head actions |
|---|---:|
| Initialize counter from stencil; position owned mask | `8L+11` |
| All predicate scans, mask appends and stencil returns | `(6L+8)M` |
| All carries, overflow detection and counter returns | `(2L+5)M-3` |
| Blank private counter data and allocated right marker; return | `5L+6` |
| Owned mask right marker and complete return | `2M+4` |

A successful carry reads exactly `L+2` symbols and makes `L+1` moves,
including its return: if there are t trailing ones, its carry examines t+1
bits and its rewind starts L-t cells from the permanent left sentinel.
The final overflowing carry reads and moves `L+1` times. Together with the
`2M-2` bit changes derived above, these give the third row. Counting each
kind of operation separately gives

```
READ  = (4L+6)M + 5L + 9
WRITE = 3M + 2L + 1
MOVE  = (4L+6)M + 6L + 8
SUM   = 8ML + 15M + 13L + 18.
```

The two length-L roles visit `L+2` cells each. The owned mask role visits
`M+2` cells. Thus complete visited space is exactly `M+2L+6` cells,
including every marker, protected input and owned output. The permanent
left sentinel is initial tape infrastructure; all counter data and its
allocated right marker are restored to blank, and all heads return.
The mask's bits/right marker remain owned output. Reuse obligations are
stated explicitly; no new tape is allocated per record or retained answer.

`cost_check.py` independently imports only this frozen machine, not the
primary verifier. It checks the separately derived per-operation and space
formulas on 14 admitted stencils covering 2,058 complete addresses: all-skip
lengths 1 through 10, single-cell digit and guard begin=end boundaries,
adjacent single-cell digits, and a two-cell MSB-first threshold case. Its
observer-tariff fault omits one READ charge without changing output or
ownership, and the independent invoice rejects it. Its AST checks are
structural guardrails against accessing observer coordinates/counters or
host loop/index helpers; they are not presented as a complete formal proof.
Normal and optimized Python results are recorded in the accompanying report.

The primary's omitted-low-counter-bit mutation is an actual terminating
incorrect enumeration and is rejected by complete output cardinality.
Its omitted-mask-return mutation violates the owned-head contract. Its
threshold/significance/parity mutants and host admission rejections are
accurately separated. There is no claimed private-erasure mutation test;
normal successful blank erasure is inspected and checked directly.

The source-binding geometry uses exactly the low active compact digits and
K-1 higher guard bits, with lower-inclusive/upper-strict comparison. Target
parity, inactive high compact digits, Y spectators and optional dirty back
bits are untested. Complete source fixtures are predicate projections, not
full production reservoir invocations. Geometry/stencil construction and
admission remain explicitly unpriced dependencies; so do exceptional keys,
extraction/sorting/reinsertion, payload movement and the complete evaluator.

No material kernel, exact-invoice, finite-inventory, cleanup, source-interface
or written-cost-proof defect remains in the reviewed stable candidate.
Independent AI review is not human review, formal-kernel acceptance or a
literal emitted finite-state transition-table certificate.
