# Actual Gaussian RHS layout for the physical block boundary

This source-bound bridge executes the actual Gaussian `Core.gather` and
`Core.first_cell` for both complex components, physically packs their RHS
streams, invokes the unchanged `BoundaryPages` consumer, and returns two
scalar streams in the original row order. It pays for the parked component,
all padding, scans, rewinds, protected return consumption and retained backing.
No frozen predecessor is modified.

The five-row case executes both nontrivial interior first passes. Its P=16,
32-bit result differs from its RHS, so bypassing the boundary consumer fails.
B=1 checks separate batches; B=4 on one actual row checks both row and column
padding. An independent Fraction reference checks every actual return.
Physical rejection controls cover component-order discrimination, nonzero
padding, short/trailing streams, metadata/payload aliases, entry heads and
reuse after failures. Nonzero dirty spectators and borrowed backing are retained.

The exact supplied reference is LU(round_P(S)). This implements the rounded
inverse-block function, whose rounding differs from the old scalar BandedSolve.
The original Core's second-cell reconstruction, normalization, full numerical
error allowance and production coefficient generation remain outside scope.
The complete caller is **not installed** by this package, and its classical
consumer does not imply the proposed fast seven-product tariff or a new kappa.

[PROOF.md](PROOF.md) states the source-relative all-size two-component layout
contract and complete cost boundary. Let K=ceil(n/B), J=ceil(2/B), and
A=KJB²w. Adapter payload coexistence is 2A+4nw bits, in addition to original
Core, page, consumer and scalar scratch. Layout work is conservatively
O((A+Jnw+1)(1+log(n+B+w+2))³), including encoded control. Unknown surrounding
supplier obligations are listed rather than priced at zero.

Run with Python 3.12 and the standard library:

```sh
python3.12 -I -B research/physical-boundary-rhs-caller/verify.py
python3.12 -I -O -B research/physical-boundary-rhs-caller/verify.py
python3.12 -I -O -B research/physical-boundary-rhs-caller/test_integrity.py
python3.12 -B scripts/research_package.py --package research/physical-boundary-rhs-caller
```

Normal replay authenticates the complete declared source closure and compares
an immutable typed receipt; `--write` is explicit receipt generation. Scientific
runs allocate only the retained fixed physical pools. Checker fixture generation
and independent reference arithmetic are outside those execution scopes.
[VALIDATION.md](VALIDATION.md) records exact replay/export evidence and limits.
Finite checks do not constitute independent human or formal-kernel review.

Canonical claim: [Discussion4182 comment19172870](https://github.com/CrocSwap/integer-mult-bounds/discussions/4182#discussioncomment-19172870).
Base 32890bc5de034ab8fc93ac88ead7279a6a416d04, priority revision7. The completed
coordination snapshot covered342openPRs and4736Discussion records at
2026-10-25T03:46:07Z /03:48:26Z; exact boundary/RHS terms found no live matching
scope. This is coverage, not a novelty guarantee. The selected PR5413 frontier
and all predecessor bytes remain unchanged.

## Open next questions

- Propagate the block/scalar rounding difference through one actual second-cell
  return and derive a complete numerical allowance before installing this solver.
- Supply a fixed-tape seven-product kernel preserving this exact ABI and its
  full quadrant/parking bill.
- Bind an actual many-field supplier before generalizing R=2 to arbitrary fields.

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0. Credit
Jose Manuel/jmbarrancoml's physical Gaussian Core, runtime and fixture;
JoyboyBrian's inverse-block physical predecessor; Vlado Vojdanovski;
Cinna Davis; Chafik Boukhalfa's interior reference; and the original Gaussian,
FFT, Harvey–van der Hoeven and retained tape-machine lineage.
