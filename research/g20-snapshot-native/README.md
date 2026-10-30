# Native G20 snapshots with zero-centre reuse

**Conditional ordinary BIT saving: `0.003487922466`**, an increase of
`0.000001313377` over [PR5641](https://github.com/CrocSwap/integer-mult-bounds/pull/5641).
This is a BIT component construction. The selected complete multiplication
coefficient is unchanged.

This package emits Dugongue [PR5639](https://github.com/CrocSwap/integer-mult-bounds/pull/5639)'s
two SOURCE-snapshot fusions and reuses the old whole-zero centre for one.
The complete 18-call program retains 11,166 independent originals, pays
56,817 queries, and allocates 16 owned banks with no output credit. All
original helper endpoints and old target debits are preserved.

[PROOF.md](PROOF.md) gives the native identity, capture deadlines,
zero-centre proof, complete bill, and finite ordinary certificate.
[WINDOWS.json](WINDOWS.json) and [WINDOW-AUDIT.json](WINDOW-AUDIT.json)
cover all 667 nested blocks without a source observer on every retained
field. Only three admit earlier same-frame binary reconstruction. The
third, helper444, is [handed to its active investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/5638#discussioncomment-19186960)
with a direct SOURCE77 snapshot that replaces five gathers. This package
emits and prices only the two non-overlapping windows.

[INPUTS.json](INPUTS.json) pins every frozen input.
[Discussion5642](https://github.com/CrocSwap/integer-mult-bounds/discussions/5642)
records the claim and scope split. Changed words and paid frame conversions
remain outside the frozen census.

## Reproduce

Python 3.12 and the standard library suffice. The registered command runs
both normal and optimized replay:

```sh
python3.12 -B scripts/research_package.py --package research/g20-snapshot-native
```

For a Git-free package copy, run `python3.12 -I -B verify.py`. Every proof
record is rebuilt in a fresh temporary directory. Exact streams and decoded
payloads must match; only CPU time and gzip metadata are ignored. Frozen
inputs and package files must stay unchanged. Expected output:

```text
PASS_NATIVE_G20_SNAPSHOT_ORDINARY_003487922466
PASS_REGISTERED_RESEARCH_PACKAGE research/g20-snapshot-native outcome=completed
```

The separate adjoint, stream, interval, and census checks are a second
implementation by the same author and AI assistant. They are not
independent scientific acceptance. Retained native/all-width, ROW,
compiler, precision, tape, and analytic contracts remain assumptions.
The finite uniform program and decimal eventual threshold are not
materialized. Full historical suites and formal-kernel proofs are not
part of this replay.

## Open next questions

Complete the helper 444 extension in Discussion 5638 using the direct
snapshot handoff. Further fusions need a changed producer or a priced
frame map. Emit the native continuation and full cost before claiming
a gain. Complete kappa also requires a compatible complex supplier.
More digits of this bill do not provide one.

## Credit

Dugongue supplied the two original fusions; ai-nanachi supplied native G20
and the ordinary framework; Ali Romman supplied PR5421/5641. Retain
DreamingOfClouds, eumemic, Cinna Davis, rohanarun, zxv, Jacob Alan Sussman,
and [all source notices](source/NOTICE.md). Prepared by Ali Romman with
substantial OpenAI Codex assistance. New work is Apache-2.0.
