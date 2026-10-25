# CRT reservoir placement and coordinate descriptors

**Scoped constructive proof and executable audit of PR4100 CRT.md §3.**
No new κ or complete multiplication theorem is claimed.

For the actual balanced CRT caller, [PROOF.md](PROOF.md) proves that each
synchronized switch layer can be split into at most **25,600 batches** whose
source functions omit three borrowed fields. It handles the whole left-child
control dependency, root inactive quarters, mixed axis widths, integer rounding,
three literal disjoint exchanges, and coordinate reconstruction after those
exchanges split axes. At most `d+12` descriptor fragments suffice. Placement and
restoration cost six width-`H` exchanges per batch; these are not free operations.

The claim is quantified for positive integer `p`, power-of-two `d>=51200`,
`ell>=max(2,ceil(log2(p+2)))`, and every assignment
`w_i in {ell-1,ell}`. With `L=sum w_i`, use the original production constants
`G=64(ell+ceil(log2(p+2)))`, `r_max=floor(L/(100G))`, `H=r_max G`.
The [allocator](allocator.py) rejects layouts outside this domain and generates
plans lazily. Its smaller `Placement` geometry type supports finite checks
without weakening the large-family conditions.

Dirty borrowed values are restored on **all addresses**, conditional on the
completed switch macro's all-address endpoint, including exceptional repair.
The finite caller uses that ideal endpoint explicitly. It does not execute or
reprove a raw compact word. [PR4169](https://github.com/CrocSwap/integer-mult-bounds/pull/4169)
addresses the separate repair boundary and is context, not an imported dependency.

## Evidence

[RESULT.json](RESULT.json) is reproduced without rewriting it by [verify.py](verify.py):

- Complete descriptor census at `d=65536`, alternating widths `24,23`,
  `p=9240576`, `L=1540096`, `G=3072`, `r_max=5`, `H=15360`:
  **104,864 batches**, **524,288 active-axis visits**, all 16 tree levels.
  This is descriptor verification, not a payload execution at that size.
- A separate 12-bit geometry fixture uses the actual CRT control algorithm for
  the root's axis 3 with moduli `(3,5,7,11)`. It checks **all 4,096 dirty addresses**,
  **28,672 single-layer conjugations**, **86,016 omitted-field toggles**, and
  **28,672 forward plus 28,672 inverse steps**, including invalid padded values.
  Its seven layers compose to the exact padded modular rotation; the receipt
  hashes the complete labeled-address permutation. This fixture is below the
  asymptotic cutoff and is not presented as a large-family instance.
- Six semantic controls expose the wrong root reservoir, overlapping exchanges,
  stale coordinates, a global/local bit-index mixup, a false contiguous-axis
  assumption, and an omitted inverse exchange. Four invalid-layout controls
  prevent the tiny fixture or inadmissible widths from entering the production API.

The verifier checks SHA256 and Git blob hashes of all five live source inputs
before loading the predecessor's `benes`, `rotation` and `decode_group` functions.
It compiles the bytes just authenticated, never cached predecessor bytecode.
All checks use explicit exceptions and remain active under `-O`. The quantified
claim comes from the written proof; these finite checks corroborate the code.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/crt-reservoir-placement --check-only
python3.12 -B scripts/research_package.py --package research/crt-reservoir-placement
```

The registered hook runs both ordinary and optimized verification, each with a
180-second limit. To replay a source export with the same relative paths and
without Git, run `python3.12 -I -O -W error -B research/crt-reservoir-placement/verify.py`
from its root. `--write-result` is an explicit receipt-generation option, not part
of either verification command. Source authentication here covers the five live
inputs; the generic metadata/preflight tools check historical provenance and the
exporter's integrity check authenticates the committed package bytes.

Base main is `12fa8c5c844be21bfefb38a19503fbd867a11244`, priority revision 7.
[SOURCES.json](SOURCES.json) pins bytes, [TASK.json](TASK.json) retains the original
card and its refinement, and [Discussion #4173](https://github.com/CrocSwap/integer-mult-bounds/discussions/4173)
is the canonical coordination record. The work starts from main independently
of PR4169. No predecessor implementation, priority or selected record is changed.

## Open next questions

The [structured handoff](TASK.json) asks for an independent fixed-tape invoice
for evaluating the transported controls, including split-axis reconstruction,
ordinary exchanges, head returns and erasure. A first step is to bind the new
descriptors to the actual `E(p,ell)` evaluator in CRT.md §2 and its caller. The
present O(d) descriptor-size bound does not establish that invoice.

The last-`K` tail branch and the ordinary exchange callee remain separate
obligations. This package does not certify the complete CRT, exceptional sorting,
native/free-algebra lift, precision, total machine budget or multiplication theorem.

## Credit

Cinna Davis supplies PR4100's construction and original reservoir argument.
The generic exchange/recoloring methods are credited to Vlado Vojdanovski's
[PR1673 support router](../capped-phase-fusion/SUPPORT-ROUTER.md) and Jose Manuel's
[physical support router](../physical-support-router/PROOF.md). RaD/hipotures,
Zhihao Chen, Douglas Colkitt and the retained routing/compact-control lineage
keep their predecessor credit. The new contribution is the CRT-specific dense
support and descriptor audit, not a new generic swap or repair identity.

Prepared by Hiroki KUMAZAKI (@kumagi), with substantial OpenAI Codex assistance
in derivation, implementation, verification, review and writing. New work is
Apache-2.0. This is not independent human review or proof-assistant formalization.
