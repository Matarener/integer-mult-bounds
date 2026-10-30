# Signed mixed-pair capture in the H6 compensation factor

The two sources `(u,v)` and `(u,-v)` share one actual H6 source frame.
Where their `C=I-K` columns are equal or opposite, one ordinary helper can
capture their sum or difference. This gives an exact `DG=C` factor with
**103,680,000 fewer helpers**, retaining both paid source reads. Full-rank
mixed buckets and all pure-source helpers remain unchanged.

| Complete compensation invoice | Before | After |
| --- | ---: | ---: |
| Ordinary helpers | 227,312,640 | 123,632,640 |
| Nonzero scatter entries | 480,337,920 | 260,536,320 |
| Nonzero capture entries | 227,312,640 | 227,312,640 |
| Component primitive allowance | 9,524,090,880 | 6,007,265,280 |

These are exact semantic counts and prescribed scalar upper allowances,
not measured wall-clock/tape costs. The helper reduction is 45.61%; the
compensation scalar allowance decreases 36.93%. Forward logical capture
range grows from `E+X` to `E+2X`. No complete physical precision, allocator,
restoration, all-size supplier or new multiplication exponent is claimed.

The [proof](PROOF.md) specifies the complete factor, the rank-two exception,
same-representative frame legality, arbitrary-dirt forward/dual chronology,
counts and inherited limits. [CERTIFICATE.json](CERTIFICATE.json) records all
16 attainable mixed pairing classes, full reduced-geometry tables by digest,
complete invoices and an all-input-column seed 83 fixture. The entire
30,960-square matrix and multi-billion-event network are not materialized.

## Independent evidence

`verify.py` enumerates doubled E8 directly as an integer lattice and groups
pure fibers by pairing signatures. `independent.py` uses a separate pattern
enumeration and direct lattice cosets, never importing the primary geometry,
factor, invoice or lifecycle code. It extracts the coefficient, Horner tariff
and helper padding convention from authenticated frozen source ASTs.
The two implementations agree on all 120 roots, 1080 pure points, all 256
cosets, 14,400 root/root, 129,600 root/pure and 1,166,400 pure/pure entries.
This is independent exact finite evidence, not a formal verification of the
full multiplication theorem or of the inherited native compiler.

The complete-fiber fixture has 24 data ports and checks every 120 original
or 110 compressed source/target/helper entrance columns, forward and dual.
Its helpers decrease 72→62, scatter entries 216→160, and scalar allowance
4056→3160; capture entries stay 72. The 25 failure controls include matched
wrong capture/cleanup signs, full-rank compression, missing prefix/K/cleanup,
premature source-FULL frames, wrong coefficients, free source reads, typed
receipts and corrupted/removed source pins before execution.

## Reproduce

From the repository root with Python 3.12; no third-party dependencies:

```sh
python3.12 -B scripts/research_package.py --package research/h6-mixed-pair-capture
```

Expected markers: `PASS_H6_MIXED_PAIR_CAPTURE`,
`PASS_INDEPENDENT_H6_PAIR_CAPTURE`, `PASS_H6_CAPTURE_CONTROLS` and
`PASS_REGISTERED_RESEARCH_PACKAGE`. The command is read-only. Standalone scripts also
run from an exported package with its eight declared inputs, without Git.
Receipt generation requires removing the old receipt explicitly and running
`verify.py --write`; the generator refuses any existing destination.

Exact canonical base: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.
[SOURCES.json](SOURCES.json) pins every live input by Git blob and SHA256;
the verifier seals the inventory itself. The selected record and task
catalogue are historical provenance. [TASK.json](TASK.json) records OS seed 83,
domain, stopping rule and the refined independent-verification card.

## Conditional asymmetric K comparison

Ross Richardson's [PR4027](https://github.com/CrocSwap/integer-mult-bounds/pull/4027)
at `1bcc4f8261d2dc322c98fa9e44c4ced43cd1cd95` supplies the unchanged
asymmetric K histogram and scalar bills in [CONTEXT.json](CONTEXT.json).
Conditionally adding those bills gives 6,250,865,392 forward and 6,250,867,840
dual component primitives, before real/imaginary doubling and native adapters.
The complete local rank mass becomes 2,102,773,216
from 3,865,333,216. The certificate also gives formal removed row-stock,
rank mass and padding terms for stages 3,5,7 under the unchanged parent
row convention. Role counts and capture range change too, so these local
differences do not imply a joint moment or κ improvement. No pending K
implementation is imported or independently admitted by this package.

## Open next questions

Can one compress an eight-column pure-source fiber with an affordable capture
matrix? Those 16,727,040 helpers are unchanged; first factor one fiber exactly
and price dense capture, scatter and range before expanding the search.

Can the reduced factor pass full approximate-child and physical admission?
First propagate error through the whole K splice, then bind source access,
restoration, bank placement and pads to actual reserve and the joint BIT
moment. The inherited copied-total/erasure and tape contracts remain blockers.
The structured questions and first steps are in [TASK.json](TASK.json).

## Credit and license

Dominik Scholz's [PR606](https://github.com/CrocSwap/integer-mult-bounds/pull/606)
supplies H6 geometry/factor; DreamingOfClouds supplies the H6 proposal.
The frozen [compensation network](../h6-compensation-network/README.md),
including PR1830's lineage, supplies the bucket, compiler and dirt contract.
Ross Richardson's PR4027 supplies the asymmetric K work and explicitly
identifies the remaining helper burden. Their native/compiler and upstream
attributions remain with the original sources, which are unchanged.

Prepared by Tekalign (`tekuuu`), with substantial OpenAI Codex assistance in
the mathematics, implementations, proof, controls and packaging. Machine
checks are not human peer review. New work is Apache-2.0.
