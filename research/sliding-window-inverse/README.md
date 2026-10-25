# Reuse exact principal-window inverses from one global source

This provides an exact preparation component for streams of overlapping windows:
after one dense initialization, each one-index slide updates the inverse in
**O(m²) rational field operations**, rather than starting another O(m³) dense
inverse. Both Schur deletion/bordering and a rank-two Woodbury route are supplied.
All coefficients and source labels remain bound to the same old-H matrix.

The result combines eight shared-library bridges: Schur, two-sided Woodbury,
robust frames, tensor packing, block-local energy, injective word transport,
footprint frames and locality. [LIBRARY-BRIDGES.md](LIBRARY-BRIDGES.md) explains
what is actually used and which tape theorems remain design precedents.
[PROOF.md](PROOF.md) gives complete sufficient conditions and proofs for the
cache, rounding/residual recovery, polynomial coefficient heights and dirty
exterior. No assumed unknown gadget or oracle replaces those proofs.

**Current relevance:** Jose Manuel's pending PR3851 constructs exact old-H
principal/Schur preparation pages and pays setup separately. This package supplies
a reuse target for that exact matrix boundary; it does not modify his code or
substitute the dense local q-model. Existing protected-page emission, encoded-tape
porting and the complete outer/setup budget still need integration. No new κ,
new physical supplier or end-to-end runtime speedup is claimed.

## Evidence

- 244 exact slides on the immutable upstream 3×3 setup fixture and a separately
  labelled synthetic weighted 13×13 cyclic band matrix; both routes match a
  separate exact solver and satisfy both inverse identities.
- Weighted rounded inverses pass full residual checks and recover deliberately
  integral payloads; correlated/scaled payload columns are included.
- Twelve source-label permutation cases also pass a separate cofactor oracle.
  Controls reject stale sources, aliasing, bad residuals and malformed domains;
  semantic controls expose diagonal double-counting and the wrong old-H model.
- Finite output-port interpretation preserves arbitrary dirty exterior, word
  composition and correlated block/tensor energy bounds.
- Width 8 counts: fresh Gauss–Jordan **1,920** rational field operations;
  Schur slide **414**; Woodbury slide **869**. These are exact instrumented
  arithmetic counts, not wall-clock, bit-cost or multitape measurements.

The universal proofs are informal. A historical typed-DAG Woodbury proof is
identified precisely; it is not a new kernel audit of the combined result.
No production Gaussian domain, native compiler or selected cold replay is claimed.

## Reproduce

Python 3.12 and its standard library, from the repository root:

```sh
python3.12 -B research/sliding-window-inverse/verify.py
python3.12 -B research/sliding-window-inverse/test_cache.py
python3.12 -O -B research/sliding-window-inverse/test_cache.py
python3.12 -B scripts/research_package.py --package research/sliding-window-inverse
```

Ordinary verification is read-only and works without Git. It authenticates the
upstream fixture source before AST-only extraction, regenerates every exact
receipt field and compares it with RESULT.json. The upstream module is never
imported or executed. The independent reference solver imports no cache code.
A frozen source object and explicit digest prevent silently switching matrices.

## Open next questions

1. Wire the cache into a separately priced stream of actual PR3851 overlapping
   windows. First freeze its global H, window index sequence and output-page
   interface; retain all setup scans and output storage. This host algorithm
   alone does not prove fixed-tape complexity or preserve that page layout.
2. Is updating the source's banded factor pages cheaper than emitting them from
   a cached inverse? First price one real shift including coefficient creation,
   factor rounding and protected-page ownership, then compare the complete bill.
3. For source-certified positive weights, test whether weighted-coordinate
   rounding reduces a concrete guard without repaying the gain in scaling work.
   Certify weighted dominance afresh; arbitrary diagonal similarity need not
   preserve ordinary row dominance.

## Credit

Jose Manuel (`jmbarrancoml`), PR3851 at
`7ab67b4a84d28cd562b9711aa315ca5b47822b37`, supplies the exact old-H preparation
contract and the immutable rational setup fixture. His retained line includes
Chafik Boukhalfa/PR489, RaD's phase-cell/microbox construction and PR3787's word
multiplier. Their complete algorithm and physical cost claims are not re-audited
here. Shared MathProof source hashes, declarations and evidence are retained in
LIBRARY-BRIDGES.json. The underlying matrix identities are standard; no exclusive
invention or global absence-of-prior-use claim is made.

Dugongue, with substantial OpenAI Codex assistance. Apache-2.0.
