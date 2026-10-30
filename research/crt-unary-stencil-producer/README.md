# Paid unary geometry to one-target CRT guard mask

PR4201’s literal scanner accepted an already admitted stencil and left its
geometry/threshold producer unpriced. This package supplies one actual
marker-driven producer for six protected unary geometry words
`G,H,K,Y,J,B_back`, with `G>=1, H>=G, K>=G+4, Y>=J+K` and nonnegative
`J,B_back`. It emits the exact retained stencil for target `J` and composes
with the unchanged scanner. `B_back` is a spectator-bit count; the radix is
`2^G`.

The program pays unary syntax checks, comparisons/subtractions, threshold
construction, all transfers/head returns and erasure of eight private words,
including their right markers. It reads no simulator coordinate, host
length, integer geometry or action counter. All roles and alphabet/control
sizes are fixed. [PROOF.md](PROOF.md) proves the identity and invoice for
**every admitted unary input**. The result starts at this representation;
production/binary/transported geometry conversion and many-target ordering
remain open.

For `L=2H+Y+B_back`, `M=2^L`, one read/write/one-cell move is one action:

- Producer: exactly `33H+25K+38Y-6G-J+12B_back+335 <= 63L+335` actions.
- Unchanged scanner: exactly `8ML+15M+13L+18` actions.
- Composition: exactly the sum, at most `8ML+15M+76L+353`, on seventeen fixed
  roles. Exact visited space is `M+6H+2K+5Y-G+3B_back+42 <= M+7L+42`.

Input values remain protected; all private data and allocated markers are
blank and all heads return. The stencil and complete BAD mask are owned
outputs. A caller must consume and clear previous owned outputs before
reusing these fixed roles. The coefficient counts are for the explicit
finite-alphabet cell/head model; fixed bit encoding gives a constant factor,
not an emitted physical transition table or measured Python cost. The
source’s `O(ML)=O(V)` interpretation additionally needs `L=Theta(p)`,
`R=Theta(p)`, `V=MR` at the actual caller.

## Evidence and reproduction

Primary verification checks 145 produced stencils and exact setup bills,
including tight boundaries, zero inactive fields and a 500-bit stencil;
four unchanged-consumer compositions cover 5,760 addresses. Seven malformed
arithmetic/encoding cases reject with private/output cleanup. Actual producer
faults change parity/threshold semantics, omit cleanup or omit output return;
corrupt source bytes reject before execution.

A code-disjoint oracle was frozen before inspecting the producer. It checks
83 geometries / 433,280 addresses and 360 larger boundary/parity/spectator
cases. `cross_check.py` feeds the paid producer’s output through the
unchanged scanner on every one of those 433,280 addresses, compares the
frozen mask hashes and both original CRT predicates, and executes three
semantic producer faults through the actual consumer. The separate cost
checker instruments primitive calls independently of the simulator bill;
its one-READ undercharge preserves final values/ownership but fails the
invoice. Receipts and exact review coverage accompany the code.

```sh
python3.12 -B scripts/research_package.py --package research/crt-unary-stencil-producer --check-only
python3.12 -B scripts/research_package.py --package research/crt-unary-stencil-producer
python3.12 -B scripts/check_research_commit.py --package research/crt-unary-stencil-producer --check-source-history
```

The registered replay uses Python 3.12’s standard library, in ordinary and
strict optimized modes. Source pins include canonical CRT bytes and four
minimal unchanged PR4201 exports. Pending source exports are retained in
this PR’s own ancestor `5a41fea466cbeb7839bde864e563e191de47a0f7`; the original
source head remains `4f49743a9df0cf7501cdc62bd5707a122fa071e9`.

## Scope, overlap and credit

Handoff-first `uniform-transfer-audit`, refined to one encoded input
boundary; canonical base `12fa8c5c844be21bfefb38a19503fbd867a11244`, priority7.
[Canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/4173#discussioncomment-19075225).
Initial live check covered 322 open/draft PR bodies and current #1166/#4173;
closed/code and broader Discussion coverage is partial. This replaces an
explicitly unpriced local input adapter, not the entire caller. The
family decision is **narrow**, with all other costs retained as unknown in
[TASK.json](TASK.json).

Cinna Davis’s PR4100 supplies the original predicate and ordered-scan
proposal. Hiroki KUMAZAKI (`kumagi`), PR4169/4174, supplies repair/placement
context. PR4201 supplies the scanner, atom format and its proof; those are
predecessor work. Douglas Colkitt/OpenAI and the full retained CRT NOTICE
lineage keep credit. Prepared for ToikY with substantial OpenAI Codex
assistance, including separate producer/proof, pre-code oracle and cost
review contexts. Those checks are not independent human or formal-kernel
acceptance. Apache-2.0. No new κ, supplier admission, merge or selected-frontier
change is claimed.

## Open next questions

Structured questions, relevance, first steps and blockers are in
[TASK.json](TASK.json). The next missing input is a paid producer at the
actual binary/transported source boundary; before expanding, pin that caller
and its complete ownership/cost ledger. Many-target ordering/admission,
exception extraction, inverse keys, sorting, repair/reinsertion, ordinary
callees, full E arithmetic, precision, physical/native and outer composition
remain open. This predicate projection is not a full production reservoir
execution or multiplication theorem.
